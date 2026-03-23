#!/usr/bin/env python3
"""Clean up leftover Discord artifacts — empty categories, orphan rules channels."""

import discord
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.openclaw/.env"))

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

TARGET_CATEGORIES = {"📋 INFO", "💬 COMMUNITY", "📦 RESOURCES"}

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    print(f"Server: {guild.name}")

    # 1. Try to disable community features so we can delete rules channels
    # Actually, let's just move the rules channel into INFO and repurpose it
    # Or delete non-target categories and orphan channels

    # Delete empty non-target categories
    for cat in guild.categories:
        if cat.name not in TARGET_CATEGORIES:
            if len(cat.channels) == 0:
                print(f"Deleting empty category: {cat.name}")
                try:
                    await cat.delete(reason="Cleanup")
                except Exception as e:
                    print(f"  Could not delete: {e}")
            else:
                print(f"Non-target category with channels: {cat.name}")
                for ch in cat.channels:
                    print(f"  - #{ch.name} (type: {ch.type})")
                    # Try to delete non-essential channels in old categories
                    if ch.name not in ("rules", "moderator-only"):
                        print(f"    Deleting #{ch.name}...")
                        try:
                            await ch.delete(reason="Cleanup")
                        except Exception as e:
                            print(f"    Could not delete: {e}")

    # Check for uncategorized channels
    for ch in guild.text_channels:
        if ch.category is None:
            print(f"Uncategorized: #{ch.name}")
            # Move rules to INFO category if needed, or try to delete
            if ch.name == "rules":
                info_cat = discord.utils.get(guild.categories, name="📋 INFO")
                if info_cat:
                    print(f"  Moving #rules to 📋 INFO")
                    try:
                        await ch.edit(category=info_cat)
                    except Exception as e:
                        print(f"  Could not move: {e}")
            elif ch.name == "moderator-only":
                print(f"  Trying to delete #moderator-only...")
                try:
                    await ch.delete(reason="Cleanup")
                except Exception as e:
                    print(f"  Could not delete: {e}")

    # Try deleting remaining empty categories again
    guild = client.get_guild(GUILD_ID)
    for cat in guild.categories:
        if cat.name not in TARGET_CATEGORIES and len(cat.channels) == 0:
            print(f"Deleting now-empty category: {cat.name}")
            try:
                await cat.delete(reason="Cleanup")
            except Exception as e:
                print(f"  Could not delete: {e}")

    # Final state
    print("\n--- FINAL STATE ---")
    guild = client.get_guild(GUILD_ID)
    for cat in guild.categories:
        print(f"\n{cat.name}:")
        for ch in cat.channels:
            print(f"  #{ch.name}")
    for ch in guild.text_channels:
        if ch.category is None:
            print(f"\nUncategorized: #{ch.name}")

    print("\n✅ Cleanup done!")
    await client.close()


client.run(BOT_TOKEN)
