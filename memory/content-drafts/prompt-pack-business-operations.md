# BuildsByBen Prompt Pack: Business Operations

**12 Production-Ready AI Prompts for Business Owners**

Use these prompts to handle the work that eats your day -- proposals, emails, reports, documentation. Copy, paste, fill in the brackets, and get output you can actually use.

Every prompt here was built for business owners, not developers. No technical setup required.

---

## 1. Client Proposal / Pitch Draft

**Category:** Client Work

**Best Model:** Claude or ChatGPT-4o

**When to Use:** A prospect said "send me a proposal" and you need a polished draft in 15 minutes instead of 3 hours.

**The Prompt:**

```
Write a professional client proposal for the following project.

Company name: [YOUR COMPANY NAME]
Client name: [CLIENT NAME / COMPANY]
Project summary: [2-3 SENTENCES DESCRIBING WHAT THE CLIENT NEEDS]
Key deliverables: [LIST THE MAIN THINGS YOU'LL DELIVER]
Timeline: [ESTIMATED DURATION, e.g., "6 weeks"]
Budget range: [DOLLAR AMOUNT OR RANGE]
Your differentiator: [WHY YOU OVER COMPETITORS -- 1-2 SENTENCES]

Structure the proposal with these sections:
1. Executive Summary (2-3 sentences max)
2. Understanding of the Problem (show you get their pain)
3. Proposed Solution (what you'll do, in plain language)
4. Deliverables & Timeline (table format)
5. Investment (present the price with confidence, no apologizing)
6. Why Us (brief, specific, no fluff)
7. Next Steps (clear call to action)

Tone: Professional but human. Confident without being salesy. Write like someone who has done this before and knows exactly what the client needs. Avoid jargon. Keep sentences short.

Do not use bullet points in the Executive Summary. Use a table for the timeline. Keep the entire proposal under 800 words.
```

**Example Use Case:** You're a marketing consultant and a local restaurant chain asked for a proposal on revamping their social media. You drop in the details and get a clean, structured proposal you can paste into a Google Doc and send within the hour.

**Pro Tip:** After generating the proposal, follow up with: "Now rewrite the 'Understanding of the Problem' section using specific language from this email the client sent me: [PASTE THEIR EMAIL]." This makes the proposal feel custom instead of templated.

---

## 2. Meeting Notes to Action Items

**Category:** Operations

**Best Model:** Any

**When to Use:** You just finished a 45-minute call and have a messy page of notes that need to become clear tasks with owners and deadlines.

**The Prompt:**

```
I just finished a meeting. Below are my raw notes. Extract and organize them into a structured summary.

Meeting context: [WHO WAS IN THE MEETING AND WHAT IT WAS ABOUT]
Date: [DATE]

Raw notes:
[PASTE YOUR MESSY NOTES, VOICE MEMO TRANSCRIPT, OR BULLET POINTS]

Produce the following:

1. MEETING SUMMARY (3-4 sentences covering what was discussed and any decisions made)

2. ACTION ITEMS (table format with these columns):
   | Action Item | Owner | Deadline | Priority |
   - Assign owners based on context from the notes
   - If a deadline wasn't stated, suggest a reasonable one and mark it with "(suggested)"
   - Priority: High / Medium / Low

3. DECISIONS MADE (bullet list of anything that was agreed upon or finalized)

4. OPEN QUESTIONS (anything unresolved that needs follow-up)

5. NEXT MEETING TOPICS (if any were mentioned or logically follow)

If an owner is unclear, mark it as "[TBD]". Do not invent details that aren't in the notes.
```

**Example Use Case:** You had a kickoff call with a new client. Your notes are half-sentences and abbreviations. You paste them in and get a clean summary you can share with the client as a "recap email" -- which makes you look extremely organized.

**Pro Tip:** If you use a transcription tool (Otter, Fathom, Fireflies), paste the full transcript instead of notes. Add to the prompt: "This is an auto-generated transcript, so ignore filler words, false starts, and off-topic tangents."

