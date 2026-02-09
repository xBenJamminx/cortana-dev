# Prompt Pack: Side Projects & Automation

**12 Production-Ready AI Prompts for Builders, Business Owners, and Side Hustlers**

By BuildsByBen

---

These prompts are for people who have an idea and want to move on it. Not theoretical. Not "someday." You have a side project, a business idea, or a workflow that wastes your time, and you want AI to help you build, validate, launch, or automate it. Copy, paste, fill in the brackets, and go.

---

## 1. Side Project Idea Validator

**Best Model:** Claude

**When to Use:** You have an idea and need to know if it's worth your next 90 days before you build anything.

**The Prompt:**

```
I have a side project idea and I need you to pressure-test it before I invest time building it.

THE IDEA: [DESCRIBE YOUR IDEA IN 2-4 SENTENCES. WHAT IT DOES, WHO IT'S FOR, HOW IT MAKES MONEY.]

MY BACKGROUND: [RELEVANT SKILLS, RESOURCES, OR ADVANTAGES YOU HAVE -- e.g., "I know Python and have 10 years in real estate"]

TIME I CAN COMMIT: [e.g., "10 hours/week" or "full-time for 3 months"]

BUDGET: [WHAT YOU CAN SPEND UPFRONT -- e.g., "$500" or "$0, just my time"]

Analyze this idea across these dimensions:

1. MARKET DEMAND
   - Who specifically would pay for this? (Be narrow, not "everyone")
   - How are they solving this problem today without your product?
   - What would you search on Google if you had this problem? List 5 search queries.
   - Are people already spending money on similar solutions? Name them if possible.

2. COMPETITION CHECK
   - List 3-5 existing products or services that overlap with this idea
   - For each: what they charge, what they do well, what they do poorly
   - Where is the gap this idea could fill?

3. FEASIBILITY SCORE (1-10)
   - Can I build a working version in 30 days given my background and constraints?
   - What are the 3 hardest technical or logistical challenges?
   - What's the simplest possible version I could ship first?

4. REVENUE REALITY
   - What's a realistic price point? Show your reasoning.
   - How many customers would I need for $1,000/month? $5,000/month?
   - What's the most likely revenue model: one-time, subscription, usage-based, or something else?

5. RISK FACTORS
   - What are the top 3 reasons this fails?
   - Which of those risks can I mitigate before launching?

6. VERDICT
   - Give me a straight answer: Build it, Modify it, or Kill it.
   - If "Modify," what specifically should I change?
   - If "Build it," what's my first move this week?

Be blunt. I'd rather hear hard truths now than waste months on a dead idea.
```

**Example Use Case:** You want to build a tool that generates rental property descriptions from photos using AI. You've been a landlord for 6 years and know Python basics. This prompt tells you the market exists (Zillow listings get 3x more views with good descriptions), there are 2 competitors but both are clunky, and your first version should be a simple web form, not a mobile app.

**Pro Tip:** Run this prompt twice with two different models (Claude and ChatGPT). If both say "Kill it," listen. If they disagree, dig into why. The disagreement usually reveals the real question you need to answer.

---

## 2. Landing Page Copy Generator

**Best Model:** Claude

**When to Use:** You need a landing page that converts visitors before you build the full product. This is your "does anyone actually want this?" test.

**The Prompt:**

```
Write landing page copy for my side project. This page needs to explain what it does, why it matters, and get people to sign up, all in under 60 seconds of reading.

PRODUCT NAME: [NAME, OR "suggest 3 options" IF YOU DON'T HAVE ONE YET]
WHAT IT DOES: [ONE SENTENCE. WHAT DOES THE USER GET?]
WHO IT'S FOR: [SPECIFIC AUDIENCE -- e.g., "freelance designers who hate writing invoices"]
THE PROBLEM IT SOLVES: [WHAT PAIN DOES YOUR AUDIENCE FEEL RIGHT NOW?]
HOW IT WORKS: [3-4 STEPS, SIMPLIFIED -- e.g., "Upload your data, pick a template, get your report"]
PRICING: [IF YOU HAVE IT. IF NOT, SAY "waitlist/free beta"]
SOCIAL PROOF: [ANY NUMBERS, TESTIMONIALS, CREDENTIALS -- OR "none yet"]
CTA GOAL: [WHAT SHOULD THEY DO -- "join waitlist," "start free trial," "buy now"]

Write these sections in order:

1. HERO SECTION
   - Headline: 8 words max. State the outcome, not the feature.
   - Subheadline: One sentence expanding on the headline. Address the pain.
   - CTA button text (not "Submit" or "Learn More" -- something specific)

2. PROBLEM SECTION
   - 3-4 sentences describing the pain. Use "you" language.
   - Make the reader feel seen, not lectured.

3. SOLUTION SECTION
   - How it works in 3 steps (icon-friendly, short descriptions)
   - Each step: bold action verb + one sentence

4. BENEFITS (NOT FEATURES)
   - 3-4 benefits, each as a bold headline + one supporting sentence
   - Focus on outcomes: time saved, money made, stress removed

5. SOCIAL PROOF SECTION
   - If I provided testimonials/numbers, use them
   - If I said "none yet," write a placeholder credibility section using my background or early results

6. FAQ (3-4 questions)
   - Anticipate objections disguised as questions
   - "Is this another [category] tool?" / "What if I'm not technical?" / "What does it cost?"

7. FINAL CTA
   - Restate the core value prop in one line
   - CTA button text (same or variation of hero CTA)

Rules:
- Write for a 7th-grade reading level
- No jargon, no buzzwords, no "revolutionary" or "game-changing"
- No em dashes
- Short paragraphs. Lots of whitespace.
- Every section should be scannable in 5 seconds
- Tone: confident, clear, human. Like a smart friend recommending something.
```

