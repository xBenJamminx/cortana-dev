# Claude Code Skills System -- Our Playbook

## What Are Skills?
A folder with a `SKILL.md` file that teaches Claude Code how to handle specific tasks. NOT the same as Cortana's operational tools in `/root/clawd/skills/`.

**Location:** `~/.claude/skills/` (personal, all projects) or `.claude/skills/` (project-specific)

## SKILL.md Format

```markdown
---
name: skill-name-kebab-case
description: What it does. Use when [trigger phrases]. Do NOT use for [negative triggers].
---

# Skill Name

## Instructions
### Step 1: ...
### Step 2: ...

## Examples
Example 1: [scenario]
User says: "..."
Actions: ...
Result: ...

## Troubleshooting
Error: [message]
Cause: [why]
Solution: [fix]
```

## Critical Rules
- File MUST be exactly `SKILL.md` (case-sensitive)
- Folder names: kebab-case only (no spaces, underscores, capitals)
- Description MUST include WHAT + WHEN (trigger phrases)
- No XML angle brackets in frontmatter
- No "claude" or "anthropic" in skill names
- Keep SKILL.md under 5,000 words
- Move detailed docs to `references/` directory

## Progressive Disclosure (3 levels)
1. **YAML frontmatter** -- always loaded in system prompt (keep lean)
2. **SKILL.md body** -- loaded when Claude thinks skill is relevant
3. **Linked files** -- Claude reads only as needed (references/, scripts/)

## Description Field (Most Important Part)
Structure: `[What it does] + [When to use it] + [Key capabilities]`

Good: "Manages sprint planning and task creation. Use when user mentions 'sprint', 'tasks', or 'project planning'."
Bad: "Helps with projects."

Add negative triggers to prevent over-triggering:
"Do NOT use for simple data exploration (use data-viz skill instead)."

## 5 Patterns
1. **Sequential Workflow** -- multi-step processes in specific order
2. **Multi-tool Coordination** -- workflows spanning multiple tools/MCPs
3. **Iterative Refinement** -- output quality improves with loops
4. **Context-aware Selection** -- same outcome, different tools by context
5. **Domain-specific Intelligence** -- specialized knowledge beyond tool access

## Optional Frontmatter Fields
- `license: MIT`
- `allowed-tools: "Bash(python:*) Read Grep"` -- restrict tool access
- `metadata:` -- author, version, tags, etc.
- `compatibility:` -- environment requirements

## Testing Checklist
- [ ] Triggers on obvious tasks
- [ ] Triggers on paraphrased requests
- [ ] Does NOT trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Error handling works

## Debug Tip
Ask Claude: "When would you use the [skill name] skill?" -- it'll quote the description back.

## Our Skills Directory
Location: `~/.claude/skills/`

| Skill | Status | Description |
|-------|--------|-------------|
| (to be built) | | |

## Airtable Content Pipeline Schema
Table: `tblvLSX7DZxIRWU5g` in base `appdFTSkXnphHLwfl`

| Field | Type | Options |
|-------|------|---------|
| Title | text | |
| Content | multiline | |
| Status | select | Idea, Draft, Review, Approved, Posted, Rejected |
| Type | select | Original, Reply, QT, Thread |
| Account | select | Cortana, Ben |
| Format | select | Tweet/Post, Thread, Short Video, Long Video, Article, Carousel |
| Scheduled | dateTime | |
| Posted URL | url | |
| Notes | multiline | |
| Platforms | select | X/Twitter, YouTube, LinkedIn, TikTok, Newsletter |
| Pillar | select | Build-in-Public, Discovery>Teaching, Retell, General |

**Always use the emoji prefix for Status:** `Idea`, `Draft`, `Review`, `Approved`, `Posted`, `Rejected`

## Content Lanes
- **Mon: Shipping Proof** (Build-in-Public)
- **Wed: DIY/Template** (steal this prompt format)
- **Fri: Operator Lessons** (systems, workflows)
- **Mindset/Psychology** (reframes, parenting, productivity)

## Source
- Anthropic PDF: `/tmp/anthropic-skills-guide.txt`
- SkillsMP: https://skillsmp.com
- Official repo: https://github.com/anthropics/skills
