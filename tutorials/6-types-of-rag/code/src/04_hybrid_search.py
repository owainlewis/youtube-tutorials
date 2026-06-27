"""
Type 4: Hybrid Search RAG

Combines full-text search and vector search using Reciprocal Rank Fusion.
Keyword precision + semantic understanding in one query.

Best for: Production RAG systems. The safe default when you're not sure.
Breaks when: Users need exact structured filters (price < 100, rating > 4).
Run: uv run src/04_hybrid_search.py
"""

import os
from openai import OpenAI
import psycopg
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
DATABASE_URL = os.environ["DATABASE_URL"]

# RRF constant. 60 is the standard value from the original research paper.
# Higher K = rankings are more "blended" and less spiky.
# You almost never need to change this.
K = 60


def embed(text: str) -> list[float]:
    """Turn text into a vector that captures its meaning."""
    response = client.embeddings.create(model="text-embedding-3-small", input=[text])
    return response.data[0].embedding


def hybrid_search(query: str, limit: int = 5) -> list[dict]:
    """
    Hybrid search: run keyword search AND vector search, then merge the results.

    The idea is simple. Keyword search is good at exact matches ("Nike").
    Vector search is good at meaning ("comfortable for long runs").
    Why not run both and combine the results?

    That's what Reciprocal Rank Fusion (RRF) does. Each result gets a score
    based on where it ranked in both lists. If a product ranked #1 in keyword
    search and #3 in vector search, it gets a high combined score.

    In production, you'd move this into a stored procedure so your Python
    code is just: SELECT * FROM hybrid_search(query_text, query_embedding, limit)
    But for learning, the inline SQL makes it easier to see what's happening.
    """
    query_embedding = embed(query)

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # This query has three parts (CTEs), run in order:
            #
            # 1. "fts" = keyword search results, ranked by text match quality
            #    Same full-text search from the previous example.
            #
            # 2. "vec" = vector search results, ranked by semantic similarity
            #    Same vector search from the previous example.
            #
            # 3. "combined" = merge both lists using RRF scoring
            #    FULL OUTER JOIN means we keep results even if they only
            #    appeared in one of the two searches.
            #    The RRF formula: score = 1/(K + rank_keyword) + 1/(K + rank_vector)
            #    Products that rank well in BOTH searches get the highest scores.
            cur.execute(
                """
                WITH fts AS (
                    SELECT id, name, brand, category, price, rating, color, description,
                           ROW_NUMBER() OVER (ORDER BY ts_rank(search_tsv, websearch_to_tsquery('english', %(query)s)) DESC) AS rank_fts
                    FROM products
                    WHERE search_tsv @@ websearch_to_tsquery('english', %(query)s)
                ),
                vec AS (
                    SELECT id, name, brand, category, price, rating, color, description,
                           ROW_NUMBER() OVER (ORDER BY embedding <=> %(embedding)s::vector) AS rank_vec
                    FROM products
                ),
                combined AS (
                    SELECT
                        COALESCE(fts.id, vec.id) AS id,
                        COALESCE(fts.name, vec.name) AS name,
                        COALESCE(fts.brand, vec.brand) AS brand,
                        COALESCE(fts.category, vec.category) AS category,
                        COALESCE(fts.price, vec.price) AS price,
                        COALESCE(fts.rating, vec.rating) AS rating,
                        COALESCE(fts.color, vec.color) AS color,
                        COALESCE(fts.description, vec.description) AS description,
                        COALESCE(1.0 / (%(k)s + fts.rank_fts), 0) +
                        COALESCE(1.0 / (%(k)s + vec.rank_vec), 0) AS rrf_score
                    FROM fts
                    FULL OUTER JOIN vec ON fts.id = vec.id
                )
                SELECT name, brand, category, price, rating, color, description, rrf_score
                FROM combined
                ORDER BY rrf_score DESC
                LIMIT %(limit)s
                """,
                {
                    "query": query,
                    "embedding": str(query_embedding),
                    "k": K,
                    "limit": limit,
                },
            )
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
    return results


def ask(question: str) -> str:
    """Hybrid search and answer with GPT-5.4."""
    results = hybrid_search(question)

    context = "\n".join(
        f"- {r['name']} ({r['brand']}) - ${r['price']} - {r['rating']}★ - {r['description']}"
        for r in results
    )

    response = client.responses.create(
        model="gpt-5.4",
        instructions="You are a helpful shopping assistant for ShopMax. Use the search results to answer the customer's question.",
        input=f"Search results:\n{context}\n\nQuestion: {question}",
    )
    return response.output_text


if __name__ == "__main__":
    # Hybrid shines: combines brand keyword match + semantic comfort match
    print("=" * 60)
    print("QUERY: 'Nike running shoes comfortable for long distance'")
    print("=" * 60)
    results = hybrid_search("Nike running shoes comfortable for long distance")
    for r in results:
        print(f"  {r['name']} ({r['brand']}) - ${r['price']} - RRF: {float(r['rrf_score']):.4f}")

    print(f"\nA: {ask('What Nike shoes are good for long distance running?')}")

    # Still can't handle structured filters
    print("\n" + "=" * 60)
    print("QUERY: 'shoes under $100 with 4+ stars'")
    print("=" * 60)
    results = hybrid_search("shoes under $100 with 4+ stars")
    for r in results:
        print(f"  {r['name']} ({r['brand']}) - ${r['price']} - {r['rating']}★")

    print("\n  ^ Still can't filter on price or rating. We need SQL for that.")
