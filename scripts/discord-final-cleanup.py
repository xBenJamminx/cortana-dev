#!/usr/bin/env python3
"""Final cleanup — move orphan rules, delete WELCOME category."""

import discord
import os
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.openclaw/.env"))

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)

    # Find the duplicate #rules in WELCOME category and delete it
    welcome_cat = discord.utils.get(guild.categories, name="WELCOME")
    if welcome_cat:
        for ch in welcome_cat.text_channels:
            if ch.name == "rules":
                # We already have rules in INFO, delete this duplicate
                print(f"Deleting duplicate #rules from WELCOME...")
                try:
                    await ch.delete(reason="Duplicate — rules already in INFO")
                except Exception as e:
                    # If can't delete, move to INFO instead
                    print(f"  Can't delete (community protected), trying to move...")
                    info_cat = discord.utils.get(guild.categories, name="📋 INFO")
                    if info_cat:
                        await ch.edit(category=info_cat)
                        print(f"  Moved to INFO")

        # Now try to delete empty WELCOME
        guild = client.get_guild(GUILD_ID)
        welcome_cat = discord.utils.get(guild.categories, name="WELCOME")
        if welcome_cat and len(welcome_cat.channels) == 0:
            print("Deleting empty WELCOME category...")
            await welcome_cat.delete(reason="Cleanup")

    # Move moderator-only somewhere unobtrusive if it exists
    for ch in guild.text_channels:
        if ch.name == "moderator-only" and ch.category is None:
            info_cat = discord.utils.get(guild.categories, name="📋 INFO")
            if info_cat:
                print("Moving #moderator-only to 📋 INFO...")
                await ch.edit(category=info_cat)

    # Final print
    guild = client.get_guild(GUILD_ID)
    print("\n--- FINAL SERVER STATE ---")
    for cat in sorted(guild.categories, key=lambda c: c.position):
        print(f"\n{cat.name}:")
        for ch in cat.channels:
            ctype = "voice" if isinstance(ch, discord.VoiceChannel) else "text"
            print(f"  #{ch.name} ({ctype})")
    for ch in guild.text_channels:
        if ch.category is None:
            print(f"\nUncategorized: #{ch.name}")

    print("\n✅ All clean!")
    await client.close()


client.run(BOT_TOKEN)
