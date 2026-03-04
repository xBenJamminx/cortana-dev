# How to Evaluate an Entire Market of Competitors in 2 Hours

**By Ben | BuildsByBen**

---

Most people do competitor research the hard way. They Google around, open 30 tabs, skim a few pricing pages, and walk away with a vague sense that "there's a lot of competition." That's not research. That's anxiety with extra steps.

AI changed competitive analysis from a week-long consulting engagement into a Tuesday afternoon. I'm going to walk you through the exact framework I use to go from "I have an idea" to "I know every player in this market, where the gaps are, and exactly how to position against them" in about two hours.

This isn't theory. I used this to evaluate the entire bookmark manager market before building BookmarkIQ. I'll use that as a real example throughout.

---

## Step 1: Define the Market

Before you research anything, you need to know what you're actually researching. Most people skip this and end up comparing apples to enterprise SaaS platforms.

Define three things: the market category, who the customer is, and what problem is being solved. Get this wrong and you waste your two hours on companies that aren't actually your competitors.

### The Prompt

```
I'm researching a market to understand the competitive landscape. Help me define and scope this market before I start my analysis.

My product idea / business: [DESCRIBE WHAT YOU'RE BUILDING OR SELLING IN 2-3 SENTENCES]
The problem it solves: [WHAT PAIN DOES IT ADDRESS]
Who it's for: [TARGET CUSTOMER -- BE SPECIFIC]

Help me with:

1. MARKET DEFINITION: What is the precise market category? Give me the industry terms people would use to search for solutions like mine. Include adjacent categories I should also check.

2. MARKET SEGMENTS: Break this market into 2-4 segments based on customer type, price point, or use case. (Example: "Enterprise vs. SMB vs. Individual" or "Free tools vs. Paid platforms vs. Agency services")

3. SEARCH TERMS: Give me 10-15 specific search queries I should use to find competitors. Include terms for Google, Product Hunt, G2, Reddit, and alternative search engines. Mix obvious terms with non-obvious ones.

4. BOUNDARIES: What is NOT in this market? Help me define what to exclude so I don't waste time analyzing companies that aren't real competitors.

Be specific. I'd rather have a narrow, accurate market definition than a broad, useless one.
```

### What You're Looking For

A clear picture of what you're evaluating. If you're building a bookmark manager, you're not competing with every "productivity tool" on earth -- you're competing with bookmark managers, read-it-later apps, and maybe link-in-bio tools. The boundaries matter. Save the search terms. You'll use them in Step 2.

### Time: 10-15 minutes

---

## Step 2: Find All the Competitors

Now you go hunting. The goal isn't to find the top 3 you already know about. It's to find all of them -- including ones you've never heard of, ones that launched last month, and dead ones that tell you what doesn't work.

Use the search terms from Step 1 across these sources:

**Where to search:**

- **Perplexity AI** -- Best starting point. Ask directly: "What are all the [category] tools available in 2026?" You get a categorized list faster than any manual search.
- **Google** -- Go past page 1. Check "People also ask" for adjacent competitors.
- **Product Hunt** -- Sort by newest for recent launches, most upvoted for established players.
- **G2 / Capterra** -- Category pages surface dozens of tools you won't find elsewhere. The reviews reveal what users actually care about.
- **Reddit** -- Search r/SaaS, r/startups, r/[your niche]. "What's the best X tool?" threads are goldmines for obscure competitors.
- **AlternativeTo** -- Type in any known competitor, see every alternative. Fastest way to expand your list.

### The Prompt

Once you've collected a list of competitors from your searching, consolidate it:

```
I'm building a comprehensive competitor list for the [YOUR MARKET] space.

Here are all the competitors I've found so far from my research:
[PASTE YOUR RAW LIST -- COMPANY NAMES, URLS, BRIEF NOTES]

Help me:

1. DEDUPLICATE: Remove any duplicates or companies that have been acquired/rebranded.

2. CATEGORIZE: Group these into tiers:
   - Tier 1: Direct competitors (solve the same problem for the same audience)
   - Tier 2: Partial competitors (overlap in features but different primary focus)
   - Tier 3: Indirect competitors (alternative solutions to the same problem)

3. GAPS: Based on the category, are there any notable competitors I might be missing? Flag any well-known players in this space that aren't on my list.

4. STATUS CHECK: For each company, if you have knowledge of it, note whether it appears to be active, growing, stagnant, or potentially dead/abandoned.

Give me the output as a clean table with columns: Company | URL | Tier | Category/Focus | Status | Notes
```

