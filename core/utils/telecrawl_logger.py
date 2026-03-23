"""
Telecrawl integration for Cortana
Logs messages to SQLite DB in real-time as they arrive
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add telecrawl to path
sys.path.insert(0, str(Path(__file__).parent))

from telecrawl.db import TeleCrawlDB
from telecrawl.query import TeleCrawlQuery

# Default DB location
DEFAULT_DB = Path.home() / ".openclaw" / "memory" / "telecrawl.db"


class TelecrawlLogger:
    """Simple message logger for real-time Telegram message storage"""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = TeleCrawlDB(self.db_path)
        self.db.connect()

    def log_message(self, message_id, chat_id, sender_id, sender_name,
                    text, topic_id=None, timestamp=None):
        """
        Log a single message to the database

        Args:
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            sender_id: Telegram user ID
            sender_name: Display name (extract username/first name)
            text: Message text content
            topic_id: Forum topic ID (optional)
            timestamp: Unix timestamp (optional, defaults to now)
        """
        if not text:
            return False

        # Parse sender name
        parts = sender_name.split() if sender_name else ["", ""]
        first_name = parts[0] if parts else ""
        last_name = parts[1] if len(parts) > 1 else None
        username = sender_name.replace(" ", "_").lower() if sender_name else None

        message = {
            'message_id': message_id,
            'chat_id': chat_id,
            'topic_id': topic_id,
            'sender_id': sender_id,
            'sender_username': username,
            'sender_first_name': first_name,
            'sender_last_name': last_name,
            'text': text,
            'timestamp': timestamp or int(datetime.now().timestamp())
        }

        return self.db.insert_message(message)

    def search(self, query, chat_id=None, limit=50):
        """Search messages"""
        query_engine = TeleCrawlQuery(self.db)
        return query_engine.search(query, chat_id=chat_id, limit=limit)

    def recent(self, chat_id=None, limit=50):
        """Get recent messages"""
        query_engine = TeleCrawlQuery(self.db)
        return query_engine.get_recent(chat_id=chat_id, limit=limit)

    def stats(self):
        """Get database stats"""
        query_engine = TeleCrawlQuery(self.db)
        return query_engine.get_stats()

    def status(self):
        """Get status like discrawl"""
        stats = self.stats()
        cursor = self.db.conn.cursor()

        date_range = cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp) FROM messages
        """).fetchone()

        lines = [
            "",
            "═" * 50,
            "  📊 telecrawl — live".center(50),
            "═" * 50,
            "",
            f"  🗂️  {stats['total_messages']:,} messages archived",
            f"  💬 {stats['total_chats']:,} chats indexed",
        ]

        if date_range[0] and date_range[1]:
            oldest = datetime.fromtimestamp(date_range[0])
            newest = datetime.fromtimestamp(date_range[1])
            days_span = (newest - oldest).days
            lines.append(f"  📅 {days_span:,} days of history")
            lines.append(f"\n  🕐 Last message: {newest.strftime('%Y-%m-%d %H:%M')}")

        lines.extend([
            "",
            "═" * 50,
            "  ✓ Database ready".center(50),
            "═" * 50,
            ""
        ])

        return "\n".join(lines)

    def close(self):
        """Close database connection"""
        self.db.close()


# Global instance for reuse
_logger = None

def get_logger(db_path=None):
    """Get or create global logger instance"""
    global _logger
    if _logger is None:
        _logger = TelecrawlLogger(db_path)
    return _logger


def log_inbound(message_id, chat_id, sender_id, sender_name, text, topic_id=None, 
                 chat_name=None, topic_name=None, reply_to=None):
    """
    Quick function to log an inbound message
    Call this from main session when messages arrive
    """
    logger = get_logger()
    
    # Enhance text with context if provided
    context_parts = []
    if chat_name:
        context_parts.append(f"[Chat: {chat_name}]")
    if topic_name:
        context_parts.append(f"[Topic: {topic_name}]")
    
    # Store context in a structured way - we'll add a context table
    message = {
        'message_id': message_id,
        'chat_id': chat_id,
        'topic_id': topic_id,
        'sender_id': sender_id,
        'sender_username': sender_name.replace(' ', '_').lower() if sender_name else None,
        'sender_first_name': sender_name.split()[0] if sender_name else '',
        'sender_last_name': ' '.join(sender_name.split()[1:]) if sender_name and len(sender_name.split()) > 1 else None,
        'text': text,
        'timestamp': int(datetime.now().timestamp())
    }
    
    # Log with context note
    if context_parts:
        print(f"📥 Logging: {''.join(context_parts)} from {sender_name}")
    
    return logger.log_message(
        message_id=message_id,
        chat_id=chat_id,
        sender_id=sender_id,
        sender_name=sender_name,
        text=text,
        topic_id=topic_id
    )


def search_memory(query, chat_id=None, limit=10):
    """Search the message memory"""
    logger = get_logger()
    return logger.search(query, chat_id=chat_id, limit=limit)


def get_status():
    """Get memory status"""
    logger = get_logger()
    return logger.status()