**Example Use Case:** You built a Notion template that tracks freelance income and expenses. You need a Carrd landing page to start collecting emails before you launch it on Gumroad. You paste in the details and get copy you can drop straight into the page builder.

**Pro Tip:** After generating the copy, ask: "Rewrite the hero headline 5 more ways. Make each one take a completely different angle: outcome-focused, pain-focused, curiosity-driven, social proof, and contrarian." Test 2-3 of these as the page headline and see which one converts.

---

## 3. MVP Feature List and Scope Definition

**Best Model:** Claude

**When to Use:** You have a big vision but need to ship something small and functional in 2-4 weeks. This prompt forces you to cut scope ruthlessly.

**The Prompt:**

```
I'm building an MVP for a side project and I need you to help me define the smallest version worth shipping.

THE PRODUCT: [WHAT YOU'RE BUILDING]
THE USER: [WHO WILL USE THE FIRST VERSION]
THE CORE PROBLEM: [THE ONE THING THIS SOLVES]
MY SKILLS/TOOLS: [WHAT YOU CAN BUILD WITH -- e.g., "no-code with Bubble," "React + Supabase," "Zapier + Google Sheets"]
MY TIMELINE: [e.g., "2 weekends" or "30 days part-time"]

Do this analysis:

1. FEATURE BRAINSTORM
   - List every feature you think this product could eventually have (aim for 15-20)
   - Don't filter yet. Get it all out.

2. RUTHLESS CUT
   For each feature, categorize it:
   - MUST HAVE: Without this, the product doesn't solve the core problem
   - NICE TO HAVE: Improves the experience but the product works without it
   - LATER: Cool idea, but irrelevant for version 1
   - NEVER: Sounds good in theory, adds complexity without real value

   Rule: The MUST HAVE list cannot exceed 5 features. If it does, cut harder.

3. MVP DEFINITION
   - Product: [Name] v0.1
   - One-sentence description of what this version does
   - The 3-5 must-have features with a one-line description of each
   - What it explicitly does NOT do (set expectations)

4. BUILD PLAN
   - Break each must-have feature into 2-4 tasks
   - Estimate time for each task based on my skill level
   - Total estimated build time
   - Suggested build order (what to tackle first and why)

5. LAUNCH CRITERIA
   - What has to be true before I can put this in front of real users?
   - List 3-5 specific checkboxes, not vague standards

6. SUCCESS METRIC
   - What single metric tells me if the MVP is working?
   - What number would make me say "worth continuing"?
   - What number would make me say "pivot or kill it"?

Be aggressive about cutting scope. The goal is not a complete product. The goal is the fastest path to learning whether anyone cares.
```

**Example Use Case:** You want to build an AI-powered meal planner for busy parents. Your feature list starts at 23 items including grocery delivery integration, nutritional tracking, and family preference profiles. This prompt cuts it to 4 features: input dietary restrictions, generate a 5-day dinner plan, output a grocery list, and a simple save/share function.

**Pro Tip:** After getting the MVP definition, ask: "What's the 'README version' -- the version I could ship in a single weekend using only tools I already know? No new frameworks, no new accounts, no infrastructure." Sometimes your MVP's MVP is the real starting point.

---

## 4. Product Launch Description Writer

**Best Model:** Claude

**When to Use:** You're about to launch on Product Hunt, Gumroad, a marketplace, or your own site and need a description that makes people click "get it."

**The Prompt:**

