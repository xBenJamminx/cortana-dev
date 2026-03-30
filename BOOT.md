# Boot Sequence

On gateway startup, run this recovery checklist silently before responding to any user message:

1. Read memory/handoff.md — note what was happening and when
2. Check the last 5 messages in the active Telegram topic via telecrawl:
   cd /root/.openclaw/workspace && python3 -m core.telecrawl.cli recent --limit 5
3. If the handoff is stale (>1 hour old) but telecrawl shows recent conversation, use telecrawl context to orient yourself
4. Do NOT announce this process to Ben. Just know the context and respond naturally.
5. If you genuinely have no context after steps 1-3, say: "I just restarted and lost our thread. What were we working on?" — do NOT claim tools are broken or handoff is broken.
