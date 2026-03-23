#!/usr/bin/env python3
"""
Restructure EverydayAI Discord server to match the new free community layout.

Final Channel Map:
  📋 INFO: #welcome, #announcements, #introductions
  💬 COMMUNITY: #general, #help, #show-and-tell, #wins
  📦 RESOURCES: #prompts, #guides, #templates, #tools
"""

import discord
import asyncio
import os
import sys

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.openclaw/.env"))

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

if not BOT_TOKEN or not GUILD_ID:
    print("Missing DISCORD_BOT_TOKEN or DISCORD_GUILD_ID in .env")
    sys.exit(1)

# Target structure
TARGET_STRUCTURE = {
    "📋 INFO": [
        {"name": "welcome", "topic": "What this place is, who Ben is, how to get started"},
        {"name": "announcements", "topic": "New drops, updates, anything important"},
        {"name": "introductions", "topic": "New members say hi — tell us who you are and what you're into"},
    ],
    "💬 COMMUNITY": [
        {"name": "general", "topic": "Main hangout — conversation, vibes, whatever's on your mind"},
        {"name": "help", "topic": "How do I do X? Ask anything AI, automation, or tools related"},
        {"name": "show-and-tell", "topic": "Share what you built, automated, or shipped"},
        {"name": "wins", "topic": "Celebrate what's working — big or small"},
    ],
    "📦 RESOURCES": [
        {"name": "prompts", "topic": "Prompt packs, tips, and techniques"},
        {"name": "guides", "topic": "Tutorials, walkthroughs, and case studies"},
        {"name": "templates", "topic": "Airtable, Notion, spreadsheets, frameworks — grab and go"},
        {"name": "tools", "topic": "Tool recommendations, deals, and reviews"},
    ],
}

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

DRY_RUN = "--dry-run" in sys.argv


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print(f"Could not find guild {GUILD_ID}")
        await client.close()
        return

    print(f"Server: {guild.name}")
    print(f"Current channels: {len(guild.channels)}")
    print(f"Current categories: {[c.name for c in guild.categories]}")
    print(f"Current text channels: {[c.name for c in guild.text_channels]}")
    print()

    if DRY_RUN:
        print("=== DRY RUN MODE — no changes will be made ===\n")

    # Keep track of channels we want to keep
    channels_to_keep = set()
    target_channel_names = set()
    for channels in TARGET_STRUCTURE.values():
        for ch in channels:
            target_channel_names.add(ch["name"])

    # Step 1: Create categories and channels
    print("--- CREATING TARGET STRUCTURE ---")
    position = 0
    for category_name, channels in TARGET_STRUCTURE.items():
        # Check if category exists
        existing_cat = discord.utils.get(guild.categories, name=category_name)
        if existing_cat:
            print(f"✅ Category exists: {category_name}")
            cat = existing_cat
        else:
            print(f"📁 Creating category: {category_name}")
            if not DRY_RUN:
                cat = await guild.create_category(category_name, position=position)
            else:
                cat = None
        position += 1

        for ch_info in channels:
            existing_ch = discord.utils.get(guild.text_channels, name=ch_info["name"])
            if existing_ch:
                print(f"  ✅ Channel exists: #{ch_info['name']}")
                # Move to correct category if needed
                if not DRY_RUN and cat and existing_ch.category != cat:
                    print(f"    ↪ Moving to {category_name}")
                    await existing_ch.edit(category=cat, topic=ch_info["topic"])
                elif not DRY_RUN and cat:
                    # Update topic
                    if existing_ch.topic != ch_info["topic"]:
                        await existing_ch.edit(topic=ch_info["topic"])
                channels_to_keep.add(existing_ch.id)
            else:
                print(f"  ➕ Creating channel: #{ch_info['name']}")
                if not DRY_RUN and cat:
                    new_ch = await cat.create_text_channel(
                        name=ch_info["name"],
                        topic=ch_info["topic"]
                    )
                    channels_to_keep.add(new_ch.id)

    # Step 2: List channels that would be deleted
    print("\n--- CHANNELS NOT IN TARGET STRUCTURE ---")
    to_delete = []
    for ch in guild.text_channels:
        if ch.id not in channels_to_keep and ch.name not in target_channel_names:
            to_delete.append(ch)
            print(f"  🗑️  #{ch.name} (category: {ch.category.name if ch.category else 'None'})")

    # Step 3: List categories that would be deleted
    target_cat_names = set(TARGET_STRUCTURE.keys())
    cats_to_delete = []
    for cat in guild.categories:
        if cat.name not in target_cat_names:
            cats_to_delete.append(cat)
            print(f"  🗑️  Category: {cat.name}")

    # Community servers require certain channels (rules, etc) - skip those
    PROTECTED_CHANNELS = {"rules", "moderator-only"}

    if to_delete or cats_to_delete:
        if DRY_RUN:
            print(f"\n⚠️  DRY RUN: Would delete {len(to_delete)} channels and {len(cats_to_delete)} categories")
        else:
            print(f"\n🗑️  Deleting {len(to_delete)} old channels and {len(cats_to_delete)} old categories...")
            for ch in to_delete:
                if ch.name in PROTECTED_CHANNELS:
                    print(f"  ⚠️  Skipping protected channel #{ch.name}")
                    continue
                print(f"  Deleting #{ch.name}...")
                try:
                    await ch.delete(reason="Server restructure for free community launch")
                except discord.HTTPException as e:
                    print(f"  ⚠️  Cannot delete #{ch.name}: {e}")
            for cat in cats_to_delete:
                # Only delete empty categories
                if len(cat.channels) > 0:
                    print(f"  ⚠️  Skipping non-empty category: {cat.name} ({len(cat.channels)} channels remain)")
                    continue
                print(f"  Deleting category: {cat.name}...")
                try:
                    await cat.delete(reason="Server restructure for free community launch")
                except discord.HTTPException as e:
                    print(f"  ⚠️  Cannot delete category {cat.name}: {e}")
    else:
        print("  (none — all channels match target structure)")

    # Step 4: Create invite link
    if not DRY_RUN:
        print("\n--- CREATING INVITE LINK ---")
        # Find #welcome or #general for the invite
        welcome_ch = discord.utils.get(guild.text_channels, name="welcome")
        general_ch = discord.utils.get(guild.text_channels, name="general")
        invite_ch = welcome_ch or general_ch or guild.text_channels[0]
        invite = await invite_ch.create_invite(max_age=0, max_uses=0, reason="Permanent community invite")
        print(f"🔗 Invite link: {invite.url}")

    print("\n✅ Done!")

    # Print final state
    if not DRY_RUN:
        # Refresh guild
        guild = client.get_guild(GUILD_ID)
        print(f"\nFinal channel count: {len(guild.text_channels)}")
        for cat in guild.categories:
            print(f"\n{cat.name}:")
            for ch in cat.text_channels:
                print(f"  #{ch.name} — {ch.topic or '(no topic)'}")

    await client.close()


client.run(BOT_TOKEN)
