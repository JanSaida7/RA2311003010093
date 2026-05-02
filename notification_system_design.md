# Campus Notification System Design

## Stage 1: API Design
The notification platform provides real-time updates for Placements, Events, and Results.

### Core Actions
- **Fetch Notifications**: Retrieve a list of notifications for the authenticated student.
- **Mark as Read**: Update the status of a specific notification to manage unread counts.
- **Real-time Delivery**: Push high-priority updates like Placement alerts immediately.

### API Contract
As shown in the screenshot, the response follows this structure:

```json
{
  "notifications": [
    {
      "id": "uuid-v4",
      "type": "Placement",
      "title": "CSX Corporation Hiring",
      "message": "CSX is hiring for SDE-1 roles. Apply by tomorrow.",
      "isRead": false,
      "timestamp": "2026-04-22T17:51:18Z"
    }
  ],
  "unreadCount": 1
}
```

### Real-time Notification Mechanism
WebSockets can be used for bidirectional, low-latency communication. Unlike standard polling, WebSockets maintain an open connection and allow the server to push high-priority notifications immediately when they are published.

## Next Stage
Stage 2 will cover persistent storage design, including the database choice and schema.

## Stage 2: Persistent Storage

### Database Choice
PostgreSQL is a good choice because of its ACID compliance, which helps keep notification read statuses synchronized reliably.

### DB Schema
```sql
CREATE TYPE notification_category AS ENUM ('Event', 'Result', 'Placement');

CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  roll_no VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id INT REFERENCES students(id),
  type notification_category NOT NULL,
  message TEXT NOT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Scaling Challenges
As volume reaches millions of rows, sequential table scans will cause high latency. A practical solution is horizontal sharding by `student_id` to distribute the data load across multiple instances.

## Next Stage
Stage 3 will focus on query optimization and indexing.

## Stage 3: Query Optimization

The query below can be slow when the notifications table grows large:

```sql
SELECT *
FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```

It can trigger a table scan because the filter and sort both need support.

### Fix
Add a composite index on `(student_id, is_read, created_at DESC)` so the database can find unread notifications for one student and return them in order more efficiently.

### Example
```sql
CREATE INDEX idx_notifications_student_unread
ON notifications (student_id, is_read, created_at DESC);
```

This is better than indexing every column because it targets the exact query pattern.

## Next Stage
Stage 4 will cover simple performance improvements.

## Stage 4: Performance Improvements

Two simple ways to improve speed are caching and read replicas.

- **Redis caching** can store unread counts and the first page of notifications so the app does not hit the database every time.
- **Read replicas** can handle fetch-heavy traffic while the main database continues handling writes.

These options are useful because notification feeds are usually read more often than they are changed.

### Tradeoff
Caching is fast, but cache invalidation must be handled carefully. Read replicas reduce load, but they can lag behind the primary database.

## Next Stage
Stage 5 will describe a simple asynchronous redesign.

## Stage 5: High-Concurrency Redesign

The synchronous version can become slow when many notifications need to be sent at once. A better approach is to use a message queue.

### Idea
- Save the notification in the database first.
- Push each delivery job into a queue.
- Let background workers send emails or app alerts separately.

### Why It Helps
This keeps the main request fast and allows failed jobs to be retried without stopping the whole process.

### Small Pseudocode
```python
def notify_all_async(student_ids, message):
  save_to_db_bulk(student_ids, message)
  for student_id in student_ids:
    notification_queue.push(student_id, message)
```

## Next Stage
Stage 6 will cover priority inbox ordering.

## Stage 6: Priority Inbox

Notifications can be ordered by importance and recency so the most useful items appear first.

### Simple Rule
- Placement gets the highest weight.
- Result comes next.
- Event has the lowest weight.

### Maintenance
Use a small min-heap to keep the top 10 notifications without sorting the full list every time.

This gives a fast priority view while still keeping the logic easy to explain and maintain.

## Final Check
Keep screenshots ready and avoid using your name in the repository title or commit messages.