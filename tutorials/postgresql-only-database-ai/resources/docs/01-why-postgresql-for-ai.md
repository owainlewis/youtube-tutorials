# Chapter 1: Why PostgreSQL for RAG

PostgreSQL is a production-grade platform for RAG. Most teams already know it, trust it, and run it. With pgvector, it handles the majority of RAG workloads without adding new infrastructure.

## The Argument

The default advice for building RAG is to spin up a dedicated vector database — Pinecone, Weaviate, Chroma, Qdrant. These are good tools. But for most production workloads, PostgreSQL already does the job — and you probably already have one running.

The case for PostgreSQL isn't "fewer databases." You can absolutely run separate services, and sometimes you should. The case is that PostgreSQL is genuinely capable at this, and most developers already understand it deeply.

## Why PostgreSQL Works for RAG

### You already know it

PostgreSQL is the most widely used relational database for a reason. Most backend engineers have years of experience with it — querying, indexing, tuning, monitoring, backing up, restoring. That operational knowledge transfers directly. You don't need to learn a new query language, a new deployment model, or a new set of failure modes.

### It's production-proven at scale

PostgreSQL has been in production for over 35 years. It handles ACID transactions, connection pooling, replication, point-in-time recovery, and row-level security out of the box. pgvector supports HNSW indexes that scale to tens of millions of vectors on a single machine — and into the hundreds of millions with appropriate hardware and partitioning. This is not a toy — it's infrastructure that teams already trust with their most critical data.

### It handles the full RAG stack

A RAG system typically needs three things:

1. **Structured relational data** — users, sessions, permissions, document metadata
2. **Full-text search** — keyword matching with ranking
3. **Dense vector embeddings** — semantic similarity search

PostgreSQL handles all three natively:

- Standard tables and indexes for relational data
- `tsvector` and GIN indexes for full-text search
- `pgvector` and HNSW indexes for vector similarity

You can query all three in the same SQL statement. Filter vectors by user permissions. Join search results against metadata. Run it all in one transaction.

### Hybrid search is a single query

The real power for RAG is hybrid search — combining keyword matching with semantic similarity. In PostgreSQL, this is a SQL function. You write one query that runs both searches and merges the results using Reciprocal Rank Fusion. No application-level coordination between services.

### Your data stays consistent

When vectors live alongside the data they represent, consistency is automatic. Delete a document and the embedding goes with it. Update metadata and the next search reflects it. No sync jobs, no eventual consistency, no orphaned vectors.

## When to Consider a Dedicated Vector DB

PostgreSQL isn't always the right choice. Consider a dedicated vector database when:

- You're working with billions of vectors and need specialized sharding
- You need sub-millisecond latency at massive concurrent query volume
- Your vector workload has fundamentally different scaling needs than your relational data
- You're building a search-first product where vector operations dominate

Chapter 7 covers this tradeoff in detail with a decision framework.

## The Point

This tutorial isn't arguing against dedicated vector databases. It's showing that PostgreSQL — a database most developers already run, already trust, and already understand — is a production-grade RAG platform. For the majority of workloads, it's enough. And "enough" with tooling you know deeply beats "optimal" with tooling you're learning in production.

## Learn More

- [pgvector GitHub repository](https://github.com/pgvector/pgvector)
- [PostgreSQL Full-Text Search documentation](https://www.postgresql.org/docs/current/textsearch.html)
- [pgvector indexing guide (HNSW and IVFFlat)](https://github.com/pgvector/pgvector#indexing)

## What's Next

In the next chapter, you will set up PostgreSQL with pgvector using Docker and create the documents table with an HNSW index.
