# CLAWDBOT WORKSPACE OS - BUILD PROMPT

**Overview:**
Build a unified web dashboard that serves as the central operating system for an AI-powered content and development workflow. This integrates content pipelines, file management, AI model routing, and task tracking into one interface.

## Tech Stack
- Backend: FastAPI (Python)
- Database: SQLite (local, simple)
- Frontend: React or simple HTML/JS (your choice)
- Real-time: WebSockets or Server-Sent Events for live updates
- Single container deployment (Docker-ready)

## Core Modules

### 1. DASHBOARD HOME
- Quick stats: active projects, pending tasks, today's API costs, scheduled posts
- Recent activity feed (files created, posts published, tasks completed)
- Quick action buttons: "New Post", "Generate Image", "Run Router", "Search"

### 2. FILE MANAGER
- Tree view of /root/clawd/ with real-time file watching
- File types: code (.py, .js), docs (.md), images (.png, .jpg), configs (.json)
- Preview pane: code syntax highlighting, markdown rendering, image thumbnails
- Tags system: auto-tag by type, manual tags, filter by tags
- Full-text search across file names and content
- File actions: edit (in-browser), delete, duplicate, open in external editor

### 3. PROJECT TRACKER (Kanban)
- Boards: Ideas → In Progress → Review → Done
- Cards link to files, URLs, or Airtable records
- Drag-and-drop status changes
- Due dates, priorities, assignees (for multi-user future)

### 4. CONTENT PIPELINE
- Integrate with Airtable API (table: Content Pipeline)
- Columns: Status, Platform (Twitter/LinkedIn/YouTube), Content, Scheduled Date, Posted URL
- Visual flow: 💡 Idea → 📝 Draft → 👀 Review → ✅ Approved → 📤 Posted
- Quick actions: "Create Draft", "Schedule", "Mark Posted"
- Calendar view of scheduled content

### 5. AI COMMAND CENTER
- Model Router Panel: see current routing rules, test a prompt, view routing decision
- Image Generator: input prompt, select complexity (simple/standard/complex), generate, save to library
- Cost Tracker: live API spend by model (Gemini, OpenAI, Anthropic), daily/weekly/monthly charts, alerts
- Usage Logs: recent AI calls, what was routed where, costs

### 6. BROWSER AUTOMATION
- Active sessions list (headless Chromium via Playwright)
- Screenshot capture of any URL
- Twitter posting interface (compose, attach image, post)
- Session logs: what was posted, when, success/fail

### 7. MEMORY & KNOWLEDGE
- Searchable index of /root/clawd/memory/ files
- Full-text search across all past conversations/work
- Quick capture: "Add to Memory" button anywhere in the UI

### 8. SETTINGS
- API keys management (encrypted storage)
- Model pricing configuration (editable table)
- Routing rules editor (keyword lists, thresholds)
- Airtable connection settings
- Backup/export data

## Integration Points

### Existing Code to Integrate:
- /root/clawd/model_router.py - intelligent model routing
- /root/clawd/image_router.py - image generation routing
- /root/clawd/social_posts/ - generated images and post copy
- /root/clawd/memory/ - daily notes and context
- Airtable base (Content Pipeline table)

## Key Requirements

1. **Real-time updates** - when I create a file in /root/clawd/, it appears in the UI immediately
2. **Responsive design** - works on desktop and tablet
3. **Dark mode** - default dark theme, easy on the eyes
4. **Keyboard shortcuts** - power user friendly
5. **Self-contained** - single command to start (docker-compose up or python main.py)

## File Structure

```
/workspace-os/
├── backend/
│   ├── main.py (FastAPI app)
│   ├── routers/
│   │   ├── files.py (file manager API)
│   │   ├── projects.py (kanban API)
│   │   ├── content.py (Airtable integration)
│   │   ├── ai.py (model routing API)
│   │   ├── browser.py (automation API)
│   │   └── memory.py (search/indexing)
│   ├── services/
│   │   ├── file_watcher.py (watch /root/clawd/)
│   │   ├── airtable_sync.py (sync with Airtable)
│   │   ├── cost_tracker.py (track API spend)
│   │   └── indexer.py (index files for search)
│   └── database.py (SQLite models)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
├── static/
│   └── uploads/ (user-uploaded/generated files)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Deliverables

1. Working application I can run with `docker-compose up`
2. README with setup instructions
3. Configuration file for API keys (template)
4. Basic tests for critical paths

## Success Criteria

- I can create a file in /root/clawd/ and see it in the UI within 5 seconds
- I can search for "model router" and find the relevant files and memory notes
- I can schedule a tweet and see it in the content pipeline
- I can generate an image and it saves to /root/clawd/ and appears in file manager
- I can track API costs in real-time as AI calls are made

## Maintainability Notes for Future Developer

- All paths should be configurable (don't hardcode /root/clawd/)
- Log everything to SQLite for debugging
- Use environment variables for secrets
- Keep frontend and backend loosely coupled

## Build Order (Priority)

1. Backend + File Manager (foundational)
2. Dashboard + Search (immediate utility)
3. Content Pipeline (Airtable integration)
4. AI Command Center (model routing UI)
5. Browser Automation (nice-to-have)
6. Polish: dark mode, keyboard shortcuts, responsive

Start simple, get core features working, then add polish. Focus on utility over beauty - this is a tool, not a portfolio piece.