```
Write a product launch description for the following product. This will be used on [PLATFORM -- e.g., "Product Hunt," "Gumroad," "my website," "Indie Hackers"].

PRODUCT NAME: [NAME]
WHAT IT DOES: [2-3 SENTENCES]
WHO IT'S FOR: [SPECIFIC AUDIENCE]
PRICE: [FREE / FREEMIUM / ONE-TIME / SUBSCRIPTION -- include the number]
KEY FEATURES: [LIST 4-6 MAIN FEATURES]
WHAT MAKES IT DIFFERENT: [WHY SHOULD SOMEONE PICK THIS OVER ALTERNATIVES]
BUILT BY: [YOUR NAME/BRAND AND ONE LINE OF CREDIBILITY]
URL: [LINK]

Write the following versions:

1. SHORT TAGLINE (under 10 words)
   - Describes the outcome, not the mechanism

2. ONE-LINER (under 30 words)
   - Could stand alone as a tweet or subtitle

3. FULL DESCRIPTION (150-250 words)
   Structure:
   - Opening hook: Start with the problem or frustration (2 sentences)
   - What it does: Plain language, no jargon (2-3 sentences)
   - Key features: Bullet list, each one = benefit, not technical spec
   - Who it's for: Name the audience directly
   - Proof/credibility: Any numbers, results, testimonials, or builder credibility
   - CTA: Clear action with the link

4. FIRST COMMENT (for Product Hunt or similar)
   - 50-80 words, written in first person as the maker
   - Share why you built this, what problem it solves for you personally
   - End with an invitation for feedback, not a sales pitch

Rules:
- No "revolutionary," "powerful," "cutting-edge," or "seamless"
- No em dashes
- Write at a 7th-grade reading level
- Every sentence should earn its place. Cut anything that doesn't add information.
- Tone: confident, specific, human
```

**Example Use Case:** You built a Chrome extension that summarizes long email threads into 3 bullet points. You're launching it on Product Hunt tomorrow. This prompt gives you the tagline ("Stop re-reading email threads"), the one-liner, the full description, and the maker comment, all ready to paste.

**Pro Tip:** Write the "first comment" yourself using the AI version as a starting point. Maker comments that feel genuinely personal (mention a specific frustration that led to building it) get 2-3x more upvotes than polished corporate ones. Authenticity converts on launch platforms.

---

## 5. Early User Email Sequence

**Best Model:** Claude

**When to Use:** You have signups (waitlist, beta, or first customers) and need an automated email sequence that onboards them, builds trust, and converts.

**The Prompt:**

```
Write a 5-email welcome/onboarding sequence for early users of my product.

PRODUCT: [PRODUCT NAME AND WHAT IT DOES]
AUDIENCE: [WHO SIGNED UP -- e.g., "freelancers who joined the waitlist" or "beta testers"]
THEIR CURRENT STATE: [WHAT THEY JUST DID TO ENTER THIS SEQUENCE -- signed up, purchased, joined waitlist]
GOAL OF THE SEQUENCE: [e.g., "get them to complete setup and use the product once" or "keep waitlist warm until launch"]
MY VOICE: [DESCRIBE IN 3-5 WORDS -- e.g., "casual, direct, slightly funny"]
SENDER NAME: [YOUR NAME OR BRAND NAME]

Write these 5 emails:

EMAIL 1: Welcome (send immediately)
- Subject line
- Confirm what they signed up for
- Set expectations: what happens next, when they'll hear from you
- One clear action to take right now (not three)
- Keep under 100 words

EMAIL 2: Quick Win (send Day 2)
- Subject line
- Show them one specific thing they can do in under 5 minutes
- Include the exact steps (numbered, 3-5 steps max)
- End with what they'll have accomplished
- Keep under 150 words

EMAIL 3: The Story Behind It (send Day 4)
- Subject line
- Brief personal story: why you built this, what problem you were solving for yourself
- Make it relatable, not impressive
- Subtle credibility without bragging
- Ask one question to invite a reply
- Keep under 200 words

EMAIL 4: Social Proof or Use Case (send Day 7)
- Subject line
- Share a real result, example, or use case
- If you don't have customer results yet, describe your own results or a hypothetical that's clearly labeled
- Show the before/after or time saved
- Include a specific number
- Keep under 150 words

EMAIL 5: Feedback Ask or Upgrade Nudge (send Day 10)
- Subject line
- If waitlist: "We're opening [X] spots this week" or progress update
- If beta: Ask for specific feedback (not "how's it going?" but "what's one thing you wish it did?")
- If paid: Introduce the next tier or feature
- Make it easy to reply
- Keep under 120 words

Rules for all emails:
- Subject lines under 50 characters (mobile-friendly)
- No em dashes
- No emojis in subject lines or body
- No "Hey [FIRST_NAME]!" as the opener for every email. Vary the openings.
- Each email should have exactly one purpose and one CTA
- Write like a person, not a brand. These should feel like they came from a founder's inbox, not a marketing platform.
- Include a P.S. line on emails 3 and 5 (P.S. lines get read even when the rest is skimmed)
```

**Example Use Case:** You launched a Notion template for tracking client projects. 87 people joined your waitlist. You need a sequence that keeps them engaged, gets them excited, and converts them when you open access. Email 1 confirms their spot, Email 3 tells the story of why you built it (you lost a $4,000 client because of missed deadlines), Email 5 opens early access.

