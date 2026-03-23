"""
Daemon mode for telecrawl - polls Telegram for live updates
Similar to discrawl tail
"""

import time
import signal
import sys
from datetime import datetime
from typing import Optional

from .db import TeleCrawlDB
from .sync import TelegramSyncer


class TelegramTail:
    """Polls Telegram Bot API for new messages and logs them"""
    
    def __init__(self, bot_token: str, db: TeleCrawlDB, chat_ids: list = None):
        self.bot_token = bot_token
        self.db = db
        self.chat_ids = chat_ids or []
        self.syncer = TelegramSyncer(bot_token, db)
        self.running = False
        self.last_update_id = None
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        print("\n🛑 Shutting down gracefully...")
        self.running = False
    
    def tail_single_chat(self, chat_id: int, poll_interval: int = 5):
        """Poll for updates in a single chat"""
        print(f"👁️  Tailing chat {chat_id}...")
        
        while self.running:
            try:
                # Get updates via long-polling
                new_messages = self.syncer.sync_chat(chat_id, verbose=False)
                
                if new_messages:
                    print(f"✓ {new_messages} new messages")
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"⚠️  Error: {e}")
                time.sleep(10)  # Back off on error
    
    def tail_updates(self, poll_interval: int = 5):
        """
        Use getUpdates endpoint to poll for messages
        This is the primary tail mode for Telegram
        """
        import requests
        
        print(f"🚀 telecrawl tail starting...")
        print(f"   Polling every {poll_interval}s")
        if self.chat_ids:
            print(f"   Monitoring chats: {self.chat_ids}")
        else:
            print("   Monitoring all chats")
        print()
        
        self.running = True
        offset = None
        
        while self.running:
            try:
                # Poll for updates
                params = {'limit': 100}
                if offset:
                    params['offset'] = offset
                
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code != 200:
                    print(f"⚠️  API error: {response.status_code}")
                    time.sleep(5)
                    continue
                
                data = response.json()
                if not data.get('ok'):
                    print(f"⚠️  Telegram error: {data}")
                    time.sleep(5)
                    continue
                
                updates = data.get('result', [])
                
                for update in updates:
                    offset = update['update_id'] + 1
                    
                    # Process message
                    message = update.get('message') or update.get('edited_message')
                    if not message:
                        continue
                    
                    # Filter by chat if specified
                    chat_id = message.get('chat', {}).get('id')
                    if self.chat_ids and chat_id not in self.chat_ids:
                        continue
                    
                    # Extract and log
                    self._log_message(message)
                
                time.sleep(poll_interval)
                
            except requests.exceptions.ReadTimeout:
                continue  # Long polling timeout is normal
            except Exception as e:
                print(f"⚠️  Error: {e}")
                time.sleep(5)
        
        print("👋 Tail stopped")
    
    def _log_message(self, message: dict):
        """Log a single message to the database"""
        msg_id = message.get('message_id')
        chat = message.get('chat', {})
        chat_id = chat.get('id')
        chat_title = chat.get('title') or chat.get('username') or 'Unknown'
        
        sender = message.get('from', {})
        sender_id = sender.get('id')
        sender_name = sender.get('first_name') or sender.get('username') or 'Unknown'
        
        text = message.get('text') or message.get('caption', '')
        if not text:
            # Skip non-text messages or log them with type
            text = f"[{message.get('content_type', 'media')}]"
        
        # Get forum topic if present
        topic_id = message.get('message_thread_id')
        
        timestamp = message.get('date', int(time.time()))
        
        # Log to database
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
        
        self.db.insert_message(msg_data)
        
        # Print live
        topic_str = f" [Topic {topic_id}]" if topic_id else ""
        dt = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        print(f"[{dt}] {chat_title}{topic_str}: {sender_name}: {text[:60]}{'...' if len(text) > 60 else ''}")


def cmd_tail(args):
    """CLI entry point for tail command"""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
    
    from .db import TeleCrawlDB
    db = TeleCrawlDB(args.db)
    db.connect()
    
    try:
        tail = TelegramTail(bot_token, db, chat_ids=args.chat_id)
        tail.tail_updates(poll_interval=args.interval)
    except KeyboardInterrupt:
        print("\n👋 Stopped")
    finally:
        db.close()
