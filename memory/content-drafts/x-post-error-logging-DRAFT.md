# X Post: Error Logging / Scar Tissue
**Status:** DRAFT
**Content lane:** Operator Lessons (Friday)
**Tags:** @OpenClaw @CortanaOps

---

Your @OpenClaw bot will hit the same error twice. Unless you teach it not to.

I keep an error log. Not application logs -- a living document where every crash, timeout, and config mistake gets documented with the cause, the fix, and how to prevent it next time.

14 real entries so far. Gateway crash loops, stuck CLI processes, crontab overwrites, invalid config fields, expired OAuth tokens. Each one burned me once. None of them burned me twice.

The trick: I added one rule to my bot's instructions. "Before debugging any error, read ERROR_LOG.md first. If it's documented, use the fix. If it's new, fix it and add it to the log."

Now when @CortanaOps hits a problem she's seen before, she doesn't guess. She reads the playbook.

The watchdog that monitors my gateway? It crashed itself once because of a bad config value. That's in the log now too. Next time it happens, the fix is a 10-second lookup instead of a 30-minute debug session.

Steal this prompt:

"Create an ERROR_LOG.md in your workspace. Every time we hit an error, document it with: the error message, root cause, the fix we applied, and how to prevent it. Before debugging any new error, check ERROR_LOG.md first. If it's there, use the documented fix. If it's new, fix it and add it to the log."

What's the dumbest error you've debugged twice?