**Pro Tip:** Email 3 (the story email) will get the most replies. Make it genuine. The people who reply to that email are your best early users, your future testimonials, and your product feedback loop. Reply to every single one personally.

---

## 6. Workflow Automation Designer

**Best Model:** Claude

**When to Use:** You're doing the same thing manually every week and want to automate it, but you don't know where to start or what tools to connect.

**The Prompt:**

```
I have a repetitive task I want to automate. Help me design the workflow.

THE TASK I DO MANUALLY:
[DESCRIBE THE TASK STEP BY STEP. BE SPECIFIC. e.g., "Every Monday I check 3 competitor websites for new blog posts, copy the titles and URLs into a spreadsheet, then write a summary of what they published and email it to my team."]

HOW OFTEN: [DAILY / WEEKLY / WHEN TRIGGERED BY X]
TIME IT TAKES MANUALLY: [e.g., "45 minutes each time"]
TOOLS I ALREADY USE: [LIST YOUR CURRENT TOOLS -- e.g., "Google Sheets, Gmail, Slack, Notion"]
AUTOMATION TOOLS I HAVE ACCESS TO: [e.g., "Zapier free plan," "Make.com," "n8n," "none, suggest one"]
TECHNICAL SKILL LEVEL: [BEGINNER / INTERMEDIATE / ADVANCED -- for automation, not coding]
BUDGET FOR TOOLS: [e.g., "$0," "$20/month," "whatever it takes"]

Design the automation:

1. WORKFLOW MAP
   - Break the manual process into discrete steps
   - For each step, identify: trigger, action, and output
   - Show the flow: Step 1 -> Step 2 -> Step 3 (use plain text, not diagrams)

2. TOOL RECOMMENDATIONS
   - For each step, recommend the specific tool/integration
   - Explain why that tool (not just "use Zapier" but "use Zapier's RSS trigger because it can monitor website feeds without an API")
   - Note any free vs. paid considerations

3. AUTOMATION BLUEPRINT
   - The complete workflow in a numbered sequence
   - For each step: Tool | Trigger/Action | Input | Output
   - Flag any steps that still need manual input and explain why

4. SETUP INSTRUCTIONS
   - Step-by-step setup guide for someone at my skill level
   - Estimated setup time
   - Common pitfalls and how to avoid them

5. WHAT CAN'T BE AUTOMATED
   - Be honest about which parts still need a human
   - Suggest how to minimize the manual portion

6. TIME SAVINGS
   - Current time spent: [X] per [frequency]
   - Estimated time after automation: [Y] per [frequency]
   - Annual time saved: [Z] hours
   - If I value my time at $[HOURLY_RATE], that's $[ANNUAL_SAVINGS] per year

Give me the simplest version that works first. I can add complexity later.
```

**Example Use Case:** Every Friday, you manually pull data from 3 client dashboards, paste it into a Google Sheet, calculate week-over-week changes, format it into a summary, and email it to each client. This takes 2 hours. The prompt designs a workflow using Make.com that pulls data via API, populates the sheet automatically, generates the summary with AI, and sends personalized emails. Setup time: 3 hours. Weekly time after: 5 minutes of review.

**Pro Tip:** Start by automating 80% and keep 20% manual. Full automation sounds great but it's fragile. Build in a "human review" step before anything goes to a client or gets published. You can remove it later once you trust the system.

---

## 7. Pricing Strategy Analyzer

**Best Model:** Claude

**When to Use:** You built something and now you're staring at a blank pricing page wondering if you should charge $9 or $49 or give it away for free.

**The Prompt:**