### What You're Looking For

You should end up with 15-40 competitors. That sounds like a lot, but you'll narrow down in the next step. The point is completeness -- you don't want to discover a key competitor six months after launch.

### Time: 30-40 minutes

---

## Step 3: Build a Comparison Matrix

Now take your competitor list and build a structured matrix for side-by-side comparison. Manually this takes days. With AI, about 20 minutes.

### The Prompt

```
I need to build a competitive comparison matrix for the [YOUR MARKET] space. I'm going to give you information about each competitor and I need you to extract and organize it into a structured format.

My product / business: [BRIEF DESCRIPTION]
My target customer: [WHO YOU'RE BUILDING FOR]

Here are my top competitors (focus on Tier 1 and Tier 2 from my previous analysis):
[LIST 8-15 COMPETITORS WITH THEIR URLS]

For each competitor, create a comparison matrix with these columns:

| Company | Founded | Pricing (lowest/highest) | Free Tier? | Target Customer | Core Value Prop | Key Features (top 5) | Integrations | Platform (Web/Mobile/Desktop) | Team Size Estimate | Funding Status | User Reviews Summary |

Rules:
- If you don't know something with confidence, write "Unknown" rather than guessing
- For pricing, note the model (per user, flat rate, usage-based, freemium)
- For user reviews, summarize the sentiment in 5-10 words (e.g., "Loved for simplicity, complaints about mobile app")
- Keep each cell concise -- this is a reference table, not an essay

After the matrix, add:

OBSERVATIONS:
- What patterns do you see across the market?
- What is the most common pricing model?
- What features does almost everyone offer? (table stakes)
- What features do only 1-2 competitors offer? (potential differentiators)
```

### How to Feed It Information

Don't just give the AI competitor names and expect magic. For your top 5-8 competitors, spend 2-3 minutes each visiting their site and pasting in key info: homepage copy, pricing page, features page. If you're using Claude or ChatGPT with web access, give it the URLs directly. For the rest, names and URLs are usually enough.

### What You're Looking For

The matrix gives you the first real picture of the market. You'll see clustering immediately -- similar pricing, same persona, same core features. The outliers are interesting. The gaps are even more interesting.

### Time: 15-20 minutes

---

## Step 4: Analyze Pricing, Positioning, and Features

The matrix gives you the what. This step gives you the so what.

### The Prompt

```
Based on the competitive matrix I've built, I need a deeper analysis of pricing strategies, market positioning, and feature differentiation.

[PASTE YOUR COMPLETED MATRIX FROM STEP 3]

My product: [WHAT YOU'RE BUILDING]
My target customer: [WHO YOU'RE BUILDING FOR]
My tentative pricing: [IF YOU HAVE ONE, OTHERWISE "Not yet determined"]

Analyze the following:

1. PRICING ANALYSIS:
   - What are the pricing tiers across the market? (Map the range from cheapest to most expensive)
   - What's the median price point?
   - How do competitors justify premium pricing? What do you get at the top tier vs. the bottom?
   - Are there pricing models that seem to be winning (freemium, flat-rate, per-seat, usage-based)?
   - Where is the pricing white space? Is there an underserved price point?

2. POSITIONING MAP:
   - Create a 2x2 positioning map. Suggest the two most meaningful axes based on this market (e.g., "Simple vs. Feature-Rich" and "Individual vs. Team" or "Cheap vs. Premium" and "Niche vs. Broad").
   - Place each competitor on the map and identify which quadrants are crowded and which are empty.

3. FEATURE ANALYSIS:
   - Table stakes features: What does EVERY competitor offer? (These are non-negotiable for market entry)
   - Common features: What do MOST competitors offer? (Expected but not universal)
   - Differentiating features: What do only 1-3 competitors offer? (Potential unique selling points)
   - Missing features: What does NO ONE offer that customers might want? (Based on review sentiment and market gaps)

4. MESSAGING ANALYSIS:
   - What words and phrases do competitors use most often in their positioning?
   - What emotional triggers are they targeting? (Productivity, fear of missing out, simplification, cost savings, etc.)
   - What messaging angle is nobody using?

Be direct and analytical. I'm making business decisions based on this, so accuracy matters more than optimism.
```

### What You're Looking For

This is where you see your opening. Maybe everyone prices at $10-15/month but nothing credible exists under $5. Maybe every tool says "simple" but reviews beg for advanced features. Maybe everyone targets individuals but nobody serves small teams.

