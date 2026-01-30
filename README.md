# Cortana → Claude Code

Dev requests from Cortana for Claude Code to implement.

## For Cortana

Create an issue when you need development work:

```bash
gh issue create --repo xBenJamminx/cortana-dev \
  --title "[Type] Short description" \
  --label "claude-code,pending" \
  --body "## Priority
high / medium / low

## Type
feature / bugfix / refactor

## Description
What needs to be done and why.

## Files
- /path/to/relevant/file.py

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

---
*Created by Cortana*"
```

## For Claude Code

When Ben says **"check cortana"**:

1. Check open issues: `gh issue list --repo xBenJamminx/cortana-dev --label pending`
2. Read the issue details
3. Implement the request
4. Comment with results and close the issue

## Repo
https://github.com/xBenJamminx/cortana-dev

---
*"I'll handle the ops. You handle the code."* — Cortana
