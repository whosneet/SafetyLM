#!/usr/bin/env python3
"""
extract_text.py — turn downloaded raw documents into clean plain text.

WHAT THIS DOES
--------------
Reads every file in ``corpus/raw/`` (produced by download_corpus.py) and writes clean,
normalised text to ``corpus/processed/text/<source_id>.txt``, plus an extraction log.

HANDLES THREE CASES (this is the messy reality of gov documents)
----------------------------------------------------------------
1. PDF  -> text via pdfplumber (MIT; no AGPL PyMuPDF), page by page.
2. HTML that IS the document (legislation registers return the full Act/Reg text as HTML)
   -> main-content text via BeautifulSoup, boilerplate (nav/scripts/footers) stripped.
3. HTML landing/wrapper page (e.g. Safe Work Australia /doc/ pages whose body is just a
   blurb + a link to the real PDF) -> detected as "thin", the primary PDF link is followed,
   downloaded, and extracted as a PDF instead. Needs network egress for this case only.

Scanned/image-only PDFs (no text layer) extract empty and are flagged for OCR (out of scope).

INPUT  : corpus/raw/<source_id>.<ext>   +   corpus/manifest/corpus_manifest.csv (metadata/URLs)
OUTPUT : corpus/processed/text/<source_id>.txt   +   corpus/processed/_extract_log.csv

USAGE:
  uv run scripts/extract_text.py            # extract everything in corpus/raw/
  uv run scripts/extract_text.py --force    # re-extract existing
  uv run scripts/extract_text.py --limit 10 # smoke test
  uv run scripts/extract_text.py --no-follow-pdf   # never fetch (fully offline)
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST = ROOT / "corpus" / "manifest" / "corpus_manifest.csv"
RAW_DIR = ROOT / "corpus" / "raw"
OUT_DIR = ROOT / "corpus" / "processed" / "text"
LOG_PATH = ROOT / "corpus" / "processed" / "_extract_log.csv"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
THIN_HTML_CHARS = 4000  # below this, an HTML page with a PDF link is treated as a wrapper
LOG_FIELDS = ["source_id", "source_file", "method", "chars", "ok", "note"]


def clean_text(text: str) -> str:
    """Normalise whitespace: trim lines, collapse blank runs, drop empty leading/trailing."""
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    out, blanks = [], 0
    for ln in lines:
        if ln.strip():
            out.append(re.sub(r"[ \t]+", " ", ln)); blanks = 0
        else:
            blanks += 1
            if blanks <= 1 and out:
                out.append("")
    return "\n".join(out).strip()


def extract_pdf(path: Path) -> str:
    import pdfplumber
    parts = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return clean_text("\n\n".join(parts))


def html_main_text(html: bytes) -> tuple[str, "BeautifulSoup"]:  # type: ignore[name-defined]
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form",
                     "noscript", "svg", "button"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.find("body") or soup
    return clean_text(main.get_text("\n")), soup


def find_pdf_link(soup, page_url: str) -> str | None:
    """Pick the most likely 'main document' PDF link from a landing page."""
    candidates = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if ".pdf" in href.lower():
            label = (a.get_text() or "").lower()
            score = 0
            if any(k in label for k in ("download", "pdf", "code", "guide", "act", "regulation")):
                score += 1
            if "sites/default/files" in href or "/documents/" in href or "assets" in href:
                score += 1
            candidates.append((score, urljoin(page_url, href)))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def load_manifest() -> dict[str, dict]:
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        return {r["source_id"]: r for r in csv.DictReader(fh)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract clean text from downloaded corpus docs.")
    ap.add_argument("--raw", default=str(RAW_DIR))
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-follow-pdf", action="store_true",
                    help="never fetch a landing page's PDF link (fully offline)")
    args = ap.parse_args()

    raw_dir, out_dir = Path(args.raw), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    files = sorted(p for p in raw_dir.iterdir()
                   if p.is_file() and not p.name.startswith((".", "_")))
    if args.limit:
        files = files[: args.limit]

    client = None
    if not args.no_follow_pdf:
        import httpx
        client = httpx.Client(headers={"User-Agent": UA}, follow_redirects=True, timeout=30.0)

    records, done = [], 0
    for path in files:
        source_id = path.stem
        rec = {k: "" for k in LOG_FIELDS}
        rec.update(source_id=source_id, source_file=path.name, ok="false")
        target = out_dir / f"{source_id}.txt"
        if target.exists() and not args.force:
            rec.update(ok="true", method="cached", chars=str(target.stat().st_size),
                       note="skipped: already extracted")
            records.append(rec); continue
        try:
            ext = path.suffix.lower().lstrip(".")
            if ext == "pdf":
                text, method = extract_pdf(path), "pdf"
            elif ext in ("html", "htm", "txt"):
                text, soup = html_main_text(path.read_bytes())
                method = "html"
                if len(text) < THIN_HTML_CHARS and client is not None:
                    page_url = manifest.get(source_id, {}).get("url", "")
                    pdf_url = find_pdf_link(soup, page_url) if page_url else None
                    if pdf_url:
                        try:
                            r = client.get(pdf_url)
                            if r.status_code == 200 and r.content:
                                tmp = out_dir / f".{source_id}.pdf"
                                tmp.write_bytes(r.content)
                                text2 = extract_pdf(tmp)
                                tmp.unlink(missing_ok=True)
                                if len(text2) > len(text):
                                    text, method = text2, "followed_pdf"
                                    rec["note"] = f"followed PDF link: {pdf_url}"
                        except Exception as e:  # keep the thin HTML text on failure
                            rec["note"] = f"pdf-follow failed ({type(e).__name__})"
            else:
                rec["note"] = f"unsupported extension: .{ext}"
                records.append(rec); continue

            if not text.strip():
                rec.update(method=method, chars="0", note=(rec["note"] + "; empty extraction "
                           "(scanned PDF? needs OCR)").lstrip("; "))
                records.append(rec); continue

            target.write_text(text, encoding="utf-8")
            rec.update(ok="true", method=method, chars=str(len(text)))
            done += 1
        except Exception as e:
            rec["note"] = f"{type(e).__name__}: {e}"
        records.append(rec)
        if len(records) % 25 == 0:
            print(f"  {len(records)}/{len(files)} processed ({done} written)", file=sys.stderr)

    if client is not None:
        client.close()

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS); w.writeheader(); w.writerows(records)

    from collections import Counter
    ok = [r for r in records if r["ok"] == "true" and "skipped" not in r["note"]]
    empty = [r for r in records if r["chars"] == "0"]
    failed = [r for r in records if r["ok"] == "false" and r["chars"] != "0"]
    print(f"\nExtracted: {len(ok)}  | methods: "
          f"{dict(Counter(r['method'] for r in ok))}")
    print(f"Empty (needs OCR / follow failed): {len(empty)}  | Failed: {len(failed)}")
    if ok:
        chars = [int(r["chars"]) for r in ok]
        print(f"Text size: min={min(chars)} median~{sorted(chars)[len(chars)//2]} max={max(chars)} chars")
    print(f"Log: {LOG_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