---

## 3. Competitive Analysis from a Company Website

**Category:** Strategy

**Best Model:** Claude or ChatGPT-4o (with browsing/web access enabled)

**When to Use:** You need to quickly understand what a competitor is doing, how they position themselves, and where the gaps are.

**The Prompt:**

```
Analyze the following competitor based on the information I provide. I need a strategic competitive breakdown I can use for positioning my own business.

Competitor name: [COMPETITOR NAME]
Their website: [URL]
What they sell: [BRIEF DESCRIPTION IF YOU KNOW IT]
My business: [YOUR BUSINESS NAME AND WHAT YOU DO]

Information from their site (paste key sections, pricing page, about page, or homepage copy):
[PASTE RELEVANT TEXT FROM THEIR WEBSITE]

Produce a competitive analysis with these sections:

1. POSITIONING SUMMARY: How do they describe themselves? What market are they targeting? What is their core value proposition in one sentence?

2. PRICING & PACKAGING: What are their tiers, pricing model, and what's included at each level? If pricing isn't public, note that.

3. STRENGTHS: What are they doing well based on their messaging, features, and positioning? Be specific.

4. WEAKNESSES / GAPS: What's missing, unclear, or poorly executed? Where is there an opening?

5. TARGET CUSTOMER: Who is their ideal customer based on their language and positioning?

6. KEY DIFFERENTIATORS vs. MY BUSINESS: Based on what you know about my business, where do I have an advantage? Where are they ahead?

7. STRATEGIC TAKEAWAYS: 3-5 specific, actionable things I should consider based on this analysis.

Be direct. No filler. If something is unclear from the provided info, say so rather than guessing.
```

**Example Use Case:** You're launching a bookkeeping service for freelancers and want to understand how Bench positions itself. You paste in their homepage copy, pricing page, and feature list. The output gives you a clear picture of their strengths and the gaps you can exploit.

**Pro Tip:** Run this prompt for 3-4 competitors, then follow up with: "Here are competitive analyses for 4 companies in my space. Identify the patterns across all of them -- what is everyone doing, and what is nobody doing? That's where my opportunity is."

---

## 4. Professional Email Response

**Category:** Communication

**Best Model:** Any

**When to Use:** You're staring at an email that needs a thoughtful reply and you don't want to spend 20 minutes wordsmithing.

**The Prompt:**

```
Write a professional email response based on the following.

The email I received:
[PASTE THE EMAIL YOU NEED TO REPLY TO]

Key points I want to make in my reply:
[BULLET LIST OF WHAT YOU WANT TO SAY]

Tone: [CHOOSE ONE: Friendly and warm / Professional and neutral / Firm but polite / Apologetic and solution-focused]

Additional context: [ANYTHING ELSE THE AI SHOULD KNOW -- RELATIONSHIP WITH THIS PERSON, SENSITIVE TOPICS, ETC.]

Requirements:
- Keep it under [NUMBER] sentences
- Start with a direct response to their main point, not a generic greeting
- End with a clear next step or call to action
- Do not use the phrase "I hope this email finds you well"
- Do not use exclamation marks
- Match the formality level of the original email
```

**Example Use Case:** A client sends a long email asking why a deliverable is late. Your bullet points: "Acknowledge the delay, explain the dependency on their team's feedback, propose new timeline, keep it constructive." You get a polished reply that's honest without being defensive.

**Pro Tip:** Add this line for tricky emails: "Before writing the reply, identify the sender's emotional state and primary concern in one sentence. Then write the response to address that concern first." This forces the AI to read between the lines before responding.

---

## 5. SOW / Scope of Work Generator

**Category:** Client Work

**Best Model:** Claude or ChatGPT-4o

**When to Use:** You've agreed on a project with a client and need to formalize the scope before work begins. This protects both of you.