The positioning map is key. A crowded quadrant next to an empty one means that empty space is either a massive opportunity or a graveyard. The next step helps you figure out which.

### Time: 15-20 minutes

---

## Step 5: Identify Gaps and Opportunities

You've got the data. Now figure out what it means for your business.

### The Prompt

```
Based on everything we've analyzed about the [YOUR MARKET] competitive landscape, I need you to identify the strategic gaps and opportunities.

Context about my situation:
- My product: [DESCRIPTION]
- My target customer: [WHO]
- My resources: [SOLO FOUNDER / SMALL TEAM / FUNDED STARTUP -- be honest about what you can actually build and support]
- My timeline: [WHEN YOU WANT TO LAUNCH OR ENTER THIS MARKET]
- My unfair advantage (if any): [WHAT DO YOU HAVE THAT COMPETITORS DON'T? Domain expertise, existing audience, technical capability, niche insight, etc.]

Based on the competitive analysis, identify:

1. MARKET GAPS:
   - What customer segments are underserved?
   - What use cases are nobody addressing well?
   - What price points have no credible option?
   - What platforms or integrations are missing market-wide?

2. COMPETITOR WEAKNESSES (by company):
   - For each Tier 1 competitor, list their 2-3 biggest weaknesses based on reviews, positioning gaps, or feature limitations. These are your attack vectors.

3. OPPORTUNITIES RANKED:
   - List the top 5 opportunities you see in this market
   - For each one, rate: Opportunity Size (S/M/L), Competition Level (Low/Med/High), and Fit With My Resources (Good/Okay/Stretch)
   - Rank them by overall attractiveness

4. RISKS AND WARNINGS:
   - What trends could disrupt this market in the next 12-18 months?
   - Which competitors are likely to expand into adjacent areas?
   - Is this market growing, mature, or consolidating?
   - What has killed previous entrants? (If you can identify failed competitors, what went wrong?)

5. POSITIONING RECOMMENDATION:
   - Based on everything above, recommend a specific positioning angle for my product
   - Who exactly should I target first?
   - What should my core message be?
   - What 3-5 features should I prioritize for market entry?
   - What should I explicitly NOT build (at least initially)?

Don't be nice. Be accurate. I'd rather hear "this market is too crowded for a solo founder" than get optimistic advice that leads me into a brick wall.
```

### What You're Looking For

The ranked opportunities are your decision framework. The risks section keeps you honest. The positioning recommendation gives you a starting point to test.

Pay special attention to "What has killed previous entrants?" Dead competitors (Product Hunt launches that went nowhere, AlternativeTo entries with dead links) tell you as much as the winners do.

### Time: 15-20 minutes

---

## Step 6: Generate a Strategic Summary

You've got pages of analysis. Now compress it into something you can use to make decisions, share with a co-founder, or reference when you're heads-down building.

### The Prompt

```
I've completed a competitive analysis of the [YOUR MARKET] space. Now I need a strategic summary document I can reference going forward.

Using all the analysis we've done in this conversation, create a one-page competitive intelligence brief with:

1. MARKET SNAPSHOT (3-4 sentences):
   - Market size/stage, number of active competitors, dominant pricing model, and the one-sentence state of the market.

2. TOP 5 COMPETITORS (table format):
   | Rank | Company | Why They're Top 5 | Their Biggest Vulnerability |

3. COMPETITIVE POSITIONING STATEMENT:
   "[My Product] is the only [category] that [unique differentiator] for [specific customer] who [specific need/frustration with alternatives]."
   Give me 3 versions of this statement to test.

4. MY COMPETITIVE ADVANTAGES:
   - Bullet list of 3-5 specific advantages I have over the current market based on our analysis.

5. THREATS TO MONITOR:
   - 3 things that could change my competitive position (new entrants, feature releases from incumbents, market shifts). For each, define a trigger that should prompt me to reassess.

6. 90-DAY ACTION PLAN:
   - Based on this analysis, what are the 5 most important things I should do in the next 90 days to enter or compete in this market? Be specific and actionable.

7. KEY METRICS TO TRACK:
   - What 3-5 competitor metrics should I monitor on an ongoing basis? (Pricing changes, feature launches, review sentiment, traffic trends, etc.)

Format this as a clean, scannable document. Bold key phrases. Use tables where they add clarity. This should be something I can re-read in 5 minutes three months from now and immediately remember the strategic landscape.
```

