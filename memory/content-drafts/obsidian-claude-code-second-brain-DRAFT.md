# Obsidian + Claude Code: The AI Second Brain Setup That Actually Works

**Status:** DRAFT
**Date:** March 24, 2026
**Format:** Thread (7 tweets) + Long-form article
**Tone:** Practical, honest, no hype

---

## THREAD VERSION (7 tweets)

**1/7**
I've been running Obsidian + Claude Code as my "AI second brain" for months now. Here's what actually works, what breaks, and why you probably already have 80% of this if you use markdown files.

No hype. Just the setup.

**2/7**
The setup is simple:
- Obsidian vault = folder of markdown files
- Claude Code runs in terminal pointed at that folder
- CLAUDE.md at the root = persistent memory (loads every session)
- Wikilinks between notes = graph connections Claude can traverse

That's it. No plugins required to start.

**3/7**
The killer workflow: phone brain dump.

Capture messy thoughts on mobile (Obsidian has iOS/Android apps). They land in an inbox folder. Claude Code processes them -- extracts tasks, files notes to the right folders, adds wikilinks to related notes, updates your daily log.

What took 30 min of manual sorting now takes 90 seconds of Claude running through your inbox.

**4/7**
Weekly reviews in 90 seconds:

Tell Claude "review my week." It reads your daily notes, extracts wins and blockers, checks which tasks moved, flags notes with no links (orphans), and generates a summary.

The graph view in Obsidian then shows you visually where your thinking clusters and where the gaps are.

**5/7**
What actually goes wrong (from real users):

- CLAUDE.md files over ~500 lines get partially ignored. Claude's system prompt says "this context may or may not be relevant." Too much noise = missed rules.
- Context window fills up fast. 15 min of work can exhaust it.
- Claude occasionally reads files it shouldn't despite .claudeignore entries.
- Rate limits on Pro tier hit mid-session. Frustrating.

**6/7**
The fix for long CLAUDE.md: keep it under 200 lines. Move specific rules to .claude/rules/ directory (modular files). For each line, ask: "Would removing this cause Claude to make a mistake?" If no, cut it.

