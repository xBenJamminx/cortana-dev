"""
Telegram message syncing via Telethon (MTProto user API)
Full history access — no conflicts with Bot API gateway
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from telethon import TelegramClient
from telethon.tl.types import Message, PeerChannel
from .db import TeleCrawlDB


class TelegramSyncer:
    def __init__(self, api_id: int, api_hash: str, db: TeleCrawlDB, session_path: str = None):
        self.api_id = api_id
        self.api_hash = api_hash
        self.db = db
        self.session_path = session_path or os.path.expanduser('~/.telecrawl/telecrawl')
        
        # Ensure session directory exists
        os.makedirs(os.path.dirname(self.session_path), exist_ok=True)
        
        self.client = TelegramClient(self.session_path, api_id, api_hash)

    async def connect(self):
        """Connect and authenticate"""
        await self.client.start()
        me = await self.client.get_me()
        print(f"Authenticated as {me.first_name} (@{me.username})")

    async def disconnect(self):
        """Disconnect client"""
        await self.client.disconnect()

    async def sync_chat(self, chat_id: int, verbose: bool = False, full: bool = False) -> int:
        """
        Sync all messages from a chat using Telethon.
        Uses get_messages() which gives full history access.
        Returns number of new messages synced.
        """
        last_message_id = self.db.get_last_message_id(chat_id) if not full else None
        new_messages = 0

        if verbose:
            print(f"Syncing chat {chat_id} (last message: {last_message_id or 'full sync'})")

        try:
            entity = await self.client.get_entity(chat_id)
        except Exception as e:
            print(f"Error getting entity for {chat_id}: {e}")
            return 0

        # Fetch messages in batches
        # min_id = last synced message (only get newer ones)
        min_id = last_message_id if last_message_id and not full else 0
        batch_size = 100
        highest_id = last_message_id or 0

        async for message in self.client.iter_messages(
            entity,
            min_id=min_id,
            limit=None,  # Get all messages
            reverse=True  # Oldest first for consistent ordering
        ):
            if not isinstance(message, Message):
                continue

            msg_data = self._parse_message(message, chat_id)
            if msg_data:
                if self.db.insert_message(msg_data):
                    new_messages += 1
                    if message.id > highest_id:
                        highest_id = message.id

                    if verbose and new_messages % 100 == 0:
                        print(f"  Synced {new_messages} messages...")

        # Update sync state
        if highest_id > 0:
            self.db.update_sync_state(chat_id, highest_id)

        if verbose:
            print(f"  Done: {new_messages} new messages")

        return new_messages

    def _parse_message(self, message: Message, chat_id: int) -> Optional[Dict[str, Any]]:
        """Parse Telethon message into our schema"""
        text = message.text or message.message
        if not text:
            # Include caption for media messages
            if hasattr(message, 'caption') and message.caption:
                text = message.caption
            else:
                return None

        sender = message.sender
        sender_id = message.sender_id
        sender_username = None
        sender_first_name = None
        sender_last_name = None

        if sender:
            sender_username = getattr(sender, 'username', None)
            sender_first_name = getattr(sender, 'first_name', None)
            sender_last_name = getattr(sender, 'last_name', None)

        # reply_to_msg_id gives us the topic/thread in forum groups
        topic_id = None
        if message.reply_to:
            topic_id = getattr(message.reply_to, 'reply_to_top_id', None) or getattr(message.reply_to, 'reply_to_msg_id', None)

        return {
            'message_id': message.id,
            'chat_id': chat_id,
            'topic_id': topic_id,
            'sender_id': sender_id,
            'sender_username': sender_username,
            'sender_first_name': sender_first_name,
            'sender_last_name': sender_last_name,
            'text': text,
            'timestamp': int(message.date.timestamp())
        }

    async def sync_multiple_chats(self, chat_ids: List[int], verbose: bool = False, full: bool = False) -> Dict[int, int]:
        """Sync multiple chats sequentially"""
        results = {}
        for chat_id in chat_ids:
            try:
                count = await self.sync_chat(chat_id, verbose=verbose, full=full)
                results[chat_id] = count
                if verbose:
                    print(f"Chat {chat_id}: synced {count} new messages")
            except Exception as e:
                print(f"Error syncing chat {chat_id}: {e}")
                results[chat_id] = 0
        return results
