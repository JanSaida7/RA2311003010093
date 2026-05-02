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