**The Prompt:**

```
Generate a professional Scope of Work (SOW) document based on the following project details.

Project name: [PROJECT NAME]
Client: [CLIENT NAME / COMPANY]
Provider: [YOUR NAME / COMPANY]
Start date: [DATE]
End date: [DATE]
Project overview: [2-4 SENTENCES DESCRIBING THE PROJECT]

Deliverables:
[LIST EACH DELIVERABLE WITH A BRIEF DESCRIPTION]

What is NOT included (exclusions):
[LIST ANYTHING YOU WANT TO EXPLICITLY EXCLUDE FROM SCOPE]

Milestones:
[LIST KEY MILESTONES WITH TARGET DATES, OR SAY "suggest milestones based on the deliverables"]

Payment terms: [e.g., "50% upfront, 50% on completion" or "monthly retainer of $X"]
Revision policy: [e.g., "2 rounds of revisions included"]

Structure the SOW with these sections:
1. Project Overview
2. Objectives
3. Scope of Work (detailed deliverables, each with description and acceptance criteria)
4. Out of Scope (explicit exclusions)
5. Timeline & Milestones (table format)
6. Roles & Responsibilities (what you'll do vs. what the client is responsible for)
7. Payment Terms
8. Change Request Process (how scope changes are handled)
9. Assumptions (things that must be true for this timeline/budget to hold)
10. Acceptance & Sign-off (signature lines)

Write in clear, plain language. Avoid legalese. This should be understood by anyone without a law degree. Be specific in the deliverables -- vague SOWs cause scope creep.
```

**Example Use Case:** You're building a website for a local business. You know the project is 8 pages, includes SEO setup, and does NOT include ongoing content creation. This SOW makes that crystal clear before anyone starts working.

**Pro Tip:** Always fill in the "Out of Scope" and "Assumptions" sections yourself rather than letting the AI guess. These two sections prevent 90% of client disputes. Common assumptions: "Client will provide all copy by [date]," "Feedback will be returned within 3 business days."

---

## 6. Invoice Follow-Up Email

**Category:** Communication

**Best Model:** Any

**When to Use:** An invoice is overdue and you need to follow up without burning the relationship.

**The Prompt:**

```
Write an invoice follow-up email based on the following details.

Client name: [CLIENT NAME]
Invoice number: [INVOICE NUMBER]
Invoice amount: [DOLLAR AMOUNT]
Original due date: [DATE]
Days overdue: [NUMBER]
Services provided: [BRIEF DESCRIPTION OF WHAT THE INVOICE IS FOR]
Previous follow-ups: [NONE / ONE REMINDER SENT ON X DATE / MULTIPLE REMINDERS]
Relationship context: [e.g., "long-term client, first late payment" or "new client, second overdue invoice"]

Tone: Professional, direct, and respectful. Not passive-aggressive. Not apologetic. Assume it's an oversight unless the context says otherwise.

Requirements:
- Subject line included
- Reference the specific invoice number and amount
- State the due date clearly
- If this is a second or third follow-up, escalate the tone slightly while staying professional
- Include a specific ask (e.g., "Could you confirm payment will be sent by [DATE]?")
- Offer to resend the invoice or answer questions about it
- Keep it under 8 sentences
- Do not use phrases like "just following up" or "friendly reminder" or "touching base"
```

**Example Use Case:** Your invoice for $3,500 of consulting work is 12 days overdue. This is a good client who's never been late before. You get an email that's warm enough to preserve the relationship but direct enough to actually get paid.

**Pro Tip:** For invoices 30+ days overdue, add this to the prompt: "Include a mention of late payment terms from our agreement: [PASTE YOUR LATE PAYMENT CLAUSE]. Reference it matter-of-factly, not as a threat." Having this in your contract and referencing it calmly is the most effective collection technique there is.

---

## 7. Weekly Status Report from Bullet Points

