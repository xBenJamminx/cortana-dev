# Prompt Pack: Everyday Life & Organization

**12 AI Prompts for the Stuff That Eats Your Time**

By BuildsByBen

---

These prompts handle the life logistics that pile up when you're busy building, working, or just trying to keep things running. Meal planning, budgets, travel, home stuff, health routines. All the things you know you should organize but never have time to sit down and figure out.

Every prompt is copy-paste ready. Fill in the [BRACKETS], paste it into the recommended model, and get a usable answer in under 60 seconds.

---

## 1. Weekly Meal Plan with Grocery List

**Best Model:** Claude

**When to Use:** Sunday planning session, or any time you're staring into the fridge wondering what to make this week.

**The Prompt:**

```
Create a 7-day meal plan (dinner only OR all 3 meals based on my preference below) with a consolidated grocery list.

Household details:
- Number of people eating: [NUMBER]
- Dietary restrictions or preferences: [e.g., no shellfish, vegetarian, low-carb, none]
- Meals to plan: [DINNER ONLY / BREAKFAST + LUNCH + DINNER]
- Budget range for the week: [e.g., $75-100]
- Cooking skill level: [BEGINNER / INTERMEDIATE / ADVANCED]
- Max cooking time per meal: [e.g., 30 minutes]
- Cuisine preferences: [e.g., Mexican, Italian, Asian, no preference]
- Ingredients I already have: [LIST WHAT'S IN YOUR FRIDGE/PANTRY]

Rules:
- Reuse overlapping ingredients across meals to reduce waste and cost
- No obscure ingredients that require a specialty store
- Include estimated prep + cook time for each meal
- Group the grocery list by store section (produce, dairy, meat, pantry, frozen)
- Include quantities, not just item names
- Flag any meals that freeze well for batch cooking
- Keep it simple on weeknights, save anything ambitious for weekends
```

**Example Use Case:** You have two adults and a picky 6-year-old, a $90 weekly budget, and half a bag of rice plus some chicken thighs already in the freezer. You want dinners only, nothing over 30 minutes on weeknights.

**Pro Tip:** Paste your results back in and ask "Which 2 meals can I batch-cook on Sunday to save time during the week?" This turns a meal plan into a meal prep plan.

---

## 2. Budget Analysis and Spending Optimizer

**Best Model:** ChatGPT (handles tables and numbers well)

**When to Use:** You just looked at your bank statement and want to know where the money actually went and what to cut.

**The Prompt:**

```
Analyze my monthly spending and find realistic ways to save money without making my life miserable.

Here's my monthly breakdown:
- Monthly take-home income: [AMOUNT]
- Rent/Mortgage: [AMOUNT]
- Utilities (electric, gas, water, internet): [AMOUNT]
- Groceries: [AMOUNT]
- Dining out / takeout: [AMOUNT]
- Subscriptions (list them): [e.g., Netflix $15, Spotify $11, gym $50, etc.]
- Transportation (gas, car payment, transit): [AMOUNT]
- Insurance (health, car, home/renters): [AMOUNT]
- Shopping / miscellaneous: [AMOUNT]
- Savings currently: [AMOUNT]
- Debt payments: [AMOUNT]
- Other: [ANYTHING ELSE]

My financial goal: [e.g., save $500/month, pay off $8K credit card, build 3-month emergency fund]
Timeline: [e.g., 6 months, 1 year]

Rules:
- Don't tell me to stop buying coffee. Give me real, impactful changes.
- Rank suggestions by dollar impact, highest first
- For each suggestion, give the estimated monthly savings
- Flag any subscriptions that overlap in function
- Compare my spending ratios to the 50/30/20 rule and tell me where I'm off
- If I'm spending more than 30% on housing, acknowledge it but focus on what I CAN control
- Give me a revised monthly budget that hits my goal
```

**Example Use Case:** You make $5,200/month after taxes, spend $1,800 on rent, and somehow have $200 left at the end of every month. You want to find $400/month to throw at a credit card.

**Pro Tip:** If you have your actual bank/credit card statement as a CSV or PDF, upload it directly and ask the model to categorize and analyze it. Way more accurate than estimating from memory.

---

## 3. Travel Itinerary Builder

