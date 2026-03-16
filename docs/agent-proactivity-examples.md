# Agent Proactivity Examples

What proactive behavior looks like for each FAM Smart Companion domain agent. Each example includes the **trigger** (what causes it), **action** (what the agent does), and a **sample message** the user would hear/see.

> **Proactivity = the agent speaks first.** Not waiting for a question — noticing something and surfacing it.

---

## Existing Infrastructure (already built)

| System | Location | What It Does |
|--------|----------|-------------|
| Rituals | `src/apis/rituals/` | 48 routine types, evaluate completion, energy check-in matrix |
| Greeting Generator | `src/apis/agents/greeting_generator.py` | 9 greeting styles with weighted variety |
| Morning Briefing | `smart-companion-telegram/src/tasks/briefing/` | Per-user scheduled briefings from 6+ sources |
| Energy Check-in | `src/agents/research_assistant/tools/rituals.py` | Schedule load x ritual completion → contextual nudge |
| Heartbeat | `AGENTS.md` | 2-4x/day context-aware background checks |

---

## All Proactivity Examples

*Filter by **Agent** column to view examples for a specific domain.*

| # | Action | Trigger | Sample Message | Agent | Feasibility | Priority |
|---|--------|---------|---------------|-------|-------------|----------|
| 1 | Gentle check-in | Unusual time for user to be active (e.g., 3 AM) | "Hey, it's pretty late. Everything good or just can't sleep?" | Context | High — uses conversation memory | High |
| 2 | Soft re-engagement | User hasn't interacted in 8+ hours during waking hours | "Haven't heard from you in a while. How's the day going?" | Context | High — uses conversation memory | Medium |
| 3 | Surface weather alert naturally | Weather API detects incoming storm or extreme temps | "Heads up — heavy rain rolling in around 4. Might want to grab that umbrella if you're heading out." | Context | Medium — needs weather API (OpenWeatherMap) | Medium |
| 4 | Switch context from work mode to personal | Phone GPS detects location shift (home) | "You're home. Switching off work notifications. Anything you need before you settle in?" | Context | Low — needs mobile GPS permissions | Low |
| 5 | Adjust all scheduling context | Time zone change detected via location | "Looks like you're in a new time zone. I've adjusted your schedule. Want me to block off some recovery time?" | Context | Low — needs mobile GPS permissions | Low |
| 6 | Pre-meeting nudge with context | Calendar event starting in 15 minutes | "You've got that call with Steven in 15. Last time you discussed the vision API migration." | Scheduling | High — uses Google Calendar | High |
| 7 | Suggest buffer | Back-to-back meetings detected (no breaks) | "You've got 4 meetings stacked today with zero breaks. Want me to move the 2pm back 30 minutes?" | Scheduling | High — uses Google Calendar | High |
| 8 | Notify + reclaim time | Calendar polling detects event removed/rescheduled | "Sarah cancelled the 3pm sync. You've got a free hour now — focus block or take a breather?" | Scheduling | High — uses Google Calendar | Medium |
| 9 | Prompt for meeting prep | Recurring meeting approaching (no notes from user) | "Team standup in an hour. Want to jot down your updates?" | Scheduling | High — uses Google Calendar | Medium |
| 10 | Gentle accountability | Overdue task detected in task system | "That proposal draft was due yesterday. Want to knock it out now or reschedule?" | Scheduling | Medium — needs task management integration | Medium |
| 11 | Ritual reminder (context-aware, not alarm) | Morning ritual window opening | "Morning. You usually meditate around now. Feeling up for it or skipping today?" | Health | High — uses Rituals DB | High |
| 12 | Wind-down prompt | Sleep routine time approaching | "It's almost 11. You usually start winding down around now. Want me to queue up something relaxing?" | Health | High — uses Rituals DB | High |
| 13 | Stretch/movement nudge | No interaction + long work block on calendar | "You've been at it for a while. Quick stretch break? Even 2 minutes helps." | Health | High — uses Rituals DB + Calendar | Medium |
| 14 | Water reminder | Hydration ritual not logged since scheduled time | "Hey, you haven't logged water since this morning. Stay hydrated." | Health | High — uses Rituals DB | Medium |
| 15 | Energy check-in using schedule x ritual matrix | Tired tone detected in voice | "I noticed you sound a bit drained. Your schedule's packed and you skipped your morning routine. Want to take 10 minutes to reset?" | Health | Low — needs voice sentiment model | High |
| 16 | Deliver personalized news digest | Morning briefing time (Celery scheduled) | "Morning. Here's what's relevant today: OpenAI dropped a new model, there's a ProductHunt launch in your space, and that Reddit thread you'd care about blew up overnight." | Discovery | High — uses briefing monitors | High |
| 17 | Proactive context injection | User mentions topic + web search finds recent developments | "Oh, you're looking at LangGraph? They actually released v0.3 yesterday with a new streaming API. Want me to pull the details?" | Discovery | High — needs web search tool added to toolkit | High |
| 18 | Extract and surface highlights | Gmail monitor detects newsletter with relevant content | "Got a newsletter from The Rundown AI. Two things you'd care about: new Claude features and a funding round in your space." | Discovery | High — uses briefing monitors | High |
| 19 | Trending topic alert | Monitor detects topic matching user interests | "Something's trending that's right up your alley — Google just open-sourced their new agent framework. Want the breakdown?" | Discovery | High — uses briefing monitors | Medium |
| 20 | Creator watch alert | Competitor monitor detects new content | "Liam Ottley just dropped a new video on AI agents. Might be worth a watch for content angles." | Discovery | High — uses briefing monitors | Medium |
| 21 | DND activation | Calendar focus block starting | "Your focus block starts now. I'll hold non-urgent notifications for the next 2 hours." | Workspace | High — uses Google Calendar | High |
| 22 | Day-close summary | End of work day approaching + conversation history available | "Wrapping up the day. You worked on 3 things today, and you've got that early meeting tomorrow." | Workspace | High — uses conversation memory | Medium |
| 23 | Unread message digest | Connected messaging app shows unread count spike | "You've got 12 unread messages in your work channel. Want the summary?" | Workspace | Medium — needs messaging OAuth per user | Medium |
| 24 | Code review nudge | Connected GitHub shows PR review requested | "Steven opened a PR for the greeting generator refactor. Want to review it now or later?" | Workspace | Medium — needs GitHub OAuth per user | Medium |
| 25 | Build alert | Connected CI/CD pipeline reports failure | "Heads up — the staging deploy just failed. Looks like a test in the vision module. Want me to pull the logs?" | Workspace | Medium — needs CI/CD webhook setup | Medium |
| 26 | Contextual environment shift | AR sensors classify environment (gym, office, cafe) | "Looks like you're at the gym. Want me to pull up your workout routine?" | Vision | High — uses AR/Vision sensors | Medium |
| 27 | Capture and digitize | Camera detects text-heavy surface (whiteboard, document) | "I see a whiteboard. Want me to grab that and turn it into notes?" | Vision | High — uses AR/Vision sensors | Medium |
| 28 | Commute mode activation | AR detects car interior / movement pattern | "Looks like you're in the car. Switching to audio-only mode. Want a podcast recommendation or your morning briefing?" | Vision | High — uses AR/Vision sensors | Medium |
| 29 | Nutritional context | Camera detects food via vision model | "That looks good. Want me to estimate the calories or log it as your lunch?" | Vision | Low — needs food recognition CV model | Medium |
| 30 | Package alert | AR detects package/delivery at door | "Looks like there's a package at your door. Expecting something?" | Vision | Low — needs fine-grained object detection | Low |
| 31 | Proactive celebration | Calendar event matches birthday/anniversary pattern | "Hey, your anniversary is this Friday. Want me to help find a restaurant or gift idea?" | Personal | High — uses Google Calendar | High |
| 32 | Continuity callback | Memory system matches current topic to past conversation | "Last time we talked about this, you said you wanted to try the async approach. Still feeling that?" | Personal | High — uses conversation memory | High |
| 33 | Preference learning confirmation | Repeated behavior pattern detected in conversation logs | "I've noticed you always check Reddit before your morning meeting. Want me to pull your feed automatically?" | Personal | High — uses conversation memory | Medium |
| 34 | Journal prompt | Self-reflection ritual scheduled in rituals DB | "It's your reflection time. What's one thing that went well today and one thing you'd change?" | Personal | High — uses Rituals DB | Medium |
| 35 | Gentle emotional check-in | Sentiment analysis detects negative shift across 3+ sessions | "You've seemed a bit off the last couple days. No pressure, but I'm here if you want to talk about it." | Personal | Low — needs cross-session sentiment model | Low |
| 36 | Payment reminder | Bill payment calendar event within 48 hours | "Your internet bill is due tomorrow. Want me to mark it as paid once you handle it?" | Finance | High — uses Google Calendar | Medium |
| 37 | Renewal heads-up | Subscription renewal calendar event approaching | "Your Figma subscription renews in 3 days at $15/month. Still using it or want to cancel?" | Finance | High — uses Google Calendar | Medium |
| 38 | Spending alert | Bank API detects unusual spending pattern | "You've spent more on dining out this week than your usual average. Just flagging it — no judgment." | Finance | Low — needs bank API (Plaid) + security infra | Low |
| 39 | Budget check-in | Monthly budget review ritual triggers | "End of the month. You're at 85% of your budget with 3 days left. Biggest category was subscriptions." | Finance | Low — needs bank API (Plaid) + security infra | Low |
| 40 | Market alert | Brokerage API detects significant portfolio movement | "Your portfolio moved 5% today. Mostly driven by tech stocks. Want a quick breakdown?" | Finance | Low — needs brokerage API + security infra | Low |
| 41 | Follow-up with findings | Memory system flags unresolved topic from previous conversation | "Remember when you asked about vector databases last week? I found a solid comparison article. Want me to break it down?" | Research | High — uses conversation memory | High |
| 42 | Suggest alternative approaches | Extended conversation on same problem (long session duration) | "You've been on this for a while. Want me to look up how others have solved similar routing problems?" | Research | High — uses conversation memory | Medium |
| 43 | Study session prompt | Learning ritual scheduled in rituals DB | "Your language learning session is in 10 minutes. Pick up where you left off or try something new?" | Research | High — uses Rituals DB | Medium |
| 44 | Research alert | Arxiv/paper monitor detects publication in user interest area | "New paper on arxiv about multi-agent orchestration. Looks relevant to what you're building. Quick summary?" | Research | Medium — needs Arxiv interest-based monitor | Medium |
| 45 | Update notification | Topic monitoring pipeline detects changes to saved topic | "That LlamaIndex integration you researched last month — they just released a major update. Want the changelog highlights?" | Research | Medium — needs topic monitoring pipeline | Medium |
| 46 | Birthday reminder for friends | Calendar event matches friend birthday pattern | "Jake's birthday is Saturday. Want to send something or just a text?" | Social | High — uses Google Calendar | High |
| 47 | Social media time-box | Social media ritual timer triggers | "Your social media window is open. 15 minutes, then I'll remind you to wrap up." | Social | High — uses Rituals DB | Low |
| 48 | Coordination assist | Connected group chat detects planning conversation | "Looks like the group is trying to pick a date for dinner. You're free Thursday and Saturday — want me to suggest those?" | Social | Medium — needs group chat integration | Medium |
| 49 | Relationship nudge | Contact log shows 2+ weeks since last interaction | "You haven't reached out to Mom in a couple weeks. Quick call or text?" | Social | Low — needs contact/social data pipeline | Low |
| 50 | Entertainment suggestion | End of last calendar event + no more events today | "Done for the day? That show you started last week has a new episode out." | Entertainment | High — uses Google Calendar | Medium |
| 51 | Activity recommendation | Calendar shows no events for next 3+ hours | "Nothing on your calendar this afternoon. Want a podcast recommendation or feel like gaming?" | Entertainment | High — uses Google Calendar | Medium |
| 52 | Session prompt | Gaming ritual timer triggers | "Gaming time. Want to pick up where you left off or try something new?" | Entertainment | High — uses Rituals DB | Low |
| 53 | Content alert | Media tracking API detects new release from followed artist | "Kendrick dropped a new track. Want to queue it up?" | Entertainment | Medium — needs music/media API (Spotify) | Low |
| 54 | Eating window alert | Intermittent fasting ritual timer ending | "Your eating window opens in 30 minutes. What are you thinking for your first meal?" | Food | High — uses Rituals DB | High |
| 55 | Meal planning prompt | Meal prep ritual triggers on scheduled day | "It's meal prep Sunday. Want to plan the week or wing it?" | Food | High — uses Rituals DB | Medium |
| 56 | Meal suggestion | Time-based trigger (noon) + no meal ritual logged | "It's almost noon and you haven't eaten. Want me to suggest something?" | Food | High — uses Rituals DB | Medium |
| 57 | Pre-trip checklist | Calendar event contains flight/travel keywords | "Your flight to LA is in 3 days. Want me to start a packing list or check the weather there?" | Travel | High — uses Google Calendar | Medium |
| 58 | Vacation prep | Vacation ritual triggers before scheduled start | "Vacation starts Monday. Want me to set up out-of-office replies and pause work notifications?" | Travel | High — uses Rituals DB | Low |
| 59 | Departure nudge | Calendar event with location + maps API travel time estimate | "Your dinner reservation is at 7. With current traffic, you should leave by 6:15." | Travel | Medium — needs Maps API (Google Maps) | High |
| 60 | Travel mode activation | Phone GPS detects airport location | "Looks like you're at the airport. Your gate is B12, boarding at 2:15. Want me to find the nearest coffee?" | Travel | Low — needs mobile GPS permissions | Medium |
| 61 | Deal alert | E-commerce price tracking detects wishlist item on sale | "Those headphones you saved dropped 30%. Want the link?" | Shopping | Low — needs wishlist + price monitoring infra | Low |
| 62 | Reorder nudge | Purchase history estimates product running low | "You usually reorder coffee beans around now. Running low?" | Shopping | Low — needs purchase history tracking | Low |
| 63 | Shopping prep | Calendar event approaching (Black Friday, Prime Day) | "Prime Day is next week. Want to review your wishlist before the deals start?" | Shopping | Low — needs wishlist + e-commerce integration | Low |
| 64 | Learning nudge | Course ritual not logged in 7+ days | "You haven't touched that Python course in a week. Want to pick it back up or swap to something else?" | Education | High — uses Rituals DB | Medium |
| 65 | Spaced repetition prompt | Knowledge review ritual scheduled | "Time for your knowledge review. 5 questions from last week's material?" | Education | High — uses Rituals DB | Medium |
| 66 | Learning suggestion | Conversation analysis detects repeated lookups on same topic | "You've been working with GraphQL a lot but seem to be looking things up frequently. Want me to find a quick crash course?" | Education | Medium — needs conversation pattern analysis | Medium |
| 67 | Learning opportunity | Course platform monitor detects new resource in user interest area | "MIT just released a free course on multi-agent systems. Right up your alley — want the link?" | Education | Medium — needs course platform API | Low |