**Category:** Operations

**Best Model:** Any

**When to Use:** It's Friday afternoon and you need to send a status update to a client or stakeholder. You have bullet points. You need a professional report.

**The Prompt:**

```
Turn my rough bullet points into a polished weekly status report.

Project: [PROJECT NAME]
Reporting period: [DATE RANGE, e.g., "Jan 27 - Jan 31, 2026"]
Audience: [WHO WILL READ THIS -- client, executive, internal team]

My rough notes:
[PASTE YOUR BULLET POINTS, INCOMPLETE SENTENCES, OR SHORTHAND]

Format the report with these sections:

1. STATUS AT A GLANCE
   - Overall status: [On Track / At Risk / Blocked] (determine this from my notes)
   - One-sentence summary

2. COMPLETED THIS WEEK
   - Clean bullet points of what got done
   - Group by workstream or category if there are more than 5 items

3. IN PROGRESS
   - What's actively being worked on and current state

4. BLOCKERS & RISKS
   - Anything slowing progress, with proposed resolution if I mentioned one
   - If none, say "No active blockers"

5. NEXT WEEK PRIORITIES
   - Top 3-5 items planned for next week

6. METRICS / KEY NUMBERS (only if my notes contain quantitative data)

Keep the language concise and results-oriented. No filler. Write for someone who will spend 90 seconds reading this. Bold the most important information in each section.
```

**Example Use Case:** You're managing a website migration for a client. Your notes say things like "DNS done, staging looks good, need final sign-off, images still loading slow on mobile." The output turns that into a report that makes you look like a seasoned project manager.

**Pro Tip:** Save a version of this prompt with your project name, audience, and formatting preferences pre-filled. When Friday comes, you only need to paste in that week's notes. Takes 2 minutes instead of 20.

---

## 8. Job Posting / Role Description

**Category:** Operations

**Best Model:** Claude or ChatGPT-4o

**When to Use:** You need to hire someone (full-time, part-time, or contractor) and want a posting that attracts the right people while filtering out the wrong ones.

**The Prompt:**

```
Write a job posting for the following role.

Role title: [JOB TITLE]
Company: [YOUR COMPANY NAME]
Company description: [1-2 SENTENCES ABOUT WHAT YOUR COMPANY DOES]
Employment type: [Full-time / Part-time / Contract / Freelance]
Location: [Remote / Hybrid / On-site in CITY]
Compensation: [SALARY RANGE OR HOURLY RATE, or "DOE" if you prefer]

What this person will do day-to-day:
[LIST 4-6 CORE RESPONSIBILITIES IN YOUR OWN WORDS]

Must-have qualifications:
[LIST HARD REQUIREMENTS -- BE HONEST ABOUT WHAT'S TRULY REQUIRED]

Nice-to-have qualifications:
[LIST THINGS THAT WOULD BE A BONUS BUT AREN'T DEALBREAKERS]

What makes this role unique or appealing:
[WHAT WOULD MAKE A GREAT CANDIDATE EXCITED ABOUT THIS? Be specific.]

Dealbreakers / who should NOT apply:
[ANY HONEST SIGNALS THAT THIS ISN'T THE RIGHT FIT]

Structure the posting as:
1. Opening hook (2-3 sentences that sell the opportunity, not the company)
2. About the Role
3. What You'll Do (bullet points)
4. What You Bring (requirements, split into must-have and nice-to-have)
5. What We Offer (compensation, benefits, perks, culture -- be specific, not generic)
6. How to Apply

Tone: Direct, honest, and specific. No corporate speak. No "fast-paced environment" or "wear many hats" or "rockstar" or "ninja." Write like a real person describing a real job to a real human. Include the salary range -- postings without pay ranges get 50% fewer applicants.
```

**Example Use Case:** You're a small agency owner hiring your first virtual assistant. You know they'll handle email, scheduling, light bookkeeping, and client onboarding. This prompt produces a posting that clearly describes the role and attracts organized, self-directed people.

