# Twitter/X Bookmark Tools -- Competitive Analysis
**Date:** 2026-02-06

---

## 1. TWILLOT (twillot.com)

### Overview
Open-source Twitter/X data management tool. Originally a bookmark search extension, evolved into a full Twitter data platform covering bookmarks, likes, tweets, followers, and anonymous browsing. GitHub repo was **archived July 31, 2025** but the product/website remains active with a new closed-source extension.

### Chrome Web Store
- **Extension Name:** "Twillot - Your Twitter, Organized"
- **Rating:** 4.7/5 stars
- **Also has:** "Twitter Bookmarks Search by Twillot" (older, simpler extension)
- **A third extension** ("Twillot Automation") had only 48 users before being removed from CWS on 2025-03-11

### GitHub Repo (twillot-app/twillot) -- ARCHIVED
- **Stars:** 126
- **Forks:** 11
- **Total Commits:** 726
- **Contributors:** 2 (essentially a solo dev project)
- **Tech Stack:** TypeScript (85.9%), Solid.js, Flowbite UI, pnpm monorepo, Vitest
- **License:** Not specified
- **Last commit:** Nov 30, 2024 (bug fix for media export)
- **Archived:** July 31, 2025
- **Monorepo packages:** x-bookmarks (main), x-bookmarks-automation, exporter, multi-publish, utilities
- **References twitter-web-exporter** as inspiration -- implies scraping/intercepting approach

### How They Access Twitter Data
- **NOT official API.** References to "Twitter API changes causing verification failures" suggest they intercept Twitter's internal GraphQL API calls via the browser extension (same cookies-based approach most extensions use).
- Data is "indexed and searched locally" -- they build a local index from scraped data.
- Cloud used only for sync/backup.

### Pricing Tiers (Current)

| Feature | Free ($0) | Mini ($3.99/mo) | Basic ($7.99/mo) | Pro ($13.99/mo) |
|---|---|---|---|---|
| Cloud Storage | 100GB | 500GB | 1,000GB | 2,000GB |
| Bookmarks/Likes/Tweets | 1,000 | 10,000 | 100,000+ | 500,000+ |
| Following/Followers/Blocked | 1,000 | 5,000 | 50,000 | 100,000+ |
| Daily Public Tweet Downloads | 1,000 | 20,000 | 200,000+ | 500,000+ |
| Twitter Viewer Quota | -- | 1,000/day | 5,000/day | 10,000/day |
| AI Concurrency | 1 | 5 | 5 | 10 |
| Batch Op Size | 50 | 200 | 500 | 500 |
| Cloud Backup | No | Yes | Yes | Yes |
| MD/PDF Export | No | Yes | Yes | Yes |
| Batch Media Download | No | Yes | Yes | Yes |
| Archive Import | No | Yes | Yes | Yes |
| Yearly discount | -- | 20% off | 20% off | 30% off |

**Yearly prices:** Mini $47.90/yr, Basic $95.90/yr, Pro $167.90/yr (with discounts)

### What They Do Well
- Extremely feature-rich -- goes far beyond bookmarks into full Twitter data management
- AI-powered auto-categorization by topic, sentiment, context
- Local-first search (blazing fast, milliseconds)
- Waterfall/gallery media browsing
- Multi-format export (PDF, CSV, MD, JSON, Google Drive)
- Anonymous Twitter viewer (browse without an account)
- Block list management
- Free tier is genuinely useful

### Where They Fall Short
- **GitHub repo archived** -- open-source version is dead. New version is closed-source.
- Stability issues: lags, login failures, pages not loading
- Payment/upgrade glitches reported
- Reports of accounts being frozen after exporting large bookmark sets
- Solo dev project (2 contributors) -- bus factor risk
- Feature bloat: trying to be everything (viewer, bookmark manager, analytics, block manager, media downloader)
- "Workflow" feature was removed due to "product strategy changes"

### User Sentiment
Mostly positive. Users call it "the most practical X/Twitter bookmark management tool." Power users love the local search speed and bulk export. Complaints cluster around stability bugs and occasional Twitter API breakage.

