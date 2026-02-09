# X Post: Newsletter Monitor
**Status:** DRAFT
**Content lane:** DIY/Template (Wednesday)
**Tags:** @OpenClaw @CortanaOps

---

Your @OpenClaw bot can read your email.

Mine reads 19 newsletters every morning, pulls out the stories that matter, throws away the ads and fluff, ranks what's left by relevance, and drops a briefing in my Telegram before I wake up.

No RSS. No Feedly. It reads the actual emails from my inbox using Composio's Gmail integration, runs every story through a two-pass LLM filter, and saves the best ones to a database.

Here's what the filter does:

Pass 1: Extract and rank. It pulls headlines, descriptions, and links from each newsletter. Merges stories that show up in multiple sources (multi-source = higher signal). Scores each one 1-100. Anything under 50 gets cut.

Pass 2: Mine nuggets. A second LLM pass pulls out tutorials, new tools, funding signals, and hot takes that the headline scan missed. Grouped by category.

The whole thing feeds into a morning briefing with my top tweets from yesterday, trending topics, and the best content ideas -- all before coffee.

Steal this prompt:

"Set up a newsletter monitor. Connect Gmail through Composio MCP. Build a script that fetches my last 2 days of emails, filters to newsletters only, extracts stories with headlines and links, and runs them through an LLM to rank by relevance for [describe your audience]. Score 1-100 and cut anything below 50. Save results to SQLite. Add a second pass that mines for tutorials, tools, and insights. Run it on a cron and send me the results every morning."

What newsletters are you drowning in?
