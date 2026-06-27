"""
Type 5b: SQL RAG (Dynamic)

The LLM generates full SQL from natural language. More flexible than
parameterized queries but requires safety guardrails.

Best for: Ad-hoc analysis, complex aggregations, questions you can't predict.
Breaks when: Users ask about unstructured attributes ("comfortable", "stylish").
Run: uv run src/05b_sql_rag_dynamic.py
"""

import os
from openai import OpenAI
import psycopg
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
DATABASE_URL = os.environ["DATABASE_URL"]

# We describe our database schema in plain English so the LLM knows
# what tables and columns exist. This is the only context it has.
# The better you describe your schema, the better the generated SQL will be.
SCHEMA = """
Table: products
Columns:
  - id: SERIAL PRIMARY KEY
  - name: TEXT (product name)
  - brand: TEXT (Nike, Adidas, Asics, Salomon, New Balance)
  - category: TEXT (running, casual, hiking, training)
  - price: DECIMAL (in USD)
  - rating: DECIMAL (1.0 to 5.0)
  - color: TEXT
  - description: TEXT
""".strip()


def generate_sql(question: str, error: str | None = None) -> str:
    """Give the LLM a question and the schema, get back a SQL query.

    This is the core of dynamic SQL RAG. The LLM reads the schema,
    understands the question, and writes a SELECT query from scratch.

    "How many Nike products do you carry?" becomes:
    SELECT COUNT(*) FROM products WHERE brand = 'Nike'

    If a previous attempt failed (bad SQL), we include the error message
    so the LLM can learn from its mistake and try a different approach.
    """
    prompt = question
    if error:
        prompt = f"{question}\n\nThe previous SQL attempt failed with this error: {error}\nPlease fix the query."

    response = client.responses.create(
        model="gpt-5.4",
        instructions=f"""You are a SQL expert. Generate a PostgreSQL SELECT query based on the user's question.

Database schema:
{SCHEMA}

Rules:
- Return ONLY the SQL query, no explanation, no markdown.
- Always use SELECT (never INSERT, UPDATE, DELETE, DROP, etc.).
- Use ILIKE for text matching when appropriate.
- Limit results to 10 unless the user asks for more.""",
        input=prompt,
    )
    return response.output_text.strip()


def execute_query(sql: str) -> list[dict]:
    """Execute a SQL query and return results as dicts."""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
    return results


def ask(question: str) -> str:
    """The full pipeline: question -> SQL -> execute -> answer.

    The LLM is involved twice:
    1. Generate SQL from the question (text -> SQL)
    2. Generate an answer from the results (SQL results -> natural language)

    If the generated SQL has a bug and crashes, we get one retry.
    We pass the error message back to the LLM so it can fix its query.
    This works surprisingly well. Most errors are small syntax issues
    that the LLM can correct on the second attempt.
    """
    sql = generate_sql(question)
    print(f"  Generated SQL: {sql}")

    try:
        results = execute_query(sql)
    except Exception as e:
        # The LLM wrote bad SQL. Pass the error back and let it try again.
        print(f"  SQL failed: {e}")
        print("  Retrying with error context...")
        sql = generate_sql(question, error=str(e))
        print(f"  Retry SQL: {sql}")
        results = execute_query(sql)

    if not results:
        context = "The query returned no results."
    else:
        context = "\n".join(str(r) for r in results)

    response = client.responses.create(
        model="gpt-5.4",
        instructions="You are a helpful shopping assistant for ShopMax. Answer the customer's question based on the query results. Be specific about prices and ratings.",
        input=f"Query results:\n{context}\n\nOriginal question: {question}",
    )
    return response.output_text


if __name__ == "__main__":
    # This works perfectly: structured filters
    print("=" * 60)
    print("QUERY: 'Show me running shoes under $100 with at least 4 stars'")
    print("=" * 60)
    answer = ask("Show me running shoes under $100 with at least 4 stars, sorted by price")
    print(f"\nA: {answer}")

    print("\n" + "=" * 60)
    print("QUERY: 'What is the cheapest product you have?'")
    print("=" * 60)
    answer = ask("What is the cheapest product you have?")
    print(f"\nA: {answer}")

    print("\n" + "=" * 60)
    print("QUERY: 'How many Nike products do you carry?'")
    print("=" * 60)
    answer = ask("How many Nike products do you carry?")
    print(f"\nA: {answer}")

    # This breaks: unstructured questions
    print("\n" + "=" * 60)
    print("QUERY: 'Find me something good for trail running in wet conditions'")
    print("=" * 60)
    answer = ask("Find me something good for trail running in wet conditions")
    print(f"\nA: {answer}")
    print("\n  ^ SQL can't understand 'wet conditions'. There's no 'wetness' column.")
