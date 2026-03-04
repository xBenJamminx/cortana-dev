#!/usr/bin/env python3
"""
Populate EverydayAI Discord with welcome message + all deliverables.
Posts intro summaries since full content exceeds Discord's 2000 char limit.
"""

import discord
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.openclaw/.env"))

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

DELAY = 1.5  # seconds between posts to avoid rate limits


async def post(channel, content):
    """Post message, splitting if over 2000 chars."""
    if len(content) <= 2000:
        await channel.send(content)
    else:
        # Split on double newlines
        parts = []
        current = ""
        for line in content.split("\n"):
            if len(current) + len(line) + 1 > 1900:
                parts.append(current)
                current = line
            else:
                current += "\n" + line if current else line
        if current:
            parts.append(current)
        for part in parts:
            await channel.send(part)
            await asyncio.sleep(DELAY)
    await asyncio.sleep(DELAY)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)

    # Get channels
    def get_ch(name):
        return discord.utils.get(guild.text_channels, name=name)

    welcome_ch = get_ch("welcome")
    announcements_ch = get_ch("announcements")
    prompts_ch = get_ch("prompts")
    guides_ch = get_ch("guides")
    templates_ch = get_ch("templates")
    tools_ch = get_ch("tools")

    # =====================
    # 1. WELCOME MESSAGE
    # =====================
    print("Posting welcome message...")
    await post(welcome_ch, """**Welcome to EverydayAI** 👋

This is a free community for people who use AI in their daily lives — for work, side projects, family stuff, and everything in between.

**Who runs this?**
I'm Ben. I work full-time at a tech startup, run a consulting practice (Parker & Taylor), and build AI tools on the side. I'm a dad of two on Long Island who uses AI for literally everything — from client proposals to meal planning.

**What you'll find here:**
📝 **#prompts** — Engineered prompt packs you can copy and use immediately
📚 **#guides** — Step-by-step tutorials on real things I've built and how
📦 **#templates** — Grab-and-go frameworks for Airtable, Notion, proposals, etc.
🛠️ **#tools** — Tool recommendations, reviews, and deals
💬 **#general** — The main hangout. Ask questions, share ideas, talk shop.
🙋 **#help** — Stuck on something? Ask here.
🏆 **#wins** — Share what you shipped, automated, or figured out.

**The vibe:**
This isn't a course. It's not an agency community. It's a room full of people who use AI every day and want to get better at it. Share freely, ask anything, help each other out.

**Start here:** Drop an intro in **#introductions** — who you are, what you're into, and what you want to get out of AI.""")

    # =====================
    # 2. ANNOUNCEMENT
    # =====================
    print("Posting announcement...")
    await post(announcements_ch, """**🎉 Resources are LIVE**

Just dropped a bunch of free resources into the channels:

**#prompts** — 4 prompt packs (48 engineered prompts total):
• Business Operations (proposals, reports, emails, SOPs)
• Content Creation (tweets, threads, blogs, newsletters, video scripts)
• Side Projects & Automation (validation, MVPs, pricing, launches)
• Everyday Life (meal planning, budgets, travel, fitness, routines)

**#guides** — 4 in-depth guides:
• The AI Stack Guide — what tools to actually use for what
• How to Sell AI Services to Clients
• How to Evaluate a Market of Competitors in 2 Hours
• The Prompt Engineering Guide — 7 techniques for 10x better output

**#templates** — 2 ready-to-use templates:
• Competitor Analysis Template
• AI Services Client Proposal Template

Everything is free. Grab what you need. More coming soon.""")

    # =====================
    # 3. PROMPTS CHANNEL
    # =====================
    print("Posting to #prompts...")

    await post(prompts_ch, """**📝 Business Operations Prompt Pack**
*12 engineered prompts for business owners*

These handle the work that eats your day — proposals, emails, reports, documentation — using expert persona priming, chain-of-thought reasoning, and built-in quality checks.

**What's inside:**
1. Client Proposal That Wins the Deal
2. Meeting Notes to Action-Driven Recap
3. Strategic Competitive Analysis
4. Strategic Email Response
5. Scope of Work That Prevents Scope Creep
6. Overdue Invoice Follow-Up Sequence
7. Status Report That Stakeholders Actually Read
8. Job Posting That Attracts the Right People
9. Process Documentation from Brain Dump
10. Customer FAQ That Handles Objections
11. Sales Call Prep Intelligence Brief
12. Quarterly Business Review with Strategic Insights

Every prompt is copy-paste ready. Fill in the [BRACKETS] and go.

**Want the full pack?** Just ask in #general and I'll share the complete file.""")

    await post(prompts_ch, """**📝 Content Creation Prompt Pack**
*12 engineered prompts for creators, founders, and side hustlers*

Not "write me a tweet" prompts. These use chain-of-thought reasoning, few-shot examples, self-evaluation loops, and persona expertise.

**What's inside:**
1. Tweet/X Post from a Lesson or Insight
2. Twitter/X Thread from a Long Piece
3. Blog Post Draft from a Rough Topic
4. Weekly Newsletter Draft from Notes
5. YouTube Video Script from a Concept
6. LinkedIn Post from a Build Log
7. Content Repurposing Engine (Long-form → Multiple Short-form)
8. Content Calendar with Strategic Rationale
9. SEO-Optimized Content Briefing
10. Email Subject Line Lab
11. Hook/Opening Line Lab
12. "Lessons Learned" Post with Narrative Structure

Each prompt forces the model to think before writing, then critique its own output.

**Want the full pack?** Ask in #general.""")

    await post(prompts_ch, """**📝 Side Projects & Automation Prompt Pack**
*12 engineered prompts for builders and side hustlers*

For people who have an idea and want to move on it. Validate, scope, build, launch, and automate.

**What's inside:**
1. Side Project Idea Validator
2. Landing Page Copy That Converts
3. MVP Feature Scoping and Build Plan
4. Product Launch Description Writer
5. Early User Email Sequence
6. Workflow Automation Designer
7. Pricing Strategy Analyzer
8. Customer Feedback System
9. Competitive Positioning Framework
10. Social Proof Collection System
11. Weekly Accountability Check-In
12. Pivot or Kill Decision Framework

Every prompt includes domain-expert personas, structured thinking frameworks, and built-in reality checks.

**Want the full pack?** Ask in #general.""")

    await post(prompts_ch, """**📝 Everyday Life & Organization Prompt Pack**
*12 engineered prompts for the stuff that eats your time*

Meal planning, budgets, travel, fitness, routines — all the things you know you should organize but never sit down to figure out.

**What's inside:**
1. Weekly Meal Plan with Grocery List
2. Budget Analysis and Spending Optimizer
3. Travel Itinerary Builder
4. Home Maintenance Schedule
5. Personalized Gift Idea Generator
6. Negotiation Prep Playbook
7. Custom Fitness and Health Routine
8. Structured Learning Plan for a New Skill
9. Event Planning Checklist and Timeline
10. Decluttering and Organization System
11. Insurance and Service Comparison Analysis
12. Morning and Evening Routine Optimizer

Each prompt works around YOUR actual constraints — budget, time, energy, preferences.

**Want the full pack?** Ask in #general.""")

    # =====================
    # 4. GUIDES CHANNEL
    # =====================
    print("Posting to #guides...")

    await post(guides_ch, """**📚 The AI Stack Guide: What Tools to Use for What**

There are hundreds of AI tools fighting for your attention. Most are wrappers on the same three models. You don't need hundreds — you need the right ten.

**What's covered:**
• **Writing Content** — Why Claude wins (and when ChatGPT is fine)
• **Building Apps & Code** — Claude Code, Cursor, and what actually ships
• **Research & Deep Dives** — Perplexity and when to use it
• **Automation & Workflows** — n8n and the automation stack
• **Voice & Audio** — ElevenLabs and the voice AI landscape
• **Image Generation** — Midjourney and alternatives
• **The Daily Stack** — What I actually open every day
• **Free vs Paid** — Where to spend and where to save
• **Priority Learning Stack** — Week-by-week what to learn first

Not a list of every tool that exists. A practical breakdown of what I actually use and whether it makes me money.

**Want the full guide?** Ask in #general.""")

    await post(guides_ch, """**📚 How to Sell AI Services to Clients**

You know how to use AI. You've built workflows, written prompts that work. At some point it hits you: people would pay for this.

**What's covered:**
• **6 Services You Can Sell** — Content systems, AI audits, workflow automation, research, chatbots, training
• **Finding Clients** — Where they hang out, how to spot opportunities, what to say
• **The Discovery Call Framework** — Diagnosis approach that positions you as an advisor
• **Delivering the Work** — Tools, documentation, setting expectations
• **Pricing Models** — Hourly, project-based, and retainer structures
• **Building a Portfolio from Scratch** — Even with zero clients

Everything comes from actually doing this — selling AI services, delivering the work, dealing with scope creep, figuring out pricing the hard way.

**Want the full guide?** Ask in #general.""")

    await post(guides_ch, """**📚 How to Evaluate an Entire Market of Competitors in 2 Hours**

Most people do competitor research the hard way — 30 tabs, vague anxiety, no conclusions. This is the exact framework I use.

**The 6-step process:**
1. **Define the Market** — Scope it properly so you're not comparing apples to enterprise SaaS
2. **Find All the Competitors** — AI-powered discovery that catches what Google misses
3. **Build a Comparison Matrix** — Structured, sortable, useful
4. **Analyze Pricing, Positioning & Features** — What they charge, who they serve, where they're weak
5. **Identify Gaps and Opportunities** — The whitespace nobody's filling
6. **Generate a Strategic Summary** — Actionable positioning recommendations

Includes prompts for every step. Used this to evaluate the entire bookmark manager market before building BookmarkIQ.

**Want the full guide?** Ask in #general.""")

    await post(guides_ch, """**📚 The Prompt Engineering Guide**
*How to Get 10x Better Output from Any AI Model*

Most people use AI like a search engine with a text box. "Write me a tweet" → garbage output → "AI isn't that good."

It is that good. You're just talking to it wrong.

**The 7 core techniques:**
1. **Role/Persona Priming** — Give the AI an expert identity
2. **Chain-of-Thought Reasoning** — Make it think step-by-step
3. **Few-Shot Examples** — Show it what "good" looks like
4. **Structured Formatting** — Use delimiters and sections
5. **Self-Evaluation Loops** — Make it critique its own output
6. **Output Primers** — Control the format and structure
7. **Clarifying Questions** — Build adaptive prompts

Plus: The complete prompt engineering framework, quick reference guide, common mistakes, and the 10 rules of prompt engineering.

**Want the full guide?** Ask in #general.""")

    # =====================
    # 5. TEMPLATES CHANNEL
    # =====================
    print("Posting to #templates...")

    await post(templates_ch, """**📦 Competitor Analysis Template**

Copy this into Notion, Airtable, or a spreadsheet. Fill in each section using the AI prompts provided. The whole thing takes about 2 hours.

**Sections included:**
• Market Overview (definition, size, growth)
• Competitor List (structured for 8+ competitors)
• Feature Comparison Matrix
• Pricing Analysis
• Positioning Map
• Strengths & Weaknesses (per competitor)
• Gap Analysis
• Strategic Summary
• Action Items

Each section includes the exact AI prompt to fill it in.

**Want the full template?** Ask in #general.""")

    await post(templates_ch, """**📦 AI Services Client Proposal Template**

The template I use for every new client opportunity. Fill in the brackets, adjust the scope, send as a PDF. This has closed real deals.

**Sections included:**
• The Problem (using the client's own words)
• The Solution (simple language, not tech jargon)
• What You Get (deliverables + what's NOT included)
• Timeline (phased with milestones)
• Investment (pricing options + payment schedule)
• Why Me (3-4 real differentiators, not adjectives)
• How to Get Started (clear next steps)

Plus an AI prompt to customize the whole thing in minutes after a discovery call.

**Want the full template?** Ask in #general.""")

    # =====================
    # 6. TOOLS CHANNEL
    # =====================
    print("Posting to #tools...")

    await post(tools_ch, """**🛠️ Ben's Daily AI Stack — What I Actually Use**

Quick rundown of the tools I open every day and why:

**Writing & Content:** Claude (Pro plan) — best writing quality, period
**Code & Building:** Claude Code — ship things fast
**Research:** Perplexity — replaces most Google searches
**Automation:** n8n (self-hosted) — connects everything, free
**Voice:** ElevenLabs — when you need realistic audio
**Images:** Midjourney — still the best for quality
**Email:** Gmail + AI triage — inbox management
**Notes:** Notion — second brain
**Content Pipeline:** Airtable — scheduling and tracking
**Communication:** Telegram — where my AI operator (Cortana) reports to me

More detailed breakdowns of each tool coming soon. Drop your tool questions in here and I'll do writeups on the ones people want to know about.""")

    print("\n✅ ALL CONTENT POSTED!")
    print(f"  Welcome: 1 message")
    print(f"  Announcements: 1 message")
    print(f"  Prompts: 4 messages (4 prompt packs)")
    print(f"  Guides: 4 messages (4 guides)")
    print(f"  Templates: 2 messages (2 templates)")
    print(f"  Tools: 1 message (daily stack)")
    print(f"  TOTAL: 13 messages")

    await client.close()


client.run(BOT_TOKEN)
