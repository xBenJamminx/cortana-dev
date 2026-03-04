# The AI Stack Guide: What Tools to Use for What

**By Ben | BuildsByBen**

---

There are hundreds of AI tools fighting for your attention and your credit card. Most of them are wrappers on the same three models with a pretty UI bolted on top. You don't need hundreds. You need the right ten or twelve, and you need to know which one to reach for when.

This is the guide I wish someone handed me a year ago. Not a list of every tool that exists -- a practical breakdown of what I actually use, organized by what you're trying to do. I'm not ranking these by hype or features. I'm ranking them by how often I open them and whether they make me money.

Let's get into it.

---

## Writing Content

**Best tool: Claude**

This isn't close. For writing -- tweets, LinkedIn posts, newsletters, client proposals, emails, landing page copy -- Claude produces the best output of any model I've used. The writing is cleaner, more natural, and requires less editing than anything else on the market.

The key is how you prompt it. Give Claude your voice, your audience, and clear constraints (word count, tone, format) and the first draft comes back 80-90% usable. With ChatGPT, I was spending almost as much time editing the output as I would have spent writing from scratch. With Claude, I'm tweaking a few sentences and hitting publish.

**Quick example:** I paste a raw idea -- "saw a competitor charge $5K for something I could automate in an afternoon" -- into Claude with a prompt that says "turn this into a Twitter post, under 280 characters, casual and direct, no hashtags." I get three variations back in ten seconds. Pick one, adjust a word or two, post it. Done.

**Runner up:** ChatGPT is fine for quick, throwaway writing. If I need a one-line email reply or something I don't care about polishing, ChatGPT works. But for anything client-facing or public, it's Claude every time.

