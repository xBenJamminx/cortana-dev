"""
Daemon mode for telecrawl — live message capture via Telethon
Listens for new messages in real-time using MTProto events
"""

import os
import sys
import time
import asyncio
import signal
from datetime import datetime
from typing import Optional, List

from telethon import TelegramClient, events
from telethon.tl.types import Message

from .db import TeleCrawlDB


class TelegramTail:
    """Real-time message capture using Telethon events"""

    def __init__(self, api_id: int, api_hash: str, db: TeleCrawlDB,
                 chat_ids: List[int] = None, session_path: str = None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.db = db
        self.chat_ids = chat_ids or []
        self.session_path = session_path or os.path.expanduser('~/.telecrawl/telecrawl')
        self.running = False

        os.makedirs(os.path.dirname(self.session_path), exist_ok=True)
        self.client = TelegramClient(self.session_path, api_id, api_hash)

    async def start(self):
        """Start listening for messages"""
        await self.client.start()
        me = await self.client.get_me()
        print(f"Authenticated as {me.first_name} (@{me.username})")

        # Register message handler
        @self.client.on(events.NewMessage(chats=self.chat_ids or None))
        async def handler(event):
            message = event.message
            if not isinstance(message, Message):
                return

            text = message.text or message.message
            if not text:
                return

            sender = await event.get_sender()
            sender_username = getattr(sender, 'username', None) if sender else None
            sender_first_name = getattr(sender, 'first_name', None) if sender else None
            sender_last_name = getattr(sender, 'last_name', None) if sender else None

            topic_id = None
            if message.reply_to:
                topic_id = getattr(message.reply_to, 'reply_to_top_id', None) or \
                           getattr(message.reply_to, 'reply_to_msg_id', None)

            chat_id = event.chat_id

            msg_data = {
                'message_id': message.id,
                'chat_id': chat_id,
                'topic_id': topic_id,
                'sender_id': message.sender_id,
                'sender_username': sender_username,
                'sender_first_name': sender_first_name,
                'sender_last_name': sender_last_name,
                'text': text,
                'timestamp': int(message.date.timestamp())
            }

            self.db.insert_message(msg_data)

            # Update sync state
            self.db.update_sync_state(chat_id, message.id)

            # Print live
            name = sender_username or sender_first_name or 'Unknown'
            topic_str = f" [T:{topic_id}]" if topic_id else ""
            dt = datetime.fromtimestamp(int(message.date.timestamp())).strftime('%H:%M:%S')
            preview = text[:60] + ('...' if len(text) > 60 else '')
            print(f"[{dt}]{topic_str} {name}: {preview}")

        self.running = True
        print(f"\nTailing {'chats: ' + str(self.chat_ids) if self.chat_ids else 'all chats'}...")
        print("Press Ctrl+C to stop\n")

        await self.client.run_until_disconnected()

    async def stop(self):
        """Stop the tail"""
        self.running = False
        await self.client.disconnect()


def cmd_tail(args):
    """CLI entry point for tail command"""
    from dotenv import load_dotenv

    # Load env
    env_paths = ['/root/.openclaw/.env', '/root/.openclaw/workspace/.env']
    for p in env_paths:
        if os.path.exists(p):
            load_dotenv(p)
            break

    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')

    if not api_id or not api_hash:
        print("Error: TELEGRAM_API_ID and TELEGRAM_API_HASH not set")
        print("Add to .env: TELEGRAM_API_ID=xxx  TELEGRAM_API_HASH=xxx")
        sys.exit(1)

    db = TeleCrawlDB(args.db)
    db.connect()

    try:
        tail = TelegramTail(int(api_id), api_hash, db, chat_ids=args.chat_id)
        asyncio.run(tail.start())
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        db.close()