**Best Model:** Gemini (strong with real-time info and maps context)

**When to Use:** You're planning a trip and want a day-by-day plan instead of 47 open browser tabs.

**The Prompt:**

```
Build a detailed day-by-day travel itinerary for my upcoming trip.

Trip details:
- Destination: [CITY/REGION/COUNTRY]
- Travel dates: [START DATE] to [END DATE]
- Travelers: [NUMBER OF ADULTS, NUMBER OF KIDS + AGES IF ANY]
- Budget level: [BUDGET / MID-RANGE / SPLURGE]
- Trip style: [RELAXED / MODERATE / PACKED SCHEDULE]
- Interests: [e.g., food, history, nature, nightlife, shopping, architecture, adventure sports]
- Must-see or must-do: [ANYTHING SPECIFIC YOU DON'T WANT TO MISS]
- Accommodation area/neighborhood: [IF ALREADY BOOKED, OR "recommend one"]
- Transportation: [RENTAL CAR / PUBLIC TRANSIT / WALKING / MIX]

Rules:
- Organize by day with morning, afternoon, and evening blocks
- Group nearby attractions together to minimize backtracking
- Include estimated time at each stop
- Add 1 restaurant recommendation per meal with cuisine type and price range
- Include 1 backup/rain plan per day
- Note anything that needs advance booking or tickets
- Flag which days are most physically demanding
- Leave buffer time, don't schedule every minute
- Include a packing reminder list specific to this destination and season
```

**Example Use Case:** 5-day trip to Lisbon, two adults, mid-range budget, you love food and history but hate tourist traps. You're staying in Alfama and using public transit.

**Pro Tip:** After getting the itinerary, follow up with "Create a Google Maps list of every location you mentioned with addresses." Copy those into a saved Google Maps list and you've got a tap-to-navigate trip plan on your phone.

---

## 4. Home Maintenance Schedule

**Best Model:** Claude

**When to Use:** You own or rent a home and want to stop forgetting about things until they become expensive emergencies.

**The Prompt:**

```
Create a complete home maintenance schedule organized by month for the full year.

Home details:
- Home type: [HOUSE / CONDO / APARTMENT / TOWNHOUSE]
- Approximate age of home: [YEARS]
- Location/climate: [CITY OR REGION, e.g., "Northeast US, cold winters"]
- Heating system: [GAS FURNACE / HEAT PUMP / ELECTRIC / BOILER / OTHER]
- Cooling system: [CENTRAL AC / WINDOW UNITS / MINI SPLITS / NONE]
- Yard: [YES - SIZE / NO]
- Pool: [YES / NO]
- Septic or sewer: [SEPTIC / MUNICIPAL SEWER]
- Any known issues: [e.g., old roof, drafty windows, water heater from 2012]

Rules:
- Organize by month, January through December
- For each task, include: what to do, estimated time, DIY difficulty (easy/moderate/call a pro), and estimated cost if hiring someone
- Flag seasonal-critical tasks that have a narrow window (like winterizing pipes or AC tune-ups)
- Include filter replacement schedules for HVAC, water, fridge, dryer vent
- Add appliance lifespan estimates for anything I listed with an age
- Separate "DIY this weekend" tasks from "schedule a professional" tasks
- Include a quarterly deep-clean checklist
- At the end, give me a list of supplies to keep on hand year-round
```

**Example Use Case:** You bought a 1985 colonial in Connecticut last year. Gas furnace, central AC, half-acre yard. You have no idea what you're supposed to be maintaining and when.

**Pro Tip:** Ask it to convert the final schedule into a format you can paste into Google Calendar, Notion, or whatever you use. Monthly recurring reminders beat a static list you'll forget about.

---

## 5. Personalized Gift Idea Generator

**Best Model:** Claude

**When to Use:** Someone's birthday, anniversary, or holiday is coming up and you want a gift that shows you actually thought about it.

**The Prompt:**

