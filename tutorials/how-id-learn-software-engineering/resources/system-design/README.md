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

## The System Design Questions

The `questions/` directory contains 20 classic system design problems. Each one includes:

- The question and constraints
- How to approach it
- Key design decisions and tradeoffs
- A diagram of the architecture
- The principles it teaches

These were generated using AI and then reviewed for accuracy. This is an example of using AI to learn faster.

### Questions

| # | Question | Key Concepts |
|---|----------|-------------|
| 1 | [Design a URL Shortener](questions/01-url-shortener.md) | Hashing, databases, read-heavy systems |
| 2 | [Design a Rate Limiter](questions/02-rate-limiter.md) | Token bucket, sliding window, distributed state |
| 3 | [Design a Chat System](questions/03-chat-system.md) | WebSockets, message queues, presence |
| 4 | Design a News Feed | Fan-out, caching, ranking |
| 5 | Design a Notification System | Queues, templates, delivery guarantees |
| 6 | Design a File Storage Service | Object storage, chunking, deduplication |
| 7 | Design a Search Autocomplete | Tries, caching, ranking by frequency |
| 8 | Design a Video Streaming Platform | CDNs, transcoding, adaptive bitrate |
| 9 | Design a Key-Value Store | Partitioning, replication, consistency |
| 10 | Design an API Rate Limiter | Gateway patterns, auth, throttling |
| 11 | Design a Job Scheduler | Queues, retry logic, idempotency |
| 12 | Design a Metrics Collection System | Time series, aggregation, dashboards |
| 13 | Design a Payment System | Idempotency, eventual consistency, audit trails |
| 14 | Design an Email Service | Queues, templates, delivery tracking |
| 15 | Design a Location-Based Service | Geospatial indexing, proximity search |
| 16 | Design a Content Delivery Network | Edge caching, invalidation, routing |
| 17 | Design a Logging System | Log aggregation, search, retention |
| 18 | Design an Authentication System | OAuth, JWT, session management |
| 19 | Design a Recommendation Engine | Collaborative filtering, real-time vs batch |
| 20 | Design a Task Queue | Workers, priorities, dead letter queues |

## Resources

- [Designing Data-Intensive Applications](https://dataintensive.net/) - The best book on this topic. Read it.
- [System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer) - Comprehensive open-source reference.
- [ByteByteGo](https://bytebytego.com/) - Visual explanations of system design concepts.

## The Test

Can you draw a diagram of how a web application handles a request from browser to database and back? Can you explain when you'd use a message queue instead of a direct API call? If yes, you're thinking like a systems engineer.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
