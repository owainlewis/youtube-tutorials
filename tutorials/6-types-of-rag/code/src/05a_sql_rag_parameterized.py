"""
Type 5a: SQL RAG (Parameterized)

The LLM extracts structured parameters from natural language.
Those parameters slot into pre-written, safe SQL queries.
No arbitrary SQL generation. Predictable, fast, and secure.

Best for: Known query patterns with user-supplied filters.
Run: uv run src/05a_sql_rag_parameterized.py
"""

import os
import json
from openai import OpenAI
import psycopg
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
DATABASE_URL = os.environ["DATABASE_URL"]

# This is like a form with blank fields.
# The LLM reads the user's question and fills in whichever fields apply.
# "Nike running shoes under $100" -> brand: "Nike", category: "running", max_price: 100
# Fields the user didn't mention stay null (empty).
FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "brand": {
            "type": ["string", "null"],
            "description": "Brand name (Nike, Adidas, Asics, Salomon, New Balance)",
        },
        "category": {
            "type": ["string", "null"],
            "description": "Product category (running, casual, hiking, training)",
        },
        "min_price": {
            "type": ["number", "null"],
            "description": "Minimum price in USD",
        },
        "max_price": {
            "type": ["number", "null"],
            "description": "Maximum price in USD",
        },
        "min_rating": {
            "type": ["number", "null"],
            "description": "Minimum rating (1.0 to 5.0)",
        },
        "color": {
            "type": ["string", "null"],
            "description": "Product color",
        },
        "sort_by": {
            "type": ["string", "null"],
            "enum": [
                "price_asc",
                "price_desc",
                "rating_asc",
                "rating_desc",
                "name_asc",
                None,
            ],
            "description": "Sort order for results",
        },
        "limit": {
            "type": ["integer", "null"],
            "description": "Max number of results to return (default 10)",
        },
    },
    "required": [
        "brand",
        "category",
        "min_price",
        "max_price",
        "min_rating",
        "color",
        "sort_by",
        "limit",
    ],
    "additionalProperties": False,
}


def extract_parameters(question: str) -> dict:
    """The LLM reads the question and fills in the form fields.

    "Blue shoes between $50 and $130" becomes:
    {color: "blue", min_price: 50, max_price: 130, everything else: null}

    We use OpenAI's structured outputs to guarantee the response
    is valid JSON matching our schema. No parsing or guessing needed.
    """
    response = client.responses.create(
        model="gpt-5.4",
        instructions="""You extract product search parameters from a user's question.
Return structured JSON with only the filters the user actually mentioned.
Set any unmentioned filter to null.

Guidelines:
- "running shoes" means category = "running"
- "under $100" means max_price = 100
- "between $50 and $130" means min_price = 50, max_price = 130
- "highest rated" means sort_by = "rating_desc", limit = 1
- "cheapest" means sort_by = "price_asc", limit = 1
- Brand names are case-insensitive but store them capitalized (Nike, Adidas, etc.)""",
        input=question,
        text={
            "format": {
                "type": "json_schema",
                "name": "product_filters",
                "schema": FILTER_SCHEMA,
                "strict": False,
            }
        },
    )
    return json.loads(response.output_text)


def build_query(params: dict) -> tuple[str, list]:
    """Turn the extracted form fields into a safe SQL query.

    This is the key difference from dynamic SQL. The LLM never writes SQL.
    We build it ourselves from the parameters. The query structure is always
    the same: SELECT ... FROM products WHERE (filters) ORDER BY ... LIMIT ...
    We just add or skip WHERE clauses based on which fields the LLM filled in.

    Values go through %s placeholders (query parameters), which means
    there's no way for the user to inject malicious SQL. The database
    treats every value as data, never as code.
    """
    sql = "SELECT name, brand, category, price, rating, color FROM products"
    conditions: list[str] = []
    values: list = []

    if params.get("brand"):
        conditions.append("brand ILIKE %s")
        values.append(params["brand"])

    if params.get("category"):
        conditions.append("category ILIKE %s")
        values.append(params["category"])

    if params.get("min_price") is not None:
        conditions.append("price >= %s")
        values.append(params["min_price"])

    if params.get("max_price") is not None:
        conditions.append("price <= %s")
        values.append(params["max_price"])

    if params.get("min_rating") is not None:
        conditions.append("rating >= %s")
        values.append(params["min_rating"])

    if params.get("color"):
        conditions.append("color ILIKE %s")
        values.append(params["color"])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    # Sorting
    sort_map = {
        "price_asc": "price ASC",
        "price_desc": "price DESC",
        "rating_asc": "rating ASC",
        "rating_desc": "rating DESC",
        "name_asc": "name ASC",
    }
    sort_by = params.get("sort_by")
    if sort_by and sort_by in sort_map:
        sql += f" ORDER BY {sort_map[sort_by]}"

    # Limit (capped at 50 so the LLM can't dump the whole table)
    limit = min(int(params.get("limit") or 10), 50)
    sql += f" LIMIT {limit}"

    return sql, values


def execute_query(sql: str, values: list) -> list[dict]:
    """Execute a parameterized query and return results as dicts."""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, values)
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
    return results


def ask(question: str) -> str:
    """Extract parameters, build safe SQL, execute, and answer."""
    # Step 1: LLM extracts structured parameters
    params = extract_parameters(question)
    print(f"  Extracted params: {json.dumps(params, default=str)}")

    # Step 2: Build parameterized query (no LLM-generated SQL)
    sql, values = build_query(params)
    print(f"  Built query: {sql}")
    print(f"  With values: {values}")

    # Step 3: Execute safely
    results = execute_query(sql, values)

    if not results:
        context = "The query returned no results."
    else:
        context = "\n".join(str(r) for r in results)

    # Step 4: LLM answers based on results
    response = client.responses.create(
        model="gpt-5.4",
        instructions="You are a helpful shopping assistant for ShopMax. Answer the customer's question based on the query results. Be specific about prices and ratings.",
        input=f"Query results:\n{context}\n\nOriginal question: {question}",
    )
    return response.output_text


if __name__ == "__main__":
    # Extracts: brand=Nike, category=running, max_price=100
    print("=" * 60)
    print("QUERY: 'Show me Nike running shoes under $100'")
    print("=" * 60)
    answer = ask("Show me Nike running shoes under $100")
    print(f"\nA: {answer}")

    # Extracts: sort_by=rating_desc, limit=1
    print("\n" + "=" * 60)
    print("QUERY: 'What's the highest rated shoe you have?'")
    print("=" * 60)
    answer = ask("What's the highest rated shoe you have?")
    print(f"\nA: {answer}")

    # Extracts: color=blue, min_price=50, max_price=130
    print("\n" + "=" * 60)
    print("QUERY: 'Blue shoes between $50 and $130'")
    print("=" * 60)
    answer = ask("Blue shoes between $50 and $130")
    print(f"\nA: {answer}")