### What You're Looking For

This is your reference document. Pin it somewhere you'll see it. The positioning statements are conversation starters, not final copy -- test them on real people. The 90-day action plan turns research into next steps.

### Time: 10-15 minutes

---

## Real Example: How I Evaluated the Bookmark Manager Market

I'll show you how this actually plays out. When I was evaluating whether to build BookmarkIQ, I ran this exact framework. Here's what happened at each step.

**Step 1 -- Defining the Market:** I started with "AI-powered bookmark manager" and quickly realized the real market was broader: "personal knowledge management tools that handle links" -- bookmark managers, read-it-later apps, web clippers, and link-in-bio tools. Defining those boundaries saved me from thinking the market was either empty or impossibly huge.

**Step 2 -- Finding Competitors:** I found 34 competitors across all tiers. The obvious ones were Raindrop.io, Pocket, Instapaper, and Notion's web clipper. But I also surfaced smaller indie tools, browser extensions with loyal followings, three tools launched in the past 60 days, and five dead competitors whose Product Hunt pages still existed.

**Step 3 -- The Matrix:** Patterns jumped out immediately. Almost everyone offered tagging and folders. Almost nobody had genuinely useful AI features -- most just slapped "AI-powered" on basic search. Pricing clustered around free-with-limits and $5-8/month premium. Nothing above $15/month.

**Step 4 -- Deeper Analysis:** The positioning map was eye-opening. The "simple + individual" quadrant was packed. The "complex + team" space had Notion and legacy enterprise tools. The "simple + team" quadrant was almost empty. "AI-native + individual" had a few new entrants but nobody dominant.

**Step 5 -- Gaps and Opportunities:** The biggest gap: nobody doing AI categorization well. G2 and Reddit reviews were full of complaints about saving links and never finding them again. Tools claiming AI features were just basic search or generic auto-tagging. The real opportunity: "save a link, AI reads it, it appears in the right place without you doing anything."

**Step 6 -- Strategic Summary:** Clear go signal. Market growing, incumbents slow-moving, and the specific angle I wanted -- AI that actually organizes for you -- had no credible competitor. The 90-day plan: build the AI categorization engine first, because that was the differentiator. Everything else was table stakes for later.

**Total time: about 2 hours and 15 minutes, including the manual searching in Step 2.**

The analysis lives in my Airtable now. I reference it monthly. When Raindrop.io launched their AI features two weeks after I started building, I already knew their approach and could see how mine was different. That's the value of doing this upfront.

---

## The Template

The Airtable template for this entire framework is in the vault. It includes:

- A pre-built competitor tracking table with all the columns from the matrix
- A positioning map template
- A strategic summary template
- Views for Tier 1/2/3 competitors
- A "Monitor" view for tracking competitor changes over time

Duplicate it, fill in your market, and you've got a living competitive intelligence system, not just a one-time analysis.

---

## When to Use This

**Before building a product.** The obvious one. Before you spend months building, spend two hours understanding the landscape. This would have saved me from at least two projects that were dead on arrival -- markets already dominated by well-funded players doing the exact thing I wanted to do.

**Before entering a new market.** If you're expanding your business into an adjacent space, run this first. The dynamics of a new market are never what you assume from the outside.

**Before a major pivot.** Thinking about repositioning? This tells you where the open space is before you commit.

**Quarterly, for your existing market.** Markets change. Run a lighter version (Steps 3-5 focused on updates) every quarter. The companies that get blindsided by competitors are the ones that stopped paying attention after launch.

**Before a pricing change.** If you're thinking about changing your pricing, run Steps 3-4 focused specifically on pricing. Know exactly where you sit in the market before you move.

**When a new competitor appears.** Someone launches a tool that looks like yours. Don't panic. Run Steps 3-5 focused on that one competitor. Usually they're less threatening than they look. Sometimes more. Either way, knowing beats guessing.

---

## The Bottom Line

Two hours. You go from "I wonder what the competition looks like" to a full strategic picture with positioning recommendations, gap analysis, and a 90-day action plan.

The prompts do the heavy lifting, but you bring the judgment. AI is great at organizing and analyzing information. It's not great at knowing which opportunities match your skills, resources, and risk tolerance. That's still on you.

Use the framework. Adapt the prompts. And when the data surfaces something interesting, dig deeper -- the best insights come from threads the AI flagged but didn't fully explore.

---

*Built by BuildsByBen. Strategy frameworks for people who'd rather build than spend weeks on research.*
