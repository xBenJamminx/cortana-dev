# OpenConcierge — Recurring Infrastructure Engine
**Version:** 2.0
**Date:** February 16, 2026
**Status:** ACTIVE BUILD TRACK (parallel to Parker & Taylor)

---

## 1. What Is This?

OpenConcierge is an AI Chief of Staff service. Each client gets their own AI assistant that reads their email, manages their calendar, tracks their follow-ups, and answers questions — all through whatever messaging app they already use (WhatsApp, Telegram, Slack, text, etc.).

Think of it as giving every client their own version of Cortana — customized to how they work, connected to their tools, learning their preferences over time.

**One sentence:** We set up, customize, and maintain a personal AI assistant for busy operators so they can stop drowning in operational overhead.

---

## 2. Who Is This For?

**Primary clients:**
- Founder-led teams doing a lot with few people
- Independent operators managing multiple things at once
- Small fund managers, family offices, search funds
- Real estate sponsors, boutique agencies
- Anyone whose time is too valuable to spend sorting email and managing calendars

**What they have in common:**
- High complexity relative to team size
- Don't want to hire another person for operational work
- Already overwhelmed by email, scheduling, and follow-ups
- Value privacy — don't want their data on someone else's servers

**Not for:** Large enterprises with IT departments, people who just want a chatbot, anyone who doesn't use email/calendar regularly.

---

## 3. What Does the Client Get?

### Core Capabilities (Day 1)

| What They See | What It Does |
|---------------|-------------|
| **Morning Summary** | Every morning, their AI sends a single message with: today's calendar, flagged emails, and anything overdue. Delivered via their preferred app. |
| **Inbox Sorting** | Their AI reads new emails, separates what's urgent from what's noise, drafts replies for the important ones, and archives the rest. Nothing gets sent without approval. |
| **Calendar Management** | Spots double-bookings, protects focus time between meetings, and suggests fixes. Can create/move events with client approval. |
| **Follow-Up Tracking** | Remembers what the client promised people ("I'll send that by Friday"), tracks deadlines, and surfaces anything overdue. |
| **On-Demand Research** | Client texts "what's the market cap of X?" or "find me 3 restaurants near the office for Friday" — gets a researched answer back in the same chat. |

### How the Client Interacts

The client talks to their AI through **whatever messaging app they prefer:**
- WhatsApp (most common expected)
- Telegram
- Slack
- Discord
- SMS / iMessage
- Web chat
- Voice call (Twilio)

They don't download anything new. They don't log into a dashboard. They just text their AI like they'd text a real assistant.

### What the Client Connects

During setup, the client clicks a few authorization links to connect their tools:
- **Gmail** — so the AI can read and draft emails
- **Google Calendar** — so the AI can see and manage their schedule
- **Slack** (optional) — if they want their AI in their team's Slack
- **CRM / HubSpot** (optional) — for deal and contact tracking
- **Notion** (optional) — for notes and project tracking

The client clicks a link, signs in with Google/etc., and that's it. No passwords shared, no API keys, no technical setup on their end.

---

## 4. The Three Things We Need to Build

### A. The AI Agent System (Core Product)

This is what runs behind the scenes — each client's personalized AI assistant.

