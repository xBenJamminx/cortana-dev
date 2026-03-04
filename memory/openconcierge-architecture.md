# OpenConcierge — Technical Architecture (v3)

## What the Client Sees (NO tech jargon — use this language externally)

| We Say | Not This |
|--------|----------|
| Your AI reads your inbox and flags what matters | Email triage pipeline |
| Draft replies ready for you to review | AI-powered response generation |
| One morning summary with everything you need | Daily briefing via multi-source aggregation |
| Your AI remembers what you promised people | Follow-up tracking with commitment extraction |
| Spots double-bookings and protects your focus time | Calendar conflict detection and optimization |
| Ask your AI anything, get a researched answer | On-demand research agent with RAG |
| Talk to your AI via text, email, or WhatsApp | Multi-channel communication interface |
| Your data stays on your systems, not ours | Client-owned infrastructure with tenant isolation |
| We connect your AI to your tools — you click a few links | Composio OAuth per-client integration |

**Rule: if Drew or a client would hear it, use the left column. The right column is internal only.**

---

## Foundation

**OpenClaw** = the agent runtime (open source, already installed and running on our Hetzner server)
**Composio** = tool integrations (500+ apps, per-client OAuth via user_id)
**Claude Code CLI** = the brain (NOT the API — the full Claude Code CLI via `claude` command, same as Cortana)

The product is literally: reproduce the Cortana experience for each client. Each client gets their own "Cortana" running via the Claude Code CLI through OpenClaw, customized to their preferences, connected to their tools. We don't manage prompts, token windows, or API calls — Claude Code CLI handles all of that. OpenClaw handles sessions, compaction, cron, multi-channel routing.

---

## Current State (What We Already Have Running)

### OpenClaw Gateway
- **Running at:** `ws://127.0.0.1:18789` on Hetzner (178.156.181.67)
- **Version:** 2026.2.9
- **Backend:** claude-cli (Sonnet primary, Haiku fallback, Opus available)
- **Multi-model:** OpenRouter configured (Kimi K2, Gemini 3 Pro, Claude Opus 4.5)
- **Channels active:** Telegram (open DM + groups), Slack (enabled)
- **Plugins:** Telegram, Slack, Lobster, LLM-task, Voice-call (Twilio configured)
- **Agents:** `main` (Cortana, /root/.openclaw/workspace) + `pro` (Kimi K2, /root/.openclaw/workspace-pro)
- **Memory:** QMD backend (SQLite + vector)

### Composio
- **API Key:** in ~/.openclaw/.env
- **Connected:** GitHub OAuth (xBenJamminx), Twitter (dead — X suspended)
- **Capabilities:** 500+ app integrations, per-user auth via user_id/entity_id
- **MCP URL:** `https://backend.composio.dev/tool_router/trs_r19DmEN65WU9/mcp`

### Existing Skills & Scripts
- 21 skills in workspace/skills/
- 40+ scripts in workspace/scripts/
- Libs: telegram.py, alerting.py, health.py, retry.py, elevenlabs.py

---

## OpenConcierge Architecture

Each client gets their own server running their own OpenClaw instance. We don't host their data — we help them set up and maintain their system. Their data stays on their infrastructure.

```
┌─────────────────────────────────────────────┐
│            CLIENT A's SERVER                │
│                                             │
│  Client communicates via preferred channel  │
│  (WhatsApp / Telegram / Slack / etc.)       │
│                    │                        │
│                    ▼                        │
│    ┌──────────────────────────────┐         │
│    │   OpenClaw Gateway           │         │
│    │   (on client's server)       │         │
│    └──────────────┬───────────────┘         │
│                   │                         │
│                   ▼                         │
│    ┌──────────────────────────────┐         │
│    │   Client A's AI Agent        │         │
│    │   ├ SOUL.md (personality)    │         │
│    │   ├ AGENTS.md (instructions) │         │
│    │   ├ skills/ (base + modules) │         │
│    │   └ memory/ (learns over time)│        │
│    │                              │         │
│    │   Composio user_id: clientA  │         │
│    │   (Gmail, Calendar, etc.)    │         │
│    └──────────────────────────────┘         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│            OUR SERVER (Cortana)              │
│                                             │
│    ┌──────────────────────────────┐         │
│    │   Cortana (our AI)           │         │
│    │   + Onboarding Wizard        │         │
│    │   + Control Panel            │         │
│    └──────────────────────────────┘         │
└─────────────────────────────────────────────┘
```

