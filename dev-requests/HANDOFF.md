# Cortana ↔ Claude Code Handoff Protocol

## For Cortana

### To request development work:
1. Create a file: 
2. Use this format:



3. Ben will say "check cortana" and Claude Code will handle it.

### To check results:
- Read  for finished work
- Each completed request includes what was changed

---

## For Claude Code

When Ben says "check cortana":
1. SSH to clawdbot
2. List files in /root/clawd/dev-requests/*.md (not README or HANDOFF)
3. Read any with Status: pending
4. Implement the request
5. Move file to /completed/ with results appended
6. Report back to Ben

---

## Quick Reference

| Who | Action | Location |
|-----|--------|----------|
| Cortana | Write request | /root/clawd/dev-requests/XXX-name.md |
| Claude | Check requests | "check cortana" |
| Claude | Write results | /root/clawd/dev-requests/completed/ |
| Cortana | Read results | /root/clawd/dev-requests/completed/ |

