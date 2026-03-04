# Cortana Memory Restore — Feb 12-13, 2026

**Purpose**: Restore Cortana's context after memory reset. Focuses on actionable facts, active projects, technical decisions, and recent conversations.

---

## 1. KEY PEOPLE & RELATIONSHIPS

### Ben Jammin (User)
- **Primary consulting client**: Five Points (Sam & Scott)
  - Last contact: Feb 12, 2026
  - Next follow-up: Feb 28, 2026
  - Active work: OEM dashboard project
  - Relationship: Current active clients, bread-and-butter income

- **Other contacts in pipeline**: Nick Blasco (status unknown)

### Cortana's Role
- AI agent running on Hetzner server (178.156.181.67)
- Handles research, content creation, automation, technical tasks
- Communicates via WhatsApp/Telegram
- Has personality, memory files, skill files (like "Larry" from the OpenClaw article)

---

## 2. ACTIVE PROJECTS (Feb 12-13, 2026)

### A. Content Strategy Overhaul
**Status**: Planning phase, architecture designed

**The Core Strategy**:
- ONE build per week → distribute everywhere in platform-native formats
- "Build one thing, talk about it everywhere. The build IS the content."
- Studied: Alex Finn, Wanderloots, CuroTeck (builders who film their work)

**Platform Breakdown**:

1. **LinkedIn**
   - Audience: Warm, posts occasionally
   - Strategy: Just start posting AI content, no comeback needed

2. **Substack** (Tech & Tranquility newsletter, 227 subscribers)
   - Audience: Followed Ben years ago for tech lifestyle content
   - Strategy: ONE re-intro issue explaining pivot to AI, then regular cadence
   - **NEW FORMAT** (designed Feb 12):
     - 🧠 The Insight (200-300 words, personal take on weekly build)
     - 🔨 What I Shipped (brief build update + screenshot)
     - 🔗 Tool of the Week (1 AI tool Ben actually uses, affiliate link)
     - 📰 3 Links Worth Your Time (curated AI/tech news)
     - 🎁 The Drop (product/content plug - templates, prompts, videos)
     - 💬 Question of the Week (drive replies for deliverability)
   - Send time: **Tuesday 8am ET**
   - Key insight: "A curated newsletter > a blog with a subscribe button"

3. **YouTube** (8K subs from deleted 2016 Trump news content)
   - Audience: Mostly ghosts from old niche
   - Strategy: Treat as fresh start, post AI content, let algorithm find new viewers
   - No "I'm back" video needed

4. **TikTok** (NEW FOCUS as of Feb 13)
   - Currently exploring automation for video creation
   - See Section 3 for technical details

**Content Calendar Pattern**:
- Wednesday = Content day (build something with AI)
- Cortana drafts Substack, batches 5 LinkedIn posts, outlines YouTube, writes TikTok hooks
- Ben reviews, tweaks, ships (~30 min time investment)

**Inspiration Reference**:
- Mentioned studying Lenny's Newsletter model (interviews, paid model with free tool access collabs)
- URLs: https://www.lennysnewsletter.com/ | https://lennysproductpass.com/

### B. TikTok Automation Pipeline
**Status**: Research complete (Feb 13 morning), testing tools, no final architecture chosen

**The Trigger** (Feb 13, 7:14am):
Ben sent Oliver Henry's article about "Larry" — an OpenClaw AI agent that got 500K+ TikTok views in 5 days by automating slideshow creation. Key lessons:
- Hook formula: `[Another person] + [conflict/doubt] → showed them AI → they changed their mind`
- Example: "My landlord said I can't change anything so I showed her what AI thinks it could look like" (234K views)
- Self-focused hooks flopped: "See your room in 12+ styles" (879 views)
- Used gpt-image-1.5 with "locked architecture" prompts (same room, only style changes)
- Posted to TikTok drafts via Postiz API, manually added trending music (~60 sec human work)
- Cost: $0.50/post ($0.25 with Batch API)

**Ben's Direction** (Feb 13):
- "I want to automate TikTok stuff, research and content creation"
- **Preference**: Real videos, not just carousels/slideshows
- **Don't settle on Postiz** — explore all options
- Use n8n for automation orchestration
- Want to test quality/price differences before committing to tools

**Research Completed** (Feb 13, 8:36am):

