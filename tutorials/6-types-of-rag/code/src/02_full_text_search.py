"""
Type 2: Full-Text Search RAG

Keyword-based retrieval using PostgreSQL's built-in tsvector/tsquery.
Matches on the actual words in your query. Fast and precise.

Best for: When users search with specific terms (brand names, exact features).
Breaks when: Users describe what they want in natural language.
Run: uv run src/02_full_text_search.py
"""

import os
from openai import OpenAI
import psycopg
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
DATABASE_URL = os.environ["DATABASE_URL"]


def full_text_search(query: str, limit: int = 5) -> list[dict]:
    """Search products using PostgreSQL full-text search."""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # Postgres has a built-in search engine. Here's how the pieces work:
            #
            # websearch_to_tsquery('english', 'blue running shoes')
            #   This is just Postgres's way of parsing a search query.
            #   You give it plain text like Google, it handles the rest.
            #   It strips filler words, and stems them ("running" -> "run")
            #   so "running" matches "runner", "runs", etc.
            #
            # search_tsv
            #   A column that stores pre-processed tokens from the product's
            #   name, brand, category, color, and description combined.
            #   Postgres builds this automatically whenever a row is inserted.
            #   We combine multiple columns so "blue Nike running shoes"
            #   can match even though those words live in different columns.
            #
            # @@
            #   The match operator. Think of it like "contains".
            #   WHERE search_tsv @@ query means
            #   "where this product's searchable text contains these words"
            #
            # ts_rank(...)
            #   Scores how well each row matches. Higher = better match.
            #   We sort by this so the best matches come first.
            cur.execute(
                """
                SELECT name, brand, category, price, rating, color, description,
                       ts_rank(search_tsv, websearch_to_tsquery('english', %s)) AS rank
                FROM products
                WHERE search_tsv @@ websearch_to_tsquery('english', %s)
                ORDER BY rank DESC
                LIMIT %s
                """,
                (query, query, limit),
            )
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
    return results


def ask(question: str) -> str:
    """Search products by keyword and answer with GPT-5.4."""
    results = full_text_search(question)

    if not results:
        context = "No products matched the search."
    else:
        context = "\n".join(
            f"- {r['name']} ({r['brand']}) - ${r['price']} - {r['rating']}★ - {r['description']}"
            for r in results
        )

    response = client.responses.create(
        model="gpt-5.4",
        instructions="You are a helpful shopping assistant for ShopMax. Use the search results to answer the customer's question. If no results match, say so.",
        input=f"Search results:\n{context}\n\nQuestion: {question}",
    )
    return response.output_text


if __name__ == "__main__":
    # This works well: specific keywords
    print("=" * 60)
    print("QUERY: 'blue running shoes'")
    print("=" * 60)
    results = full_text_search("blue running shoes")
    for r in results:
        print(f"  {r['name']} ({r['brand']}) - ${r['price']} - {r['color']}")

    print(f"\nA: {ask('What blue running shoes do you have?')}")

    # This breaks: natural language description
    print("\n" + "=" * 60)
    print("QUERY: 'comfortable shoes for long distance running'")
    print("=" * 60)
    results = full_text_search("comfortable shoes for long distance running")
    for r in results:
        print(f"  {r['name']} ({r['brand']}) - ${r['price']}")

    if not results:
        print("  No results! Full-text search can't match 'comfortable' to 'cushioned'.")
