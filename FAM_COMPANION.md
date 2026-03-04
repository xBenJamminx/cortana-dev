# FAM Smart Companion - Project Context

Last updated: 2026-03-03

## What It Is
AI avatar companion app — 3D animated character that has real-time voice/text conversations. Think AI companion with personality, memory, goals, and tool integrations. Currently POC stage, transitioning to alpha with hundreds of Animoca internal testers.

## The Team
| Name | Role | Handle |
|------|------|--------|
| Ben (me) | PM/TPM + personality/soul system | @xBenJamminx |
| Steven (Cao Tan Luc) | Backend engineer | - |
| Bilal (Muhammad Bilal Akram) | Frontend/Unity engineer | - |
| Cass (Cassandra Rosenthal) | Business/strategy | - |

## Key Partners
- **Animoca Minds** - Main alpha launch target (internal testers)
- **CryptoSlam / Ethoswarm** - Technical integration target
- Mo + Animoca PM - Business alignment contacts

## Codebase
- **Frontend (Unity + React)**: `C:\Projects\Smart-Companion-POC`
  - Main POC: Unity 2022.3.44f1, AR mobile (iOS/Android)
  - FAMBOT variant: Unity 6 + Next.js/React → WebGL Telegram Mini App
  - 3 avatar characters: Particle Ink char (glasses, no eyes), female char, Bored Ape (BAYC)
  - Animation system: 24 JSON configs for semantic emotion→animation mapping
  - TTS: ElevenLabs WebSocket streaming
  - Auth: Firebase (POC) / Telegram WebApp (FAMBOT)

- **Backend (Python)**: `C:\Projects\smart.companion.agent.poc-1`
  - FastAPI + LangGraph (state machine agent)
  - PostgreSQL + pgvector (memory embeddings)
  - Redis (cache + pub/sub)
  - Celery (background tasks)
  - Voice: Hume EVI (voice + emotion) + ElevenLabs TTS + Deepgram STT
  - 10 personality personas: Bestie, Sage, Coach, Pro, Jester, Empath, Analyst, Rebel, Poet, Chill
  - 25+ tools: calendar, tasks, weather, Yelp, fitness (Strava/Oura), crypto, maps
  - Latency optimized: 8-12s response (was 22-30s)

## Current Status (as of March 3, 2026)
### Recently completed (Build 5 / staging):
- Avatar selection API complete (Steven) - avatar_id, name, personality prompt all wired
- Avatar-level personality differentiation working (selecting avatar changes voice/sound/personality)
- Persistent memory + proactivity re-enabled across sessions
- Hume sentiment analysis live in DB
- Model routing decided: GPT-4o Mini for tool calling, GPT-5.1 Nano for conversation
- Mapbox integration done (Bilal)
- Sub-agent/background execution layer 90% done

### In progress:
- Build 5 upload (Bilal) - avatar selection + staging backend + release notes
- MOCA character integration (new 3rd character)
- AR-52 blendshapes / viseme pipeline for lip sync SDK
- Rituals feature (proactive daily check-ins)
- QA test sheet alignment with Notion tasks

### Ben's open tasks:
- Send correct Ape textures to Bilal
- Provide personality presets for 3 characters to Steven
- Notion/QA alignment (deep work block this afternoon)
- Prioritize features for Bilal + Steven (parallel frontend/backend)
- Compile proactivity behavior examples for Steven
- Fill QA test cases in Google Sheet
- Review Silas's in-session controls → settings list for Joel
- Animate wireframes: avatar + personality selection UI (Joel to design)

## Notion Task Database
- URL: https://www.notion.so/26c4666bd1ca807b930dca5ffff9c8e9
- Bot token: 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
- As of Mar 2: ~198 tasks total (171 after first sync + 27 from Mar 2 meetings), all linked to FAM POC project
- Statuses: Done, In Progress, Not Started, In Testing (new)
- Assignees in Notion: Cao Tan Luc, Muhammad Bilal Akram, Ben Jammin, Cassandra Rosenthal

## Architecture Decisions (key)
- **LLM routing**: 4o Mini for tools (reliability), 5.1 Nano for chat (speed)
- **Sub-agent pattern**: Background tasks delegated async, main agent stays responsive
- **Personality = "soul" system**: Each avatar has its own identity/voice/prompt
- **Model-agnostic**: Building routing layer to pick best LLM per task type
- **Edge AI consideration**: Cass flagged for data safety vs cloud (unresolved)
- **White-label / portable**: Positioning as application layer that can run on top of any company's platform

## Key Context for Ben's Work
- Ben owns personality presets (from OpenClaw system) → feeds to Steven for implementation
- Telegram mini-app prototype is separate track (FAMBOT) for Animoca testing
- Build testing device: Samsung Galaxy S10 (Android)
- Lip sync SDK + WebAR SDK: Bilal to send links → Cass to purchase ($13 lip sync)
