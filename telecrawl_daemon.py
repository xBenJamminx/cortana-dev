#!/usr/bin/env python3
"""
Telecrawl Daemon - Standalone message logger
Runs continuously and logs Telegram messages to SQLite
"""

import sys
import os
import time
import signal
import requests
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, '/root/.openclaw/workspace/lib')
sys.path.insert(0, '/tmp/telecrawl')

from telecrawl.db import TeleCrawlDB

# Global state
running = True
db = None

def signal_handler(signum, frame):
    global running
    print("\n🛑 Shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_env_token():
    """Get token from OpenClaw env"""
    env_path = Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    return line.split('=', 1)[1].strip()
    return os.getenv('TELEGRAM_BOT_TOKEN')

def main():
    global db, running
    
    # Get configuration
    bot_token = get_env_token()
    chat_id = int(os.getenv('TELEGRAM_CHAT_ID', '-1003856131939'))
    
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN not found")
        sys.exit(1)
    
    # Initialize DB
    db_path = Path.home() / ".openclaw" / "memory" / "telecrawl.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = TeleCrawlDB(db_path)
    db.connect()
    
    print(f"🚀 Telecrawl daemon started")
    print(f"   Chat: {chat_id}")
    print(f"   DB: {db_path}")
    print(f"   Logging messages...")
    print("")
    
    offset = None
    
    while running:
        try:
            # Poll for updates
            params = {'limit': 100, 'timeout': 30}
            if offset:
                params['offset'] = offset
            
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code != 200:
                print(f"⚠️ API error: {response.status_code}")
                time.sleep(5)
                continue
            
            data = response.json()
            if not data.get('ok'):
                print(f"⚠️ Telegram error: {data}")
                time.sleep(5)
                continue
            
            updates = data.get('result', [])
            
            for update in updates:
                offset = update['update_id'] + 1
                
                message = update.get('message') or update.get('edited_message') or update.get('channel_post')
                if not message:
                    continue
                
                # Filter by chat
                msg_chat_id = message.get('chat', {}).get('id')
                if msg_chat_id != chat_id:
                    continue
                
                # Log the message
                log_message(message)
                
        except requests.exceptions.ReadTimeout:
            continue
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)
    
    print("👋 Daemon stopped")
    db.close()

def log_message(message):
    """Log a single message"""
    global db
    
    msg_id = message.get('message_id')
    chat = message.get('chat', {})
    chat_id = chat.get('id')
    chat_title = chat.get('title') or chat.get('username') or 'Unknown'
    
    sender = message.get('from', {})
    sender_id = sender.get('id')
    sender_name = sender.get('first_name') or sender.get('username') or 'Unknown'
    
    text = message.get('text') or message.get('caption', '')
    if not text:
        text = f"[media message]"
    
    topic_id = message.get('message_thread_id')
    timestamp = message.get('date', int(time.time()))
    
    # Insert to DB
    msg_data = {
        'message_id': msg_id,
        'chat_id': chat_id,
        'topic_id': topic_id,
        'sender_id': sender_id,
        'sender_username': sender.get('username'),
        'sender_first_name': sender.get('first_name'),
        'sender_last_name': sender.get('last_name'),
        'text': text,
        'timestamp': timestamp
    }
    
    db.insert_message(msg_data)
    
    # Print live
    topic_str = f" [Topic {topic_id}]" if topic_id else ""
    dt = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    print(f"[{dt}] {chat_title}{topic_str}: {sender_name}: {text[:60]}{'...' if len(text) > 60 else ''}")

if __name__ == "__main__":
    main()
