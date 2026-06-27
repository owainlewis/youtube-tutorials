"""
Seed the database with product data and document chunks.

Uses Docling to parse documents and OpenAI to generate embeddings.
Run: uv run src/seed.py
"""

import os
import psycopg
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

PRODUCTS = [
    {
        "name": "TrailBlazer Pro",
        "brand": "Nike",
        "category": "running",
        "price": 89.99,
        "rating": 4.5,
        "color": "blue",
        "description": "Lightweight trail running shoe with responsive cushioning and aggressive grip. Built for rocky terrain and long distances. Features a breathable mesh upper and reinforced toe cap.",
    },
    {
        "name": "UltraGlide 3000",
        "brand": "Nike",
        "category": "running",
        "price": 129.99,
        "rating": 4.7,
        "color": "black",
        "description": "Premium road running shoe with plush cushioned midsole designed for marathon training. Supportive arch and energy-return foam make it ideal for all-day comfort on long runs.",
    },
    {
        "name": "SprintForce Elite",
        "brand": "Adidas",
        "category": "running",
        "price": 74.99,
        "rating": 4.2,
        "color": "red",
        "description": "Affordable racing flat for speed workouts and 5K races. Minimal cushioning for ground feel. Lightweight at just 6.5oz. Not recommended for distances over 10K.",
    },
    {
        "name": "CloudWalk Max",
        "brand": "Nike",
        "category": "casual",
        "price": 64.99,
        "rating": 4.8,
        "color": "white",
        "description": "Everyday casual sneaker with cloud-like cushioning. Perfect for walking, errands, and all-day wear. Slip-on design with memory foam insole. Goes with everything.",
    },
    {
        "name": "MountainGrip X",
        "brand": "Salomon",
        "category": "hiking",
        "price": 149.99,
        "rating": 4.6,
        "color": "green",
        "description": "Waterproof hiking boot with Vibram outsole for maximum traction in wet and muddy conditions. Ankle support and Gore-Tex lining keep feet dry on the trail.",
    },
    {
        "name": "StreetStyle Low",
        "brand": "Adidas",
        "category": "casual",
        "price": 54.99,
        "rating": 4.3,
        "color": "navy",
        "description": "Classic low-top casual shoe inspired by skateboarding culture. Vulcanized rubber sole and canvas upper. Available in 12 colorways.",
    },
    {
        "name": "EnduroRun 500",
        "brand": "Asics",
        "category": "running",
        "price": 109.99,
        "rating": 4.4,
        "color": "grey",
        "description": "Stability running shoe with gel cushioning system designed for overpronators. Supportive and durable for daily training up to marathon distance. Wide toe box option available.",
    },
    {
        "name": "FlexFit Trainer",
        "brand": "Nike",
        "category": "training",
        "price": 84.99,
        "rating": 4.1,
        "color": "blue",
        "description": "Versatile cross-training shoe for gym workouts, HIIT classes, and weightlifting. Flat stable base with lateral support. Breathable mesh upper.",
    },
    {
        "name": "RainRunner Pro",
        "brand": "Asics",
        "category": "running",
        "price": 119.99,
        "rating": 4.3,
        "color": "black",
        "description": "All-weather running shoe with water-resistant upper and enhanced grip for wet pavement. Reflective details for low-light visibility. Ideal for runners who train in any conditions.",
    },
    {
        "name": "BudgetRun 100",
        "brand": "New Balance",
        "category": "running",
        "price": 39.99,
        "rating": 3.8,
        "color": "blue",
        "description": "Entry-level running shoe at an unbeatable price. Basic cushioning suitable for beginners and short runs. Durable rubber outsole. Great starter shoe for new runners.",
    },
    {
        "name": "LuxeComfort Elite",
        "brand": "New Balance",
        "category": "running",
        "price": 179.99,
        "rating": 4.9,
        "color": "white",
        "description": "Top-of-the-line running shoe with carbon fiber plate and nitrogen-infused foam. Designed for competitive runners chasing personal records. Incredibly light yet supremely cushioned.",
    },
    {
        "name": "TrailStar Waterproof",
        "brand": "Salomon",
        "category": "running",
        "price": 134.99,
        "rating": 4.5,
        "color": "orange",
        "description": "Trail running shoe built for wet and muddy conditions. Waterproof membrane keeps feet dry while drainage ports handle stream crossings. Aggressive lug pattern for technical terrain.",
    },
]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using OpenAI."""
    client = OpenAI()
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [item.embedding for item in response.data]


def chunk_document(filepath: Path) -> list[str]:
    """Parse and chunk a document using Docling.

    Docling handles the full pipeline: parse the document format,
    understand its structure, then chunk it intelligently based on
    headings, paragraphs, and semantic boundaries.
    """
    converter = DocumentConverter()
    result = converter.convert(str(filepath))

    chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5", max_tokens=512)
    chunks = list(chunker.chunk(result.document))

    return [chunk.text for chunk in chunks if chunk.text.strip()]


def seed():
    print("Connecting to database...")
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            # Clear existing data
            cur.execute("DELETE FROM document_chunks")
            cur.execute("DELETE FROM products")

            # Seed products
            print(f"Embedding {len(PRODUCTS)} products...")
            descriptions = [p["description"] for p in PRODUCTS]
            embeddings = embed_texts(descriptions)

            for product, embedding in zip(PRODUCTS, embeddings):
                cur.execute(
                    """
                    INSERT INTO products (name, brand, category, price, rating, color, description, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                    """,
                    (
                        product["name"],
                        product["brand"],
                        product["category"],
                        product["price"],
                        product["rating"],
                        product["color"],
                        product["description"],
                        str(embedding),
                    ),
                )
            print(f"Inserted {len(PRODUCTS)} products.")

            # Seed document chunks
            data_dir = Path(__file__).parent.parent / "data"
            for doc_path in sorted(data_dir.glob("*.md")):
                chunks = chunk_document(doc_path)
                print(f"Chunking {doc_path.name}: {len(chunks)} chunks")

                chunk_embeddings = embed_texts(chunks)
                for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                    cur.execute(
                        """
                        INSERT INTO document_chunks (source, chunk_index, content, embedding)
                        VALUES (%s, %s, %s, %s::vector)
                        """,
                        (doc_path.name, i, chunk, str(embedding)),
                    )
                print(f"Inserted {len(chunks)} chunks from {doc_path.name}.")

        conn.commit()
    print("Done.")


if __name__ == "__main__":
    seed()