```
Generate 10 personalized gift ideas ranked by how memorable and thoughtful they'd feel to the recipient.

About the recipient:
- Who they are to me: [e.g., wife, brother, best friend, coworker, dad]
- Age: [APPROXIMATE]
- Their interests and hobbies: [LIST 3-5 THINGS THEY GENUINELY ENJOY]
- Something they've mentioned wanting or needing recently: [IF ANYTHING]
- Their personality: [e.g., practical, sentimental, adventurous, homebody, minimalist]
- What they already have too much of: [e.g., candles, gift cards, books]
- Occasion: [BIRTHDAY / ANNIVERSARY / HOLIDAY / JUST BECAUSE]
- My budget: [$MIN - $MAX]

Rules:
- No generic suggestions like "a nice candle" or "a gift card to their favorite store"
- Each idea should connect to something specific about them, not just their category (don't give me "a book" for someone who reads, give me a specific book and why)
- Include a mix: 3 physical gifts, 3 experience gifts, 2 personalized/custom items, 2 wildcard surprises
- For each gift, include: what it is, estimated cost, where to get it, and a 1-sentence reason why it fits this person
- Flag anything that needs to be ordered in advance with lead time
- If my budget is under $30, lean creative over cheap-looking
```

**Example Use Case:** Your wife's birthday is in 3 weeks. She's into yoga, true crime podcasts, and cooking. She's a practical minimalist who hates clutter. Budget is $50-150.

**Pro Tip:** Mention one specific recent conversation or moment. "She said last week she wished she could take a pottery class" gives the AI a thread to pull that produces dramatically better suggestions than just listing hobbies.

---

## 6. Negotiation Prep Playbook

**Best Model:** Claude

**When to Use:** Before any conversation where money is on the table: car dealership, salary review, contractor quote, rent renewal, medical bill, or canceling a subscription.

**The Prompt:**

```
Help me prepare for a negotiation. Give me a complete playbook I can review before walking in (or getting on the call).

Situation:
- What I'm negotiating: [e.g., new car purchase, salary raise, contractor quote for kitchen remodel, rent increase, medical bill]
- The other party: [WHO, e.g., car dealer, my manager, a roofing company, landlord]
- What they're asking / current offer: [THEIR NUMBER OR TERMS]
- What I want to get to: [MY TARGET NUMBER OR TERMS]
- My walk-away point: [THE WORST DEAL I'D STILL ACCEPT]
- My leverage: [ANYTHING THAT GIVES ME POWER, e.g., competing offers, long tenure, cash payment, flexibility on timing]
- Their likely leverage: [WHAT THEY MIGHT USE AGAINST ME]
- Relationship importance: [ONE-TIME TRANSACTION / ONGOING RELATIONSHIP]
- My negotiation experience: [BEGINNER / SOME EXPERIENCE / COMFORTABLE]

Rules:
- Give me the 3 strongest arguments for my position with specific talking points
- Anticipate their 3 most likely counter-arguments and give me responses for each
- Provide a specific opening statement I can use or adapt
- Include 2-3 strategic concessions I can offer that cost me little but feel valuable to them
- List common tactics they might use (anchoring, urgency, guilt) and how to handle each
- Give me exact phrases for: asking for more time, redirecting pressure, and saying no politely
- Include a "if they say X, you say Y" quick-reference section
- Tell me the single biggest mistake people make in this specific type of negotiation
```

**Example Use Case:** A contractor quoted $18,000 for a bathroom remodel. You got two other quotes at $14,500 and $15,200. You want this contractor because of their reviews but need the price closer to $15,000.

**Pro Tip:** After the negotiation, paste the outcome back in and ask "What could I have done differently?" Building a personal negotiation playbook from real results makes you sharper every time.

---

## 7. Custom Fitness and Health Routine

**Best Model:** ChatGPT

**When to Use:** You want a workout or health routine designed around your actual life, not a generic "5 days a week, 90 minutes" plan you'll abandon in a week.

**The Prompt:**

