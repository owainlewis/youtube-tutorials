"""
Type 1: Document Loading RAG

The simplest form of RAG. Load entire documents into the prompt.
No database, no embeddings, no chunking. Just files in a prompt.

Two approaches shown here:
  1a. Load everything: dump all docs into the prompt. Dead simple.
  1b. Indexed loading: the LLM picks which document to load based on the question.
      Still no database, but smarter about what goes into the prompt.

Best for: Small document sets, policy docs, FAQs, runbooks.
Run: uv run src/01_document_loading.py
"""

import json
from openai import OpenAI
from pathlib import Path

client = OpenAI()

DATA_DIR = Path(__file__).parent.parent / "data"


# ─── Approach 1a: Load everything ───────────────────────────────
# Just read all the files and stuff them into the prompt.
# Simple. Works great when your docs are small enough to fit in context.


def load_all_documents() -> str:
    """Load every document from the data directory."""
    docs = []
    for filepath in sorted(DATA_DIR.glob("*.md")):
        content = filepath.read_text()
        docs.append(f"--- {filepath.name} ---\n{content}")
    return "\n\n".join(docs)


def ask_simple(question: str) -> str:
    """Load all documents and ask a question."""
    context = load_all_documents()

    response = client.responses.create(
        model="gpt-5.4",
        instructions="You are a helpful support agent for ShopMax, an online shoe store. Use the provided documents to answer questions accurately. If the answer is not in the documents, say so.",
        input=f"Documents:\n{context}\n\nQuestion: {question}",
    )
    return response.output_text


# ─── Approach 1b: Indexed loading ──────────────────────────────
# Instead of loading everything, keep an index that describes each document.
# The LLM reads the index, picks the right document, and we load only that one.
# This saves tokens and scales to more documents.
#
# Think of it like a table of contents. You read the chapter titles
# to find the right chapter, then you only read that chapter.

DOCUMENT_INDEX = {
    "faq.md": "Frequently asked questions about shipping, orders, payment methods, products, shoe sizing, and gift wrapping.",
    "refund-policy.md": "Return and refund policy including return windows, refund amounts, exchanges, defective items, and how to start a return.",
}


# Structured output schema for document selection.
# By using an enum of valid filenames, the LLM can ONLY return
# one of our real documents. No hallucinated filenames, no extra text,
# no parsing needed. The response is guaranteed to be valid.
DOCUMENT_SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "filename": {
            "type": "string",
            "enum": list(DOCUMENT_INDEX.keys()),
            "description": "The most relevant document for the user's question",
        },
    },
    "required": ["filename"],
    "additionalProperties": False,
}


def pick_document(question: str) -> str:
    """Ask the LLM which document is most relevant to the question.

    We show it the index (just filenames and descriptions, not the full content)
    and it tells us which file to load. One cheap LLM call instead of loading
    everything into context.

    We use structured outputs so the LLM can only return a valid filename.
    No free text, no parsing, no surprises.
    """
    index_text = "\n".join(
        f"- {filename}: {description}"
        for filename, description in DOCUMENT_INDEX.items()
    )

    response = client.responses.create(
        model="gpt-5.4",
        instructions=f"""You are a document router. Based on the user's question, pick the most relevant document.

Available documents:
{index_text}""",
        input=question,
        text={
            "format": {
                "type": "json_schema",
                "name": "document_selection",
                "schema": DOCUMENT_SELECTION_SCHEMA,
                "strict": True,
            }
        },
    )

    result = json.loads(response.output_text)
    chosen = result["filename"]
    print(f"  Index selected: {chosen}")
    return chosen


def ask_indexed(question: str) -> str:
    """Use the index to pick the right document, then answer the question."""
    # Step 1: LLM reads the index and picks a document
    filename = pick_document(question)

    # Step 2: Load only that document
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return f"Document '{filename}' not found."

    context = filepath.read_text()
    print(f"  Loaded: {filename} ({len(context)} chars)")

    # Step 3: Answer the question using just that document
    response = client.responses.create(
        model="gpt-5.4",
        instructions="You are a helpful support agent for ShopMax, an online shoe store. Use the provided document to answer questions accurately. If the answer is not in the document, say so.",
        input=f"Document ({filename}):\n{context}\n\nQuestion: {question}",
    )
    return response.output_text


if __name__ == "__main__":
    # --- 1a: Load everything ---
    print("=" * 60)
    print("APPROACH 1a: Load all documents")
    print("=" * 60)

    for q in [
        "What's your return policy for opened items?",
        "How long does shipping take?",
    ]:
        print(f"\nQ: {q}")
        print(f"A: {ask_simple(q)}")
        print("-" * 60)

    # --- 1b: Indexed loading ---
    # Same questions, but now the LLM picks which document to load.
    # Watch the "Index selected:" line to see it choosing.
    print("\n" + "=" * 60)
    print("APPROACH 1b: Indexed loading (LLM picks the document)")
    print("=" * 60)

    for q in [
        "Can I get a refund if I wore the shoes outside?",
        "Do you ship internationally?",
        "How do I start a return?",
    ]:
        print(f"\nQ: {q}")
        print(f"A: {ask_indexed(q)}")
        print("-" * 60)
