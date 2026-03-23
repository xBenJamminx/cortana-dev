# Auto-Logging Setup for OpenClaw

To make telecrawl logging automatic, add this to the OpenClaw gateway message processing:

## Option 1: Middleware Hook (Recommended)

In the OpenClaw gateway, before dispatching to the agent:

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/lib')
from telecrawl.db import TeleCrawlDB
from pathlib import Path

def log_inbound_message(inbound_meta, sender_meta, text):
    '''Log every message to telecrawl.db'''
    try:
        db_path = Path.home() / ".openclaw" / "memory" / "telecrawl.db"
        db = TeleCrawlDB(db_path)
        db.connect()
        
        msg_id = inbound_meta.get('message_id')
        chat_id = inbound_meta.get('chat_id')
        if isinstance(chat_id, str):
            chat_id = int(chat_id.split(':')[-1])
        
        db.insert_message({
            'message_id': msg_id,
            'chat_id': chat_id,
            'topic_id': inbound_meta.get('topic_id'),
            'sender_id': sender_meta.get('id'),
            'sender_username': sender_meta.get('username'),
            'sender_first_name': sender_meta.get('name', '').split()[0],
            'sender_last_name': ' '.join(sender_meta.get('name', '').split()[1:]) if len(sender_meta.get('name', '').split()) > 1 else None,
            'text': text,
            'timestamp': int(time.time())
        })
        db.close()
    except Exception:
        pass  # Never fail on logging

# Call this in OpenClaw before dispatching to agent
log_inbound_message(inbound_metadata, sender_metadata, message_text)
```

## Option 2: Agent-Side Logging (Current)

Agent manually logs at start of every response:

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/lib')
from telecrawl.db import TeleCrawlDB
from pathlib import Path

# Log current message
db_path = Path.home() / ".openclaw" / "memory" / "telecrawl.db"
db = TeleCrawlDB(db_path)
db.connect()
db.insert_message({...})
db.close()
```

## Current Status

- DB is at: `~/.openclaw/memory/telecrawl.db`
- 16 messages logged manually
- Need OpenClaw gateway change OR agent-side logging to make automatic
