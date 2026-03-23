"""
AUTO-LOG: This runs at the start of EVERY message processing
Call log_current_message() immediately when a message arrives
"""

import sys
from pathlib import Path
from datetime import datetime

# Ensure telecrawl is available
sys.path.insert(0, str(Path(__file__).parent))

from telecrawl.db import TeleCrawlDB

# Global DB connection (persistent)
_db = None
_db_path = Path.home() / ".openclaw" / "memory" / "telecrawl.db"

def get_db():
    """Get or create persistent DB connection"""
    global _db
    if _db is None:
        _db_path.parent.mkdir(parents=True, exist_ok=True)
        _db = TeleCrawlDB(_db_path)
        _db.connect()
    return _db


def log_current_message(message_id, chat_id, sender_id, sender_name, text, topic_id=None):
    """
    AUTO-LOG: Call this immediately on EVERY inbound message
    
    Usage: At the very top of message processing, call:
        log_current_message(message_id, chat_id, sender_id, sender_name, text, topic_id)
    """
    try:
        if not text:
            return False
            
        db = get_db()
        
        # Parse sender name
        parts = sender_name.split() if sender_name else ["", ""]
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else None
        username = sender_name.replace(" ", "_").lower() if sender_name else None
        
        # Handle chat_id format (might be "telegram:-100...")
        if isinstance(chat_id, str) and ":" in chat_id:
            chat_id = int(chat_id.split(":")[-1])
        else:
            chat_id = int(chat_id)
        
        result = db.insert_message({
            'message_id': int(message_id),
            'chat_id': chat_id,
            'topic_id': int(topic_id) if topic_id else None,
            'sender_id': int(sender_id) if sender_id else None,
            'sender_username': username,
            'sender_first_name': first_name,
            'sender_last_name': last_name,
            'text': text,
            'timestamp': int(datetime.now().timestamp())
        })
        
        return result
        
    except Exception as e:
        # Silently fail - logging should NEVER break the main flow
        return False


def close_db():
    """Close DB connection (call on shutdown)"""
    global _db
    if _db:
        _db.close()
        _db = None
