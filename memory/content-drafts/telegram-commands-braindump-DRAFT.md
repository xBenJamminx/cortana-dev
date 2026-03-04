# Brain Dump: I Gave My AI Agent 50+ Telegram Commands

Status: DRAFT
Format: Thread / Brain Dump
Schedule: TBD
Tags: brain-dump, AI tools, openclaw, telegram, automation
Pillar: AI workflow, building in public

---

Most people use Telegram for group chats.

I use it to control my AI agent.

Her name is Cortana. She runs on OpenClaw. And she lives in my Telegram.

I type /reply_guy and she scans Twitter across 5 content pillars, scores posts by engagement velocity, and sends me the top reply targets. From my phone. While I'm making coffee.

I type /search "vibe coding" and get instant results with engagement data and links. No opening Twitter. No doomscrolling.

I type /bird tweet "text" and she posts to X for me.

I type /summarize and drop a URL. She reads the whole thing and sends me the summary in 10 seconds.

I type /vapi_call and she literally picks up the phone and calls someone.

Here's how it works:

OpenClaw is an AI operator framework. You give it a personality, tools, and a Telegram bot token. It connects to Telegram and starts listening.

Every "skill" you create becomes a slash command automatically. Write a SKILL.md file, drop a script next to it, and it just works.

The skill file tells the AI what the command does and how to run it. The AI reads the instructions, executes the script, and sends results back to your chat.

That's it. No webhook servers. No custom bot code. No infrastructure.

The real power: it's not a dumb bot that runs pre-programmed responses. It's Claude. It reads your command, understands context, runs real tools, and responds intelligently.

/reply_guy hot_takes 6h → she knows to filter for hot take posts from the last 6 hours
/reply_guy --min-followers 50000 → she adjusts the threshold

You're not memorizing syntax. You're talking to an AI that has access to your tools.

Why Telegram specifically?
- Slash commands autocomplete (type / and see all your options)
- Works on phone AND desktop
- Push notifications when tasks complete
- You can share the bot with your team
- It's free

The unlock nobody talks about: your AI agent is always on.

You don't open a laptop. You don't start a terminal session. You don't SSH into anything.

You pull out your phone, type a command, and your agent does the work.

I built a Reply Guy tool today. Took 30 minutes. It searches Twitter, scores engagement velocity, filters by follower count, and surfaces the best posts to reply to. All from one slash command.

Tomorrow I might build a /content_ideas command that generates post ideas based on what's trending in my niche.

The day after, maybe a /analytics command that pulls my Twitter stats.

Each one is just a script + a SKILL.md file. The AI figures out the rest.

Building in public means your tools should work where YOU work. And I work from my phone half the time.

What commands would you build?

---

## CONTENT IDEA: From DMs to Command Center — Telegram Topics + @Mention Fix

**Format:** Thread / Carousel / Short video walkthrough / LinkedIn post
**Angle:** Single monolithic DM = hard to track. Topics = modular, organized. Plus a separate @mention config fix.
**Hook:** "I stopped DMing my AI agent. Here's what I did instead."

### The Problem
- A single Telegram DM with your AI agent is monolithic — everything in one thread
- Research, tasks, content drafts, status updates all bleed together
- Impossible to find anything or keep track of what you're working on
- It's like having every conversation you've ever had in one endless scroll

### The Fix
- Telegram has Topics — forum-style threads inside a group
- Created a Telegram group with just me and my AI agent, with Topics enabled
- Each topic is its own isolated thread:

**The Setup:**
- General — Quick back-and-forth, like Slack #general
- Content Pipeline — Drafts, ideas, approvals all in one thread
- Research — Deep dives land here, not buried in chat
- Alerts & Monitoring — Server health, cron failures, API issues
- Ideas Parking Lot — New ideas go here to wait their turn (anti-shiny-object channel)

### How It Works
- I post in a specific topic, she responds in that same topic
- Conversations stay modular — research doesn't pollute my task list
- I can scroll back through any topic to find what I need
- Adding a new topic is like adding a new Slack channel — takes 2 seconds

### The @Mention Fix (Separate Thing)
- By default, bots in Telegram groups only see messages where they're @mentioned
- One config change (`requireMention: false`) removes that requirement
- Just a quality-of-life tweak so I don't have to type @CortanaBot every message
- Unrelated to Topics — this is about the bot seeing all messages in the group

### The Insight
A single DM is monolithic. Topics make it modular.

That's it. Same agent, same capabilities — but now conversations are organized instead of one giant scroll.

### Platform-Native Drafts

**LinkedIn Post:**
"I stopped DMing my AI agent.

Not because it stopped working — because a single DM thread is a mess.

Everything in one monolithic scroll. Research, tasks, content drafts, server alerts. Try finding something from 3 days ago. Good luck.

So I did something simple: Telegram group with Topics.

Now instead of one endless thread, I have:
→ #research — deep dives stay here
→ #content-pipeline — drafts and approvals
→ #alerts — server health and errors
→ #parking-lot — shiny new ideas that can wait

Same agent. But modular instead of monolithic.

I post in a topic, she responds in that topic. Context stays clean. I can actually find things.

It took 5 minutes to set up. Free. And it completely changed how I work with my AI.

What's your setup look like?"

**TikTok/Short-Form Hook Ideas:**
- "Stop DMing your AI agent. Do this instead."
- "I turned Telegram into an AI command center in 5 minutes"
- "One DM thread with your AI? You're doing it wrong."
- "Monolithic vs modular — how I organize my AI agent"

**Substack Angle:**
"What I Shipped" section — monolithic DM → modular Topics. Screenshots of the topic list. @mention fix as a separate bonus tip.

**YouTube Angle:**
Screen recording walking through the Telegram group, showing each topic with real messages, explaining why modular > monolithic.

### Extra Notes
- Core message: monolithic DM = hard to track, Topics = modular and organized
- Screenshots of the actual topic list make this very tangible
- Cost angle: Telegram is FREE
- The parking lot concept addresses "shiny object syndrome"
- @mention fix is a separate bonus tip, not the main story

**Target audience:** AI builders, productivity nerds, solo founders managing multiple projects