```
Help me figure out the right pricing strategy for my product.

PRODUCT: [WHAT YOU'RE SELLING]
TARGET CUSTOMER: [WHO BUYS THIS -- be specific about their budget reality]
WHAT IT REPLACES: [WHAT ARE THEY DOING/PAYING FOR NOW -- e.g., "doing it manually," "paying a VA $500/month," "using a free but clunky tool"]
VALUE DELIVERED: [WHAT OUTCOME DOES THE USER GET -- time saved, money made, pain removed. Include numbers if you have them.]
MY COSTS: [WHAT DOES IT COST YOU TO DELIVER/MAINTAIN -- hosting, API costs, time, etc.]
COMPETITORS: [LIST 2-4 COMPETITORS AND THEIR PRICES IF YOU KNOW THEM]
MY GOAL: [e.g., "maximize revenue," "get 1,000 users fast," "cover costs and grow slowly"]

Analyze and recommend:

1. PRICING MODEL OPTIONS
   For each of these models, explain whether it fits my product and why:
   - One-time purchase
   - Monthly subscription
   - Annual subscription (with discount)
   - Freemium (free tier + paid upgrade)
   - Usage-based (pay per use)
   - Credit/token system
   Recommend the top 2 models for my situation.

2. PRICE POINT ANALYSIS
   - Floor price: The minimum I should charge to be taken seriously and cover costs
   - Ceiling price: The maximum the market will bear based on competition and value
   - Sweet spot: Your recommended price with reasoning
   - Show the math: At [price] x [realistic conversion rate] x [realistic traffic/leads], monthly revenue = $[X]

3. TIER STRUCTURE (if subscription or freemium)
   - Design 2-3 tiers with names, prices, and features
   - Each tier should have a clear "who is this for" description
   - The free/low tier should be useful enough to attract users but limited enough to create upgrade desire
   - Identify the "upgrade trigger" -- what makes someone move to the next tier

4. PRICING PSYCHOLOGY
   - Should I anchor high or start low? Why?
   - Should I show the "per day" or "per month" price?
   - Should I offer a free trial? If so, how long and with what limitations?
   - Any pricing page tactics specific to my type of product

5. LAUNCH PRICING STRATEGY
   - Should I launch at full price or discounted? By how much?
   - How long should the launch discount last?
   - How to transition early users to full price without backlash

6. RED FLAGS
   - What pricing mistakes would kill this product?
   - What signals should I watch for that indicate my price is wrong (too high or too low)?

Be specific with numbers. "It depends" is not a useful answer. Make assumptions where needed and state them clearly.
```

**Example Use Case:** You built an AI tool that generates social media captions from product photos. Your competitors charge $10-30/month. Your API costs are $0.02 per generation. Your target users are small Etsy and Shopify sellers who make $2,000-10,000/month. This prompt recommends a $12/month plan with 100 generations (covers your costs at 10x margin), a free tier with 5/day to get traction, and a Pro tier at $29/month for power sellers.

**Pro Tip:** After getting the pricing analysis, ask: "Now pretend you're a potential customer earning [TARGET INCOME] per month. You see this pricing page. What's your gut reaction? What would make you pay? What would make you leave?" This flips the perspective and catches blind spots in your pricing logic.

---

## 8. Customer Survey and Feedback Analyzer

**Best Model:** Claude

**When to Use:** You need to understand what your users actually want (before building), or you have feedback and need to make sense of it.

**The Prompt:**

```
I need help with customer feedback. Here's my situation:

MY PRODUCT/IDEA: [WHAT YOU'RE BUILDING OR SELLING]
MY AUDIENCE: [WHO YOU'RE ASKING]
MY GOAL: [WHAT DECISION WILL THIS FEEDBACK INFORM -- e.g., "what to build next," "whether to pivot," "how to price it"]

TASK: [CHOOSE ONE]

OPTION A: DESIGN A SURVEY
Create a short customer survey (max 8 questions) that will give me actionable data.

Requirements:
- Mix of question types: multiple choice, scale (1-5), and 1-2 open-ended
- First question should be easy and non-threatening (warm-up)
- Include one question that reveals willingness to pay
- Include one question I wouldn't think to ask but should
- For each question: explain what insight it gives me and how I'll use the answer
- Keep the entire survey completable in under 3 minutes
- Write a brief intro message (2 sentences) explaining why I'm asking and what they get in return
- Write a thank-you message with a next step

OPTION B: ANALYZE EXISTING FEEDBACK
Here is the feedback I've collected:

[PASTE SURVEY RESPONSES, EMAILS, REVIEWS, SUPPORT TICKETS, SOCIAL COMMENTS, OR ANY RAW FEEDBACK]

Analyze it and produce:
1. TOP THEMES: Group the feedback into 3-5 themes. For each: the theme, how many people mentioned it, representative quotes.
2. SENTIMENT BREAKDOWN: Overall positive/negative/neutral split with percentages.
3. FEATURE REQUESTS: Ranked list of what people are asking for, by frequency.
4. PAIN POINTS: The 3 biggest frustrations, with specific language people used.
5. SURPRISES: Anything unexpected or contradictory in the data.
6. RECOMMENDED ACTIONS: Based on this feedback, what are the top 3 things I should do? Be specific and prioritize by impact.
7. WHAT'S MISSING: What questions should I ask next that this feedback doesn't answer?

Be honest about sample size limitations. If I only have 12 responses, don't pretend the data is statistically significant. Tell me what it suggests and what I'd need to confirm it.
```

**Example Use Case (Option A):** You're about to launch a tool that helps freelancers track project hours. Before building the invoicing feature, you want to survey your 40 beta users to see if they'd actually use it. The prompt designs a 7-question survey that reveals 68% would pay extra for invoicing, but only if it integrates with QuickBooks.

**Example Use Case (Option B):** You collected 53 responses from your beta testers via a Google Form. The raw data is a mess. You paste it in and get a structured analysis showing that "mobile access" is the most requested feature (mentioned by 71% of respondents), but the feedback also reveals that 40% don't understand how to use the export function, which is a bigger problem to fix first.

