# Obsidian Setup Guide

## What This Is
Your knowledge base (`memory/`, `context/`, daily logs, research, strategy docs) is now structured as an Obsidian vault. This gives you a visual interface to browse, search, and see connections between everything Cortana has built.

## Mac Setup (10 minutes)

### 1. Install Obsidian
- Download from https://obsidian.md (free)
- Install it

### 2. Clone the vault to your Mac
Open Terminal and run:
```bash
git clone root@your-server-ip:/root/.openclaw/workspace ~/obsidian-cortana
```

Or if you prefer SSH key auth:
```bash
git clone ssh://root@your-server-ip/root/.openclaw/workspace ~/obsidian-cortana
```

### 3. Open as vault
- Open Obsidian
- Click "Open folder as vault"
- Select `~/obsidian-cortana`
- The vault opens with your memory index

### 4. Install recommended plugins
Go to Settings > Community Plugins > Browse:
- **Obsidian Git** - Auto-sync with server every 5-10 minutes
- **Dataview** - Query your notes like a database
- **Calendar** - Visual daily note navigation

### 5. Configure Obsidian Git
Settings > Obsidian Git:
- Auto pull interval: 5 minutes
- Auto push interval: 10 minutes
- Pull on startup: ON

This keeps your local vault synced with what Cortana writes on the server.

## Phone Setup (5 minutes)

### 1. Install Obsidian Mobile
- iOS: App Store > "Obsidian"
- Android: Play Store > "Obsidian"

### 2. Sync options (pick one)
**Option A: iCloud (easiest for iPhone)**
- Move your vault folder to iCloud Drive
- Obsidian Mobile auto-syncs via iCloud

**Option B: Obsidian Sync ($4/mo)**
- Built-in, works perfectly, end-to-end encrypted
- Settings > Sync > Set up

**Option C: Syncthing (free, nerdier)**
- Install Syncthing on Mac + phone
- Sync the vault folder
- Works great, just more setup

### 3. Mobile brain dump workflow
- Open Obsidian on phone
- Navigate to `memory/inbox/`
- Create a new note, dump your thought
- It syncs to the server
- Cortana picks it up next session and files it properly

## What You'll See

### Graph View (the killer feature)
- Press Cmd+G (Mac) or tap the graph icon (mobile)
- Every note is a node, every `[[wikilink]]` is an edge
- Strategy docs cluster together, research clusters together
- Orphan notes (unconnected) stand out visually

### Key folders
- `memory/` - Daily logs, research, strategy, drafts
- `memory/content-drafts/` - All content pieces
- `memory/inbox/` - Your brain dump landing zone
- `context/` - Domain knowledge Cortana loads on demand

### Search
- Cmd+O: Quick file open
- Cmd+Shift+F: Full-text search across all files
- Click any `[[wikilink]]` to jump to that note

## What Cortana Does Differently Now
- All new notes include `[[wikilinks]]` to related files
- Daily logs link to relevant strategy/research docs
- Index stays updated with proper links
- Inbox gets processed and filed each session

## Related
- [[index]] - Full memory index
- [[context-engine-design]] - How Cortana loads context