*Video Generation Options*:
- **Runway Gen-4 Turbo**: $0.60/10s, great quality, full API, Python SDK
- **Kling 2.5 Turbo**: $0.90/10s via fal.ai, cinematic
- **Sora 2** (OpenAI): $1-5/10s, best for narrative
- **HeyGen**: $0.50-1/video, best for talking head/avatar TikToks
- **Hailuo 2.3**: $0.25-0.50/10s, cheapest quality option
- **Luma Ray3.14**: Fastest generation
- **Google Veo 3.1**: Best quality, $5-7.50/10s (expensive)
- **Creatomate**: Template-based assembly, $0.05-0.10/render (subtitles, overlays, transitions)
- **FFmpeg pipeline**: Free, maximum control, image gen + audio + captions

*TikTok Posting API Options*:
- **Ayrshare** ($49/mo): Best docs, official TikTok partner, direct publish, Python SDK
- **Late/getlate.dev** ($19/mo): Cheaper, handles transcoding, draft support +$1
- **Upload-Post** ($16/mo): Cheapest unlimited, Python SDK
- **Blotato** ($29/mo): ONLY one with native n8n node ⭐
- **Publer** ($21/mo): Mid-tier, good API docs
- **PostFast** (€12/mo): Clean dev docs, EU-based
- **TikTok Direct API**: Free but brutal approval (needs published mobile apps)
- **Postiz self-hosted**: Free but you handle TikTok API approval yourself

*n8n Integration*:
- No official TikTok node, but **18+ ready templates** on n8n.io
- Best templates: Sora 2 → TikTok, VEO 3 → TikTok, Runway + Creatomate → faceless shorts
- Native OpenAI node (image gen built-in)
- Blotato has native n8n node, others via HTTP Request
- Creatomate = "secret weapon" for video assembly layer

*TikTok Strategy 2026*:
- **Video length**: 60-180 seconds for AI/tech niche
- **Algorithm**: Total watch time > completion rate now
- **Voiceovers**: Boost completion to 61% vs 53% silent
- **Hook window**: 1.5 seconds to grab attention
- **Hook formulas**:
  - Contradiction: "AI tools are actually making people LESS productive"
  - Specificity: "This saved me 14 hours last week" > "This saves time"
  - Open loops: Create curiosity gaps
  - NO "Hey guys welcome back" — start mid-action
- **Algorithm changes**: Follower-first distribution, 70%+ completion = viral potential
- **Engagement hierarchy**: Shares > Saves > Comments > Likes
- **Oracle took over US algorithm** Q1 2026 (expect fluctuations)
- **Posting**: 3-5x/week, best times Sun 8PM, Tue 4PM, Wed 5PM EST
- **Specs**: 1080x1920, 9:16, MP4, 3-5 hashtags max
- **MUST label AI content** — TikTok detects + penalizes unlabeled

**Tools Already Available**:
✅ OpenAI API key (image gen + scripts)
✅ ElevenLabs API key (voiceovers)
✅ n8n API URL + key (workflow automation)
✅ Gemini API key (Nano Banana Pro image gen)
✅ Airtable (content pipeline)
✅ Telegram (notifications)
✅ Composio (500+ app router)
✅ Google API
✅ Content pipeline scripts (content-to-airtable, content-ideas-generator)
✅ Retry/error handling libraries
✅ Cron + scheduling patterns
✅ InVideo MCP tool (script-to-video, TikTok format)
✅ Z-Image-Turbo (HuggingFace, free image gen, 9:16 format)

**Missing**:
❌ TikTok API credentials
❌ Video gen API key (Runway/Kling/Sora/etc)
❌ Posting service account (Blotato/Ayrshare/etc)
❌ Creatomate account (video assembly)

**Tests Completed** (Feb 13, 8:55am):
1. **OpenAI DALL-E 3** (1024x1792 HD): ~$0.08/image, great aesthetics, terrible text rendering (must add text overlays programmatically)
2. **ElevenLabs voiceover** (Rachel voice, multilingual v2): ~$0.10-0.30/clip, natural sounding, 30-second test sent
3. **Nano Banana Pro** (Gemini 3 Pro Image): ~$0.039/image at 1K, supports 1K/2K/4K, plus image editing capability