**Pro Tip:** For surveys, always include one open-ended question: "What's the one thing you wish [PRODUCT] did that it doesn't?" This single question will consistently surface your best product ideas. People will tell you exactly what to build if you ask the right way.

---

## 9. Competitor Comparison Framework

**Best Model:** Claude

**When to Use:** You need to understand your competitive landscape clearly, either for your own strategy or to create a comparison page that helps buyers choose you.

**The Prompt:**

```
Build a competitor comparison framework for my product.

MY PRODUCT: [NAME AND BRIEF DESCRIPTION]
MY TARGET CUSTOMER: [WHO BUYS THIS]
MY PRICE: [YOUR PRICING]

COMPETITORS (list 3-6):
[For each competitor, include what you know: name, URL, price, what they do, strengths you've noticed, weaknesses you've noticed. It's fine if some info is missing.]

1. [COMPETITOR 1]: [DETAILS]
2. [COMPETITOR 2]: [DETAILS]
3. [COMPETITOR 3]: [DETAILS]

Produce the following:

1. COMPARISON TABLE
   Create a feature-by-feature comparison table with these columns:
   | Feature/Criteria | My Product | Competitor 1 | Competitor 2 | Competitor 3 |

   Include rows for:
   - Core functionality (3-5 rows)
   - Pricing (monthly, annual, free tier)
   - Target user
   - Ease of use (your honest assessment)
   - Integrations / ecosystem
   - Support quality (if known)
   - Unique differentiator

   Use checkmarks, X marks, and brief notes. Not paragraphs.

2. POSITIONING MAP
   Place each product (including mine) on two axes:
   - X axis: [SUGGEST THE MOST RELEVANT SPECTRUM -- e.g., "Simple <-> Feature-rich"]
   - Y axis: [SUGGEST THE MOST RELEVANT SPECTRUM -- e.g., "Budget <-> Premium"]
   Describe each product's position in one sentence.

3. WHERE I WIN
   - 3 specific scenarios where my product is the clear best choice
   - For each: the user profile, their situation, and why they pick me

4. WHERE I LOSE
   - 3 specific scenarios where a competitor wins over me
   - For each: the user profile, their situation, and what I'd need to change

5. STRATEGIC GAPS
   - What is nobody in this space doing well?
   - What customer segment is underserved?
   - What's the one feature or angle that could separate me from the pack?

6. OBJECTION HANDLING
   - For each competitor, write the one-sentence answer to: "Why should I choose you over [COMPETITOR]?"
   - Be factual, not dismissive. Acknowledge their strength, then pivot to your advantage.

Do not fabricate features or capabilities. If you don't have enough info about a competitor, say "[VERIFY]" and tell me what to check.
```

**Example Use Case:** You're building an AI writing tool for e-commerce product descriptions. Your competitors are Jasper, Copy.ai, and a smaller tool called Descriptionly. This prompt produces a comparison table showing Jasper is feature-rich but expensive ($49/month), Copy.ai has a good free tier but generic output, and Descriptionly is niche but has no integrations. Your gap: Shopify-native integration with product photo analysis.

**Pro Tip:** Update this comparison quarterly. Competitors change their pricing, add features, and shift positioning constantly. A comparison you built 6 months ago is probably wrong in at least 3 places. Set a calendar reminder.

---

## 10. Social Proof and Testimonial Request System

**Best Model:** Claude or ChatGPT-4o

**When to Use:** You need testimonials but don't know how to ask, or you have raw feedback and need to turn it into persuasive social proof for your site.

**The Prompt:**

```
Help me build a system for collecting and using social proof for my product.

MY PRODUCT: [WHAT YOU SELL]
MY CUSTOMERS: [WHO USES IT]
CURRENT SOCIAL PROOF: [WHAT I HAVE NOW -- "nothing," "a few nice emails," "12 reviews on Gumroad," etc.]
WHERE I'LL USE IT: [WEBSITE, LANDING PAGE, SALES PAGE, SOCIAL MEDIA, PRODUCT HUNT, ALL OF THE ABOVE]

TASK: [CHOOSE ONE OR BOTH]

PART 1: TESTIMONIAL REQUEST TEMPLATES
Write 3 different testimonial request messages:

A. THE QUICK ASK (for happy customers, sent via email or DM)
   - Under 60 words
   - Specific: don't ask "can you write a testimonial?" -- ask a targeted question that naturally produces a usable quote
   - Include 2-3 guiding questions so they don't stare at a blank text box

B. THE STRUCTURED ASK (for detailed case study-style testimonials)
   - A short form or questionnaire (5-6 questions)
   - Questions should pull out: the problem they had before, what they tried, why they chose you, specific results, who they'd recommend it to
   - Easy to answer in 5 minutes

C. THE FOLLOW-UP (for people who agreed but haven't sent anything)
   - Gentle, not pushy
   - Under 40 words
   - Include an easy out: "Even a one-sentence response helps"

For all templates:
- No guilt-tripping or excessive flattery
- No em dashes
- Make it easy for them to say yes with minimal effort

PART 2: TESTIMONIAL POLISHING
Take the following raw testimonials/feedback and polish them for use on my website:

[PASTE RAW TESTIMONIALS, EMAILS, REVIEWS, OR COMMENTS]

For each one:
1. A polished pull-quote (1-2 sentences, keeps their voice but tightens the language)
2. A headline version (under 10 words, captures the key impact)
3. Where to use it: hero section, pricing page, feature section, or social media
4. What makes this testimonial effective (or what's missing)
5. A follow-up question I could ask this person to get an even stronger quote

Rules:
- Never fabricate or exaggerate. Polish, don't rewrite.
- Flag any testimonial that's too vague to be useful ("Great product!" is not usable social proof)
- Prioritize testimonials that include specific numbers, outcomes, or before/after comparisons
```

