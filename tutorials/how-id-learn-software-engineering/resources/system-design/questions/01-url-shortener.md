# Design a URL Shortener

## The Question

Design a service like bit.ly that takes long URLs and generates short, unique links. When someone visits the short link, they get redirected to the original URL.

**Constraints:**
- 100M new URLs per month
- 10:1 read-to-write ratio (1B redirects per month)
- Short URLs should be as short as possible
- Links should expire after a configurable time

## How to Approach It

Start with the basics: what are the core operations?

1. **Create:** Take a long URL, return a short URL
2. **Redirect:** Take a short URL, redirect to the long URL
3. **Analytics (optional):** Track click counts

## Key Design Decisions

### Generating Short URLs

**Option 1: Hash the URL.** Take an MD5/SHA256 hash of the long URL and use the first 7 characters. Problem: collisions. Two different URLs could produce the same short code.

**Option 2: Counter-based.** Use an auto-incrementing counter and encode it in base62 (a-z, A-Z, 0-9). Counter 1 = "a", counter 62 = "10", etc. No collisions. Predictable. A 7-character base62 string gives you 3.5 trillion unique URLs.

**Option 3: Pre-generated keys.** Generate a pool of random short codes in advance. When a request comes in, grab one from the pool. No collision checking needed at write time.

Best choice for most cases: **counter-based with base62 encoding.** Simple, no collisions, and the math is predictable.

### Storage

A relational database (PostgreSQL) works fine here. The schema is simple:

```sql
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    click_count BIGINT DEFAULT 0
);

CREATE INDEX idx_short_code ON urls(short_code);
```

The read-heavy ratio (10:1) means you want a cache in front of the database.

### Caching

Put Redis between the application and the database. When a redirect request comes in:

1. Check Redis for the short code
2. If found, redirect (cache hit)
3. If not found, check the database, store in Redis, then redirect

With a 10:1 read ratio and popular URLs being accessed repeatedly, cache hit rates above 90% are typical.

### Architecture

```
Client → Load Balancer → Application Servers → Redis Cache → PostgreSQL
```

For 1B redirects/month (~400 requests/second), 2-3 application servers behind a load balancer is sufficient.

## Principles This Teaches

- **Read vs write optimization.** The 10:1 ratio tells you where to focus. Optimize reads with caching.
- **Encoding and hashing tradeoffs.** Hash-based approaches are simple but have collision risks. Counter-based approaches are predictable but need coordination.
- **Caching strategy.** Not everything needs a cache. But when your read ratio is high and your data is small, caching is the obvious move.
- **Back-of-envelope math.** 100M URLs/month = ~40 writes/second. 1B redirects/month = ~400 reads/second. These numbers tell you what infrastructure you need.

## Follow-up Questions

- How would you handle link expiration? (Background job that deletes expired entries)
- How would you scale to 100x the traffic? (Partition the database by short code range)
- How would you prevent abuse? (Rate limiting on the create endpoint)
