"""
Milestone 3 — chunking.

Reads every .txt file in documents/, splits each document's body into
overlapping chunks, and writes them to chunks.json (plus a human-readable
chunks_preview.txt).

Chunking strategy (from planning.md):
  - Chunk size : 350-500 characters  (target ~450)
  - Overlap    : 50-70 characters    (target ~60)

The splitter is boundary-aware: within the 350-500 window it prefers to cut at
a sentence end (. ! ?) or newline, and otherwise at a word boundary, so a chunk
never ends mid-word. Each new chunk starts ~60 characters before the previous
chunk ended, which preserves context that would otherwise be lost at the seam.

The 3-line header in each document (Source / URL / Type) is parsed into
per-chunk metadata for source attribution and is NOT embedded in the chunk text.
"""

import json
import re
from pathlib import Path

DOC_DIR = Path("documents")
OUT_JSON = Path("chunks.json")
OUT_PREVIEW = Path("chunks_preview.txt")

MIN_CHARS = 350
MAX_CHARS = 500
TARGET = 450
OVERLAP = 60

SENTENCE_END = re.compile(r"[.!?]['\")\]]?\s")


def parse_document(path):
    """Return (metadata dict, body string) for a documents/*.txt file."""
    raw = path.read_text(encoding="utf-8")
    meta = {"source": path.stem, "url": "", "type": ""}
    body_lines = raw.splitlines()
    consumed = 0
    for line in body_lines[:5]:
        if line.startswith("Source:"):
            meta["source"] = line[len("Source:"):].strip()
            consumed += 1
        elif line.startswith("URL:"):
            meta["url"] = line[len("URL:"):].strip()
            consumed += 1
        elif line.startswith("Type:"):
            meta["type"] = line[len("Type:"):].strip()
            consumed += 1
        else:
            break
    body = "\n".join(body_lines[consumed:]).strip()
    # Normalise whitespace: collapse spaces/tabs, keep paragraph breaks as ". "
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n{2,}", "\n\n", body)
    return meta, body


def find_break(text, start):
    """Pick the end index of a chunk beginning at `start`.

    Returns an index in (start, len(text)]. Prefers a sentence boundary, then a
    word boundary, inside the [MIN_CHARS, MAX_CHARS] window.
    """
    hard_end = min(start + MAX_CHARS, len(text))
    if hard_end >= len(text):
        return len(text)

    window_lo = start + MIN_CHARS
    region = text[window_lo:hard_end]

    # 1) last sentence boundary in the window
    last_sentence = None
    for m in SENTENCE_END.finditer(region):
        last_sentence = m.end()
    if last_sentence is not None:
        return window_lo + last_sentence

    # 2) last newline in the window
    nl = region.rfind("\n")
    if nl != -1:
        return window_lo + nl + 1

    # 3) last space in the window
    sp = region.rfind(" ")
    if sp != -1:
        return window_lo + sp + 1

    # 4) nothing found -> hard cut
    return hard_end


def chunk_text(text):
    """Split `text` into overlapping chunks following the strategy above."""
    chunks = []
    pos = 0
    n = len(text)
    while pos < n:
        end = find_break(text, pos)
        chunk = text[pos:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        # back up for overlap, then snap forward to a word boundary
        next_pos = max(pos + 1, end - OVERLAP)
        space = text.find(" ", next_pos)
        if space != -1 and space < end:
            next_pos = space + 1
        pos = next_pos
    return chunks


def main():
    docs = sorted(DOC_DIR.glob("*.txt"))
    all_chunks = []
    per_doc = []
    skipped = []
    for path in docs:
        meta, body = parse_document(path)
        # Skip not-yet-filled templates (e.g. the Yelp pages that block scraping).
        if not body or body.lstrip().startswith("[PASTE"):
            skipped.append(path.name)
            continue
        pieces = chunk_text(body)
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "id": f"{path.stem}::chunk_{i:03d}",
                "source": meta["source"],
                "url": meta["url"],
                "type": meta["type"],
                "doc_file": path.name,
                "chunk_index": i,
                "char_len": len(piece),
                "text": piece,
            })
        per_doc.append((path.name, len(body), len(pieces)))

    OUT_JSON.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    with OUT_PREVIEW.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(f"--- {c['id']}  ({c['char_len']} chars) ---\n{c['text']}\n\n")

    # Report
    print(f"{'document':45s} {'body_chars':>10s} {'chunks':>7s}")
    print("-" * 65)
    for name, blen, nchunks in per_doc:
        print(f"{name:45s} {blen:>10d} {nchunks:>7d}")
    print("-" * 65)
    if all_chunks:
        lens = [c["char_len"] for c in all_chunks]
        print(f"Total chunks: {len(all_chunks)}")
        print(f"Chunk length: min={min(lens)}  max={max(lens)}  avg={sum(lens)//len(lens)}")
        in_range = sum(1 for l in lens if MIN_CHARS <= l <= MAX_CHARS)
        print(f"In 350-500 range: {in_range}/{len(lens)} "
              f"(remainder are last-of-document tails, expected to be shorter)")
    if skipped:
        print(f"\nSkipped {len(skipped)} un-filled template(s): {', '.join(skipped)}")
    print(f"\nWrote {OUT_JSON} and {OUT_PREVIEW}")


if __name__ == "__main__":
    main()