**What exists today:**
- OpenClaw (open-source agent runtime) is battle-tested — we run it ourselves for Cortana
- It already supports multiple agents, message routing, memory, scheduled tasks
- Composio (tool connector) already supports 500+ apps with per-client authentication
- We already run Cortana (Ben's personal AI) through this exact system — so we know it works

**What we need to build:**
1. A reusable workspace template for new clients (personality settings, operating instructions, tool connections, preferences)
2. **Base skills** (every client gets these): inbox sorting, morning summary, calendar management, follow-up tracking, research
3. **Module skill sets** (installed per client based on what they're paying for): Operator, Household CEO, Finance, Creator Engine
4. Per-client configuration (routing their messages to their agent, connecting their tools, activating their modules)

**Internal technical detail:** Each client gets OpenClaw installed on their own server with their own workspace directory, memory, skills, and Composio user_id. Claude Code CLI is the brain — handles reasoning, tool use, context. We help them set it up, configure it, and maintain it — but it runs on their infrastructure.

### B. The Onboarding Wizard (Setup Flow)

Right now, setting up a new client would mean spinning up their server, manually creating directories, editing config files, and generating auth links by hand. That doesn't scale past 2-3 clients.

**What we need:** A simple web-based setup flow that walks through client onboarding step by step.

#### Onboarding Steps (What the Admin Sees)

**Step 1 — Client Info**
- Client name, company, role
- Preferred communication channel (WhatsApp / Telegram / Slack / etc.)
- Their phone number or chat ID for that channel

**Step 2 — Personality & Preferences**
- Communication style: formal / balanced / casual
- Working hours and timezone
- Morning summary time (e.g., 7am)
- How they want to be addressed
- Any specific preferences ("never schedule meetings before 9am", "always flag emails from X")

**Step 3 — Tool Connections**
- Shows a checklist of tools to connect: Gmail, Calendar, Slack, CRM, Notion
- Each tool has a "Connect" button that generates a Composio authorization link
- Client clicks the link, authorizes, comes back — green checkmark
- Gmail + Calendar are required; everything else is optional

**Step 4 — Review & Activate**
- Summary of everything configured
- "Activate" button that:
  - Creates the client's workspace from the template
  - Fills in their name, preferences, schedule into the config files
  - Registers the agent in OpenClaw
  - Sets up message routing
  - Enables their scheduled tasks (morning summary, inbox sorting)
  - Sends the client a welcome message on their channel

**What happens behind the scenes on Activate:**
1. Provisions client's server (or connects to one they provide)
2. Installs OpenClaw + Claude Code CLI on their server
3. Creates workspace from template, populates SOUL.md (personality), USER.md (profile), AGENTS.md (instructions), config/schedule.md (working hours)
4. Configures agent and message routing in openclaw.json
5. Stores Composio connected account IDs in client config
6. Sets up cron schedules for email sorting + morning summary
7. Sends a test morning summary to verify everything works

#### Onboarding Steps (What the Client Sees)

The client's experience is minimal:
1. Gets an email/message: "Click these links to connect your email and calendar"
2. Clicks 2-3 links, signs into Google/Slack/etc.
3. Gets a welcome message from their new AI: "Hi [name], I'm set up and ready to help. Your first morning summary arrives tomorrow at [time]."

That's it. No accounts to create, no apps to install, no dashboards to learn.

### C. The Control Panel (Management Dashboard)

Once we have multiple clients on their own servers, we need a way to see what's going on and manage everything without SSH-ing into each server individually.

#### Dashboard Features

**Client Overview (Home Page)**
- List of all active clients
- Status indicators: active / paused / needs attention
- Last activity timestamp
- Quick stats: messages this week, emails processed, follow-ups tracked

**Per-Client Detail View**
- Client profile (name, company, channel, timezone)
- Connected tools with status (Gmail ✅, Calendar ✅, Slack ❌)
- Recent activity log (last 20 interactions)
- Memory highlights (what the AI has learned about this client)
- Configuration: edit personality, schedule, preferences
- Actions: pause agent, reconnect tool, send test message, view logs

**System Health (across all client servers)**
- Per-client server status (OpenClaw gateway running, memory usage, disk)
- Agent status for each client (active sessions, errors)
- Composio connection health (any expired tokens?)
- Upcoming scheduled tasks

**Quick Actions**
- Add new client (launches onboarding wizard)
- Pause/resume any client
- Reconnect expired tool auth
- Send manual message as any client's AI
- View/edit any client's configuration

---

## 5. Technical Architecture (Internal Only)

### Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Agent Runtime | OpenClaw (self-hosted, open source) | Multi-agent orchestration, message routing, memory, cron, channels |
| AI Brain | Claude Code CLI (`claude` command) | Reasoning, tool use, context management, conversation |
| Tool Integrations | Composio (API) | Per-client OAuth for Gmail, Calendar, Slack, CRM, 500+ apps |
| Client Server | Their own server (we help provision) | Runs their OpenClaw instance, agent, and data — entirely on their infrastructure |
| Our Infrastructure | Hetzner (178.156.181.67) | Runs Cortana (our own AI) + onboarding/control panel tools |
| Onboarding + Dashboard | SvelteKit + Tailwind CSS | Web UI for admin setup and management |
| Landing Page | SvelteKit (Vercel) | Marketing site at openconcierge.com |

### How Messages Flow

```
Client sends WhatsApp message
        │
        ▼
OpenClaw Gateway (on CLIENT'S server)
        │
        ├── Routes message to their agent
        │
        ▼
Client's Agent (their workspace, their memory, their skills)
        │
        ├── Claude Code CLI processes the message
        ├── Calls Composio tools if needed (read email, check calendar)
        ├── Updates memory
        │
        ▼
Response sent back through same channel
```

### Per-Client Isolation

Each client gets:
- **Own server** — their data never touches our systems or any other client's systems
- **Own OpenClaw instance** running on that server
- **Own workspace directory** with their agent config, skills, and memory
- **Own Composio user_id** (separate tool auth, separate data)
- **Own personality/preferences** (SOUL.md, schedule, rules)

### Data & Privacy

- All client data stays on the client's own server — not ours
- We help set it up and maintain it, but the infrastructure belongs to them
- Tool auth is per-client via Composio OAuth (we never see their passwords)
- Composio auto-refreshes tokens — clients authorize once
- If a client leaves, the server and all their data is theirs to keep or delete
- No data sold, no training on client data
- We access their server for maintenance only — with their permission

---

## 6. Pricing

### Base: AI Chief of Staff
| | |
|---|---|
| **Setup fee** | $2,500 (one-time) |
| **Monthly** | $1,500/mo |

Includes everything in the core capabilities: inbox sorted with draft replies, calendar conflicts resolved, daily & weekly briefings, follow-ups tracked, on-demand research & meeting prep, privacy by default, and a hands-on tuning period.

### Add-On Modules
Clients start with the base and add modules based on who they are and what they need. Each module plugs into the existing AI — it's not a separate product, it's an expansion.

| Module | Who It's For | Monthly Add-On |
|--------|-------------|----------------|
| **Operator System** | Founders & Executives | +$1,000–$1,500/mo |
| **Household CEO** | Busy Families | +$500–$1,000/mo |
| **Finance Module** | Investors & Business Owners | +$750–$1,500/mo |
| **Creator Engine** | Consultants & Creators | +$750–$1,250/mo |

**Operator System** — Deal tracking & pipeline visibility, client follow-up automation, proposal & document drafting, revenue summary briefings, strategic planning support.

**Household CEO** — Family calendar optimization, kids activity & schedule management, travel coordination & planning, vendor & home services tracking, household budget intelligence.

**Finance Module** — Investment briefings & alerts, expense oversight & categorization, tax prep summaries, capital event reminders, financial snapshot reports.

**Creator Engine** — Content ideation & research, voice calibration & brand consistency, repurposing workflows, publishing preparation, audience analytics summaries.

### Packaging (How It's Presented on the Landing Page)

| Package | Setup | Monthly | What's Included |
|---------|-------|---------|----------------|
| **AI Chief of Staff** (base) | $2,500 | $1,500/mo | Full core system |
| **Chief of Staff + Module** (most popular) | $2,500 | $2,000–$3,000/mo | Base + 1 module of choice + custom workflows + monthly check-ins + priority support |
| **Full Suite** | $5,000 | $3,000–$5,500/mo | Base + 2-3 modules + advanced automation + dedicated support channel + quarterly reviews + white-glove onboarding |

AI usage costs are separate and paid directly to the providers. No markup from us.

### Unit Economics

**Client pays directly:** Server hosting (~$10-30/mo), Claude Code CLI subscription (~$20-200/mo), Composio if they exceed free tier
**We charge:** Setup fee + monthly retainer for configuration, maintenance, tuning, and support
**Our cost per client:** Mainly our time — setup, hypercare, ongoing maintenance
**Revenue per client:** $1,500–$5,500/month

---

## 7. Onboarding Flow (Full Journey)

### Week -1: Discovery
1. Discovery call with client (30-60 min)
2. Understand: what tools they use, what overwhelms them, how they communicate, what their ideal morning looks like
3. Identify which tier fits

### Week 0: Setup
1. Run the onboarding wizard (admin side)
2. Send client the tool connection links (2-3 clicks on their end)
3. Configure preferences: personality, schedule, VIP contacts, ignore patterns
4. Activate agent
5. Send welcome message

### Week 1-2: Hypercare
1. Daily monitoring of the AI's performance
2. Review morning summaries — are they useful? Too long? Missing things?
3. Check inbox sorting accuracy — are important emails getting flagged?
4. Tune preferences based on client feedback
5. Daily check-in with client: "How's it going? Anything feel off?"

### Week 3+: Steady State
1. AI runs autonomously
2. Weekly quality spot-check (internal)
3. Monthly check-in call with client
4. Ongoing improvements: add skills, refine sorting rules, expand tool connections

---

## 8. Success Metrics

### For Clients (What We'll Track — No Claims Until We Have Data)
- Morning summary delivered on time every day
- Inbox sorting catches the important stuff (measured during hypercare via client feedback)
- Client feels like they're spending less time on email and scheduling (qualitative, from check-ins)
- Follow-ups don't slip through the cracks
- Client actually uses the AI regularly (engagement = value)

### For Us
- Time to activate a new client (goal: streamline with each new client)
- Client retention past the 3-month minimum
- Monthly recurring revenue growth
- Support load per client after hypercare

**Note:** We don't have real numbers yet — we haven't shipped this to anyone. These metrics get filled in during dogfooding and the first few clients. Don't put specific percentages or time savings on the website or in sales conversations until we can back them up.

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| AI sends wrong email on client's behalf | High — trust broken | **Nothing gets sent without explicit client approval.** AI drafts, client confirms. |
| Tool auth expires and AI goes silent | Medium — client misses a summary | Composio auto-refreshes tokens. Control panel shows connection health. Alert on failures. |
| Client data leaks between clients | Critical — business-ending | Each client has their own server. No shared infrastructure between clients. |
| Claude Code CLI has an outage | High — client's AI goes offline | Fallback models configured (Haiku, OpenRouter alternatives). Alert system notifies us. |
| Client doesn't adopt / doesn't find it useful | Medium — churn | 14-day hypercare with daily tuning. Monthly check-ins. Personality customization. |
| Client's server goes down | High — that client goes offline | Health monitoring alerts us. We help restore. Other clients unaffected (separate servers). |

---

## 10. Build Phases

### Phase 1: Base Product (Weeks 1-2)
**Goal:** One working AI Chief of Staff (the base package) that we dogfood ourselves.

- [ ] Create the reusable workspace template (AGENTS.md, SOUL.md, USER.md, TOOLS.md, config/)
- [ ] Build the 5 **base skills** (included for every client):
  - [ ] Inbox sorting (Composio Gmail integration)
  - [ ] Morning summary (calendar + email + follow-ups combined)
  - [ ] Calendar management (conflict detection, buffer time)
  - [ ] Follow-up tracking (commitment extraction, deadline monitoring)
  - [ ] Research (web search + synthesized answers)
- [ ] Set up Composio Gmail + Calendar with Ben as test client
- [ ] Register Ben as a test client agent in OpenClaw
- [ ] Run the full loop: inbox sort → morning summary → on-demand chat
- [ ] Dogfood for 1-2 weeks, fix issues

**Exit criteria:** Ben gets a useful morning summary every day, inbox is pre-sorted, follow-ups are tracked, and he can text his AI for anything. If Ben finds it genuinely useful, that proves out the $1,500/mo base package.

### Phase 2: Onboarding + First Module (Weeks 3-4)
**Goal:** Set up a new client in under 2 hours. Build the first add-on module so we can sell the "Chief of Staff + Module" package.

- [ ] Build the onboarding wizard (SvelteKit web app):
  - [ ] Client info form
  - [ ] Personality/preference configurator
  - [ ] **Module picker** (which add-ons does this client get?)
  - [ ] Composio tool connection flow (generate + track auth links)
  - [ ] One-click agent activation (installs only the selected module skills)
- [ ] Build the control panel dashboard:
  - [ ] Client overview with status indicators + **active modules shown per client**
  - [ ] Per-client detail view (config, activity, health, modules)
  - [ ] Quick actions (pause, reconnect, test message, add/remove module)
  - [ ] System health view
- [ ] Onboarding automation script (provisions client server, installs OpenClaw + Claude CLI, creates workspace, registers agent, sets up routing, installs selected module skills, enables cron)
- [ ] Build the **Operator System module** skills (most likely first client need):
  - [ ] Deal tracking & pipeline visibility
  - [ ] Client follow-up automation
  - [ ] Proposal & document drafting
  - [ ] Revenue summary briefings
  - [ ] Strategic planning support
- [ ] Test: onboard a second test user end-to-end through the wizard with base + Operator module

**Exit criteria:** New client goes from "signed up" to "getting morning summaries + operator features" via the wizard with zero SSH required. We can sell the $2,000-$3,000/mo package.

### Phase 3: Remaining Modules + Scale (Weeks 5+)
**Goal:** Build remaining modules as client demand dictates. Ready for Full Suite package.

- [ ] WhatsApp channel setup (most clients will want this)
- [ ] Build **Household CEO module** skills (family calendar, kids schedules, travel, vendors, household budget)
- [ ] Build **Finance module** skills (investment alerts, expenses, tax prep, capital events)
- [ ] Build **Creator Engine module** skills (content ideas, brand voice, repurposing, publishing, analytics)
- [ ] Client self-service: view their own activity, update preferences
- [ ] Streamline server provisioning (automate spinning up + configuring new client servers)
- [ ] Case studies from Ben's usage for sales material
- [ ] Billing integration (Stripe or manual invoicing)

**Note:** We don't need all 4 modules to start selling. Build modules as clients need them — if the first client is a founder, we build Operator first. If they're a busy parent, Household CEO first. No wasted work.

---

## 11. Open Questions

1. **WhatsApp Business API** — Do we need a Meta Business account and verified number? What's the cost? (Most clients will want WhatsApp as their channel.)
2. **Claude Code CLI licensing** — One Anthropic Pro/Max subscription per client agent, or does OpenClaw handle this differently? Need to confirm per-agent billing.
3. **Composio scaling** — 20K free calls/month total across all clients. At what client count do we need a paid plan? What's the cost?
4. **Landing page domain** — Is openconcierge.com secured? Need to confirm DNS + deployment.
5. **Drew's involvement** — Is Drew (mentioned in architecture doc) a co-founder, first client, or both? Affects pricing and priority.
6. **Legal** — Do we need a Terms of Service / Privacy Policy before taking on clients? Data processing agreements?
7. **Backup strategy** — Do we offer automated backups of client servers as part of the service? Or is that on them?

---

## 12. Summary

**What we're building:** A done-for-you AI Chief of Staff service. Each client gets a personal AI that handles their email, calendar, follow-ups, and questions — delivered through whatever messaging app they already use.

**What makes it work:** OpenClaw (agent runtime we already run) + Composio (tool connections) + Claude Code CLI (the brain). Same stack that powers Cortana, reproduced and customized per client.

**What we need to build:** (1) Core skills for email/calendar/follow-ups, (2) an onboarding wizard to set up clients fast, (3) a control panel to manage everyone.

**Business model:** $2,500 setup + $1,500/mo base, with add-on modules ($500-$1,500/mo each) for operators, families, investors, and creators. Client owns the infrastructure; we charge for setup, customization, and ongoing support. Target 1-3 clients in the first 90 days to eliminate the $3.5k/month burn rate.

**First milestone:** Dogfood the full system on Ben within 2 weeks. If it genuinely makes his mornings easier, we have a product.
