# Design a Rate Limiter

## The Question

Design a rate limiting system that prevents users or services from making too many requests in a given time window. This could be applied at an API gateway level or within individual services.

**Constraints:**
- Support multiple rate limiting rules (e.g., 100 requests/minute per user, 1000 requests/hour per API key)
- Low latency (rate check should add < 5ms to request processing)
- Distributed (works across multiple servers)
- Return appropriate headers (X-RateLimit-Remaining, Retry-After)

## How to Approach It

Rate limiting is about counting requests and rejecting those that exceed a threshold. The core question is: how do you count accurately in a distributed system?

## Key Design Decisions

### Algorithm Choice

**Token Bucket:** Each user has a bucket with N tokens. Each request consumes one token. Tokens refill at a fixed rate. If the bucket is empty, reject the request.
- Pros: Allows bursts (bucket can be full), smooth rate limiting
- Cons: Slightly more complex to implement

**Sliding Window Counter:** Count requests in a sliding time window. If the count exceeds the limit, reject.
- Pros: Simple to understand, accurate
- Cons: No burst tolerance, requires storing timestamps

**Fixed Window Counter:** Count requests in fixed time windows (e.g., each minute). Reset the counter at the start of each window.
- Pros: Simplest to implement
- Cons: Allows 2x burst at window boundaries (user sends 100 at 0:59, 100 at 1:00)

Best choice for most APIs: **Token Bucket.** It handles bursts gracefully and is what most production systems use (including AWS API Gateway and Stripe).

### Storage

Redis is the standard choice. It's fast (sub-millisecond), supports atomic operations, and has built-in TTL for automatic key expiration.

```
Key: rate_limit:{user_id}:{rule_name}
Value: {tokens_remaining, last_refill_timestamp}
TTL: matches the rate limit window
```

### Distributed Coordination

With multiple application servers, all rate limit checks must go through the same Redis instance (or cluster). This is why in-memory rate limiting doesn't work in production. Server A doesn't know what Server B has seen.

**Race condition:** Two requests arrive simultaneously, both read 1 token remaining, both allow the request. Solution: use Redis MULTI/EXEC or Lua scripts for atomic read-and-decrement.

```lua
-- Redis Lua script for atomic token bucket check
local tokens = tonumber(redis.call('get', KEYS[1]) or ARGV[1])
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- Refill tokens based on elapsed time
-- ... (calculate new token count)

if tokens > 0 then
    redis.call('set', KEYS[1], tokens - 1)
    return 1  -- allowed
else
    return 0  -- rejected
end
```

### Architecture

```
Client → Load Balancer → API Gateway (rate check) → Redis → Application Servers
```

The rate limiter sits at the gateway level, before the request reaches your application servers. This protects the entire system.

## Principles This Teaches

- **Distributed state.** Counting things across multiple servers is harder than it sounds. You need a shared store.
- **Atomic operations.** Race conditions in concurrent systems. Why "read then write" is dangerous without atomicity.
- **Algorithm tradeoffs.** Token bucket vs sliding window vs fixed window. Each has different burst behavior, accuracy, and complexity.
- **Response design.** Rate limit headers (Retry-After, X-RateLimit-Remaining) are part of a good API. The client needs to know what happened and when to retry.

## Follow-up Questions

- How would you handle rate limiting across multiple data centers? (Sync counters with eventual consistency, or use a global Redis cluster)
- How would you rate limit by different dimensions (per user, per IP, per API key)? (Multiple buckets with different keys)
- What happens when Redis goes down? (Fail open or fail closed? Most systems fail open to avoid blocking all traffic)