**Example Use Case:** You have an AI scheduling tool with 200 users. You've gotten 4 nice emails from users but never asked for formal testimonials. This prompt gives you 3 request templates (one for quick DMs, one for a detailed form, one follow-up), plus polishes the 4 emails into pull-quotes like: "Cut my scheduling time from 2 hours to 15 minutes every week." -- Sarah M., Freelance Consultant.

**Pro Tip:** The best time to ask for a testimonial is immediately after a user gets a win. Set up an automated trigger: when someone completes their 10th session, hits a milestone, or sends a positive support reply, fire off the Quick Ask template within 24 hours. Timing beats persuasion.

---

## 11. Weekly Project Accountability Check-In

**Best Model:** Any

**When to Use:** Every Sunday night or Monday morning. Forces you to be honest about what you actually did, what slipped, and what matters this week.

**The Prompt:**

```
Run my weekly side project accountability check-in. Be direct and hold me to my commitments.

PROJECT: [YOUR SIDE PROJECT NAME AND ONE-LINE DESCRIPTION]
WEEK OF: [DATE]

LAST WEEK'S COMMITMENTS (what I said I'd do):
[LIST THE 3-5 THINGS YOU COMMITTED TO LAST WEEK]

WHAT ACTUALLY HAPPENED:
[HONEST ACCOUNT OF WHAT YOU DID, WHAT YOU DIDN'T, AND WHY]

HOURS SPENT THIS WEEK: [NUMBER]
TARGET HOURS: [NUMBER]

CURRENT BLOCKERS: [ANYTHING STOPPING YOU -- technical, motivational, life stuff]

WINS (even small ones):
[LIST ANYTHING THAT WENT RIGHT]

Produce my accountability report:

1. COMPLETION SCORECARD
   - For each commitment from last week: DONE / PARTIAL / MISSED
   - No sugarcoating. If I said I'd do 5 things and did 2, say "2 out of 5. 40% completion rate."

2. HONEST ASSESSMENT
   - What's the real reason things slipped? Not the excuse, the actual reason.
   - Am I spreading too thin, avoiding hard tasks, or dealing with legitimate blockers?
   - Is the project moving forward, stalling, or sliding backward?

3. THIS WEEK'S PRIORITIES
   - Based on what happened (and didn't happen), recommend my top 3 priorities for this week
   - Each priority: specific, measurable, completable in the available hours
   - At least one should be the most important thing I've been avoiding

4. ONE HARD QUESTION
   - Ask me one question I probably don't want to answer about this project
   - Something that forces me to confront whether I'm on the right track

5. MOMENTUM SCORE (1-10)
   - 1 = project is basically dead
   - 5 = treading water
   - 10 = shipping fast and learning
   - Give the score with a one-sentence justification

Format: Keep it tight. This should take me 2 minutes to read and immediately know what to do this week.
```

**Example Use Case:** You committed to finishing the landing page, writing 3 blog posts, and setting up payment integration. You finished the landing page, wrote 1 blog post, and didn't touch payments because you got distracted redesigning the logo. The accountability report says: "2.5 out of 5. 50% completion. You spent time on a logo nobody will see instead of payments that generate revenue. This week: payments first, second blog post, third blog post. The logo is a LATER task."

**Pro Tip:** Do this check-in at the same time every week. Consistency matters more than length. If you skip a week, the prompt for the following week should include: "I skipped last week's check-in. Why?" The act of writing down why you skipped is usually more valuable than the check-in itself.

---

## 12. Pivot or Kill Decision Framework

**Best Model:** Claude

**When to Use:** Your side project isn't working and you need a structured way to decide: push through, change direction, or shut it down.

**The Prompt:**

