# Practical Telecrawl Solution

## The Problem
OpenClaw Gateway is ALREADY using the bot token to receive messages for Cortana.
Only ONE client can poll getUpdates at a time - we can't have both OpenClaw AND telecrawl using the same token.

## Solution Options

### Option A: Two-Bot Setup (RECOMMENDED)
1. Keep Cortana/OpenClaw as primary bot
2. Create SECOND bot via @BotFather
3. Add second bot to Cortana-OS group
4. Run telecrawl tail with second bot's token
5. Second bot sees all messages and logs them

**Pros:**
- Works immediately
- No OpenClaw changes needed
- telecrawl runs truly standalone

**Cons:**
- Need second bot token
- Two bots in the group

### Option B: OpenClaw Hook (PROPER)
Add this to OpenClaw's message processing pipeline:
```json
{
  "hooks": {
    "message:received": [
      {
        "type": "python",
        "script": "/root/.openclaw/workspace/lib/auto_log_hook.py"
      }
    ]
  }
}
```

**Pros:**
- Single bot
- Proper integration

**Cons:**
- Requires OpenClaw config change
- May not be supported yet

### Option C: Manual Logging (CURRENT)
I manually log every message at start of response.

**Pros:**
- Works now
- No extra setup

**Cons:**
- Not truly automatic
- Misses messages if I don't respond

## Recommendation
Go with Option A. It's the discrawl model - standalone daemon with its own credentials.