---

## Feasibility Dependencies

| Dependency | Examples That Need It | Effort |
|-----------|----------------------|--------|
| Google Calendar (already integrated) | #6, #7, #8, #9, #21, #31, #36, #37, #46, #50, #51, #57 | None |
| Rituals DB (already built) | #11, #13, #14, #12, #34, #43, #47, #52, #54, #55, #56, #58, #64, #65 | None |
| Morning briefing monitors (already built) | #16, #19, #18, #20 | None |
| Conversation memory (already built) | #2, #22, #33, #32, #41, #42 | None |
| AR/Vision sensors (already built) | #26, #27, #28 | None |
| Voice tone analysis | #15 | Medium — needs sentiment model on voice input |
| Weather API | #3 | Low — simple API call (OpenWeatherMap) |
| Web search tool | #17 | Low — add search tool to agent toolkit |
| Phone GPS / location services | #4, #5, #60 | Medium — needs mobile app location permissions |
| Messaging app integration (user-connected) | #23 | Medium — OAuth per user |
| GitHub integration (user-connected) | #24 | Medium — OAuth per user |
| CI/CD webhook | #25 | Medium — per-user webhook setup |
| Food-specific CV model | #29 | Medium — needs food recognition training/API |
| Maps API (travel time) | #59 | Low — Google Maps API call |
| Bank/financial API (Plaid etc.) | #38, #39, #40 | High — significant infra + security |
| Contact graph / communication log | #49 | High — needs social data pipeline |
| Multi-session sentiment tracking | #35 | High — needs cross-session emotion model |
| Arxiv/paper monitoring | #44 | Medium — needs per-user interest-based monitor |
| Topic monitoring pipeline | #45 | Medium — extends existing briefing monitors |
| E-commerce price tracking | #61, #62 | High — needs wishlist + price monitoring |
| Course platform monitoring | #63, #67 | Medium — needs course API integrations |
| Media tracking (Spotify etc.) | #53 | Medium — needs music/media API |
| Conversation pattern analysis | #66 | Medium — needs lookup frequency detection |
| AR object detection (specific) | #30 | High — needs fine-grained CV at distance |

---

## Design Principles

1. **Never annoying.** If the user doesn't respond to a proactive nudge, don't repeat it. Respect autonomy.
2. **Context is king.** A nudge at the wrong time is worse than no nudge. Check schedule load, time of day, recent interactions.
3. **Speak like a friend.** Not "Your hydration goal is 30% below target." Instead: "Hey, drink some water."
4. **Earn trust gradually.** Start with low-stakes proactivity (weather, time vibes). Escalate to higher-stakes (financial alerts, emotional check-ins) as the user engages.
5. **Always offer an out.** Every proactive message should be easy to dismiss or defer.
6. **Batch when possible.** Don't send 5 separate nudges in an hour. Bundle into one natural message.
7. **Learn from dismissals.** If a user consistently ignores a type of nudge, reduce its frequency automatically.
