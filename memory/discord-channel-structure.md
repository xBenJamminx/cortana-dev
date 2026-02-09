# BuildsByBen Discord Server Structure

Last updated: 2026-02-07

---

## Roles (Managed by Whop)

| Role | Color | Source | Access Level |
|------|-------|--------|-------------|
| @Admin | Red | Manual | Everything |
| @Founding-Member | Gold | Whop ($29/mo, 50 spots) | Core + Founders-only |
| @Standard-Member | Blue | Whop ($49/mo) | Core + Premium |
| @Free | Gray | Whop ($0) | Limited |
| @everyone | Default | Discord | Public channels only |

---

## Channel Structure

### PUBLIC (visible to everyone, including non-members)

**WELCOME**
- `#welcome` (read-only) -- Server rules, what this place is, how to get access
- `#how-to-join` (read-only) -- Step-by-step: buy on Whop, click Claim Access, get your role
- `#announcements` (read-only) -- Major updates, new content drops, events

### FREE TIER (visible to @Free + all paid members)

**COMMUNITY**
- `#introductions` -- New member intros. Name, what you do, what you want to learn.
- `#general-chat` -- Open conversation. AI, business, life. Low stakes.
- `#share-your-wins` -- Ship something? Land a client? Automate a task? Post it here.

### PAID TIER (visible to @Founding-Member + @Standard-Member)

**LEARN AI**
- `#prompt-engineering` -- Share prompts, ask for help, post results
- `#tool-talk` -- Discuss AI tools, compare options, share discoveries
- `#tutorials-and-guides` -- Written walkthroughs and how-tos (Ben + community)
- `#show-and-tell` -- Show what you built or automated. Screenshots encouraged.

**BUILD STUFF**
- `#side-projects` -- Working on something? Get feedback, accountability, ideas.
- `#automation-help` -- n8n, Make, Zapier, workflows. Ask questions, share solutions.
- `#business-ops` -- Using AI for business? Client work, proposals, processes. Talk here.

**RESOURCES**
- `#tool-deals` -- Discounts, free tiers, limited offers. Vetted by Ben, not spam.
- `#content-drops` (read-only) -- New prompt packs, tutorials, and guides as they ship.
- `#links-and-bookmarks` -- Useful articles, videos, threads. Community-curated.

### FOUNDERS ONLY (visible to @Founding-Member only)

- `#founders-lounge` -- Smaller room. Direct access to Ben. Early previews. Candid conversation.
- `#founders-feedback` -- Shape what gets built next. Your input directly influences the roadmap.

### STANDARD + FOUNDERS (visible to @Standard-Member + @Founding-Member)

- `#live-session-replays` -- Recordings from monthly AMAs and live builds
- `#advanced-resources` -- Deeper content: multi-step workflows, complex automations, technical builds
- `#ask-ben` -- Direct Q&A channel. Ben answers within 24 hours on weekdays.

### ADMIN (visible to @Admin only)

- `#admin-log` -- Bot activity, member joins/leaves, moderation actions
- `#content-planning` -- What to build next, content calendar, ideas

---

## Bot Setup

### Required Bots
1. **Whop Bot** -- Role assignment on purchase. Must be highest role in hierarchy.
2. **MEE6 or Carl-bot** -- Welcome messages, auto-moderation, reaction roles (optional)

### Whop Bot Configuration
- Founding Member product -> assigns @Founding-Member role
- Standard Member product -> assigns @Standard-Member role
- Free product -> assigns @Free role
- On cancellation: "Remove given roles" (keeps them in server, removes channel access)

---

## Channel Count: 20 total

- 3 public
- 3 free tier
- 9 paid tier (shared)
- 2 founders only
- 3 standard + founders
- 2 admin

Lean on purpose. Easy to add channels later. Painful to remove them once people are using them.

---

## Onboarding Flow

1. User finds BuildsByBen (X, YouTube, landing page)
2. Goes to Whop storefront, picks a tier
3. Purchases on Whop
4. Whop shows "Claim Access" button for Discord
5. User clicks it, authorizes Whop Bot, gets role assigned
6. Lands in #welcome which tells them to post in #introductions
7. Ben (or Cortana) sends a DM welcoming them and pointing to key channels

### Common friction point
Users forget to click "Claim Access." Mitigation:
- Post-purchase page on Whop prominently says "Click the button below to join Discord"
- Welcome email includes direct Discord link + instructions
- #how-to-join channel visible to everyone explains the process with screenshots
