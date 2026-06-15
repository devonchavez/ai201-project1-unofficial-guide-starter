"""
Milestone 5 (part 2) — query interface (Gradio).

A minimal web UI over the full RAG pipeline:
    question -> retrieve top-k chunks -> grounded Groq answer (validated cites)
    -> answer text + the source list the answer was actually built from.

The heavy objects (embedding model, ChromaDB collection, Groq client) are loaded
ONCE at startup via a module-level GroundedGenerator, not per request, so each
query is just an embed + vector search + one LLM call.

Run it:
    python app.py
then open the printed local URL (default http://127.0.0.1:7860).
"""

import gradio as gr

from generate import GroundedGenerator

# Built once at import time and reused for every request.
GENERATOR = GroundedGenerator()

EXAMPLE_QUESTIONS = [
    "Does the Vista Room have a set or rotating menu?",
    "Where is the Vista Room at SFSU located?",
    "What's a popular food item at the Halal shop at SFSU?",
    "What neighborhoods is SFSU near?",
    "What dining hall do first-year SFSU students usually start with?",
]


def ask(question):
    """Gradio callback: run one question through the pipeline.

    Returns the unified response format (answer + attributed source list) as a
    single Markdown string.
    """
    return GENERATOR.answer(question).formatted()


def build_ui():
    with gr.Blocks(title="The Unofficial Guide — SFSU Food") as demo:
        gr.Markdown(
            "# 🍔 The Unofficial Guide — SFSU Food\n"
            "Ask about good and affordable food in and around San Francisco "
            "State University. Answers are grounded **only** in the retrieved "
            "source documents, and every source shown was actually cited by the "
            "model — if nothing in the sources supports an answer, the guide says "
            "so instead of guessing."
        )

        with gr.Row():
            question = gr.Textbox(
                label="Your question",
                placeholder="e.g. What's a popular item at the Halal shop?",
                lines=2,
                scale=4,
            )
            ask_btn = gr.Button("Ask", variant="primary", scale=1)

        response = gr.Markdown(label="Answer")

        gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=question)

        # Click the button or press Enter in the textbox.
        ask_btn.click(fn=ask, inputs=question, outputs=response)
        question.submit(fn=ask, inputs=question, outputs=response)

    return demo


if __name__ == "__main__":
    build_ui().launch()
