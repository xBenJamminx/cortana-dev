# FAM Smart Companion POC — Open Issues (2026-03-24)

**Sources:** Fathom (10 meetings, Mar 16-24) | Slack (#meeting-notes, #testing, #poc) | Notion (96 open items)

---

## 🔴 CRITICAL — Demo Blockers

| # | Issue | Owner | Status |
|---|-------|-------|--------|
| 1 | **System prompt leaking** — Bot reads voice instructions aloud to users | Steven | Reported Mar 24 |
| 2 | **Core features regressed after multi-avatar update** — Calendar, email/text, avatar interactions all broken | Steven/Bilal | Acknowledged Mar 24 |
| 3 | **WebSocket disconnects mid-conversation** — Recurring since Jan 6, "fixed" multiple times, keeps coming back | Bilal | In Testing |
| 4 | **"Hmm let me think" dead-end** — Sub-agent triggers but nothing happens unless user speaks again | Steven | Reported Mar 24 |
| 5 | **Calendar event editing broken** — Adding works, deleting/recreating does not | Steven | Reported Mar 24 |
| 6 | **Google Calendar 403 errors** — Insufficient OAuth scopes | Steven | In Progress |
| 7 | **Bot doesn't know user's connected email** — Can't send emails | Steven | Reported Mar 24 |
| 8 | **Memory retrieval bug** — Missing user data during retrieval | Steven | In Testing |
| 9 | **Memory persistence broken** — Previous session data not saved | Steven | In Testing |
| 10 | **Hallucination + self-repeating responses** | Steven | In Testing |
| 11 | **Dynamic filler responses failing** — Hard-coded/static instead of dynamic during sub-agent processing | Steven | In Testing |

## 🟠 HIGH — Functionality Broken

| # | Issue | Owner | Status |
|---|-------|-------|--------|
| 12 | **Build 32+ instability** — Choppy, scene keeps resetting (v25 stable baseline) | Bilal | In Progress |
| 13 | **Frontend/backend version misalignment** — Staging vs prod URLs causing inconsistent behavior | Bilal/Steven | Unresolved |
| 14 | **Respawn goes to character selection instead of respawning in place** | Bilal | Reported Mar 24 |
| 15 | **AR mode mutes bot audio** | Bilal | Reported Mar 24 |
| 16 | **Cannot tap/move character position** | Bilal | Reported Mar 24 |
| 17 | **Cannot zoom in/out** | Bilal | In Progress |
| 18 | **Cannot dismiss restaurant/shop suggestion popups** | Bilal | Reported Mar 24 |
| 19 | **Text display bugs (v26 regression)** | Bilal | Not Started |
| 20 | **Voice input bugs (v26 regression)** | Steven | Not Started |
| 21 | **Female avatar issues** — ground detection, animation transitions, proportions | Bilal | In Testing |
| 22 | **Floating avatar / ground plane issue** | Bilal | In Testing |
| 23 | **iOS audio playback choppy (Build 33)** | Bilal | In Testing |
| 24 | **iOS WebSocket timeout (Build 33)** | Bilal | In Testing |
| 25 | **Computer vision hallucinations** — OpenAI detects nonexistent objects, Gemini/Astra migration status unclear | Steven | In Testing |
| 26 | **`manage_user_goals_tool` not registered** in evi_tool_registry.py | Steven | Unresolved |
| 27 | **`close_ui_tool` has no domain assignment** | Steven | Unresolved |
| 28 | **Background noise / interruption handling** — AI picks up noise, interrupts itself | Steven | Recurring |
| 29 | **Vibe description colors reverted to grey** | Bilal | Reported Mar 24 |
| 30 | **Moca + Woman character name styling inconsistent** | Bilal | Reported Mar 24 |
| 31 | **Location suggestions first item shows no data** | Steven/Bilal | In Progress |
| 32 | **Proactivity trigger hiccup/repeat issue** | Steven | In Testing |
| 33 | **particle_ink avatar + any persona not triggering WebSocket** | Steven | In Testing |
| 34 | **Female voice playing for Johnny Ape + Bestie combo** | Steven | In Testing |
| 35 | **Time-of-day/location accuracy bug — wrong timezone** | Steven | In Testing |
| 36 | **Business search voice output — Yelp results spoken aloud raw** | Steven | In Progress |
| 37 | **Ape avatar texture/material/outfit rendering issues** | Bilal | In Testing |
| 38 | **Foot sinking / lower-body animation** | Bilal | In Testing |
| 39 | **Business card UI issues** — cards disappear, off-screen, squished, Mapbox issues | Bilal | In Testing |
| 40 | **Animation NullRef — LightningController spamming errors** | Bilal | In Testing |
| 41 | **Lightling and Moca UI noise/glitches in v27** | Bilal | In Testing |
| 42 | **Multiple avatars spawning in 3D scene** | Bilal | In Testing |
| 43 | **AR / 3D UI toggle behavior reversed** | Bilal | In Progress |

## 🟡 ARCHITECTURE / SCALE BLOCKERS

| # | Issue | Owner | Status |
|---|-------|-------|--------|
| 44 | **Single-tenant architecture** — Multi-tenant requires DB schema + auth refactoring. Blocks Animoca Minds at scale | Steven | Not Started |
| 45 | **Architecture not scalable** — 4 avatars already exposing need for modular design | Cassandra flagged | Discussion |
| 46 | **No integration framework** — Finance, health, social, email features all blocked by missing integrations | Steven/Bilal | Not Started |

## 🟡 PROCESS ISSUES

| # | Issue | Owner | Status |
|---|-------|-------|--------|
| 47 | **No adequate testing of core use cases before shipping advanced features** | All | Acknowledged Mar 24 |
| 48 | **Proactivity feature status unknown** — Nobody can confirm what's implemented vs. planned | Tram | Action item Mar 19 |
| 49 | **Builds shipped without notes** — Discussed multiple times, not enforced | Bilal | Recurring |

## 📋 KEY FEATURES — In Progress / Not Started

| # | Feature | Owner | Status |
|---|---------|-------|--------|
| 50 | Redesign sub-agent architecture into specialized domain agents | Steven | In Testing |
| 51 | Proactive suggestions based on user context | Steven/Bilal | In Testing |
| 52 | Rituals feature for proactive daily check-ins | Steven | In Testing |
| 53 | Memory system upgrade — semantic dedup, write gate, scoring | Steven | In Testing |
| 54 | Parallel dispatch — proactive multi-tool runs | Steven | In Testing |
| 55 | Context engine | Steven | In Progress |
| 56 | Upgrade computer vision to Gemini/Astra | Steven | In Testing |
| 57 | SALSA real-time lip-sync for Ape, Girl, Moca | Bilal | In Testing |
| 58 | Turn-by-turn directions UI (Mapbox) | Bilal | In Testing |
| 59 | Emotion detection + animation mapping | Steven/Bilal | In Progress |
| 60 | Voice-selection system for non-NFT avatars | Steven | Not Started |
| 61 | Voice assignment for NFT avatars | Steven | Not Started |
| 62 | Integrate two small open-source models (Llama via Groq) | Steven | Not Started |
| 63 | Auto-spawn avatar on app launch | Bilal | In Testing |
| 64 | Loading recovery: auto-restart if loading >10s | Bilal | In Testing |
| 65 | Portrait-friendly character selection screen | Bilal | In Testing |
| 66 | Joel wireframe alignment for avatar + personality UI | Cassandra | In Progress |

## 📋 PENDING ACTION ITEMS

- **Steven:** Regroup team, fix core bugs, deliver testable build
- **Bilal:** WebSocket fix, avatar UI consistency, animation fixes (out Mon/Tue for Eid)
- **Tram:** Update proactivity feature status in shared document
- **Cassandra:** Block testing time, North Star document, CryptoSlam/Ethoswarm tech call, Joel wireframes
- **Ben:** Continue testing, update QA sheet, Animoca Minds brief

## WORKLOAD

- **Bilal:** ~50 open items (frontend/avatar/AR) — overloaded
- **Steven:** ~35 open items (backend/AI/memory/voice) — overloaded
- **Tram:** 1 item (QA testing) — underutilized
- **Cassandra:** 4 items (strategy/coordination)
- **Ben:** ~10 items (QA, docs, design decisions)