**Pro Tip:** After generating the posting, ask: "Review this posting from the perspective of a highly qualified candidate. What questions would they have that this posting doesn't answer? What might make them hesitate to apply?" Then revise based on the feedback.

---

## 9. Process Documentation from Rough Notes

**Category:** Operations

**Best Model:** Claude

**When to Use:** You have a process that lives in your head (or in scattered notes) and you need it documented so someone else can follow it.

**The Prompt:**

```
Turn my rough notes into a clear, step-by-step process document that someone with no prior context could follow.

Process name: [NAME OF THE PROCESS, e.g., "New Client Onboarding"]
Who will use this document: [ROLE / PERSON, e.g., "New hire on the ops team"]
Tools involved: [LIST ANY SOFTWARE, PLATFORMS, OR TOOLS USED]

My rough notes / brain dump:
[PASTE EVERYTHING YOU KNOW ABOUT THIS PROCESS -- MESSY IS FINE. INCLUDE STEPS, EDGE CASES, THINGS YOU ALWAYS FORGET, TIPS, WARNINGS, LINKS, ETC.]

Create a process document with:

1. PURPOSE: One sentence on what this process accomplishes and why it matters.

2. WHEN TO USE: What triggers this process? (e.g., "When a new client signs a contract")

3. BEFORE YOU START: Prerequisites, access needed, tools to have open.

4. STEP-BY-STEP INSTRUCTIONS:
   - Numbered steps, each one a single clear action
   - Sub-steps where needed
   - Include specific details: which button to click, which field to fill in, what to name things
   - Flag common mistakes with "NOTE:" callouts
   - Include decision points: "If [X], do [Y]. If [Z], do [W]."

5. TROUBLESHOOTING: Common issues and how to fix them (based on anything I mentioned).

6. CHECKLIST VERSION: A condensed checklist (just the step titles, no details) for someone who's done this before and just needs a quick reference.

Write for someone doing this for the first time. Assume nothing. If my notes are ambiguous about a step, flag it with "[CLARIFY]" so I know to fill in the detail.
```

**Example Use Case:** You onboard 2-3 new clients per month and the process involves 15 steps across 4 different tools. Right now it's all in your head. This prompt turns your brain dump into a document you can hand to a VA or new team member.

**Pro Tip:** Test the document by reading it as if you've never done the process. Every time you think "well, obviously you'd..." that's a missing step. The best process docs are the ones that feel almost insultingly detailed.

---

## 10. Customer FAQ Generator from Product Info

**Category:** Communication

**Best Model:** Any

**When to Use:** You're launching a product or service and need a FAQ section for your website, sales page, or help center.

**The Prompt:**

```
Generate a comprehensive FAQ section based on the following product/service information.

Product/service name: [NAME]
What it does: [2-3 SENTENCE DESCRIPTION]
Target customer: [WHO IS THIS FOR]
Price: [PRICING DETAILS]
How it works: [BRIEF OVERVIEW OF THE PROCESS OR DELIVERY]

Additional details (paste any of the following that apply):
- Features list: [FEATURES]
- Limitations or restrictions: [WHAT IT DOESN'T DO]
- Delivery timeline: [HOW LONG IT TAKES]
- Refund/guarantee policy: [POLICY]
- Technical requirements: [IF ANY]
- Common objections you hear from prospects: [LIST THEM]

Generate 15-20 FAQs organized into these categories:

1. GENERAL (what it is, who it's for)
2. PRICING & BILLING (cost, payment, refunds)
3. HOW IT WORKS (process, delivery, timeline)
4. GETTING STARTED (onboarding, setup, requirements)
5. SUPPORT & TROUBLESHOOTING (what happens when something goes wrong)

For each FAQ:
- Write the question the way a real customer would ask it (conversational, not formal)
- Keep answers concise: 2-4 sentences max
- Include specific details (numbers, timelines, steps) wherever possible
- Address the underlying concern, not just the surface question
- If a question relates to a common objection, address it head-on without being defensive

Do not make up policies or details I haven't provided. If a question would require information I haven't given, include it but mark the answer with "[UPDATE WITH YOUR SPECIFIC DETAILS]."
```

