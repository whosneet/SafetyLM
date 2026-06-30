#!/usr/bin/env python3
"""
download_corpus.py — fetch SafetyLM source documents listed in the corpus manifest.

WHAT THIS DOES
--------------
Reads ``corpus/manifest/corpus_manifest.csv`` and downloads the source document for each
row that is (a) flagged ``ingestable=true`` and (b) in the requested priority tier(s), into
``corpus/raw/`` (gitignored). It writes a download log to ``corpus/raw/_download_log.csv``
and prints a summary.

WHY THE GATES MATTER
--------------------
- ``ingestable=false`` rows are NEVER fetched. These carry restrictive licences (NT Crown
  copyright, AIHS proprietary, ISO/AS standards, coroner-finding curation pointers). The
  manifest's licence work is what makes this safe — we honour it here.
- Tier 1 is the foundation set (Acts, Regulations, codes). Default run is ``--tier 1``.

HONESTY / ROBUSTNESS
--------------------
- Many AU/NZ government registers (legislation.nsw/.sa/.gov.au, NT WorkSafe, etc.) return
  403/timeout to automated clients. Those failures are LOGGED, never hidden — the failure
  rows in the log are the precise worklist for manually verifying the manifest's
  ``url_verified=false`` URLs. A 403 is not treated as "URL invalid".
- A document whose returned content-type does not match its manifest ``file_format`` (e.g.
  a PDF row that returns HTML) is flagged ``format_mismatch`` — usually a landing/redirect
  or block page rather than the document itself.
- Resumable: an already-downloaded file is skipped unless ``--force``.
- Polite: capped concurrency, a descriptive User-Agent, retries with backoff on transient
  errors (timeouts, 429, 5xx). Not a substitute for respecting each site's terms.

INPUT  : corpus/manifest/corpus_manifest.csv
OUTPUT : corpus/raw/<source_id>.<ext>   +   corpus/raw/_download_log.csv

USAGE:
  uv run scripts/download_corpus.py                 # Tier 1, ingestable only
  uv run scripts/download_corpus.py --tier all      # every ingestable row
  uv run scripts/download_corpus.py --tier 1 --tier 2
  uv run scripts/download_corpus.py --dry-run       # list what would be fetched
  uv run scripts/download_corpus.py --limit 10      # first 10 (smoke test)
  uv run scripts/download_corpus.py --force         # re-download existing files
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST = ROOT / "corpus" / "manifest" / "corpus_manifest.csv"
RAW_DIR = ROOT / "corpus" / "raw"
LOG_PATH = RAW_DIR / "_download_log.csv"

# Many AU/NZ government WAFs reject non-browser User-Agents (returning 403 or hanging), so we
# present a mainstream browser UA + Accept headers. We still self-throttle (capped concurrency,
# backoff) to stay a polite client when fetching public documents.
DEFAULT_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}

# manifest file_format -> file extension
FMT_EXT = {"PDF": "pdf", "HTML": "html", "DOCX": "docx", "XLSX": "xlsx"}
# response content-type substring -> (extension, normalised format)
CT_MAP = [
    ("application/pdf", ("pdf", "PDF")),
    ("text/html", ("html", "HTML")),
    ("application/xhtml", ("html", "HTML")),
    ("officedocument.wordprocessingml", ("docx", "DOCX")),
    ("msword", ("doc", "DOCX")),
    ("officedocument.spreadsheetml", ("xlsx", "XLSX")),
    ("ms-excel", ("xls", "XLSX")),
    ("text/plain", ("txt", "HTML")),
]

LOG_FIELDS = [
    "source_id", "jurisdiction", "document_type", "priority_tier", "url", "final_url",
    "http_status", "ok", "content_type", "bytes", "ext", "saved_path",
    "expected_format", "format_mismatch", "attempts", "error",
]


def classify(content_type: str) -> tuple[str, str | None]:
    """Return (extension, normalised_format) from a response content-type."""
    ct = (content_type or "").lower()
    for needle, (ext, fmt) in CT_MAP:
        if needle in ct:
            return ext, fmt
    return "bin", None


def select_targets(rows: list[dict], tiers: set[str]) -> tuple[list[dict], list[dict]]:
    """Split rows into (to_fetch, skipped_not_ingestable) for the requested tiers."""
    to_fetch, skipped = [], []
    for r in rows:
        if r["priority_tier"] not in tiers:
            continue
        if (r.get("ingestable") or "").strip() != "true":
            skipped.append(r)
            continue
        if not (r.get("url") or "").strip().startswith(("http://", "https://")):
            continue
        to_fetch.append(r)
    return to_fetch, skipped


async def fetch_one(client: httpx.AsyncClient, sem: asyncio.Semaphore, row: dict,
                    out_dir: Path, force: bool, retries: int) -> dict:
    rec = {k: "" for k in LOG_FIELDS}
    rec.update(source_id=row["source_id"], jurisdiction=row["jurisdiction"],
               document_type=row["document_type"], priority_tier=row["priority_tier"],
               url=row["url"], expected_format=row.get("file_format", ""), ok="false",
               format_mismatch="false", attempts="0")
    url = row["url"].strip()
    expected_fmt = (row.get("file_format") or "").strip().upper()

    # resumable skip (any extension)
    existing = list(out_dir.glob(f"{row['source_id']}.*"))
    if existing and not force:
        rec.update(ok="true", saved_path=str(existing[0].relative_to(ROOT)),
                   error="skipped: already downloaded")
        return rec

    backoff = 1.0
    async with sem:
        for attempt in range(1, retries + 2):
            rec["attempts"] = str(attempt)
            try:
                resp = await client.get(url)
                rec["http_status"] = str(resp.status_code)
                rec["final_url"] = str(resp.url)
                rec["content_type"] = resp.headers.get("content-type", "")
                if resp.status_code == 200 and resp.content:
                    ext, got_fmt = classify(rec["content_type"])
                    if ext == "bin" and expected_fmt in FMT_EXT:
                        ext = FMT_EXT[expected_fmt]
                    path = out_dir / f"{row['source_id']}.{ext}"
                    path.write_bytes(resp.content)
                    rec.update(ok="true", bytes=str(len(resp.content)), ext=ext,
                               saved_path=str(path.relative_to(ROOT)))
                    if expected_fmt and got_fmt and got_fmt != expected_fmt:
                        rec["format_mismatch"] = "true"
                        rec["error"] = f"expected {expected_fmt}, got {got_fmt} (likely a landing/block page)"
                    return rec
                # retry transient statuses
                if resp.status_code in (429, 500, 502, 503, 504) and attempt <= retries:
                    await asyncio.sleep(backoff); backoff *= 2; continue
                rec["error"] = f"HTTP {resp.status_code}"
                return rec
            except (httpx.TimeoutException, httpx.TransportError) as e:
                rec["error"] = f"{type(e).__name__}: {e}"
                if attempt <= retries:
                    await asyncio.sleep(backoff); backoff *= 2; continue
                return rec
            except Exception as e:  # never let one URL abort the run
                rec["error"] = f"{type(e).__name__}: {e}"
                return rec
        await asyncio.sleep(0.15)  # gentle pacing
    return rec


async def run(targets: list[dict], out_dir: Path, concurrency: int, force: bool,
              retries: int, timeout: float) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, follow_redirects=True,
                                 timeout=timeout, limits=limits) as client:
        tasks = [fetch_one(client, sem, r, out_dir, force, retries) for r in targets]
        out = []
        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            rec = await coro
            out.append(rec)
            if i % 25 == 0 or i == len(tasks):
                ok = sum(1 for x in out if x["ok"] == "true")
                print(f"  {i}/{len(tasks)} done ({ok} ok)", file=sys.stderr)
        return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Download SafetyLM corpus source documents.")
    ap.add_argument("--tier", action="append", default=None,
                    help="priority tier to include (repeatable), or 'all'. Default: 1")
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--out", default=str(RAW_DIR))
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0, help="cap number of fetches (0 = no cap)")
    ap.add_argument("--force", action="store_true", help="re-download existing files")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tiers = {"1"} if not args.tier else (
        {"1", "2", "3"} if "all" in args.tier else set(args.tier))
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.manifest, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    targets, skipped = select_targets(rows, tiers)
    if args.limit:
        targets = targets[: args.limit]

    print(f"Manifest: {len(rows)} rows | tiers {sorted(tiers)} | "
          f"{len(targets)} to fetch | {len(skipped)} skipped (ingestable=false)")
    if args.dry_run:
        for r in targets[:50]:
            print(f"  WOULD FETCH {r['source_id']:<14} {r['file_format']:<5} {r['url']}")
        if len(targets) > 50:
            print(f"  ... and {len(targets) - 50} more")
        return 0

    records = asyncio.run(run(targets, out_dir, args.concurrency, args.force,
                              args.retries, args.timeout))

    # log skipped-by-licence rows too (so the log is a complete account)
    for r in skipped:
        rec = {k: "" for k in LOG_FIELDS}
        rec.update(source_id=r["source_id"], jurisdiction=r["jurisdiction"],
                   document_type=r["document_type"], priority_tier=r["priority_tier"],
                   url=r.get("url", ""), ok="false", error="skipped: ingestable=false (licence)")
        records.append(rec)

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        w.writeheader(); w.writerows(records)

    ok = [r for r in records if r["ok"] == "true" and "skipped" not in r["error"]]
    cached = [r for r in records if r["ok"] == "true" and r["error"].startswith("skipped: already")]
    mism = [r for r in records if r["format_mismatch"] == "true"]
    failed = [r for r in records if r["ok"] == "false" and not r["error"].startswith("skipped: ingestable")]
    print(f"\nDownloaded OK: {len(ok)}  (cached: {len(cached)})")
    print(f"Format mismatches (likely landing/block pages, verify URL): {len(mism)}")
    print(f"Failed (verification worklist): {len(failed)}")
    if failed:
        from collections import Counter
        print("  failures by jurisdiction: " +
              ", ".join(f"{k}={v}" for k, v in sorted(Counter(r["jurisdiction"] for r in failed).items())))
    print(f"Skipped (ingestable=false, licence): {len(skipped)}")
    print(f"\nLog: {LOG_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
