# System Design

This is the supporting material for the video: System Design.

The metaskill. AI can write any function. It cannot design your system. This is where you invest the most time.

## What to Learn

- [ ] How web applications work (client, server, database)
- [ ] APIs and HTTP (REST, status codes, headers, authentication)
- [ ] Databases: SQL vs NoSQL, when to use each
- [ ] Caching (Redis, CDNs, when caching helps vs hurts)
- [ ] Load balancing and horizontal scaling
- [ ] Message queues (when to decouple with a queue vs direct API call)
- [ ] How data flows between services
- [ ] What happens when things fail (retries, circuit breakers, timeouts)
- [ ] Authentication and authorization patterns
- [ ] Basic networking (DNS, TCP/IP, HTTPS)

## The Worked System Design Questions

The `questions/` directory contains three worked system design problems. Each one includes:

- The question and constraints
- How to approach it
- Key design decisions and tradeoffs
- A diagram of the architecture
- The principles it teaches

### Questions

| # | Question | Key Concepts |
|---|----------|-------------|
| 1 | [Design a URL Shortener](questions/01-url-shortener.md) | Hashing, databases, read-heavy systems |
| 2 | [Design a Rate Limiter](questions/02-rate-limiter.md) | Token bucket, sliding window, distributed state |
| 3 | [Design a Chat System](questions/03-chat-system.md) | WebSockets, message queues, presence |

## Resources

- External: [Designing Data-Intensive Applications](https://dataintensive.net/)
- External: [System Design Primer on GitHub](https://github.com/donnemartin/system-design-primer)
- External: [ByteByteGo](https://bytebytego.com/)

## The Test

Can you draw a diagram of how a web application handles a request from browser to database and back? Can you explain when you'd use a message queue instead of a direct API call? If yes, you're thinking like a systems engineer.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