**Example Use Case:** You're launching an online course on AI for small business owners. You paste in your course description, pricing, what's included, and the objections you keep hearing ("Is this too technical?", "What if I fall behind?"). You get a full FAQ section ready to drop into your sales page.

**Pro Tip:** After generating the FAQ, ask: "Which 5 of these questions are most likely to be asked by someone who is close to buying but hasn't committed yet? Move those to the top." Ordering your FAQ by purchase intent is a subtle conversion optimization most people miss.

---

## 11. Sales Call Prep / Research Brief

**Category:** Strategy

**Best Model:** Claude or ChatGPT-4o

**When to Use:** You have a sales call in 30 minutes and need to walk in prepared instead of winging it.

**The Prompt:**

```
Prepare a sales call research brief so I walk into this meeting informed and ready.

My business: [YOUR COMPANY AND WHAT YOU SELL]
Prospect company: [THEIR COMPANY NAME]
Prospect name and title: [THEIR NAME AND ROLE]
How the lead came in: [REFERRAL / INBOUND / COLD OUTREACH / NETWORKING EVENT / ETC.]
What I know so far: [ANY CONTEXT FROM EMAILS, THEIR WEBSITE, LINKEDIN, PREVIOUS CONVERSATIONS]

Their website: [URL]
Information from their site:
[PASTE KEY SECTIONS FROM THEIR WEBSITE -- ABOUT PAGE, SERVICES, TEAM PAGE, RECENT NEWS]

Their LinkedIn (if available):
[PASTE RELEVANT LINKEDIN PROFILE DETAILS OR RECENT POSTS]

Produce a one-page call prep brief with:

1. COMPANY SNAPSHOT: What they do, size estimate, target market, recent activity (based on provided info).

2. PROSPECT PROFILE: Their role, likely priorities, and what they probably care about based on their title and company.

3. LIKELY PAIN POINTS: Based on their industry and company type, what problems do they probably face that my offering solves? List 3-5, ranked by likelihood.

4. DISCOVERY QUESTIONS: 5 open-ended questions I should ask to uncover their specific needs. These should sound natural, not scripted. Start with broad context questions and narrow to specific pain.

5. VALUE ALIGNMENT: For each of my key offerings, map it to a likely pain point. Format: "If they say [X], position [Y]."

6. POTENTIAL OBJECTIONS: 3 likely objections and a concise response for each.

7. CONVERSATION STRUCTURE:
   - Opening (how to start without being generic)
   - Discovery phase (what to learn)
   - Value presentation (what to share)
   - Close (specific next step to propose)

Keep the entire brief scannable. I'll review this in 5 minutes before the call. Use bullet points, bold key phrases, and keep text tight.
```

**Example Use Case:** You sell AI automation services and you're about to get on a call with an operations manager at a 50-person e-commerce company. You paste in their website's about page and their LinkedIn. The brief tells you their likely pain points (manual order processing, inventory syncing, customer service volume) and gives you 5 discovery questions tailored to their situation.

**Pro Tip:** After the call, paste your notes back into the AI with: "Here's how the call actually went. Compare to the pre-call brief. What did we get right? What did we miss? Update the prospect profile based on what I learned." This builds a living profile you can use for the follow-up.

---

## 12. Quarterly Business Review Summary

**Category:** Strategy

**Best Model:** Claude or ChatGPT-4o

**When to Use:** End of quarter. You need to step back and look at the big picture -- what happened, what worked, what to change.

**The Prompt:**