**What about Gemini?** Gemini's writing quality is noticeably behind both Claude and ChatGPT. It's not where you go for content creation. It has other strengths (we'll get there).

---

## Building Apps and Writing Code

**Best tool: Claude Code (CLI)**

If you want to go from idea to working application, Claude Code is the move. It's a command-line tool that lets you describe what you want in plain English and it writes, edits, and debugs the code for you. I've shipped multiple products this way -- full web apps with databases, auth, APIs, the works -- without writing most of the code by hand.

The difference between Claude Code and other coding assistants is scope. Cursor and Copilot are great at helping you write code line by line. Claude Code thinks in terms of entire features and systems. You say "add user authentication with Google OAuth" and it builds the whole thing -- frontend, backend, database schema, error handling.

**Quick example:** "Build me a dashboard that pulls my Twitter analytics from the API, stores them in Supabase, and displays a chart of follower growth over time." Claude Code sets up the project, writes the components, connects the database, and handles the API calls. You review, test, and deploy. What used to be a weekend project becomes an afternoon.

**Best tool for day-to-day coding: Cursor**

If you already know how to code and you're working inside an existing codebase, Cursor is the best editor available. It's a VS Code fork with AI baked into every interaction -- tab completion that reads your mind, inline chat that understands your whole project, and the ability to reference files and docs naturally.

I use both: Claude Code for building new features and major architectural work, Cursor for editing, debugging, and smaller tasks inside existing projects.

**Runner up: Windsurf** is a solid alternative to Cursor with a similar concept but a different approach to how AI integrates with your workflow. Worth trying if Cursor doesn't click for you. GitHub Copilot is cheaper ($10/mo vs $20/mo) but noticeably less capable.

---

## Research and Deep Dives

**Best tool: Perplexity**

For research, Perplexity is the tool I open first. It searches the web, reads the sources, and gives you a synthesized answer with citations. It's what Google should have become.

The difference between Perplexity and just asking ChatGPT or Claude is grounding. When you need current, factual information -- market data, competitor analysis, technical documentation, "what's the best way to do X in 2026" -- you need something that actually checks sources instead of generating plausible-sounding answers from training data.

**Quick example:** "What automation platforms have the best free tiers for solo founders in 2026?" Perplexity pulls from recent reviews, pricing pages, and community discussions, then gives you a ranked answer with links to verify everything. Try that with a standard LLM and you'll get a confident answer that might be six months out of date.

**Runner up:** Gemini is strong for research that involves very long documents. Its context window handles 1M+ tokens, which means you can feed it an entire 200-page PDF or a full codebase and ask questions about it. No other model touches that. If your research involves processing massive amounts of text, Gemini is the play. For web-grounded research, though, Perplexity wins.

**ChatGPT's browsing feature** is decent for quick checks but the research quality is inconsistent. Sometimes it nails it, sometimes it hallucinates a source that doesn't exist. Perplexity is more reliable.

---

## Automation and Workflows

**Best tool: n8n**

If you're paying for Zapier right now, I need you to hear this: you are probably overpaying by a lot. n8n does everything Zapier does, plus you can self-host it for free, run custom code inside your workflows, and build automations that would cost $300-500/mo on Zapier for literally $0.

n8n is a visual workflow builder. You drag nodes onto a canvas, connect them, and data flows from one step to the next. New email comes in, AI processes it, summary goes to Slack, follow-up task gets created in Notion. That kind of thing. Except the ceiling is way higher than Zapier because you're not limited to pre-built integrations -- you can hit any API, run any code, and chain as many steps as you want.

**Quick example:** I have an n8n workflow that monitors competitor content, runs it through Claude's API for analysis, writes a summary to my database, and sends me a Telegram notification with the highlights. Runs automatically every day. Cost: $0 for n8n (self-hosted) plus a few cents in API calls.

**Runner up: Make.com** if you want something hosted and slightly easier to learn. Make's visual builder is genuinely great, and for client work I often use Make because it's easier to hand off -- clients don't need to manage a server. The pricing is reasonable ($9/mo gets you pretty far).

**What about Zapier?** Zapier is the simplest option but the most expensive by far. If you're doing more than five automations, the per-task pricing adds up fast. I'd only recommend it if you need one or two simple zaps and don't want to learn anything new.

**What about Composio?** Composio sits in a different lane. It's not a workflow builder -- it's a platform that gives AI agents access to external tools and APIs. Think of it as the bridge between your AI and the rest of your software stack. If you're building AI agents that need to take actions (post to social media, create GitHub issues, send emails), Composio handles the authentication and API connections so you don't have to build that plumbing yourself. It's a power-user tool, not something you need on day one.

---

## Voice and Audio

**Best tool: ElevenLabs**

The voice quality is unreal. Two years ago, AI voices sounded like a GPS navigation system trying to read poetry. Now ElevenLabs produces voices that are genuinely hard to distinguish from real humans. The API is clean, fast, and starts at $5/mo.

**What you can do with it:**
- Turn blog posts and newsletters into audio versions (accessibility + new distribution channel)
- Create voiceovers for video content without recording yourself
- Clone your own voice with 30 seconds of sample audio (yes, really)
- Build voice-enabled applications and bots

**Quick example:** I have a system where my AI operator, Cortana, can send me voice messages through Telegram using ElevenLabs. Status updates, alerts, summaries -- delivered as natural-sounding audio instead of walls of text. It took an afternoon to set up and it's one of those things that feels like the future every time it triggers.

**Runner up:** OpenAI's TTS is cheaper and decent for basic text-to-speech, but the voice quality is noticeably lower. If you just need a quick audio version of something and don't care about it sounding premium, OpenAI TTS works fine. For anything client-facing or public, ElevenLabs.

---

## Image Generation

**Best tool: Midjourney**

For consistent, high-quality image generation, Midjourney is still the leader. The aesthetic quality of its output is a step above everything else. Thumbnails, social media visuals, blog headers, concept art -- it produces images that look like a professional designer made them.

**Quick example:** "/imagine a clean, minimal hero image for a SaaS landing page about workflow automation, dark background, subtle blue gradient, abstract connected nodes" -- and you get four options in under a minute that you'd be happy putting on a live website.

**Runner up: DALL-E** (inside ChatGPT) is the most convenient option because you don't need a separate tool. The quality is good enough for social media posts and quick visuals. If you're already in ChatGPT and need an image, don't bother switching tools. For anything where the visual quality really matters -- landing pages, product shots, portfolio pieces -- Midjourney is worth the extra step.

**Flux** is the open-source contender that's improving fast. If you're technical and want more control (or want to avoid subscription fees), Flux through ComfyUI or various hosted providers is worth exploring. Google's Imagen is strong for photorealistic images specifically.

---

## My Daily Stack

Here's what a typical workday actually looks like in terms of tools:

**Morning:**
- **Claude** for planning the day, drafting content, answering client messages
- **Perplexity** for any research I need for content or client work
- **n8n** workflows have already run overnight -- I check the results (competitor monitoring, content aggregation, trend reports)

**Building/working:**
- **Claude Code** if I'm building something new or adding major features
- **Cursor** if I'm editing existing code, debugging, or making smaller changes
- **Gemini** if I need to process a long document or want a second opinion on research

**Content creation:**
- **Claude** for writing drafts from raw ideas
- **Midjourney** or **DALL-E** (via ChatGPT) for visuals
- **ElevenLabs** if anything needs audio

**Automation/operations:**
- **n8n** for building and monitoring workflows
- **Make.com** for client-facing automations
- **Composio** when I need AI agents to interact with external services

**Evening:**
- Review what the automations captured during the day
- Queue up content for the next day
- Let n8n handle the overnight monitoring

The point isn't that you need all of these. The point is that each tool has a specific job and I'm not forcing one tool to do everything poorly.

---

## Free vs Paid: What's Actually Worth the Money

### What you can do for free (and should start here)

- **Claude free tier:** Good for 20-30 quality conversations per day. Enough to learn whether AI writing works for you before paying.
- **ChatGPT free tier:** Generous limits. Good for getting started with AI in general.
- **Gemini free tier:** Includes the massive context window. Google AI Studio gives you free API access for testing.
- **Perplexity free tier:** 5 Pro searches per day. Enough for casual research.
- **n8n self-hosted:** Completely free if you have a server (a $5/mo DigitalOcean droplet works). Unlimited workflows, unlimited executions.
- **Cursor free tier:** Limited AI completions per month but enough to see if the workflow clicks for you.
- **DALL-E via ChatGPT free:** Basic image generation included.

**Total cost to get started: $0-5/mo.** That's not a gimmick. You can genuinely run a meaningful AI-assisted workflow for free.

### What's worth paying for (in order of priority)

1. **Claude Pro ($20/mo):** The single best investment on this list. You'll hit the free limits within a week if you're using it seriously. Pro removes the friction.

2. **Cursor Pro ($20/mo):** If you write code at all -- even if you're just learning -- the productivity jump is massive. This pays for itself in the first week.

3. **Perplexity Pro ($20/mo):** Unlimited Pro searches, access to multiple models, file uploads for analysis. Worth it if research is part of your daily work.

4. **Midjourney ($10/mo):** If you need visuals regularly. If you only need an image once a week, DALL-E through ChatGPT's free tier is fine.

5. **ElevenLabs ($5/mo):** Cheap enough that if you have any use case for AI voice, just get it.

6. **ChatGPT Plus ($20/mo):** Honestly, this one's optional if you're already paying for Claude. I keep it for voice mode, DALL-E, and as a second opinion. If budget is tight, skip it.

### What you should NOT pay for

- **Zapier** when n8n exists for free (self-hosted)
- **Any "AI writing tool"** that's just a ChatGPT wrapper with a nicer UI (Jasper, Copy.ai, etc.). Just use Claude directly.
- **Multiple coding assistants** at the same time. Pick Cursor or Windsurf, not both.
- **AI tools that require annual commitments** before you've used them for at least a month on a monthly plan.

---

## What to Learn First: The Priority Stack

If you're starting from zero, here's the order I'd learn these tools. Each one builds on the previous.

### Week 1-2: Get comfortable with one LLM

Pick Claude or ChatGPT. Just one. Use it for everything -- writing, research, brainstorming, analyzing documents, drafting emails. The goal isn't to master prompting. The goal is to build the habit of reaching for AI before doing things manually.

**The skill you're building:** Knowing what to delegate to AI and how to ask for what you want.

### Week 3-4: Add research

Start using Perplexity alongside your main LLM. Use your LLM for creation (writing, drafting, brainstorming) and Perplexity for information gathering (research, fact-checking, competitive analysis). Having two tools with distinct purposes teaches you to pick the right tool for the job instead of forcing one tool to do everything.

**The skill you're building:** Choosing the right AI for the right task.

### Month 2: Add coding or automation (pick one based on your path)

**If you want to build things:** Get Cursor. Start with small projects -- a personal website, a simple tool, a Chrome extension. Use AI to write code you don't fully understand yet. Reading AI-generated code is one of the fastest ways to learn programming.

**If you want to automate things:** Set up n8n or Make.com. Start with one simple workflow -- maybe "new email from X triggers a Slack notification" or "new Airtable entry triggers an AI summary." The goal is to understand how tools connect to each other.

**The skill you're building:** Turning ideas into real, working things with AI as your co-builder.

### Month 3: Stack the tools

Now you start combining. Use Claude to write content, n8n to automate its distribution, Perplexity to research topics, and Cursor or Claude Code to build custom tools when off-the-shelf products don't do what you need. Add Midjourney or ElevenLabs based on whether your work is more visual or audio.

**The skill you're building:** Systems thinking. Knowing how to chain AI tools together to create something bigger than any single tool can offer.

### Month 4+: Specialize and sell

By now you know which tools you actually use daily and which ones gather dust. Double down on 3-4 tools. Get genuinely good at them. That's where the money is. Nobody pays for "I know a little bit about 15 AI tools." People pay for "I can build you an automated content pipeline using Claude, n8n, and Airtable in a week."

**The skill you're building:** Expertise worth paying for.

---

## The Bottom Line

You don't need every tool on this list. You need a writing/thinking AI (Claude), a way to find information (Perplexity), and a way to automate the boring stuff (n8n or Make). Everything else is a multiplier on top of those three.

Start free. Upgrade when you hit the limits. Learn one tool well before adding the next. And remember -- the tool is never the bottleneck. Knowing what to build and who to build it for is the hard part. The tools just make the building faster.

---

*Updated February 2026. Tools and pricing change fast -- if something here looks wrong, flag it in the community and I'll update it.*