```
Design a realistic fitness and health routine I'll actually stick to.

About me:
- Age: [AGE]
- Current fitness level: [SEDENTARY / LIGHTLY ACTIVE / MODERATELY ACTIVE / VERY ACTIVE]
- Any injuries, limitations, or health conditions: [LIST OR "NONE"]
- Primary goal: [e.g., lose 20 lbs, build muscle, improve energy, reduce back pain, general health]
- Secondary goal: [e.g., sleep better, reduce stress, improve flexibility]
- Available time per day: [MINUTES]
- Days per week I can work out: [NUMBER]
- Equipment available: [e.g., full gym, dumbbells at home, nothing, just bodyweight]
- Activities I enjoy: [e.g., walking, swimming, cycling, lifting, yoga]
- Activities I hate: [LIST THEM, SERIOUSLY]
- Current diet situation: [e.g., mostly healthy, fast food 3x/week, skip breakfast, no idea where to start]
- Biggest obstacle: [e.g., motivation, time, energy after work, don't know what to do]

Rules:
- Build the plan around my available time, not an ideal scenario
- Include specific exercises with sets, reps, and rest times (not just "do cardio")
- Provide a week 1-4 progression so I'm not doing the same thing forever
- Include a 5-minute warm-up and cool-down for each session
- Add 3 nutrition adjustments ranked by impact (not a full meal plan, just the 3 changes that move the needle most)
- Give me 1 habit to add per week for the first 4 weeks instead of overhauling everything at once
- Include a "bare minimum" version for days when motivation is zero
- No fitness jargon without explanation
```

**Example Use Case:** You're 38, sit at a desk all day, have bad knees, and can realistically commit to 25 minutes, 4 days a week with a pair of dumbbells at home. You want to lose weight and stop your back from hurting.

**Pro Tip:** Ask for a "Level 0" version: the absolute minimum you should do on days you don't want to do anything. Having a 5-minute fallback routine prevents all-or-nothing thinking, which is what kills most fitness plans.

---

## 8. Structured Learning Plan for a New Skill

**Best Model:** Claude

**When to Use:** You want to learn something new but don't know where to start or how to structure it so you actually make progress instead of watching random YouTube videos.

**The Prompt:**

```
Create a structured learning plan for me to go from zero to competent in a new skill.

What I want to learn: [SKILL, e.g., Spanish, photography, Excel, woodworking, investing, cooking]
Why: [YOUR MOTIVATION, e.g., travel to Mexico in 6 months, career change, personal interest]
Time I can dedicate: [HOURS PER WEEK]
Deadline or target date: [DATE OR "no deadline, just steady progress"]
My starting level: [COMPLETE BEGINNER / SOME BASICS / INTERMEDIATE WANTING TO LEVEL UP]
Learning style preference: [VIDEO / READING / HANDS-ON PRACTICE / MIX]
Budget for courses or tools: [$AMOUNT OR "free only"]

Rules:
- Break it into phases (Foundation, Building, Applying, Refining) with clear milestones for each
- Give me specific resources for each phase: name the course, book, YouTube channel, or app (not "find a good tutorial")
- Include weekly goals, not just a topic list
- Add practice exercises or projects at the end of each phase that prove I've actually learned something
- Estimate total time to reach each milestone
- Include 3 common mistakes beginners make and how to avoid them
- Give me a "minimum viable skill" definition: what's the smallest useful version of this skill I can reach fastest?
- If there are certifications or portfolio pieces worth pursuing, mention them
- Include 1 community or forum where I can ask questions and get feedback
```

**Example Use Case:** You want to learn Excel beyond basic spreadsheets because your job keeps requiring it. You can do 4 hours a week, you're an intermediate who knows formulas but not pivot tables or VLOOKUP, and you'd prefer video tutorials.

**Pro Tip:** After completing each phase, paste your notes back in and ask "Based on what I struggled with, what should I focus on next?" This turns a static plan into an adaptive curriculum.

---

## 9. Event Planning Checklist and Timeline

**Best Model:** Claude

**When to Use:** You're hosting something and need a complete plan with timeline, not just a vague idea that you'll "figure out closer to the date."

**The Prompt:**