```
Create a quarterly business review (QBR) summary based on the following data and notes.

Business: [YOUR BUSINESS NAME]
Quarter: [e.g., "Q4 2025"]
Previous quarter context: [1-2 SENTENCES ON HOW LAST QUARTER WENT, FOR COMPARISON]

Revenue / financial data:
[PASTE REVENUE NUMBERS, EXPENSES, PROFIT MARGINS, OR WHATEVER FINANCIAL DATA YOU TRACK]

Key metrics:
[PASTE ANY METRICS YOU TRACK -- CLIENTS ACQUIRED, CHURN, WEBSITE TRAFFIC, CONVERSION RATES, LEADS, ETC.]

Wins this quarter:
[LIST YOUR MAJOR WINS, ACCOMPLISHMENTS, MILESTONES]

Challenges / misses:
[LIST WHAT DIDN'T GO WELL, GOALS YOU MISSED, PROBLEMS THAT CAME UP]

Projects / initiatives status:
[LIST MAJOR PROJECTS AND WHETHER THEY'RE COMPLETE, IN PROGRESS, OR STALLED]

Team / capacity notes:
[ANY CHANGES TO TEAM, HIRING, BANDWIDTH ISSUES]

Produce a QBR with these sections:

1. EXECUTIVE SUMMARY: 3-4 sentences capturing the quarter. Lead with the most important takeaway, not a recap.

2. FINANCIAL OVERVIEW:
   - Revenue vs. previous quarter (calculate % change if data allows)
   - Key financial metrics in a table
   - Trend analysis: heading in the right direction or not?

3. PERFORMANCE SCORECARD:
   - Table with: Metric | Target | Actual | Status (On Track / Behind / Exceeded)
   - If I didn't provide targets, note that and just show actuals with directional indicators

4. TOP WINS: The 3-5 most impactful accomplishments with brief context on why they matter.

5. CHALLENGES & LESSONS: What went wrong and, more importantly, what the lesson is. Don't sugarcoat.

6. STRATEGIC INSIGHTS: Based on the data, what 2-3 patterns or trends should I pay attention to? What does the data suggest about where the business is heading?

7. NEXT QUARTER PRIORITIES: Recommend 3-5 focus areas for next quarter based on this review. Be specific and tie each one back to something in the data.

8. DECISIONS NEEDED: Flag any decisions that this review surfaces -- things I need to commit to, stop doing, or change.

Write with the directness of an advisor who has seen the numbers and is giving their honest assessment. No fluff. If something is going poorly, say so clearly with a recommendation attached.
```

**Example Use Case:** You're a freelance consultant. Q4 revenue was $42K (up from $31K in Q3), you landed 3 new retainer clients, but your project margins dropped because you underpriced two fixed-bid projects. The QBR turns this into a structured review that shows you exactly where to focus in Q1.

**Pro Tip:** Do this even if you're a one-person operation. Especially if you're a one-person operation. Nobody is going to give you a performance review. This is how you give one to yourself. Save each QBR in the same folder so you can see the trajectory across quarters. After your second QBR, add to the prompt: "Here is last quarter's QBR for comparison: [PASTE IT]. Call out what improved and what didn't."

---

## How to Get the Most From These Prompts

**Fill in every bracket.** The more context you provide, the better the output. Vague input produces generic output. Specific input produces usable output.

**Iterate, don't restart.** If the first output is 80% right, tell the AI what to fix: "Make the tone more direct," "Add a section on timeline," "The pricing section is too vague -- here's the actual breakdown." One follow-up message usually gets you from good to great.

**Save your customized versions.** Once you've tuned a prompt for your business, save it. Next time you need it, the only thing you're changing is the project-specific details.

**Match the model to the task.** Quick emails and formatting tasks work fine with any model. Complex analysis, long-form writing, and nuanced strategy work better with Claude or ChatGPT-4o.

---

*Built by BuildsByBen. AI prompts for people who build things.*
