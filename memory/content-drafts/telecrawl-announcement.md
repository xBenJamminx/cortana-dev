# Telecrawl Announcement Post

**Status:** Approved
**Type:** Blog/Long-form post
**Account:** @BuildsByBen / Blog
**Pillar:** AI automation
**Image:** telecrawl-stats.png (same directory)
**Date approved:** 2026-03-10

---

Does your OpenClaw bot on Telegram forget everything between sessions?

Not because it's broken. Telegram's bot system literally can't read message history. Bots only see messages the moment they arrive. Session ends, memory gone.

Peter Steinberger built [discrawl](https://github.com/steipete/discrawl) to solve this on Discord. Telegram had nothing like it. So I built telecrawl.

One command to set up. It finds every group and channel you're in, shows you a list, you pick which ones to track. That's it.

From there, your agent just knows things:

- "What did we talk about regarding the launch last week?" It pulls every relevant message.
- "Find what Ben said about pricing in the last 7 days." Filtered by person, timeframe, topic.
- "What was the decision we made on Tuesday?" It traces the full conversation thread.

No commands to memorize. You talk to your agent the way you already do. It handles the rest.

Full JSON output under the hood, so developers can pipe it into any workflow. But most people will never touch that. They'll just notice their agent suddenly remembers everything.

I've been running this in production for weeks. Over 3,000 messages indexed, searchable in milliseconds, zero maintenance after setup.

Open source, MIT licensed: github.com/xBenJamminx/telecrawl

Your bot should remember what you told it. Now it can.
