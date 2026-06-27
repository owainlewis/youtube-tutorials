# Design a Chat System

## The Question

Design a real-time messaging system like Slack or WhatsApp. Users can send messages to individuals or groups, see when others are typing, and receive messages in real time.

**Constraints:**
- Support 1:1 and group messaging (up to 500 members per group)
- Messages delivered in real time (under 500ms)
- Message history must be persistent and searchable
- Show online/offline status and typing indicators
- Support message read receipts

## How to Approach It

A chat system has two distinct problems: real-time delivery and persistent storage. Solving one doesn't solve the other. You need both.

## Key Design Decisions

### Real-Time Delivery: WebSockets

HTTP is request-response. The server can't push a message to the client without the client asking. For real-time chat, you need a persistent connection.

**WebSockets** maintain a long-lived connection between client and server. Either side can send messages at any time. This is how every production chat system works.

Each connected user maintains a WebSocket connection to a chat server. When User A sends a message to User B:

1. User A's client sends the message over its WebSocket
2. The server stores the message in the database
3. The server looks up User B's WebSocket connection
4. The server pushes the message to User B over that connection

### Connection Management

With millions of users, you need multiple chat servers. User A might be connected to Server 1 and User B to Server 3. How does Server 1 find User B?

**Connection registry:** A Redis hash mapping user_id to server_id. When a user connects, register them. When they disconnect, remove them.

```
user:123 → server:1
user:456 → server:3
```

When Server 1 needs to deliver a message to User B on Server 3, it publishes the message to a message queue (Redis Pub/Sub or Kafka). Server 3 subscribes to messages for its connected users and delivers them.

### Storage

Messages need two things: fast writes and fast reads by conversation.

```sql
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    sender_id UUID NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversation_time ON messages(conversation_id, created_at DESC);
```

For search, you'd add a full-text search index (PostgreSQL's built-in tsvector, or Elasticsearch for scale).

### Presence and Typing Indicators

**Online/offline:** Each user sends a heartbeat every 30 seconds over their WebSocket. If no heartbeat for 60 seconds, mark them offline. Store status in Redis with TTL.

**Typing indicators:** When a user starts typing, send a "typing" event over the WebSocket. The server broadcasts it to other participants in the conversation. These are ephemeral and don't need storage.

### Architecture

```
Clients ←→ Load Balancer ←→ Chat Servers ←→ Redis (connections, presence)
                                          ←→ Message Queue (cross-server delivery)
                                          ←→ PostgreSQL (message history)
                                          ←→ Elasticsearch (search)
```

## Principles This Teaches

- **Push vs pull.** HTTP is pull. WebSockets are push. Real-time features need push.
- **Connection state.** Stateful connections (WebSockets) are harder to load balance than stateless HTTP. You need a registry.
- **Fan-out problem.** A message to a 500-person group needs to be delivered to 500 connections, potentially across many servers. Message queues solve this.
- **Ephemeral vs persistent data.** Typing indicators don't need storage. Messages do. Different data has different requirements.

## Follow-up Questions

- How would you handle message ordering in a group chat? (Sequence numbers per conversation, not timestamps)
- What happens when a user is offline? (Queue undelivered messages, deliver on reconnect)
- How would you support file/image sharing? (Upload to object storage, send URL as message)