### Growth Trajectory
**Uncertain.** The open-source repo being archived is a yellow flag. The product is still active and the website shows a waitlist for new features, suggesting a pivot to a more commercial, closed-source model. Active development appears to continue on the closed-source side.

---

## 2. TWEETSMASH (tweetsmash.com)

### Overview
Bookmark-to-knowledge-digest tool. Won 1st prize in Twitter's Chirp developer challenge (2022). Differentiator is turning bookmarks into scheduled email digests and auto-syncing to Notion. More of a "consumption" tool than a "management" tool.

### Chrome Web Store
- **Extension Name:** "TweetsMash"
- **Rating:** 3/5 stars (conflicting reports -- some sources say 5/5 but on very few reviews)
- **Users:** ~4,000
- **Approach:** Installs as extension, syncs bookmarks periodically

### Pricing

| Plan | Cost | Type |
|---|---|---|
| Reader Pass | $14/month | Subscription |
| Premium/Yearly | $99/year (~$8.25/mo) | Subscription |
| Exports Only | $49 one-time | One-time |
| Believer Pass (Lifetime) | $198 one-time | Lifetime |

**7-day free trial** available on subscription plans.

### Lifetime Deal (via Lifetimo)
- **Export Only:** $29.99 (regular $49)
- **Believer Pass:** $119 with code SPECIAL40 (regular $198) -- 40% off auto-applied
- Deal page shows 5/5 rating based on 1 review (statistically meaningless)

### Notion Integration (Key Differentiator)
- **Auto-sync:** Bookmarks auto-export to Notion the moment you bookmark on Twitter
- **Rich data:** Threads are fully unrolled, media included, replies grouped by conversation
- **Tags preserved:** Custom tags carry over to Notion
- **Filtering:** Control what goes to Notion with tags and filters
- **Multi-database:** Can organize exports across multiple Notion databases or Google Sheets
- Also integrates with: Google Sheets, Zotero (research papers)

### Full Feature Set
- AI chat with bookmarks (Cmd+K)
- Daily/weekly email digests with adjustable read time (5 min to 2 hours)
- "Recipe" system: customizable filters for topic-based digests
- Thread reader with conversation grouping
- Smart folders (auto-sort: "most viral," by author, by topic)
- Unlimited labels
- Full-text search
- Mobile PWA
- PDF export of search results
- Newsletter creation from bookmarks

### What They Do Well
- **Notion integration is genuinely strong** -- auto-sync, thread unrolling, grouped replies, filtered exports
- Digest/email system is unique -- no other tool does scheduled bookmark digests
- Recipe system for automated organization is clever
- Clean product vision: bookmarks as a knowledge base, not just storage
- Won Twitter's own developer challenge -- legitimacy signal
- Zotero integration appeals to researchers/academics

### Where They Fall Short
- **Not an official X/Twitter partner** -- relies on unofficial access
- Chrome extension rating is mediocre (3/5)
- Small user base (~4,000 installs)
- $14/month is steep for a bookmark tool
- Limited to consumption/export -- no media downloading, no analytics, no anonymous viewing
- No block management, no tweet deletion, no follower management
- Mobile experience is PWA only (not native)
- The "Exports Only" plan at $49 feels expensive for a one-time export

### User Sentiment
Mixed. Users who want Notion integration love it. The digest feature has a loyal niche. But the rating suggests reliability or UX issues that turn some users off. The small user base means limited community and feedback loop.

### Growth Trajectory
**Slow but alive.** The Lifetimo deal suggests they're trying to generate cash flow. 4,000 users after years in market is modest. The Chirp contest win gave early credibility but hasn't translated into explosive growth. Product is actively maintained.

---

## 3. XBASE (xbase.so / getxbase.com)

### Overview
Speed-focused bookmark manager. Differentiator is local-first storage and sub-100ms search. Built with SvelteKit. Targets power users with large bookmark collections.

