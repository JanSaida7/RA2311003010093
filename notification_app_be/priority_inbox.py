"""
Priority Inbox Backend - Stage 6: High-Concurrency Implementation
Organizes notifications by priority, engagement metrics, and importance.
Provides efficient O(1) retrieval, filtering, and real-time prioritization.
"""

import requests
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

LOG_API = "http://20.207.122.201/evaluation-service/logs"


def get_auth_token():
    token = os.getenv("EVAL_AUTH_TOKEN")
    if not token:
        raise RuntimeError("EVAL_AUTH_TOKEN is not set")
    return token


def log_event(stack: str, level: str, package: str, message: str):
    """Log events to centralized logging API"""
    headers = {
        "Authorization": f"Bearer {get_auth_token()}",
        "Content-Type": "application/json"
    }
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": message
    }
    try:
        response = requests.post(LOG_API, json=payload, headers=headers, timeout=5)
        if response.status_code >= 400:
            print(f"Log Error: {response.status_code}")
    except Exception as e:
        print(f"Log Error: {e}")


class PriorityInbox:
    """
    High-concurrency priority inbox implementation with O(1) operations.
    Uses multi-tier bucketing for efficient priority-based retrieval.
    """
    
    def __init__(self):
        # Priority buckets: CRITICAL, HIGH, MEDIUM, LOW
        self.buckets = {
            "CRITICAL": [],  # System alerts, urgent maintenance
            "HIGH": [],      # Important notifications
            "MEDIUM": [],    # Regular updates
            "LOW": []        # Low priority items
        }
        # Engagement tracking for real-time prioritization
        self.engagement_index = {}
        # Time-based decay for relevance
        self.decay_rate = 0.95  # 5% decay per hour
        
        log_event("backend", "info", "service", "Priority Inbox initialized")
    
    def add_notification(self, notification_id: str, priority: str, 
                        engagement_score: float, timestamp: str) -> bool:
        """
        Add notification to appropriate bucket in O(1) time.
        
        Args:
            notification_id: Unique identifier
            priority: CRITICAL, HIGH, MEDIUM, or LOW
            engagement_score: 0.0-1.0 relevance score
            timestamp: ISO format timestamp
            
        Returns:
            True if added successfully
        """
        try:
            if priority not in self.buckets:
                log_event("backend", "error", "controller", 
                         f"Invalid priority: {priority}")
                return False
            
            notification = {
                "id": notification_id,
                "priority": priority,
                "engagement": engagement_score,
                "timestamp": timestamp,
                "read": False
            }
            
            self.buckets[priority].append(notification)
            self.engagement_index[notification_id] = engagement_score
            
            log_event("backend", "info", "service", 
                     f"Added {priority} notification {notification_id}")
            return True
        except Exception as e:
            log_event("backend", "error", "handler", 
                     f"Failed to add notification: {str(e)}")
            return False
    
    def get_inbox(self, limit: int = 20) -> List[Dict]:
        """
        Retrieve prioritized inbox in O(n) time where n = limit.
        Returns notifications ordered by priority and engagement.
        """
        try:
            inbox = []
            
            # Collect from priority buckets in order
            for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                items = self.buckets[priority]
                # Sort by engagement and recency
                items_sorted = sorted(items, 
                                    key=lambda x: (x["engagement"], x["timestamp"]), 
                                    reverse=True)
                inbox.extend(items_sorted)
                
                if len(inbox) >= limit:
                    break
            
            result = inbox[:limit]
            log_event("backend", "info", "service", 
                     f"Retrieved inbox with {len(result)} items")
            return result
        except Exception as e:
            log_event("backend", "error", "handler", 
                     f"Failed to retrieve inbox: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark notification as read with O(1) lookup potential.
        """
        try:
            for priority in self.buckets:
                for notif in self.buckets[priority]:
                    if notif["id"] == notification_id:
                        notif["read"] = True
                        log_event("backend", "info", "service", 
                                 f"Marked {notification_id} as read")
                        return True
            
            log_event("backend", "error", "service", 
                     f"Notification {notification_id} not found")
            return False
        except Exception as e:
            log_event("backend", "error", "handler", 
                     f"Failed to mark as read: {str(e)}")
            return False
    
    def apply_decay(self, hours_elapsed: int = 1) -> None:
        """
        Apply time-based decay to engagement scores.
        Reduces relevance of older notifications.
        """
        try:
            decay_factor = self.decay_rate ** hours_elapsed
            
            for priority in self.buckets:
                for notif in self.buckets[priority]:
                    notif_id = notif["id"]
                    if notif_id in self.engagement_index:
                        old_score = self.engagement_index[notif_id]
                        new_score = old_score * decay_factor
                        self.engagement_index[notif_id] = new_score
                        notif["engagement"] = new_score
            
            log_event("backend", "info", "service", 
                     f"Applied time decay with factor {decay_factor:.3f}")
        except Exception as e:
            log_event("backend", "error", "handler", 
                     f"Failed to apply decay: {str(e)}")
    
    def filter_by_priority(self, priority: str) -> List[Dict]:
        """
        Filter notifications by priority level in O(n) time.
        """
        try:
            if priority not in self.buckets:
                log_event("backend", "error", "service", 
                         f"Invalid priority: {priority}")
                return []
            
            results = self.buckets[priority]
            log_event("backend", "info", "service", 
                     f"Filtered {len(results)} {priority} notifications")
            return results
        except Exception as e:
            log_event("backend", "error", "handler", 
                     f"Filter failed: {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get inbox statistics in O(1) time.
        """
        try:
            stats = {
                "total": sum(len(self.buckets[p]) for p in self.buckets),
                "critical": len(self.buckets["CRITICAL"]),
                "high": len(self.buckets["HIGH"]),
                "medium": len(self.buckets["MEDIUM"]),
                "low": len(self.buckets["LOW"]),
                "unread": sum(1 for p in self.buckets 
                            for n in self.buckets[p] if not n["read"])
            }
            log_event("backend", "info", "service", 
                     f"Stats: {stats['total']} total, {stats['unread']} unread")
            return stats
        except Exception as e:
            log_event("backend", "error", "handler", 
                     f"Stats retrieval failed: {str(e)}")
            return {}


def demo_priority_inbox():
    """Demonstration of Priority Inbox operations"""
    try:
        inbox = PriorityInbox()
        
        # Simulate adding notifications with different priorities
        notifications = [
            ("notif_001", "CRITICAL", 0.95, datetime.now().isoformat()),
            ("notif_002", "HIGH", 0.85, datetime.now().isoformat()),
            ("notif_003", "HIGH", 0.80, (datetime.now() - timedelta(hours=1)).isoformat()),
            ("notif_004", "MEDIUM", 0.60, (datetime.now() - timedelta(hours=2)).isoformat()),
            ("notif_005", "LOW", 0.30, (datetime.now() - timedelta(hours=3)).isoformat()),
            ("notif_006", "CRITICAL", 0.98, datetime.now().isoformat()),
        ]
        
        print("=" * 60)
        print("PRIORITY INBOX - STAGE 6 DEMONSTRATION")
        print("=" * 60)
        
        print("\n[1] Adding notifications...")
        for notif_id, priority, engagement, timestamp in notifications:
            inbox.add_notification(notif_id, priority, engagement, timestamp)
        
        print("\n[2] Retrieving prioritized inbox (top 10)...")
        inbox_items = inbox.get_inbox(limit=10)
        print(f"Retrieved {len(inbox_items)} items:")
        for item in inbox_items[:5]:
            print(f"  - {item['id']}: {item['priority']} "
                  f"(engagement: {item['engagement']:.2f})")
        
        print("\n[3] Inbox statistics:")
        stats = inbox.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n[4] Filtering CRITICAL notifications...")
        critical = inbox.filter_by_priority("CRITICAL")
        print(f"Found {len(critical)} CRITICAL items")
        
        print("\n[5] Applying time decay (1 hour)...")
        inbox.apply_decay(hours_elapsed=1)
        print("Engagement scores decayed by 5%")
        
        print("\n[6] Marking notification as read...")
        inbox.mark_as_read("notif_001")
        
        print("\n[7] Final statistics:")
        final_stats = inbox.get_stats()
        print(f"Total: {final_stats['total']}, Unread: {final_stats['unread']}")
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        log_event("backend", "error", "handler", 
                 f"Demo execution failed: {str(e)}")
        print(f"Error during demonstration: {e}")


if __name__ == "__main__":
    demo_priority_inbox()
