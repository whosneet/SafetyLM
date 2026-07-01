#!/usr/bin/env python3
"""
chunk_corpus.py — split extracted text into embedding-ready chunks with metadata.

WHAT THIS DOES
--------------
Reads ``corpus/processed/text/<source_id>.txt`` (from extract_text.py), splits each document
into ~512-token chunks with ~64-token overlap (per docs/03-corpus-strategy.md), and writes
one JSON object per chunk to ``corpus/processed/chunks.jsonl``. Every chunk inherits the full
manifest metadata for its ``source_id`` (jurisdiction, document_type, currency, hazard, tier,
licence, url, …) so retrieval can filter on it downstream.

CHUNKING STRATEGY (structure-aware, as specified in Phase 0)
-----------------------------------------------------------
- Target 512 tokens / 64-token overlap.
- Splits on paragraph boundaries and never mid-word; overlap is carried as whole trailing
  paragraphs (up to ~64 tokens) so a clause split across a boundary keeps its context.
- Tracks the current section heading (legislative markers: Part / Division / Section /
  Schedule / Clause / numbered headings) and stores it on each chunk.
- A single oversized paragraph is windowed by tokens (512 with 64 overlap).

TOKENIZER NOTE
--------------
Uses tiktoken's ``cl100k_base`` as a fast, permissive (MIT) proxy for token counting. This is
close but NOT identical to the eventual embedding model's tokenizer (bge-m3 is the Phase-4
benchmark candidate). Swap ``count_tokens`` for the chosen model's tokenizer in Phase 2 if
exact 512-token windows matter; for chunk *sizing* the proxy is fine.

INPUT  : corpus/processed/text/<source_id>.txt   +   corpus/manifest/corpus_manifest.csv
OUTPUT : corpus/processed/chunks.jsonl           +   corpus/processed/_chunk_log.csv

USAGE:
  uv run scripts/chunk_corpus.py
  uv run scripts/chunk_corpus.py --max-tokens 512 --overlap 64
  uv run scripts/chunk_corpus.py --limit 5
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST = ROOT / "corpus" / "manifest" / "corpus_manifest.csv"
TEXT_DIR = ROOT / "corpus" / "processed" / "text"
CHUNKS_PATH = ROOT / "corpus" / "processed" / "chunks.jsonl"
LOG_PATH = ROOT / "corpus" / "processed" / "_chunk_log.csv"

# manifest fields copied onto every chunk (retrieval filters use these)
META_FIELDS = [
    "jurisdiction", "regulator", "document_type", "document_title", "instrument_id",
    "url", "legislative_currency", "hazard_category", "industry_relevance",
    "priority_tier", "pre_harmonisation", "license_notes",
]

HEADING_RE = re.compile(
    r"^(part|division|subdivision|schedule|chapter|section|clause|appendix)\b",
    re.IGNORECASE,
)
NUMBERED_RE = re.compile(r"^\d+(\.\d+)*[\.\)]?\s+\S")


def make_counter():
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    return enc


def is_heading(para: str) -> bool:
    if "\n" in para:
        return False
    p = para.strip()
    if not p or len(p) > 120:
        return False
    if HEADING_RE.match(p) or NUMBERED_RE.match(p):
        return True
    # Title/UPPER case line with no terminal sentence punctuation
    if p[-1] not in ".:;," and (p.isupper() or p.istitle()):
        return len(p.split()) <= 12
    return False


def chunk_document(text: str, enc, max_tokens: int, overlap: int):
    """Yield (section_heading, chunk_text, token_count) tuples."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    cur: list[str] = []
    cur_tok = 0
    heading = ""
    out = []

    def flush():
        if cur:
            body = "\n\n".join(cur)
            out.append((heading, body, len(enc.encode(body))))

    for p in paras:
        if is_heading(p):
            heading = p[:200]
        ptok = len(enc.encode(p))

        if ptok > max_tokens:
            flush(); cur.clear(); cur_tok_reset = True
            cur_tok = 0
            ids = enc.encode(p)
            i = 0
            step = max(1, max_tokens - overlap)
            while i < len(ids):
                window = ids[i:i + max_tokens]
                wtext = enc.decode(window)
                out.append((heading, wtext, len(window)))
                i += step
            continue

        if cur and cur_tok + ptok > max_tokens:
            flush()
            # start next chunk with trailing paragraphs (~overlap tokens) for context
            carry, ct = [], 0
            for q in reversed(cur):
                qt = len(enc.encode(q))
                if ct + qt > overlap:
                    break
                carry.insert(0, q); ct += qt
            cur[:] = carry
            cur_tok = ct

        cur.append(p); cur_tok += ptok

    flush()
    return out


def load_manifest():
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        return {r["source_id"]: r for r in csv.DictReader(fh)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Chunk extracted corpus text with metadata.")
    ap.add_argument("--text", default=str(TEXT_DIR))
    ap.add_argument("--out", default=str(CHUNKS_PATH))
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--overlap", type=int, default=64)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    text_dir = Path(args.text)
    if not text_dir.exists():
        print(f"ERROR: {text_dir} not found — run extract_text.py first.", file=sys.stderr)
        return 1

    enc = make_counter()
    manifest = load_manifest()
    files = sorted(text_dir.glob("*.txt"))
    if args.limit:
        files = files[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    log_rows = []
    total_chunks = 0
    missing_meta = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for fp in files:
            source_id = fp.stem
            meta = manifest.get(source_id)
            if meta is None:
                missing_meta += 1
                log_rows.append({"source_id": source_id, "chunks": 0,
                                 "note": "no manifest row for this source_id"})
                continue
            text = fp.read_text(encoding="utf-8")
            chunks = chunk_document(text, enc, args.max_tokens, args.overlap)
            for i, (section, body, ntok) in enumerate(chunks):
                rec = {
                    "chunk_id": f"{source_id}::{i:04d}",
                    "source_id": source_id,
                    "chunk_index": i,
                    "section": section,
                    "token_count": ntok,
                    "char_len": len(body),
                    "text": body,
                }
                for k in META_FIELDS:
                    rec[k] = meta.get(k, "")
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            total_chunks += len(chunks)
            log_rows.append({"source_id": source_id, "chunks": len(chunks),
                             "note": ""})

    with open(LOG_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["source_id", "chunks", "note"])
        w.writeheader(); w.writerows(log_rows)

    docs = len([r for r in log_rows if r["chunks"]])
    counts = [r["chunks"] for r in log_rows if r["chunks"]]
    print(f"Documents chunked: {docs}  | total chunks: {total_chunks}")
    if counts:
        print(f"Chunks/doc: min={min(counts)} median~{sorted(counts)[len(counts)//2]} max={max(counts)}")
    if missing_meta:
        print(f"WARNING: {missing_meta} text files had no manifest row (skipped).")
    print(f"Output: {out_path.relative_to(ROOT)}  ({total_chunks} lines)")
    print(f"Log: {LOG_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