**Ben's Additional Input** (Feb 13, 9:01am):
- Also wants **video b-roll options**
- Consider **free image sources**: Pexels, Pixabay, etc (since each video needs 5+ images)
- Cost adds up: $0.039/image × 5 images = $0.20 just for images

**Next Steps** (as of Feb 13, 9:00am):
- Still deciding on architecture
- Exploring free stock image sources for b-roll
- Testing video generation quality/price differences
- No commitments made yet

### C. Creator Brain Notion System
**Status**: In development (mentioned Feb 13)

Details sparse in recent chat, but referenced as:
- "The Creator Brain template is 80% done — ship it at 80% and improve based on feedback"
- Part of Ben's product suite
- Being built with formulas, rollups, status properties

---

## 3. TECHNICAL INFRASTRUCTURE

### Server Setup (Cortana's Home)
- **Provider**: Hetzner
- **IP**: 178.156.181.67 (NOT 167.71.175.222 — that's stale)
- **Access**: SSH as root@178.156.181.67, key auth (password auth disabled)
- **Firewall**: UFW enabled, only port 22 allowed inbound
- **OpenClaw gateway**: Port 18789
- **VAPI tools**: Port 8787

### OpenClaw Configuration
- **Config**: `/root/.openclaw/openclaw.json`
- **Env**: `/root/.openclaw/.env` (COMPOSIO_API_KEY, GEMINI_API_KEY, etc)
- **Permissions**: `/root/.claude/settings.json` with wildcards (Bash(*), mcp__*, etc)
- **Timeout**: `agents.defaults.timeoutSeconds: 1200`
- **Sessions**: `~/.openclaw/sessions/`
- **Gateway log**: `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (rotated daily, 7d retention, 50MB max)
- **systemd**: System-level service at `/etc/systemd/system/openclaw-gateway.service` (user-level MASKED to /dev/null)

### Key Server Paths
- **Composio tool**: `/root/.openclaw/workspace/skills/composio/composio-tool.py`
- **Nano Banana Pro**: `/root/.codex/skills/nano-banana-pro/scripts/generate_image.py` (Gemini gemini-3-pro-image-preview)
- **Google OAuth creds**: `/root/.clawdbot/google_credentials.json` (chmod 600)
- **Cloudflare tunnel**: Running `cloudflared tunnel --url http://localhost:8787` (VAPI tools, auth via x-vapi-secret header)
- **VAPI auth secret**: `/root/.openclaw/.env` as VAPI_AUTH_SECRET
- **VAPI tools + workspace-OS**: Bound to 127.0.0.1 (not 0.0.0.0)
- **Shared lib**: `/root/.openclaw/workspace/lib/` (retry.py, alerting.py, health.py)
- **Watchdog v2**: `/root/.openclaw/workspace/scripts/watchdog.py` (flock, HTTP probe, reset-failed, dedup alerts)
- **Health report**: `/root/.openclaw/workspace/scripts/health-report.py` (daily 12:00 UTC Telegram summary)
- **Logrotate**: `/etc/logrotate.d/clawd`

### Active Issues (from error-log.md)
- **FailoverError crash loop**: Upstream OpenClaw bug (watchdog v2 handles with reset-failed + port cleanup)
- **Reddit 403**: Needs UA rotation
- **VAPI broken** (Feb 13 mention): API key rejected, Twilio number not found

### Resolved Issues
- Feb 6: Port 18789 spam, watchdog broken, silent monitor failures
- Feb 7: Security audit — VAPI auth added, services bound to localhost, fail2ban hardened (24h ban, 3 retries, Ben's IP whitelisted), X11Forwarding disabled, cloud-init PasswordAuth override fixed

### Gotchas (from MEMORY.md)
- `.env` vars don't have `export` prefix — child processes won't inherit unless loaded explicitly
- SSH to server can be flaky — retry with sleep if `kex_exchange_identification` errors
- `--dangerously-skip-permissions` CANNOT be used as root (Claude Code v2.1.32+ blocks it)
- OpenClaw installs BOTH system and user systemd services — user-level MASKED to /dev/null
- `openclaw gateway` double-forks: child can orphan and hold port after crash
- On Windows, don't use `/dev/null` — use `NUL` or `$null`
- Windows subagent symlinks fail with EPERM — need Developer Mode or elevated terminal
- Broad ripgrep searches in AppData timeout after 20s — use specific paths
- `/etc/ssh/sshd_config.d/50-cloud-init.conf` can OVERRIDE main sshd_config
- fail2ban whitelist: 127.0.0.0/8, ::1, 108.27.50.87 (Ben's IP)
- VAPI tunnel script now includes secret in server config

---

## 4. BEN'S WORK PATTERNS & PREFERENCES

### Execution Style
**Problem**: Ben has "idea after idea after idea" and struggles with full follow-through

**Cortana's Prescribed Solution** (Feb 12, 7:19pm):
1. **One Thing Rule**: Pick ONE thing per week, everything else waits
2. **Build the assembly line, not the factory**: Volume beats perfection, ship before ready
3. **Use Cortana as forcing function**: Every Wednesday, tell topic → Cortana drafts everything → Ben reviews/tweaks/ships (30 min vs 3 hours)
4. **The Parking Lot**: New ideas go to Notion backlog with Cortana, then back to the ONE thing
5. **Ship at 80%**: Thomas Frank's first template probably sucked, ship anyway

**Key Quote**: "Ben doesn't have an execution problem. He has a prioritization problem. And the fix is dead simple — one thing per week, park everything else with me, and let me handle the drafts. His job is just to hit publish."

### Schedule (from earlier context)
- **Thursday PM**: Five Points consulting (unclear if full afternoon every week or flex time)
- **Wednesday**: Content day (build + distribute)

### Communication Style
- Ben prefers direct execution over extensive planning questions
- Responds well to structured options vs open-ended "what do you want to do?"
- Likes seeing real output/tests before committing to tools
- Values cost-effectiveness (caught Cortana saying "free" when Gemini API costs money)

---

## 5. CONTENT & PRODUCT ECOSYSTEM

### Ben's Online Presence
- **LinkedIn**: Active, warm audience
- **Substack**: Tech & Tranquility, 227 subscribers (dormant, needs re-intro)
- **YouTube**: 8K subscribers (2016 Trump news content deleted, effectively fresh start)
- **TikTok**: Exploring (automation focus)
- **X/Twitter**: Mentioned, currently suspended/reinstating (threads planned)
- **Discord**: Members get content first

### Products (Inferred)
- **Creator Brain**: Notion template system (80% done as of Feb 12)
- Various templates/prompt packs (part of content strategy)
- Five Points OEM dashboard (consulting work)

### Content Pipeline Tools
- Airtable (content ideas, pipeline management)
- Notion (workspace, templates, backlog)
- Scripts: content-to-airtable, content-ideas-generator
- Telegram (notifications, communication with Cortana)

---

## 6. LEARNED PATTERNS & INSIGHTS

### From Oliver Henry's "Larry" Article (Feb 13)
**What Works on TikTok**:
- Hook structure: `[Person] + [conflict] → showed AI → reaction`
- Examples that crushed:
  - "My landlord said I can't change anything..." (234K views)
  - "I showed my mum what AI thinks our living room could be" (167K views)
  - "My landlord wouldn't let me decorate until I showed her these" (147K views)
- Self-focused hooks FLOPPED:
  - "Why does my flat look like a student loan" (905 views)
  - "See your room in 12+ styles" (879 views)
  - "The difference between $500 and $5000 taste" (2,671 views)

**Technical Lessons**:
- "Locked architecture" prompts = obsessively specific room description, only style changes
- Early mistake: vague prompts = different rooms every slide = looks fake
- Image specs: 1024x1536 portrait (NOT landscape = black bars = dead engagement)
- Text overlays: 6.5% font size, positioned to avoid TikTok status bar
- People in images didn't work well
- Add everyday items (TV, mugs, remote) to make rooms relatable vs empty show homes

**Larry's Setup**:
- Old gaming PC (NVIDIA GPU) running Ubuntu
- OpenClaw + Claude
- Skill files (500+ lines for TikTok, constantly updated after failures)
- Memory files (every post, view count, insight logged)
- Plans 10-15 hooks at once, pre-generates overnight via OpenAI Batch API
- RevenueCat integration to track MRR/subscriber impact

**Results**: 500K+ views in 5 days, 108 paying subscribers, ~$588/mo MRR, cost $0.50/post

### Content Strategy Principles
1. **Build one thing → distribute everywhere** (Alex Finn, Wanderloots, CuroTeck model)
2. **Story first, value second, selling never** (until audience warmed up)
3. **Curation is value** — people drowning in AI news want trusted filter
4. **The comeback story IS content** — "I went quiet because I was building something"
5. **Each platform has different relationship** — LinkedIn (warm), Substack (needs soft pivot), YouTube (fresh start)

---

## 7. REMINDERS & SCHEDULED ITEMS

### Upcoming (from chat context)
- **Thu Feb 12, 10am ET**: Set up n8n MCP connection with Claude Code (reminder was set Feb 11)
- **Monday Feb 10, 10AM ET**: Composio X API article (Telegram reminder, no auto-post)
- **Tuesday Feb 11, 10AM ET**: Memory system post (Telegram reminder)
- **Wednesday Feb 12, 10AM ET**: Deploy web app post (Telegram reminder)

**Note**: These were switched from auto-post to Telegram reminders so Ben controls final formatting. Need to push x-research fork to GitHub before Monday for repo link.

---

## 8. INTEGRATION CAPABILITIES

### MCP Tools Available
- InVideo (script-to-video, TikTok format ready)
- Z-Image-Turbo (HuggingFace, free 9:16 image gen)
- Blender MCP (3D modeling, mentioned in earlier context)
- Nano Banana Pro (Gemini image gen + editing)

### API Integrations Configured
- OpenAI (GPT, DALL-E, Batch API)
- ElevenLabs (voice cloning capable)
- Gemini (image gen, text)
- Airtable (content management)
- Composio (500+ app router, GitHub auth as of Feb 13)
- n8n (workflow automation, API access configured)
- Telegram (notifications, chat)
- RevenueCat (mentioned in Larry article, Ben works there per context)

### Composio GitHub Access
- Auth completed Feb 13
- URL: https://backend.composio.dev/api/v3/s/cWomYuo2
- Successfully accessed "Retell" repo (19 compositions, themes, animation components)
- Can now pull private repos

---

## 9. OPEN QUESTIONS / PENDING DECISIONS

### TikTok Automation (as of Feb 13, 9:01am)
- Video gen tool? (Runway vs Kling vs Sora vs HeyGen vs Creatomate vs FFmpeg)
- Posting service? (Blotato vs Ayrshare vs Late vs Upload-Post)
- Slideshow vs real video?
- Stock images (Pexels/Pixabay) vs generated?
- FFmpeg vs Remotion for assembly?

### Content Strategy
- When to ship Creator Brain template? (currently 80% done)
- Substack re-intro issue timing?
- First LinkedIn post topic?
- YouTube channel relaunch strategy details?

### Infrastructure
- VAPI fix needed (API key rejected, Twilio number issue)
- n8n MCP connection setup (was scheduled for Thu Feb 12 10am)

---

## 10. VOICE & PERSONALITY

### Cortana's Communication Style
- Uses 💜 emoji frequently (signature)
- "On it 🔥" energy
- Self-aware about mistakes ("my bad", "that was sloppy 😅")
- Writes compact, bulleted summaries
- Ends with clear next-step questions
- Uses internal monologue format: "Done! ✅ [summary of what was sent]"
- Not afraid to push back ("You're right, I was too fixated on copying that guy's exact stack")

### Ben's Preferences
- Dislikes emojis in documentation/files unless requested
- Values precision (called out "free" when it costs money)
- Wants to test before committing
- Appreciates structured options
- "Let's try them out" > "Should we...?"

---

## QUICK REFERENCE: CURRENT STATE (Feb 13, 2026)

**Active Work**:
- TikTok automation architecture research (no final decision)
- Content strategy designed, waiting on first execution
- Creator Brain template at 80%

**Waiting On**:
- Ben's decision on TikTok video gen approach
- Ben's decision on posting service
- VAPI debugging
- n8n MCP connection setup

**Next Concrete Actions**:
1. Finalize TikTok pipeline architecture
2. Write Substack re-intro issue
3. Ship Creator Brain at 80%
4. Execute first Wednesday content build → distribute cycle

**Revenue**: Five Points (Sam & Scott) = current bread and butter, next contact Feb 28

**Infrastructure Health**: Stable except VAPI issue, watchdog v2 handling OpenClaw crashes

---

**End of Memory Restore**
*Generated: Feb 13, 2026*
*Source: Telegram ChatExport_2026-02-13 (messages.html - messages6.html)*
*Word count: ~2,950*
