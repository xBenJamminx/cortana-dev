# Content Pipeline Skill

Save all content to Airtable content pipeline. **NO LOCAL FILES**.

## When to Use

ALWAYS use this when:
- Creating content drafts (articles, posts, tweets, threads)
- Saving content ideas
- Storing any written content

NEVER use Write tool for content. This is THE ONLY WAY.

## Workflow

1. **Show content in chat first** - Let Ben see it
2. **Get approval/feedback**  
3. **Save to Airtable** using this tool

## Usage

\`\`\`bash
/root/clawd/scripts/content-to-airtable.py \"<title>\" \"<content>\" [status] [type]
\`\`\`

## Parameters

- **title** (required): Content title/headline
- **content** (required): Full content body
- **status** (optional): Draft (default), Ready, Scheduled, Published
- **type** (optional): Article (default), Tweet, Thread, Post, Idea

## Examples

### Article Draft
\`\`\`bash
/root/clawd/scripts/content-to-airtable.py \
  \"10 Lessons from Building AI Agents\" \
  \"Here's what I learned after 6 months...\" \
  \"Draft\" \
  \"Article\"
\`\`\`

### Tweet Idea
\`\`\`bash
/root/clawd/scripts/content-to-airtable.py \
  \"AI agents replacing workflows\" \
  \"The best AI agents don't assist you. They replace entire workflows.\" \
  \"Ready\" \
  \"Tweet\"
\`\`\`

### Content Idea
\`\`\`bash
/root/clawd/scripts/content-to-airtable.py \
  \"Video: How I built Cortana\" \
  \"Behind the scenes of building an AI operator...\" \
  \"Idea\" \
  \"Video\"
\`\`\`

## Output

Returns JSON with success status and Airtable record link:

\`\`\`json
{
  \"success\": true,
  \"record_id\": \"recXXXXXXX\",
  \"message\": \"✅ Content saved to Airtable: 10 Lessons...\",
  \"url\": \"https://airtable.com/appgqpqWgN7BcvKQ1/...\"
}
\`\`\`

## CRITICAL RULES

1. **ALWAYS show content in chat first** before saving
2. **NEVER use Write tool** for content
3. **NEVER save content as .md files**
4. **Content goes to Airtable** - no exceptions

Breaking these rules = personality drift. Stay sharp.
