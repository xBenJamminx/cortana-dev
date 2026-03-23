"""Two-step Telethon authentication"""
import os
import sys
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv("/root/.openclaw/.env")
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION = os.path.expanduser("~/.telecrawl/telecrawl")
os.makedirs(os.path.dirname(SESSION), exist_ok=True)

async def request_code(phone):
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    result = await client.send_code_request(phone)
    print(f"Code sent to {phone}")
    print(f"phone_code_hash: {result.phone_code_hash}")
    # Save for step 2
    with open(os.path.expanduser("~/.telecrawl/.auth_state"), "w") as f:
        f.write(f"{phone}\n{result.phone_code_hash}\n")
    await client.disconnect()

async def verify_code(code):
    with open(os.path.expanduser("~/.telecrawl/.auth_state")) as f:
        phone = f.readline().strip()
        phone_code_hash = f.readline().strip()
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    await client.sign_in(phone, code, phone_code_hash=phone_code_hash)
    me = await client.get_me()
    print(f"Authenticated as {me.first_name} (@{me.username})")
    await client.disconnect()
    os.remove(os.path.expanduser("~/.telecrawl/.auth_state"))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: auth.py request <phone>  OR  auth.py verify <code>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "request":
        asyncio.run(request_code(sys.argv[2]))
    elif cmd == "verify":
        asyncio.run(verify_code(sys.argv[2]))