Real GitHub issues (#7777, #15443, #668) confirm this is the #1 complaint. It's a known limitation, not a skill issue.

**7/7**
Honest take: if you already use markdown files in any folder structure, you have 80% of this.

Obsidian adds: visual graph, mobile sync, wikilinks, community plugins (including ones that embed Claude Code directly).

But the core -- Claude Code reading and editing local markdown -- works in VS Code, terminal, anywhere. Don't let anyone sell you on a complicated stack. Start with a folder and a terminal.

---

## LONG-FORM ARTICLE VERSION

### Obsidian + Claude Code as an AI Second Brain: The Practical Guide (2026)

Everyone's talking about AI second brains. Most of the advice is overengineered nonsense -- custom RAG pipelines, vector databases, elaborate plugin stacks. Here's what actually works for a knowledge worker who wants to think better, not build infrastructure.

---

### Why plain markdown + Claude Code beats every AI note-taking app

The premise is simple: your notes are markdown files in a folder. Claude Code is an AI that can read, edit, and create files in that folder. Point Claude Code at your Obsidian vault and you have an AI that understands your entire knowledge base.

Why this beats Notion AI, Mem, Reflect, and every other AI-native note app:

**You own your data.** Your notes are .md files on your filesystem. No vendor lock-in. If Claude Code disappears tomorrow, your notes are still there. If Notion AI disappears, you're exporting from a proprietary format.

**You can switch AI providers.** Today it's Claude. Tomorrow it might be GPT-5 or Gemini or a local model. Because your notes are just files, any AI tool that can read files works. You're not married to one provider's AI implementation.

**No sync tax.** Notion AI processes your data on their servers. Obsidian + Claude Code processes locally. Your private journal entries, business ideas, and client notes never leave your machine (unless you choose to share them).

**Full control over AI behavior.** CLAUDE.md lets you define exactly how Claude interacts with your vault -- naming conventions, folder structure, tagging rules, tone preferences. No AI note app gives you this level of customization.

---

### The specific setup

**What you need:**
- Obsidian (free) installed on desktop and mobile
- Claude Code (requires Anthropic subscription)
- A terminal -- either Obsidian's built-in terminal plugin, VS Code, or just a standalone terminal pointed at your vault

**Folder structure that works:**

```
vault/
  CLAUDE.md              # Persistent instructions for Claude
  .claude/rules/         # Modular rule files
  00-inbox/              # Raw captures from mobile
  01-daily/              # Daily notes
  02-projects/           # Active project folders
  03-areas/              # Ongoing life areas (health, finance, work)
  04-references/         # Saved articles, book notes, research
  05-archive/            # Completed/inactive material
  templates/             # Note templates
```

**CLAUDE.md -- the persistent memory file:**

This is the most important file. It loads into every Claude Code session automatically. Keep it focused:

```markdown
# CLAUDE.md

## Vault rules
- New notes go in 00-inbox/ unless I specify otherwise
- Use [[wikilinks]] to connect related notes
- Daily notes format: YYYY-MM-DD.md in 01-daily/
- Never delete notes without asking first
- When processing inbox, file to the correct numbered folder

## My conventions
- Tags: #task, #idea, #question, #meeting, #decision
- Project folders get their own CLAUDE.md with project-specific context
- Weekly review notes go in 01-daily/ with prefix "weekly-review-"

## What I'm working on
- [Update this section regularly]
```

Critical: keep CLAUDE.md under 200 lines. This is not a suggestion -- it's the difference between Claude following your rules and Claude ignoring half of them. Multiple GitHub issues (#7777, #15443, #6120) document that bloated CLAUDE.md files cause Claude to skip instructions. The system prompt includes language saying this context "may or may not be relevant," so if there's too much noise, Claude's attention scatters.

If you need more rules, use `.claude/rules/` directory. Each file there is a modular instruction set that loads contextually.

**Wikilinks for graph connections:**

This is where Obsidian earns its keep. When Claude processes your notes, it can add `[[wikilinks]]` to connect related concepts. Over time, your vault builds a graph of connections -- ideas linked to projects, meeting notes linked to decisions, questions linked to answers.

Obsidian's graph view then lets you see these connections visually. Clusters form naturally. Orphaned notes (no links) become obvious candidates for processing or archiving.

---

### The inbox workflow: phone brain dump to properly filed notes

This is the workflow that saves the most time.

**Step 1: Capture on mobile.**
Open Obsidian on your phone. Brain dump into the inbox folder. Don't worry about formatting, tagging, or filing. Just get the thought out. Examples:
- "Meeting with Sarah -- she wants the API done by March 15, concerned about auth"
- "Idea: weekly email digest from bookmarked tweets"
- "Need to call dentist, also renew car registration"

**Step 2: Claude processes the inbox.**
Back at your desk, open terminal in your vault:

```
claude "Process my inbox. For each note: extract tasks (tag with #task), identify which project or area it belongs to, file it to the correct folder, add wikilinks to any related existing notes, and update today's daily note with a summary of what was processed."
```

Claude reads each inbox note, understands the content, moves it to the right folder, adds wikilinks, and creates tasks. A messy brain dump about a meeting becomes a properly filed meeting note in `02-projects/api-project/` with links to the relevant people, decisions, and open tasks.

**Step 3: Review.**
Check Claude's work. It usually gets 85-90% right. The remaining 10-15% is edge cases -- notes that could belong in multiple places, ambiguous references, personal vs. professional overlap. Quick manual corrections take 30 seconds.

Total time: what used to be 20-30 minutes of manual sorting is now 90 seconds of Claude running + 30 seconds of review.

---

### Weekly reviews in 90 seconds

The weekly review is where the system compounds.

```
claude "Do my weekly review. Read all daily notes from this week. Summarize: what got done (completed tasks), what's still open (incomplete tasks), what decisions were made, what new ideas came up. Flag any notes from this week with no wikilinks -- they might be orphans that need connecting. Show me the top 3 things I should focus on next week based on patterns you see."
```

Claude scans 5-7 daily notes, cross-references with project folders, and produces a structured review. The "orphan check" catches notes that fell through the cracks -- a meeting note that never got linked to its project, a task that was captured but never assigned.

Obsidian's graph view after a weekly review shows you visually where your thinking concentrated. Dense clusters = active focus areas. Isolated nodes = ideas you captured but haven't connected yet.

The whole thing takes 90 seconds. A traditional weekly review (David Allen GTD style) takes 30-60 minutes.

---

### What actually goes wrong

I'm not going to pretend this is flawless. Here's what breaks in practice, based on real user reports and my own experience.

**1. Long CLAUDE.md files get ignored.**

This is the biggest issue. When your CLAUDE.md grows past ~500 lines (some report issues even at 200-300 lines), Claude starts ignoring rules. It's not malicious -- the system prompt literally tells Claude the context "may or may not be relevant to your tasks." With too much context, important rules get lost in the noise.

The fix: ruthlessly trim CLAUDE.md. For every line, ask: "Would removing this cause Claude to make a mistake I care about?" If no, remove it. Move specific, rarely-needed rules to `.claude/rules/` files.

**2. Context window exhaustion.**

Claude Code has a large but finite context window. 15 minutes of active work -- reading files, making edits, running commands -- can fill it up. When the context is full, performance degrades. Claude starts forgetting earlier instructions, repeating itself, or making errors.

The fix: work in focused sessions. Process inbox, then start a new session. Do weekly review in its own session. Don't try to do everything in one marathon conversation. Plan mode (Shift+Tab in Claude Code) lets you research without burning context.

**3. Privacy tradeoffs.**

Your notes go through Anthropic's servers when Claude Code processes them. For most people, this is fine -- Anthropic's data policy is reasonable. But if your vault contains client NDAs, medical records, legal documents, or truly sensitive material, think carefully about what you're exposing.

There have also been reports of Claude reading files despite `.claudeignore` entries (The Register, Jan 2026). If you have secrets or credentials in your vault, don't rely on .claudeignore alone -- move sensitive files outside the vault entirely.

**4. Rate limits hit mid-session.**

On the Pro tier, heavy usage can trigger rate limits. You're in the middle of processing a week's worth of notes and suddenly Claude stops responding. The Max tier ($200/mo) helps but doesn't eliminate this for power users.

**5. Sync conflicts.**

If you use Obsidian Sync or iCloud sync across devices, Claude Code editing files on desktop while you're capturing on mobile can create sync conflicts. The fix: don't run Claude Code while actively capturing on mobile. Process inbox when you're done capturing.

---

### The honest take

Here's what nobody writing "AI second brain" content will tell you:

**If you already use markdown files in any folder structure, you have 80% of this system.**

Obsidian adds three things on top of plain markdown folders:
1. Visual graph view (genuinely useful for seeing connections)
2. Mobile app for capture (important for the inbox workflow)
3. Community plugins (including ones that embed Claude Code as a sidebar)

But the core of the system -- Claude Code reading and editing local markdown files -- works in any terminal pointed at any folder. VS Code, iTerm, even a basic bash prompt. You don't need Obsidian specifically. You don't need plugins. You don't need a complicated setup.

The value is in the habits, not the tools:
- Capture thoughts immediately (any text app works)
- Process regularly (Claude Code just makes this faster)
- Connect ideas with links (wikilinks or just file references)
- Review weekly (Claude summarizes, but you could do it manually)

**Start simple.** A folder of markdown files and Claude Code in a terminal. Add Obsidian if you want the graph and mobile sync. Add plugins if you find specific gaps.

The people getting the most value from this setup aren't the ones with the most elaborate configuration. They're the ones who capture consistently and process regularly. The AI just makes the processing step fast enough that you actually do it.

---

### Recommended setup for different levels

**Minimal (10 minutes to set up):**
- Folder on your desktop with markdown files
- Claude Code pointed at that folder
- A CLAUDE.md with 20 lines of rules
- Process inbox once a day

**Standard (30 minutes):**
- Obsidian with the folder structure above
- CLAUDE.md + .claude/rules/ for modular instructions
- Obsidian mobile app for capture
- Inbox processing daily, weekly review on Fridays

**Power user (1-2 hours):**
- Everything above plus:
- Agent Client plugin (Claude Code embedded in Obsidian sidebar)
- Custom templates for different note types
- Project-specific CLAUDE.md files in each project folder
- Automated daily note creation via template

Don't start at power user. Start minimal. Add complexity only when you hit a real limitation, not a theoretical one.

---

### Tools and resources

- Obsidian: free for personal use, $50/yr for commercial
- Claude Code: requires Anthropic Pro ($20/mo) or Max ($200/mo) subscription
- Obsidian Sync: $4/mo (optional, iCloud/Dropbox work too)
- Agent Client plugin: free, brings Claude Code into Obsidian sidebar
- Obsidian mobile: free on iOS and Android

---

*This setup is what I actually use. Not a sponsored recommendation. Not a "look at my perfect system" post. Just a practical workflow that saves me time and helps me think better. Your mileage will vary based on how much you write and how consistently you capture.*
