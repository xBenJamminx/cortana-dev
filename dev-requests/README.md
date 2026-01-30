# Dev Requests for Claude Code

Cortana writes requests here. Claude Code (via Ben) picks them up and implements them.

## How to create a request

Create a new  file with this format:

```markdown
# Request: [Short Title]

## Priority
high / medium / low

## Type
feature / bugfix / refactor / research

## Description
What needs to be done and why.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Context
Any relevant files, errors, or background info.

## Status
pending / in-progress / completed / blocked
```

## Workflow
1. Cortana creates a request file (e.g., `001-add-bookmark-api.md`)
2. Ben tells Claude Code to "check Cortana's dev requests"
3. Claude Code implements, tests, and marks complete
4. Claude Code writes results to `/root/clawd/dev-requests/completed/`

---
*"I'll handle the ops. You handle the code."* — Cortana