```
I need to make a hard decision about my side project. Help me think through it clearly.

PROJECT: [NAME AND DESCRIPTION]
HOW LONG I'VE BEEN WORKING ON IT: [TIMELINE]
TOTAL TIME INVESTED: [HOURS]
TOTAL MONEY INVESTED: [DOLLARS]
CURRENT TRACTION: [USERS, REVENUE, SIGNUPS, ENGAGEMENT -- whatever metrics you have, even if they're small]
WHAT I EXPECTED BY NOW: [WHAT YOU THOUGHT WOULD HAPPEN BY THIS POINT]
WHAT ACTUALLY HAPPENED: [THE REALITY]
MY EMOTIONAL STATE: [BE HONEST -- "frustrated," "still excited," "dreading working on it," "conflicted"]
WHAT'S STILL WORKING: [ANY BRIGHT SPOTS, EVEN SMALL ONES]
WHAT'S CLEARLY NOT WORKING: [THE STUFF YOU KNOW IS BROKEN]

Run this analysis:

1. REALITY CHECK
   - Gap analysis: Expected vs. actual across key metrics
   - Trend direction: Are things getting better, worse, or flat?
   - Effort-to-result ratio: How much input is producing how much output?
   - Be specific with numbers. No hand-waving.

2. ROOT CAUSE DIAGNOSIS
   - Is this a product problem (built the wrong thing)?
   - Is this a market problem (right product, wrong audience)?
   - Is this a distribution problem (right product, right audience, they just don't know about it)?
   - Is this an execution problem (haven't given it a real shot yet)?
   - Is this a timing problem (too early, too late)?
   - Pick the most likely root cause and explain your reasoning.

3. THREE OPTIONS WITH HONEST ASSESSMENT

   OPTION A: PUSH THROUGH
   - What would need to change in the next 30 days to justify continuing?
   - Specific milestones that would prove momentum
   - What am I committing to if I choose this?

   OPTION B: PIVOT
   - Based on what I've learned, what's the smartest pivot?
   - What can I keep (code, users, brand, knowledge)?
   - What would the pivoted version look like in one sentence?
   - How long before I'd know if the pivot is working?

   OPTION C: KILL IT
   - What do I salvage (skills learned, content created, relationships built, code I can reuse)?
   - What should I do with existing users/customers?
   - How do I shut it down cleanly?
   - What's the next best use of my time?

4. SUNK COST CHECK
   - Am I continuing because the project has potential, or because I've already invested [X] hours and $[Y]?
   - If I were starting fresh today with no history, would I choose this project?

5. THE DECISION MATRIX
   Score each option (Push / Pivot / Kill) on:
   | Criteria | Push Through | Pivot | Kill |
   | Likelihood of success in 90 days (1-10) | | | |
   | Alignment with my goals (1-10) | | | |
   | Energy and motivation level (1-10) | | | |
   | Opportunity cost (1-10, higher = lower cost) | | | |
   | Total | | | |

6. RECOMMENDATION
   - Based on the analysis, what should I do? Give a clear answer.
   - If "Pivot," be specific about what the pivot is.
   - If "Push," be specific about the 30-day plan.
   - If "Kill," be specific about what to do next.
   - One sentence on what I should remember from this project regardless of the decision.

Don't be gentle. I need clarity, not comfort. The worst outcome is spending another 3 months on something I should have stopped or changed today.
```

**Example Use Case:** You've spent 4 months and $800 building an AI resume builder. You have 31 signups but zero paying customers. You expected 200 signups and $500 MRR by now. The analysis reveals the root cause is distribution (you haven't done real marketing, just posted twice on LinkedIn), not product. The recommendation: Push through with a 30-day marketing sprint. If you don't hit 10 paying users by day 30, kill it. The product works. Nobody knows it exists.

**Pro Tip:** Run this prompt when you're calm, not when you just had a bad day. Frustration distorts your "what actually happened" section. Write the inputs on a Saturday morning with coffee, not at 11pm after a failed feature deploy. The quality of the decision depends entirely on the honesty of the inputs.

---

## How to Use These Prompts

**Fill in every bracket.** Vague inputs produce vague outputs. The more specific you are about your situation, the more useful the analysis. "I'm building an app" gives you generic advice. "I'm building a $12/month meal planning tool for parents of toddlers with food allergies" gives you something actionable.

**Run them in sequence.** These prompts work together. Start with Prompt 1 (validate), move to Prompt 3 (scope the MVP), then Prompt 2 (landing page), then Prompt 5 (email sequence). Each output feeds the next.

**Revisit, don't just run once.** Prompt 7 (pricing) should be revisited every time you get 50 more users. Prompt 11 (check-in) is weekly. Prompt 12 (pivot/kill) is quarterly. These aren't one-and-done exercises.

**Edit the output.** AI gets you 80% of the way. The last 20% is your judgment, your market knowledge, and the details only you have. Use these as thinking tools, not decision-makers.

---

*Built by BuildsByBen. AI prompts for people who build things.*