### Chrome Web Store
- **Extension Name:** "xbase -- The ultimate bookmark manager for X"
- **Rating:** 3.7-4.3/5 stars (varies by listing)
- **Ratings count:** ~6 ratings
- **Very small user base**

### Pricing
- **Free tier:** Basic plan with 30-day free trial
- **Pro Plan:** Exact price not publicly listed; promotional code EARLY33 gives 33% off for life
- **Early adopter deal:** First 200 users get 50% lifetime discount
- **90-day money-back guarantee**
- Positioning: "affordable because data is stored locally" (lower server costs)

### Key Features
- Instant search (<100ms) via local storage
- Tags and note-taking on individual tweets
- Keyboard shortcuts for fast navigation
- Sort by: threads, links, videos, images
- Thread/tweetstorm summarization
- JSON export
- Data stored locally (privacy-first)
- Bookmarks accessible even if original tweets are deleted

### What They Do Well
- Fastest search in the category (local-first architecture)
- Note-taking on tweets is unique
- Keyboard-driven UX appeals to power users
- Privacy-focused (no server-side data)
- Deleted tweet preservation

### Where They Fall Short
- Tiny user base (single-digit reviews)
- Limited export formats (JSON only)
- No AI categorization
- No Notion/Sheets integration
- No email digests
- No media downloading
- Weak multi-language support (Chinese specifically called out)
- No mobile experience
- Two domains (xbase.so and getxbase.com) creates confusion
- Opaque pricing

### User Sentiment
Small but positive niche. Users who find it praise the speed and UI. Not enough users to establish broad sentiment.

### Growth Trajectory
**Early stage, uncertain.** The "first 200 early adopters" messaging suggests they're still trying to find product-market fit. Very small user base. Active development unclear.

---

## 4. xBOOKMARKS (x-bookmarks.com)

### Overview
Export-focused tool. Not a full bookmark manager -- primarily lets you export Twitter bookmarks as markdown files with images in organized folders.

### Chrome Web Store
- **Extension Name:** "xBookmarks"
- **Extension ID:** efjimcfcnnoahhdcjipfhgpakjiaefhi

### Pricing (Points-Based)
| Pack | Cost | Points | Tweets Exportable | Cost/Tweet |
|---|---|---|---|---|
| Regular Small | $5 | 15,000 | ~1,500 | ~0.33 cents |
| Regular Medium | $15 | 50,000 | ~5,000 | ~0.30 cents |
| Value Pack | $50 | 200,000 | ~20,000 | ~0.25 cents |

Each tweet costs 10 points to export.

### Key Features
- Export bookmarks as markdown files in ZIP format
- Each tweet gets its own folder with images
- Time-range filtering for exports
- Visual analytics on bookmarking habits
- Waterfall display for browsing
- Lightning-fast search
- Privacy-first design

### What They Do Well
- Clean, focused product: export your bookmarks, done
- Points system means you pay only for what you use
- Markdown + folder structure is developer-friendly
- Visual analytics is a nice touch

### Where They Fall Short
- Very narrow feature set (primarily export)
- No AI, no categorization, no digests
- No ongoing sync or management
- Points expire? (unclear)
- No Notion/Sheets integration
- No mobile experience
- Copyright 2024 -- uncertain if actively maintained
- Blog exists ("Why I Built xBookmarks") suggesting solo developer

### Growth Trajectory
**Niche/uncertain.** Serves a very specific use case (bulk export). Not positioned for growth as a full bookmark management solution.

---

## 5. BOOKMARKSAVE (bookmarksave.com)

### Overview
Claims to be a "free" Twitter bookmark export and organization tool. Makes bold claims about features but reality appears much thinner.

### Chrome Web Store
- **Extension Name:** "Bookmark Save"
- **Rating:** 3.4/5 stars (5 ratings)
- **Users:** 165
- **Version:** 1.0

### Website Claims vs Reality

