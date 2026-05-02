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