### Example Client Config (openclaw.json on their server)

```json5
{
  agents: {
    defaults: {
      model: { primary: "claude-cli/sonnet" },
      cliBackends: { "claude-cli": { command: "claude", args: ["-p", "--output-format", "json"] } }
    },
    list: [
      {
        id: "chief-of-staff",
        name: "Jessica's Chief of Staff",
        workspace: "/root/.openclaw/workspace",
        model: { primary: "claude-cli/sonnet" }
      }
    ]
  },
  bindings: [
    // Route all messages to their agent
    { agentId: "chief-of-staff" }
  ]
}
```

---

## Per-Client Workspace Template

```
/root/.openclaw/clients/<name>/workspace/
├── AGENTS.md          # Operating instructions — Chief of Staff role
├── SOUL.md            # Personality (formal/casual), comm prefs, working hours
├── USER.md            # Client profile (name, role, company, key contacts)
├── TOOLS.md           # Routing table for this client's skills
├── skills/
│   ├── email-triage/
│   │   └── SKILL.md   # Classify, prioritize, draft, archive via Composio Gmail
│   ├── daily-briefing/
│   │   └── SKILL.md   # Morning summary (calendar + email + follow-ups)
│   ├── calendar-ops/
│   │   └── SKILL.md   # Conflict detection, scheduling, buffer time
│   ├── follow-up-tracker/
│   │   └── SKILL.md   # Extract commitments, track, surface overdue
│   └── research/
│       └── SKILL.md   # Web research on demand
├── memory/
│   ├── MEMORY.md      # Curated long-term facts about client
│   └── 2026-02-15.md  # Daily memory (auto-managed by OpenClaw)
└── config/
    ├── triage-rules.md    # Client-specific email rules (VIPs, ignore patterns)
    └── schedule.md        # Working hours, meeting preferences, buffer rules
```

### Template AGENTS.md (Chief of Staff)

```markdown
# AI Chief of Staff

You are an AI Chief of Staff for {CLIENT_NAME}. You manage their operational overhead
so they can focus on high-value work.

## Your Responsibilities
1. Triage their inbox every morning — classify, prioritize, draft responses
2. Deliver a daily briefing at {BRIEFING_TIME} via {CHANNEL}
3. Monitor calendar for conflicts and optimize scheduling
4. Track all commitments and follow-ups — never let anything slip
5. Respond to on-demand requests via {CHANNEL}

## Rules
- Never send emails without client approval
- Flag anything financial, legal, or highly sensitive for manual review
- Always cite sources when providing research
- Maintain a professional but warm tone
- Remember preferences — learn from corrections

## Composio User ID: {COMPOSIO_USER_ID}
Use this when calling any Composio tool to access this client's authenticated apps.
```

---

## Composio Integration (Per-Client OAuth)

### Client Onboarding Auth Flow

1. Create a Composio entity for the client:
   ```python
   # POST https://backend.composio.dev/api/v1/connectedAccounts
   {
     "integrationId": "gmail-integration-id",
     "entity_id": "client-jessica",
     "redirectUrl": "https://openconcierge.com/onboarding/success"
   }
   ```

2. Send client the **Connect Link** — they click it, authorize Gmail/Calendar, done
3. Composio stores tokens, auto-refreshes, we call tools with their user_id:
   ```python
   # Execute tool on behalf of specific client
   requests.post(
     "https://backend.composio.dev/api/v2/actions/GMAIL_FETCH_EMAILS/execute",
     headers={"x-api-key": COMPOSIO_API_KEY},
     json={
       "connectedAccountId": "client-jessica-gmail-uuid",
       "input": {"max_results": 50, "label_ids": ["INBOX"]}
     }
   )
   ```

### Required Composio Integrations Per Client
| App | Purpose | Composio Action Examples |
|-----|---------|------------------------|
| Gmail | Read/triage/draft/send | GMAIL_FETCH_EMAILS, GMAIL_SEND_EMAIL, GMAIL_MODIFY_MESSAGE |
| Google Calendar | Read/create/modify events | GOOGLECALENDAR_LIST_EVENTS, GOOGLECALENDAR_CREATE_EVENT |
| Slack (optional) | Communication channel | SLACK_SEND_MESSAGE, SLACK_LIST_CHANNELS |
| HubSpot (Operator) | CRM integration | HUBSPOT_LIST_DEALS, HUBSPOT_CREATE_CONTACT |
| Notion (optional) | Notes/project tracking | NOTION_CREATE_PAGE, NOTION_SEARCH |

