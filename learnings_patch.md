

### 15. Sticky model fallback poisons ALL sessions silently (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Cortana was responding poorly for weeks -- stalling, giving shallow answers, using NO_REPLY to skip messages. Investigation revealed she was running on Kimi K2.5 (OpenRouter fallback) instead of Claude across ALL 6 active Telegram topics.
- **Root cause:** OpenClaw's fallback system (model.fallbacks in openclaw.json) is STICKY. When Claude's API hiccupped once, the gateway switched to the fallback model. That model override was saved in sessions.json per-session and NEVER reverted -- even after Claude came back online. Every topic accumulated the override independently.
- **Fields that get stuck:** model, modelProvider, fallbackNoticeSelectedModel, fallbackNoticeActiveModel, cliSessionIds, claudeCliSessionId, systemPromptReport
- **Fix applied:** Removed all fallbacks from config (model.fallbacks: []). Cleaned all sticky model overrides from sessions.json. Reset all session bindings so topics start fresh.
- **Rule:** Do NOT use model fallbacks in openclaw.json. A silent degradation to a worse model is far more damaging than a visible failure. If Claude goes down, it should fail loud -- not pretend to work while running on a model that doesn't understand the system prompt.
- **Diagnostic:** Check sessions.json for any session with a model field that doesn't match the primary. Or check openclaw session files for model-snapshot entries showing the wrong provider.

### 16. NO_REPLY token suppresses responses entirely (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Ben sent a detailed content brief. Cortana reacted (ack emoji) but never responded. Session file showed the model returned NO_REPLY -- a single token that tells the gateway to suppress the response completely.
- **Root cause:** NO_REPLY is a built-in openclaw feature (defined in tokens-rNiM9362.js). When the model outputs only NO_REPLY, the gateway treats it as "this message doesn't need a response" and sends nothing to Telegram. The fallback model (Kimi) didn't understand Cortana's rules and used it inappropriately.
- **Fix applied:** Added explicit rule to CLAUDE.md Core Rule #1: "NEVER output NO_REPLY."
- **Rule:** If an agent appears to receive a message (shows ack reaction) but never responds, check the session .jsonl file for NO_REPLY in the assistant content. The fix is a system prompt rule banning the token.

### 17. Watchdog kills working Claude after 180s of no streamed output (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Claude was actively working (reading files, calling tools, thinking) but the openclaw watchdog killed it after 180 seconds because no text had been streamed to stdout yet. Error: "CLI produced no output for 180s and was terminated."
- **Root cause:** The noOutputTimeoutMs default is 180000ms (3 min). This timer counts time since the LAST text output -- tool calls, file reads, and thinking don't count as "output." Complex tasks that require multiple tool calls before generating text will always hit this limit.
- **Fix applied:** Set noOutputTimeoutSeconds: 600 (10 min) in agents.defaults in openclaw.json.
- **Rule:** If Cortana is getting killed mid-task with "no output for 180s," increase noOutputTimeoutSeconds. The default 180s is too short for tasks involving file reads, web fetches, or multi-step tool use.

### 18. Typing indicator service crash-looping silently (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Ben couldn't see any typing indicators when Cortana was working. The tg-reaction-monitor.service had been crash-looping (4,500+ restart attempts) because the script path was wrong.
- **Root cause:** tg-reaction-monitor.py was moved from /root/.openclaw/workspace/scripts/ to /root/.openclaw/workspace/automation/social/ but the systemd service file still pointed to the old path.
- **Fix applied:** Updated the ExecStart path in /etc/systemd/system/tg-reaction-monitor.service.
- **Rule:** After moving ANY script that has a systemd service, update the service file path. Check crash-looping services with systemctl status -- a restart counter in the thousands means it's been broken for a long time.

### 19. Session symlink mapping between openclaw and Claude CLI (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Cortana responded to the first message in a topic but crashed on every subsequent message with "No conversation found with session ID."
- **Root cause:** Openclaw creates its own session ID (e.g. 76063dde) but Claude CLI creates a DIFFERENT session ID (e.g. 69761d4f). Normally openclaw creates a symlink in /root/.openclaw/agents/main/sessions/ from its ID to the Claude CLI session file. When sessions are cleared/reset, the symlink is lost and claude --resume fails because Claude CLI doesn't know the openclaw ID.
- **Fix applied:** Manually created symlink and updated cliSessionIds/claudeCliSessionId in sessions.json.
- **Rule:** Never manually clear session fields in sessions.json without understanding the symlink mapping. If sessions must be reset, let the gateway create fresh ones by restarting -- don't surgically remove fields. If resume fails with "No conversation found," check if the symlink exists in /root/.openclaw/agents/main/sessions/.

### 20. noOutputTimeoutSeconds is wrong key — use cliBackends.reliability.watchdog (2026-03-16)
- **Date:** Mar 2026
- **What happened:** Tried to fix 180s watchdog by setting `agents.defaults.noOutputTimeoutSeconds: 600` — openclaw rejected it as an unrecognized key and crashed on startup.
- **Root cause:** The correct config path is `agents.defaults.cliBackends.claude-cli.reliability.watchdog.fresh.noOutputTimeoutMs` (and `.resume`). The internal variable is in milliseconds and lives in the `reliability.watchdog` nested object.
- **Fix applied:**
```json
"cliBackends": {
  "claude-cli": {
    "reliability": {
      "watchdog": {
        "fresh": { "noOutputTimeoutMs": 600000 },
        "resume": { "noOutputTimeoutMs": 600000 }
      }
    }
  }
}
```
- **Rule:** When setting the watchdog timeout, use `agents.defaults.cliBackends.claude-cli.reliability.watchdog.{fresh|resume}.noOutputTimeoutMs`. Value is in milliseconds. No max limit (unlike the per-provider timeout which caps at 120000ms).
