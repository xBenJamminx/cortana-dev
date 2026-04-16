# Session Handoff

- **Topic:** Infrastructure / FAM
- **What we were doing:** Fixed Cortana and MiMoo after Anthropic cut off Claude subscriptions from openclaw (2026-04-04). Both servers migrated to `openai-codex/gpt-5.4-mini`. Also ran the April 6 and April 7 meeting briefings manually because Cortana's behavior degraded on GPT.
- **Status:** Done. Both servers running. Meeting briefings delivered.
- **Key context:**
  - Cortana and MiMoo are now on `openai-codex/gpt-5.4-mini` — authenticated with benjoselson@gmail.com OpenAI account
  - Claude Max plan staying on 20x ($200/month) — Ben uses Claude Code heavily for work
  - Cortana's behavior on GPT is degraded vs Sonnet: she confuses meeting briefing with FAM sync, mixes meeting data across sessions, makes excuses instead of using tools
  - Server CLAUDE.md updated with explicit meeting briefing process including: use `client.py meeting <id>` for full transcript, use `-` bullets not `•`, never auto-post, action items from transcript not summary
  - Meeting briefing format fully documented in `memory/feedback_meeting_briefing.md`
  - Tram works under Steven (old memory had this wrong — corrected)
