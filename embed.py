"""
Milestone 4 (part 1) — embedding + vector store.

Reads chunks.json (produced by chunk.py), embeds each chunk's text with the
all-MiniLM-L6-v2 sentence-transformer, and stores the vectors — together with
their metadata for source attribution — in a persistent ChromaDB collection on
disk (chroma_db/).

Retrieval approach (from planning.md):
  - Embedding model : all-MiniLM-L6-v2 (local, 384-dim, no API key needed)
  - Vector store    : ChromaDB persistent collection
  - Top-k           : 5 (used at query time, see retrieve.py)

Run this once after (re)building chunks.json:
    python embed.py
It is idempotent — the collection is dropped and rebuilt on each run so the
index always matches the current chunks.json.
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_JSON = Path("chunks.json")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "sfsu_food"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 64


def load_chunks():
    """Load the chunk records written by chunk.py."""
    if not CHUNKS_JSON.exists():
        raise FileNotFoundError(
            f"{CHUNKS_JSON} not found — run chunk.py first to build it."
        )
    chunks = json.loads(CHUNKS_JSON.read_text(encoding="utf-8"))
    if not chunks:
        raise ValueError(f"{CHUNKS_JSON} is empty — nothing to embed.")
    return chunks


def get_collection(reset=False):
    """Return the ChromaDB collection, optionally dropping it first.

    Embeddings are supplied explicitly by us (see build_index), so the
    collection itself needs no embedding function configured.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass  # collection didn't exist yet — fine on a first run
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_index():
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_JSON}")

    print(f"Loading embedding model: {EMBED_MODEL} ...")
    model = SentenceTransformer(EMBED_MODEL)

    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks ...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    collection = get_collection(reset=True)
    # Chroma stores only str/int/float/bool in metadata, so keep the scalar
    # fields and use the chunk text as the document body.
    metadatas = [
        {
            "source": c["source"],
            "url": c["url"],
            "type": c["type"],
            "doc_file": c["doc_file"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=metadatas,
    )

    print(
        f"\nIndexed {collection.count()} chunks into ChromaDB "
        f"collection '{COLLECTION_NAME}' at {CHROMA_DIR}/"
    )


if __name__ == "__main__":
    build_index()