---

## The Core Skills to Build

### 1. email-triage/SKILL.md
**Trigger:** Cron (6am daily) + on-demand
**Flow:**
1. Call Composio GMAIL_FETCH_EMAILS for unread inbox
2. For each email, classify: `urgent` / `needs_response` / `fyi` / `ignore`
3. Draft responses for urgent + needs_response
4. Archive fyi + ignore via GMAIL_MODIFY_MESSAGE
5. Store triage results in memory
6. Compose summary for daily briefing

### 2. daily-briefing/SKILL.md
**Trigger:** Cron (client's preferred morning time)
**Flow:**
1. Pull today's calendar via Composio GOOGLECALENDAR_LIST_EVENTS
2. Pull email triage summary from memory
3. Pull pending follow-ups from memory
4. Check for overdue items
5. Generate briefing via Claude
6. Deliver via client's channel (OpenClaw routes automatically)

### 3. calendar-ops/SKILL.md
**Trigger:** On-demand + part of briefing
**Flow:**
1. Fetch events for today/this week
2. Detect conflicts (overlapping times)
3. Check for missing buffer time between meetings
4. Suggest resolutions
5. Create/modify events via Composio on client approval

### 4. follow-up-tracker/SKILL.md
**Trigger:** After email triage + on-demand
**Flow:**
1. After each email/meeting interaction, extract commitments ("I'll send X by Friday")
2. Store in memory with: description, due date, source (email/meeting), status
3. Query overdue/upcoming for briefings
4. Client can ask "what's overdue?" or "what did I promise Sam?"

### 5. research/SKILL.md
**Trigger:** On-demand
**Flow:**
1. Client asks a question via chat
2. Use web search (Brave API) + any relevant Composio tools
3. Synthesize answer with sources
4. Deliver via same channel

---

## Client Onboarding Flow

1. **Discovery call** — Learn workflow, tools, preferences, priorities
2. **Create agent:**
   - Copy workspace template to `/root/.openclaw/clients/<name>/`
   - Customize SOUL.md, USER.md, AGENTS.md
   - Add agent to openclaw.json agents.list
   - Add binding (route their channel DMs to their agent)
3. **Composio Connect Links** — Client clicks links to auth Gmail, Calendar, Slack
4. **Configure triage rules** — VIP contacts, ignore patterns, urgency keywords
5. **Enable cron jobs** — Email triage schedule, briefing time
6. **Test run** — Do a full triage + briefing cycle, review with client
7. **Hypercare (14 days)** — Daily monitoring, tuning triage accuracy, adjusting personality
8. **Ongoing care** — Monthly check-ins, skill improvements, adding modules

---

## Cost Per Client

| Item | Monthly Cost |
|------|-------------|
| OpenClaw (self-hosted, open source) | $0 |
| Server share (Hetzner) | ~$5-15 |
| Composio (20K free calls/mo total) | $0 at small scale |
| Claude Code CLI (Pro/Max plan per client) | ~$20-200 |
| AgentMail (optional AI email) | ~$5-10 |
| **Total cost** | **~$30-105/client/mo** |
| **Revenue** | **$1,500-5,500/client/mo** |
| **Margin** | **93%+** |

---

## Build Order

### Phase 1: Core (Weeks 1-2)
1. Create the workspace template (AGENTS.md, SOUL.md, USER.md, TOOLS.md)
2. Write the 5 core skills (email-triage, daily-briefing, calendar-ops, follow-up-tracker, research)
3. Set up Composio Gmail + Calendar integration with Ben as test user
4. Add Ben as a test client agent in openclaw.json
5. Test the full loop: email triage → briefing → on-demand interaction
6. Dogfood for 1-2 weeks

### Phase 2: Polish (Weeks 3-4)
1. Onboarding script (automate agent creation + Composio auth)
2. Operator Module skill (HubSpot/CRM via Composio)
3. Household CEO skill (family calendar management)
4. Tune triage accuracy from dogfood feedback

### Phase 3: Scale (Weeks 5+)
1. Finance + Creator module skills
2. WhatsApp channel setup (most clients will prefer this)
3. Client onboarding portal (optional web UI)
4. Multi-server if client count demands it
5. Case studies from Ben + Drew's usage