| Claim | Reality |
|---|---|
| "4.8/5 rating" | Actual CWS rating is 3.4/5 |
| "10,000+ active users" | Actual CWS users: 165 |
| "1,000 total reviews" | Actual CWS reviews: 5 |
| "AI-powered categorization" | Unverifiable with so few users |
| "Thread intelligence" | Unverifiable |
| "End-to-end encryption" | Requires Google Sign-In and browser tab access |

### Key Features (as claimed)
- One-click export (TXT, CSV, PDF, MD)
- Smart categorization
- Thread detection
- Declutter/cleanup tools
- Export history tracking
- Local processing

### What They Do Well
- Free (genuinely)
- Multi-format export
- Clean website design

### Where They Fall Short
- **Massively inflated metrics on website** -- this is a major red flag
  - Claims 10,000+ users when actual count is 165
  - Claims 1,000 reviews when actual count is 5
  - Claims 4.8 rating when actual is 3.4
- Only 165 users total
- Version 1.0 suggests very early/abandoned
- Requires "sensitive permissions" including browser tab access
- Google Sign-In requirement contradicts "privacy-first" claim
- No evidence of active development
- Solo developer project

### User Sentiment
Essentially no real user base to generate sentiment. The fake metrics on the website destroy trust.

### Growth Trajectory
**Dead or near-dead.** 165 users, inflated claims, version 1.0. Either abandoned or a very early experiment that never gained traction.

---

## COMPARATIVE MATRIX

| Feature | Twillot | Tweetsmash | Xbase | xBookmarks | BookmarkSave |
|---|---|---|---|---|---|
| **CWS Rating** | 4.7/5 | 3/5 | 3.7-4.3/5 | Unknown | 3.4/5 |
| **User Base** | Largest in category | ~4,000 | Very small | Very small | 165 |
| **Free Tier** | Yes (generous) | 7-day trial | 30-day trial | No (pay-per-use) | Yes (free) |
| **Monthly Cost** | $0-$13.99 | $14 | Unknown | Points-based | Free |
| **Lifetime Deal** | No | $198 ($119 w/code) | No | No | N/A |
| **AI Categorization** | Yes | Yes (chat) | No | No | Claimed |
| **Local Search** | Yes (fast) | Yes | Yes (<100ms) | Yes | Unknown |
| **Notion Sync** | No | Yes (auto) | No | No | No |
| **Email Digests** | No | Yes | No | No | No |
| **Media Download** | Yes (batch) | No | No | No | No |
| **Export Formats** | PDF/CSV/MD/JSON | Notion/Sheets/Zotero/PDF | JSON | Markdown/ZIP | TXT/CSV/PDF/MD |
| **Thread Handling** | Basic | Unrolled + grouped | Summarized | Basic | Claimed |
| **Mobile** | No | PWA | No | No | No |
| **Open Source** | Was (archived) | No | No | No | No |
| **Anonymous Viewing** | Yes | No | No | No | No |
| **Note-Taking** | No | No | Yes | No | No |
| **Block Management** | Yes | No | No | No | No |
| **Active Development** | Yes (closed-source) | Yes | Uncertain | Uncertain | No |

---

## KEY TAKEAWAYS

1. **Twillot is the most feature-complete** but is becoming a sprawling Swiss Army knife. The open-source death and pivot to closed-source could alienate the developer community that helped build early traction.

2. **Tweetsmash has the best Notion integration** and the most unique value prop (digest system), but struggles with adoption. At $14/month it's expensive for what many see as a "nice to have."

3. **Xbase is the speed king** but lacks breadth. Good for power users who just want fast local search and nothing else.

4. **xBookmarks and BookmarkSave are not real competitors** -- too small, too narrow, uncertain maintenance.

5. **None of these tools generate video/audio content from bookmarks.** This is a gap Retell could potentially fill if positioned correctly (turn bookmarked video tweets into repurposed content).

6. **The entire category relies on unofficial Twitter data access** -- one API change from Twitter could break all of them simultaneously.

7. **Pricing ranges from free to $14/month subscription to $198 lifetime.** The market is price-sensitive -- Twillot's generous free tier puts pressure on paid-only tools like Tweetsmash.
