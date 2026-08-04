"""
Type 3: Vector Search RAG

Semantic retrieval using OpenAI embeddings and pgvector.
Matches on meaning, not exact words. Understands natural language.

Best for: Natural language queries, finding semantically similar content.
Breaks when: Users need exact filters (price, brand, rating).
Run: .venv/bin/python src/03_vector_search.py
"""

from config import CHAT_MODEL, EMBEDDING_MODEL, connect, get_client


def embed(text: str) -> list[float]:
    """Turn text into a list of numbers (a "vector") that captures its meaning.

    OpenAI's embedding model reads the text and returns a vector of numbers.
    Texts with similar meaning get similar numbers.
    "comfortable running shoe" and "cushioned jogging sneaker" would
    produce vectors that are close together, even though the words are different.
    """
    response = get_client().embeddings.create(model=EMBEDDING_MODEL, input=[text])
    return response.data[0].embedding


def vector_search(query: str, limit: int = 5) -> list[dict]:
    """Search products using vector similarity (cosine distance).

    In production, you'd move this query into a stored procedure so your
    Python code is just: SELECT * FROM vector_search(query_embedding, limit)
    But for learning, the inline SQL makes it easier to see what's happening.
    """
    # Step 1: Turn the user's question into a vector (list of numbers)
    query_embedding = embed(query)

    with connect() as conn:
        with conn.cursor() as cur:
            # Step 2: Find the products whose descriptions are closest in meaning
            #
            # embedding <=> %s::vector
            #   The <=> operator measures the distance between two vectors.
            #   Small distance = similar meaning. Think of it like measuring
            #   how far apart two points are on a map.
            #   We sort by this distance so the closest matches come first.
            #
            # 1 - (distance) AS similarity
            #   We flip the distance into a similarity score.
            #   Higher values mean smaller cosine distance for this index.
            cur.execute(
                """
                SELECT name, brand, category, price, rating, color, description,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM products
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (str(query_embedding), str(query_embedding), limit),
            )
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
    return results


def ask(question: str) -> str:
    """Search products by meaning and answer with the configured model."""
    results = vector_search(question)

    context = "\n".join(
        f"- {r['name']} ({r['brand']}) - ${r['price']} - {r['rating']}★ - {r['description']}"
        for r in results
    )

    response = get_client().responses.create(
        model=CHAT_MODEL,
        instructions="You are a helpful shopping assistant for ShopMax. Use the search results to answer the customer's question.",
        input=f"Search results:\n{context}\n\nQuestion: {question}",
    )
    return response.output_text


if __name__ == "__main__":
    # This works: semantic understanding
    print("=" * 60)
    print("QUERY: 'comfortable shoes for long distance running'")
    print("=" * 60)
    results = vector_search("comfortable shoes for long distance running")
    for r in results:
        print(f"  {r['name']} ({r['brand']}) - ${r['price']} - sim: {r['similarity']:.3f}")

    print(f"\nA: {ask('What shoes are good for long distance running?')}")

    # This breaks: exact filters
    print("\n" + "=" * 60)
    print("QUERY: 'Nike shoes under $100'")
    print("=" * 60)
    results = vector_search("Nike shoes under $100")
    for r in results:
        print(f"  {r['name']} ({r['brand']}) - ${r['price']} - sim: {r['similarity']:.3f}")

    print("\n  ^ Vector search doesn't understand price filters.")
    print("  It may return shoes over $100 or non-Nike brands.")
