"""
Command-line interface for telecrawl
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

from .db import TeleCrawlDB
from .sync import TelegramSyncer
from .query import TeleCrawlQuery
from .tail import cmd_tail


DEFAULT_DB = os.path.expanduser("~/.telecrawl/telecrawl.db")


def load_config():
    env_paths = ["/root/.openclaw/.env", "/root/.openclaw/workspace/.env", ".env"]
    for p in env_paths:
        if os.path.exists(p):
            load_dotenv(p)
            break

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    if not api_id or not api_hash:
        print("Error: TELEGRAM_API_ID and TELEGRAM_API_HASH not found")
        sys.exit(1)

    return int(api_id), api_hash


def cmd_sync(args):
    api_id, api_hash = load_config()
    db = TeleCrawlDB(args.db)
    db.connect()
    syncer = TelegramSyncer(api_id, api_hash, db)

    async def run():
        await syncer.connect()
        chat_ids = [int(cid.strip()) for cid in args.chat_id.split(",")]
        results = await syncer.sync_multiple_chats(chat_ids, verbose=args.verbose, full=args.full)
        total = sum(results.values())
        print(f"\nSync complete: {total} new messages")
        await syncer.disconnect()

    asyncio.run(run())
    db.close()


def cmd_search(args):
    db = TeleCrawlDB(args.db)
    db.connect()
    query_engine = TeleCrawlQuery(db)
    results = query_engine.search(args.query, chat_id=args.chat_id, limit=args.limit)
    if not results:
        print("No results found")
    else:
        print(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            topic = f" [T:{result['topic_id']}]" if result.get("topic_id") else ""
            print(f"{i}. [{result['message_id']}]{topic} {result['sender']} @ {result['timestamp']}")
            print(f"   {result['text'][:200]}")
            print(f"   Relevance: {result['relevance']:.2f}\n")
    db.close()


def cmd_recent(args):
    db = TeleCrawlDB(args.db)
    db.connect()
    query_engine = TeleCrawlQuery(db)
    results = query_engine.get_recent(chat_id=args.chat_id, limit=args.limit)
    if not results:
        print("No messages found")
    else:
        for result in results:
            topic = f" [T:{result['topic_id']}]" if result.get("topic_id") else ""
            print(f"[{result['message_id']}]{topic} {result['sender']} @ {result['timestamp']}")
            print(f"   {result['text'][:200]}\n")
    db.close()


def cmd_stats(args):
    db = TeleCrawlDB(args.db)
    db.connect()
    stats = TeleCrawlQuery(db).get_stats()
    print(f"Total messages: {stats['total_messages']}")
    print(f"Total chats: {stats['total_chats']}")
    if stats["chats"]:
        for chat in stats["chats"]:
            print(f"  Chat {chat['chat_id']}: {chat['message_count']} messages")
    db.close()


def cmd_doctor(args):
    db = TeleCrawlDB(args.db)
    db.connect()
    health = TeleCrawlQuery(db).verify()
    print(f"Messages: {health['messages_count']}")
    print(f"FTS entries: {health['fts_count']}")
    status = "HEALTHY" if health["healthy"] else "ISSUES DETECTED"
    print(f"Status: {status}")
    db.close()


def cmd_status(args):
    from datetime import datetime
    db = TeleCrawlDB(args.db)
    db.connect()
    stats = TeleCrawlQuery(db).get_stats()
    cursor = db.conn.cursor()
    dr = cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM messages").fetchone()
    print(f"{stats['total_messages']:,} messages archived")
    print(f"{stats['total_chats']:,} chats indexed")
    if dr[0] and dr[1]:
        days = (datetime.fromtimestamp(dr[1]) - datetime.fromtimestamp(dr[0])).days
        print(f"{days:,} days of history")
        print(f"Last message: {datetime.fromtimestamp(dr[1]).strftime('%Y-%m-%d %H:%M')}")
    db.close()


def main():
    parser = argparse.ArgumentParser(description="telecrawl: Telegram memory with full-text search")
    parser.add_argument("--db", default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("sync")
    sp.add_argument("--chat-id", required=True)
    sp.add_argument("-v", "--verbose", action="store_true")
    sp.add_argument("--full", action="store_true", help="Full resync")

    sp = sub.add_parser("search")
    sp.add_argument("query")
    sp.add_argument("--chat-id", type=int)
    sp.add_argument("-l", "--limit", type=int, default=50)

    sp = sub.add_parser("recent")
    sp.add_argument("--chat-id", type=int)
    sp.add_argument("-l", "--limit", type=int, default=50)

    sub.add_parser("stats")
    sub.add_parser("status")
    sub.add_parser("doctor")

    sp = sub.add_parser("tail")
    sp.add_argument("--chat-id", type=int, action="append")
    sp.add_argument("-i", "--interval", type=int, default=5)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "sync": cmd_sync, "search": cmd_search, "recent": cmd_recent,
        "stats": cmd_stats, "status": cmd_status, "tail": cmd_tail, "doctor": cmd_doctor
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