```
Create a complete event planning checklist with a countdown timeline so nothing falls through the cracks.

Event details:
- Type of event: [e.g., kid's birthday party, dinner party for 8, backyard BBQ, holiday gathering, anniversary dinner, graduation party]
- Date: [DATE]
- Number of guests: [NUMBER]
- Venue: [HOME / RENTED SPACE / RESTAURANT / OUTDOOR]
- Budget: [$AMOUNT]
- Vibe or theme: [e.g., casual, elegant, themed, no theme]
- Food plan: [COOKING MYSELF / CATERING / POTLUCK / ORDERING]
- Ages of attendees: [e.g., all adults, mixed with kids ages 3-7, mostly 30s-40s]
- Any must-haves: [e.g., specific dietary needs, activities, entertainment]
- Things I'm stressed about: [WHAT WORRIES YOU MOST ABOUT THIS EVENT]

Rules:
- Build a reverse timeline: what to do 4 weeks out, 2 weeks out, 1 week out, 3 days before, day before, day of, and day after
- Include a complete supply/shopping list organized by where to buy (grocery store, party store, Amazon)
- Give me a food and drink quantity calculator based on my guest count
- Include a day-of hour-by-hour schedule
- Add a music/playlist suggestion that fits the vibe
- Budget breakdown: allocate my total budget across food, drinks, decor, entertainment, and buffer
- Include a cleanup plan (this always gets forgotten)
- Flag anything that needs to be ordered or booked NOW based on my event date
```

**Example Use Case:** Your kid is turning 7 in 3 weeks. You're hosting 15 kids and their parents at your house. Budget is $300. You need a plan because right now all you've done is pick the date.

**Pro Tip:** Ask it to generate the invite text too, including RSVP deadline and any info guests need (parking, what to bring, allergy heads-up). One less thing on your plate.

---

## 10. Decluttering and Organization System

**Best Model:** Claude

**When to Use:** A room, closet, garage, or your entire house feels chaotic and you want a system, not just "throw stuff away."

**The Prompt:**

```
Create a realistic decluttering and organization plan I can actually follow without losing a whole weekend to it.

What I'm organizing: [e.g., master closet, garage, kitchen, kids' playroom, home office, entire apartment]
Current state: [MILDLY CLUTTERED / PRETTY BAD / DISASTER ZONE]
Time I can dedicate: [MINUTES PER DAY OR HOURS PER WEEKEND]
My organizing style: [VISUAL (I NEED TO SEE EVERYTHING) / HIDDEN (CLEAN SURFACES, STUFF IN BINS) / MINIMAL (GET RID OF MOST OF IT)]
Biggest pain point: [e.g., can never find anything, too much stuff for the space, no system for incoming items]
Budget for storage/organization products: [$AMOUNT OR "use what I have"]
Past attempts: [WHAT I'VE TRIED AND WHY IT DIDN'T STICK]

Rules:
- Break it into sessions of [MY AVAILABLE TIME], not one marathon day
- Use the 4-box method (keep, donate, trash, relocate) but adapt it to my specific space
- Give me a decision framework for items I'm unsure about (specific questions to ask myself, not just "does it spark joy")
- Recommend specific storage solutions with product names and approximate prices, not just "get some bins"
- Include a maintenance system: daily 5-minute, weekly 15-minute, and monthly 30-minute routines to keep it organized
- Address the inflow problem: how to stop accumulating new clutter
- Prioritize by impact: start with the change that will feel the biggest difference first
- If I have kids, include realistic kid-friendly systems that they can actually maintain
- No shame, no judgment, just systems
```

**Example Use Case:** Your garage has become a dumping ground for 3 years of "I'll deal with it later." You have 2 hours on Saturday mornings and $100 for storage solutions. You want to park a car in there again.

**Pro Tip:** Take a "before" photo and paste it in (Claude and ChatGPT accept images). The AI can spot specific problem areas and suggest layout changes you might not think of when you're standing in the middle of the mess.

---

## 11. Insurance and Service Comparison Analysis

**Best Model:** ChatGPT

**When to Use:** You need to compare quotes, plans, or service providers and make a decision based on more than just the monthly price.

**The Prompt:**

