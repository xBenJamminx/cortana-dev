---
name: seo-content-engine
description: "SEO and digital marketing expert for analyzing and creating high-performing content. Use when asked to: (1) Analyze content for SEO optimization, (2) Write SEO-optimized blog posts, articles, or landing pages, (3) Create viral or shareable social media content, (4) Generate headline/title options, (5) Create content briefs for keywords, (6) Improve content shareability or engagement, (7) Write platform-specific content (LinkedIn, Twitter/X, Reddit, email), (8) Audit meta titles/descriptions, or any task involving SEO, content marketing, virality, or digital engagement optimization."
---

# SEO Content Engine

Expert system for SEO-optimized, viral, shareable content.

## Core Workflows

### Workflow 1: SEO Content Analysis

When analyzing existing content:

1. **Identify target keyword** — Ask if not provided
2. **Run SEO audit** — See `references/seo-checklist.md` for full criteria
3. **Score content** — Rate 1-10 on: keyword optimization, search intent match, structure, readability, E-E-A-T signals
4. **Provide actionable fixes** — Prioritize by impact (high/medium/low)

Output format:
```markdown
## SEO Analysis: [Content Title]

**Target Keyword:** [keyword]
**Overall Score:** X/10

### Strengths
- [what's working]

### Critical Issues (Fix First)
- [high-impact problems]

### Optimization Opportunities
- [medium-impact improvements]

### Quick Wins
- [easy fixes]
```

### Workflow 2: SEO Content Creation

When creating new content:

1. **Clarify brief** — Target keyword, search intent, audience, content type, desired length
2. **Research intent** — Determine if informational, navigational, transactional, or commercial
3. **Structure content** — Use search-intent-appropriate format
4. **Write with SEO principles** — Natural keyword integration, proper headers, internal link opportunities
5. **Add viral elements** — See `references/viral-patterns.md` for hooks and emotional triggers
6. **Output as markdown file**

### Workflow 3: Viral Content Creation

When creating shareable/viral content:

1. **Identify platform** — LinkedIn, Twitter/X, Reddit, blog, email
2. **Select viral pattern** — See `references/viral-patterns.md`
3. **Apply platform-specific rules** — See `references/platform-guides.md`
4. **Craft hook** — First line must stop the scroll
5. **Build tension/value** — Middle delivers on hook's promise
6. **End with engagement driver** — CTA, question, or share trigger

### Workflow 4: Headline Generation

When asked for headline/title options:

1. Generate 10+ options using formulas from `references/viral-patterns.md`
2. Mix emotional triggers: curiosity, FOMO, controversy, utility, social proof
3. Include variations: question, how-to, list, statement, command
4. Flag top 3 recommendations with reasoning

### Workflow 5: Content Brief Creation

When creating briefs for writers:

```markdown
## Content Brief: [Primary Keyword]

**Target Keyword:** [keyword]
**Secondary Keywords:** [list]
**Search Intent:** [informational/transactional/etc.]
**Target Word Count:** [range]
**Target Audience:** [description]

### Content Angle
[Unique perspective or hook]

### Required Sections
- H1: [suggested title]
- H2: [section]
- H2: [section]
- ...

### Key Points to Cover
- [point 1]
- [point 2]

### Internal Link Opportunities
- [relevant pages to link]

### Competitor Insights
- [what top results do well]
- [gaps to exploit]
```

## SEO Principles (Always Apply)

**Keyword Integration:**
- Primary keyword in: title, H1, first 100 words, 1-2 H2s, meta description, URL slug
- Keyword density: 1-2% (natural, not forced)
- Use semantic variations and LSI keywords throughout

**Search Intent Alignment:**
- Informational → comprehensive guides, how-tos, explanations
- Transactional → product pages, clear CTAs, trust signals
- Commercial → comparisons, reviews, "best of" lists
- Navigational → clear branding, direct answers

**Structure for SEO:**
- One H1 only (includes primary keyword)
- Logical H2/H3 hierarchy (outline should make sense standalone)
- Short paragraphs (2-4 sentences)
- Bucket brigades to maintain engagement ("Here's the thing:", "But wait:", "The result?")
- Featured snippet opportunities (definition boxes, numbered steps, tables)

**E-E-A-T Signals:**
- Experience: First-person insights, real examples, original data
- Expertise: Accurate information, technical depth when appropriate
- Authoritativeness: Cite sources, link to authoritative references
- Trustworthiness: Balanced perspective, acknowledge limitations

**Readability:**
- Target 8th-grade reading level for general content
- Active voice preferred
- Scannable: headers, bullets, bold key phrases
- Short sentences mixed with varied lengths

## Reference Files

- **`references/seo-checklist.md`** — Complete SEO audit criteria and scoring
- **`references/viral-patterns.md`** — Headline formulas, emotional triggers, hook templates
- **`references/platform-guides.md`** — Platform-specific optimization (LinkedIn, Twitter/X, Reddit, email)

Load these as needed based on the task.
