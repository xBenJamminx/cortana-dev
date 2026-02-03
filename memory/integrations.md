# Integrations Status

## Model Providers

| Provider | Status | Models |
|----------|--------|--------|
| Claude Code CLI | ✅ Primary | claude-cli/opus, claude-cli/haiku (via Ben's Max subscription) |
| OpenRouter | ✅ Fallback | openrouter/google/gemini-3-flash-preview |

## Current Routing

- **Primary:** claude-cli/opus (Claude Max subscription - no API credits)
- **Fallbacks:** claude-cli/haiku → openrouter/gemini-flash

## Model Shortcuts
- Default: Opus (automatic)
- No manual routing needed - Opus handles everything

## Other Integrations

| Integration | Status | Notes |
|-------------|--------|-------|
| Telegram | ✅ Active | @Cortana_MoltBot |
| ElevenLabs TTS | ✅ Configured | Voice synthesis |
| Brave Search | ✅ Configured | Web search |
| Bird CLI | ✅ Configured | X/Twitter search (AUTH_TOKEN + CT0 in ~/.bashrc) |
| Composio | ✅ Configured | MCP tools |
| Blender MCP | ✅ Configured | 3D generation |

## Notes

1. **No more OpenRouter credit burn** - Using Claude Max subscription via Claude Code CLI
2. Claude Code CLI runs with `-p --output-format json` flags
3. Workspace: /root/clawd
4. Credentials: /root/.claude/.credentials.json (synced from Ben's local machine)