```
Help me compare these options and make a smart decision. I don't want to just pick the cheapest one and regret it later.

What I'm comparing: [e.g., health insurance plans, car insurance quotes, internet providers, phone plans, home warranty companies, credit cards]

Option 1: [NAME]
- Monthly cost: [AMOUNT]
- Key features/coverage: [LIST WHAT'S INCLUDED]
- Deductible/fees: [IF APPLICABLE]
- Contract length: [IF APPLICABLE]
- Anything notable: [PERKS, DRAWBACKS, FINE PRINT YOU NOTICED]

Option 2: [NAME]
- [SAME FORMAT]

Option 3: [NAME]
- [SAME FORMAT]

(Add more options if you have them)

My priorities ranked:
1. [MOST IMPORTANT, e.g., low out-of-pocket costs, reliable coverage, speed, flexibility]
2. [SECOND MOST IMPORTANT]
3. [THIRD]

My situation: [RELEVANT CONTEXT, e.g., healthy 35-year-old, family of 4, work from home, drive 25K miles/year]

Rules:
- Build a side-by-side comparison table
- Calculate the TRUE annual cost for each option (not just monthly x 12, include deductibles, fees, typical usage costs)
- Flag hidden costs or gotchas in each option
- Score each option against my ranked priorities
- Tell me which option wins overall AND which option wins on pure value
- If none of these options are great, tell me what to look for instead
- Include 3 questions I should ask each provider before signing
```

**Example Use Case:** You're picking between 3 health insurance plans during open enrollment. One has low premiums but a $6,000 deductible. Another costs $200/month more but covers everything after $1,500. You have a kid who goes to the doctor regularly.

**Pro Tip:** If you can export or screenshot the plan details, upload them directly instead of retyping. Most comparison errors come from accidentally leaving out a detail when copying info by hand.

---

## 12. Morning and Evening Routine Optimizer

**Best Model:** Claude

**When to Use:** Your mornings are chaotic, your evenings are unstructured, and you want a routine that works with your life instead of a productivity influencer's fantasy schedule.

**The Prompt:**

```
Design a realistic morning and evening routine based on my actual life, not an idealized version of it.

My situation:
- Wake-up time: [TIME]
- Time I need to leave the house (or start work): [TIME]
- Bedtime goal: [TIME]
- Other people in my morning routine: [e.g., getting 2 kids ready for school, partner leaves at 7, nobody else]
- Current morning: [DESCRIBE WHAT ACTUALLY HAPPENS NOW, HONESTLY]
- Current evening: [SAME]
- What I wish I had time for: [e.g., exercise, reading, journaling, meal prep, actual breakfast, 10 minutes of quiet]
- What's non-negotiable: [e.g., kids' school prep, dog walk, morning coffee ritual]
- Biggest morning friction point: [WHAT MAKES YOUR MORNING FALL APART]
- Biggest evening time-waster: [BE HONEST]
- Energy pattern: [MORNING PERSON / NIGHT OWL / DEPENDS ON SLEEP]

Rules:
- Build the routine in 5-minute blocks so I can see exactly where time goes
- Don't add anything without removing or shortening something else. I don't have hidden free time.
- Include a "prep the night before" section that makes mornings easier
- Give me a transition ritual between work and personal time (even if it's just 5 minutes)
- Build in 1 buffer block for when things go sideways (because they will)
- Start with a "week 1" version that changes just 2-3 things, not a complete overhaul
- Include trigger-based habits (after I do X, I do Y) instead of time-based ones
- Be honest about trade-offs: if I want to add morning exercise, tell me what has to give
- No "wake up at 5 AM" advice unless I specifically asked for it
```

**Example Use Case:** You wake up at 6:30, need to be at your desk by 8:30, and currently spend 20 minutes scrolling your phone in bed before rushing through everything. You want to add a 15-minute workout and actual breakfast but have no idea where the time comes from.

**Pro Tip:** Track your actual routine for 3 days first, noting exact times (6:32 alarm, 6:45 out of bed, 6:47 phone scrolling...). Paste that data in. The gap between what you think you do and what you actually do is where all the time savings hide.

---

## How to Get the Most Out of These Prompts

1. **Fill in every bracket.** The more specific your input, the more useful the output. "I like food" gets you generic results. "I love Thai and Mexican but hate seafood and my partner is vegetarian" gets you a meal plan you'll actually cook.

2. **Iterate, don't restart.** After you get the first result, reply with what you'd change. "This is good but make the workouts shorter" or "Swap Thursday's dinner for something kid-friendly." The second pass is always better than the first.

3. **Save what works.** When a prompt gives you a great result, save the filled-in version somewhere. Next time you need it, you're 30 seconds from an updated plan instead of starting from scratch.

4. **Combine prompts.** The meal plan feeds into the budget analysis. The learning plan connects to the routine optimizer. These work together. Use them that way.