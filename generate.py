"""
Milestone 5 (part 1) — grounded generation with validated source attribution.

Takes a user question, retrieves the top-k chunks (retrieve.py), and asks a Groq
LLM to answer using ONLY those chunks. Grounding and attribution are enforced —
not merely requested — at three layers:

  1. Structural — the model never sees the corpus, only the retrieved chunks,
     formatted as a numbered list of sources. Very-low-relevance chunks are
     filtered out before the model ever sees them.
  2. Instructional — a strict system prompt tells the model to answer only from
     the numbered context and to declare which source numbers it used.
  3. Programmatic — the model must return structured JSON
     {answer, cited_sources}. We validate every cited number against the real
     retrieved set, render ONLY validated sources, and treat an answer that
     cites nothing as ungrounded (→ a fixed fallback message). So the source
     list the user sees is derived from retrieval + validation, never from
     free-text the model could hallucinate.

  Note: true per-sentence proof that a claim came from the context is not
  achievable with an LLM. What is guaranteed here is that every *displayed*
  source was retrieved and explicitly claimed by the model, that invalid
  citations are dropped, and that an uncited answer is never shown.

Use as a library:
    from generate import GroundedGenerator
    gen = GroundedGenerator()
    result = gen.answer("popular item at the Halal shop?")
    print(result.text)
    for s in result.sources: print(s.number, s.source, s.url)

Or run directly as a quick end-to-end smoke test:
    python generate.py "where is the Vista Room located?"
"""

import json
import os
import sys
from dataclasses import dataclass, field

from dotenv import load_dotenv
from groq import Groq

from retrieve import Retriever

# Groq's hosted Llama model — fast, free tier, good enough for short grounded
# answers. Swap via the GROQ_MODEL env var without touching code.
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# Chunks below this cosine-similarity score are dropped before generation. The
# retriever always returns top-k, even for off-topic questions; this guard stops
# barely-related chunks from being offered as "context" the model might lean on.
MIN_SCORE = 0.15

# Shown whenever the system cannot produce a grounded, cited answer.
UNGROUNDED_MSG = "I don't have enough information on that."

SYSTEM_PROMPT = """\
You are The Unofficial Guide, a question-answering assistant for students looking \
for good and affordable food in and around San Francisco State University (SFSU).

You are given a numbered CONTEXT (a list of source excerpts). Follow these rules \
without exception:
1. Answer the question using ONLY the information in the provided documents \
(the CONTEXT). Never use outside or prior knowledge, and never guess.
2. If the documents don't contain enough information to answer, set "answer" to \
an empty string and "cited_sources" to an empty list (the system will then reply \
"I don't have enough information on that.").
3. Otherwise, write a concise, specific answer and list the EXACT source numbers \
you used in "cited_sources". Only include a number if that source genuinely \
supports your answer. In the answer text, mark each claim with its source number \
in square brackets, e.g. "[3]".

Respond with ONLY a JSON object of this exact shape, nothing else:
{"answer": "<your answer, or empty string>", "cited_sources": [<source numbers>]}\
"""


@dataclass
class Source:
    """One retrieved chunk's attribution, surfaced alongside the answer.

    Only sources the model actually cited (and that passed validation) become
    Source objects, so this list is the programmatic attribution guarantee.
    """

    number: int  # the [n] the model cited
    source: str
    url: str
    type: str
    score: float


@dataclass
class Answer:
    """The grounded generation result returned to the interface layer."""

    question: str
    text: str
    sources: list = field(default_factory=list)  # list[Source], citation order
    grounded: bool = True  # False when no valid citation backed the answer

    def formatted(self):
        """Render the full response format: answer text + attributed sources.

        This is the canonical output format — the answer is always followed by
        the "Sources" section that maps each [n] citation in the answer to the
        real document it came from, so attribution travels with the response
        wherever it's used. When the answer isn't grounded there are no sources
        to attribute, so just the message is returned.
        """
        if not self.sources:
            return self.text
        lines = [self.text, "", "**Sources**"]
        for s in self.sources:
            lines.append(
                f"- **[{s.number}] {s.source}** ({s.type}) · relevance {s.score:.2f}  \n"
                f"  {s.url}"
            )
        return "\n".join(lines)


def _format_context(hits):
    """Render retrieved chunks as a numbered context block for the prompt."""
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(
            f"[{i}] Source: {h['source']} ({h['type']})\n"
            f"URL: {h['url']}\n"
            f"{h['text']}"
        )
    return "\n\n".join(blocks)


def _parse_response(raw):
    """Parse the model's JSON reply into (answer_text, cited_numbers).

    Defensive: the response_format=json_object setting makes Groq return valid
    JSON, but we still guard against malformed shapes rather than trusting it.
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return "", []
    answer = data.get("answer", "")
    cited = data.get("cited_sources", [])
    if not isinstance(answer, str):
        answer = str(answer)
    if not isinstance(cited, list):
        cited = []
    # Coerce to ints, drop anything non-numeric.
    clean = []
    for n in cited:
        try:
            clean.append(int(n))
        except (ValueError, TypeError):
            continue
    return answer.strip(), clean


class GroundedGenerator:
    """Wires retrieval + Groq generation + citation validation into one call."""

    def __init__(self, retriever=None, model=None):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
                "key from https://console.groq.com"
            )
        self.client = Groq(api_key=api_key)
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
        self.retriever = retriever or Retriever()

    def answer(self, question, min_score=MIN_SCORE):
        """Retrieve, ground, generate, and validate citations for `question`."""
        question = (question or "").strip()
        if not question:
            return Answer(question, "Please enter a question.", [], grounded=False)

        hits = self.retriever.retrieve(question)
        hits = [h for h in hits if h["score"] >= min_score]
        if not hits:
            return Answer(question, UNGROUNDED_MSG, [], grounded=False)

        context = _format_context(hits)
        user_prompt = (
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION: {question}\n\n"
            "Answer using only the context above. Return the JSON object described "
            "in the instructions, citing the source numbers you used."
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,  # low — we want faithful, not creative, answers
            max_tokens=700,
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content
        text, cited = _parse_response(raw)

        # --- Programmatic citation validation -------------------------------
        # Keep only citations that point at a real retrieved source (1..len),
        # de-duplicated and in the order the model gave them.
        valid_numbers = []
        seen = set()
        for n in cited:
            if 1 <= n <= len(hits) and n not in seen:
                valid_numbers.append(n)
                seen.add(n)

        # An answer with no valid citation is treated as ungrounded and never
        # shown — this is the enforcement, not a suggestion.
        if not text or not valid_numbers:
            return Answer(question, UNGROUNDED_MSG, [], grounded=False)

        sources = [
            Source(
                number=n,
                source=hits[n - 1]["source"],
                url=hits[n - 1]["url"],
                type=hits[n - 1]["type"],
                score=hits[n - 1]["score"],
            )
            for n in valid_numbers
        ]
        return Answer(question, text, sources, grounded=True)


def main():
    if len(sys.argv) < 2:
        print('Usage: python generate.py "your question here"')
        sys.exit(1)
    question = " ".join(sys.argv[1:])

    gen = GroundedGenerator()
    result = gen.answer(question)

    print(f"\nQ: {result.question}\n" + "=" * 70)
    print(result.formatted())


if __name__ == "__main__":
    main()
