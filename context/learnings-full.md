# Context: Full Learnings Archive

All mistakes logged with corrections. Top 5 most relevant are in CLAUDE.md.

## 1. Don't hallucinate diagnoses -- check the simple explanation first
Wrong input > bad config > broken API. Verify your own inputs before blaming the system.

## 2. Never guess phone numbers or identifiers
If you don't know it, check the config or ask. vapi-call defaults to Ben's number with no args.

## 3. Sleep video title cards need separate dark images
Generate a purpose-built dark image (deep navy, charcoal). Darken to 75% minimum. Never reuse scene images.

## 4. Don't sugarcoat or spin when giving advice
Give the honest assessment upfront, including risks. Don't make Ben push back to get the real answer.

## 5. Verify actual cause before diagnosing
Don't assume from memory. Confirm with the user before building strategy on assumptions.

## 6. Context window is a resource -- treat it like disk space
Read BRAIN.md for state. Only load what the task needs. Heavy work to subagents. Update BRAIN.md after.

## 7. Heartbeats should be fast, not thorough
Target <3 seconds. Check for messages, respond if needed, HEARTBEAT_OK if not.

## 8. Check BRAIN.md before doing work -- don't duplicate
Read BRAIN.md, check workspace, grep for related files. Build on existing work.

## 9. Always spawn background sub-agents -- stay available
Default: acknowledge task, spawn background agent, stay responsive. Only inline for 1-2 step tasks.

## 10. Kill stale Claude processes after SSH test commands
`ps aux | grep claude | grep -v grep`. Kill anything not the active openclaw session.

## 11. Server migration: snapshot + new server, not in-place resize
Snapshot -> new server -> verify -> update configs -> delete old.

## 12. run_in_background: true DOES NOT WORK with CLI backend
Children killed when parent claude -p exits. Use spawn_task.sh instead.

## 13. Silent compaction hang -- reduce resume watchdog timeout
Keep long tasks in sub-agents. Resume watchdog at 120s, fail fast.

## 14. OpenClaw default session config wipes context
Check openclaw.json for session block. Set idle mode + high timeout. Defaults are for casual chatbots.
