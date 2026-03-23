"""
Internal memory helper for Cortana
Auto-logs messages + queries for natural language memory

USAGE:
  Call auto_log_message() in every session when messages arrive
  Import at top of main.py or use as middleware
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from telecrawl.db import TeleCrawlDB
from telecrawl.query import TeleCrawlQuery


def search_conversation_memory(query, chat_id=None, topic_id=None, limit=10):
    """
    Search past conversations to answer user's questions
    
    Args:
        query: What to search for (e.g., "telegaf decision")
        chat_id: Optional specific chat
        topic_id: Optional specific topic
        limit: Number of results
    
    Returns:
        Formatted string with results
    """
    # Look in memory dir
    db_paths = [
        Path.home() / ".openclaw" / "memory" / "telecrawl.db",
        Path.home() / ".openclaw" / "memory" / "telegaf.db",  # legacy
    ]
    
    db_path = None
    for p in db_paths:
        if p.exists():
            db_path = p
            break
    
    if not db_path:
        return "No memory database found yet."
    
    db = TeleCrawlDB(db_path)
    db.connect()
    
    try:
        query_engine = TeleCrawlQuery(db)
        results = query_engine.search(query, chat_id=chat_id, limit=limit)
        
        if not results:
            return f"No results found for '{query}'."
        
        lines = [f"Found {len(results)} messages about '{query}':\n"]
        
        for r in results:
            # Format timestamp (handle both int and pre-formatted string)
            ts_val = r['timestamp']
            if isinstance(ts_val, str) and ts_val.count('-') == 2:
                # Already formatted like '2026-03-08 13:23:54'
                time_str = ts_val[:16]  # Just take YYYY-MM-DD HH:MM
            elif isinstance(ts_val, (int, float)):
                ts = datetime.fromtimestamp(ts_val)
                time_str = ts.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = str(ts_val)[:16]
            
            # Get sender
            sender = r.get('sender_first_name', 'Unknown')
            if r.get('sender_last_name'):
                sender += f" {r['sender_last_name']}"
            
            # Build context
            context = ""
            if r.get('topic_id'):
                context = f" [Topic {r['topic_id']}]"
            
            lines.append(f"• {time_str} - {sender}{context}")
            lines.append(f"  \"{r['text'][:200]}{'...' if len(r['text']) > 200 else ''}\"")
            lines.append("")
        
        return "\n".join(lines)
        
    finally:
        db.close()


def get_recent_context(chat_id=None, topic_id=None, minutes=60, limit=20):
    """
    Get recent conversation context
    
    Args:
        chat_id: Specific chat
        topic_id: Specific topic
        minutes: How far back to look
        limit: Max results
    
    Returns:
        Formatted string with recent messages
    """
    db_paths = [
        Path.home() / ".openclaw" / "memory" / "telecrawl.db",
        Path.home() / ".openclaw" / "memory" / "telegaf.db",
    ]
    
    db_path = None
    for p in db_paths:
        if p.exists():
            db_path = p
            break
    
    if not db_path:
        return "No memory database."
    
    db = TeleCrawlDB(db_path)
    db.connect()
    
    try:
        query_engine = TeleCrawlQuery(db)
        results = query_engine.get_recent(chat_id=chat_id, limit=limit)
        
        if not results:
            return "No recent messages found."
        
        lines = [f"Recent conversation ({len(results)} messages):\n"]
        
        for r in results:
            ts_val = r['timestamp']
            if isinstance(ts_val, str) and ':' in ts_val:
                # Pre-formatted, extract just the time
                time_str = ts_val[11:16] if len(ts_val) > 16 else ts_val[:5]
            elif isinstance(ts_val, (int, float)):
                ts = datetime.fromtimestamp(ts_val)
                time_str = ts.strftime('%H:%M')
            else:
                time_str = "??:??"
            sender = r.get('sender_first_name', 'Unknown')
            lines.append(f"[{time_str}] {sender}: {r['text'][:100]}")
        
        return "\n".join(lines)
        
    finally:
        db.close()


def should_query_memory(user_message):
    """
    Detect if user is asking about past conversations
    Returns True if message contains memory-query patterns
    """
    import re
    
    patterns = [
        r"what did (we|you|I) (say|decide|discuss|talk about|mention)",
        r"(remember|recall) (when|what|how) (we|you|I)",
        r"what was (the decision|our decision|that about)",
        r"(earlier|before|last time|yesterday|last week)",
        r"(search|find) (for|in|our) (messages|conversations|history)",
        r"did (we|you) (say|mention|talk about)",
        r"refresh my memory",
        r"remind me (what|how|when)",
    ]
    
    msg_lower = user_message.lower()
    for pattern in patterns:
        if re.search(pattern, msg_lower):
            return True
    
    return False


# === AUTO-LOGGING ===
# Global logger instance (lazy-loaded)
_auto_logger = None

def get_auto_logger():
    """Get singleton logger instance"""
    global _auto_logger
    if _auto_logger is None:
        from telecrawl_logger import TelecrawlLogger
        db_path = Path.home() / ".openclaw" / "memory" / "telecrawl.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _auto_logger = TelecrawlLogger(db_path)
    return _auto_logger


def auto_log_message(message_id, chat_id, sender_id, sender_name, text, topic_id=None):
    """
    AUTO-LOG: Call this silently on EVERY inbound message
    
    This is fire-and-forget - exceptions caught silently
    """
    try:
        logger = get_auto_logger()
        return logger.log_message(
            message_id=message_id,
            chat_id=chat_id,
            sender_id=sender_id,
            sender_name=sender_name,
            text=text,
            topic_id=topic_id
        )
    except Exception:
        # Fail silently - logging should never break the main flow
        pass


def auto_log_current_context():
    """
    Auto-log using the current OpenClaw context metadata
    Call this at the start of every message processing
    """
    try:
        import json
        import os
        
        # OpenClaw injects metadata as environment or context
        # Try to get from environment first
        inbound_json = os.environ.get('OPENCLAW_INBOUND_META')
        sender_json = os.environ.get('OPENCLAW_SENDER_META')
        message_text = os.environ.get('OPENCLAW_MESSAGE_TEXT')
        
        if inbound_json and sender_json:
            inbound = json.loads(inbound_json)
            sender = json.loads(sender_json)
            
            message_id = inbound.get('message_id')
            chat_id = inbound.get('chat_id')
            if isinstance(chat_id, str) and ':' in chat_id:
                chat_id = int(chat_id.split(':')[-1])
            
            sender_id = sender.get('id')
            sender_name = sender.get('name') or sender.get('username') or 'Unknown'
            topic_id = inbound.get('topic_id')
            
            auto_log_message(
                message_id=message_id,
                chat_id=chat_id,
                sender_id=sender_id,
                sender_name=sender_name,
                text=message_text or '',
                topic_id=topic_id
            )
            return True
    except Exception:
        pass
    return False
