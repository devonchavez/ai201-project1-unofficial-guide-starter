"""
Milestone 4 (part 2) — retrieval.

Embeds a user question with the same all-MiniLM-L6-v2 model used at index time
and queries the ChromaDB collection for the top-k=5 most similar chunks
(cosine distance). Returns the chunks with their source-attribution metadata so
the generation step (Milestone 5) can both ground its answer and cite sources.

Use as a library:
    from retrieve import Retriever
    r = Retriever()
    hits = r.retrieve("popular item at the Halal shop?")

Or run directly as a quick retrieval-only smoke test:
    python retrieve.py "where is the Vista Room located?"
"""

import sys

import chromadb
from sentence_transformers import SentenceTransformer

from embed import CHROMA_DIR, COLLECTION_NAME, EMBED_MODEL

TOP_K = 5  # from planning.md


class Retriever:
    """Loads the embedding model + ChromaDB collection once and reuses them."""

    def __init__(self, top_k=TOP_K):
        self.top_k = top_k
        self.model = SentenceTransformer(EMBED_MODEL)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            self.collection = client.get_collection(COLLECTION_NAME)
        except Exception as exc:
            raise RuntimeError(
                f"Collection '{COLLECTION_NAME}' not found — run embed.py first."
            ) from exc

    def retrieve(self, query, top_k=None):
        """Return a list of the top-k chunks most relevant to `query`.

        Each result is a dict: id, text, source, url, type, doc_file,
        chunk_index, and `score` (cosine similarity in [0, 1], higher = closer).
        """
        k = top_k or self.top_k
        query_embedding = self.model.encode(
            [query], normalize_embeddings=True
        )[0].tolist()

        res = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            hits.append(
                {
                    "text": doc,
                    "source": meta.get("source", ""),
                    "url": meta.get("url", ""),
                    "type": meta.get("type", ""),
                    "doc_file": meta.get("doc_file", ""),
                    "chunk_index": meta.get("chunk_index"),
                    # Chroma cosine distance = 1 - cosine similarity.
                    "score": round(1 - dist, 4),
                }
            )
        return hits


def main():
    if len(sys.argv) < 2:
        print('Usage: python retrieve.py "your question here"')
        sys.exit(1)
    query = " ".join(sys.argv[1:])

    retriever = Retriever()
    hits = retriever.retrieve(query)

    print(f"\nQuery: {query}")
    print(f"Top {len(hits)} chunks:\n" + "=" * 70)
    for rank, h in enumerate(hits, 1):
        print(f"\n[{rank}] score={h['score']}  source: {h['source']}")
        print(f"    {h['url']}")
        print(f"    {h['text']}")


if __name__ == "__main__":
    main()
