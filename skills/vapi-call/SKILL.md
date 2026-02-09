---
name: vapi-call
description: Make outbound phone calls via VAPI. Cortana calls someone for you. ALWAYS use this script - NEVER craft raw curl calls to the VAPI API.
metadata: {"clawdbot":{"emoji":"📞","requires":{"env":["VAPI_API_KEY"],"bins":["curl"]},"primaryEnv":"VAPI_API_KEY"}}
---

# VAPI Call

Make outbound phone calls through Cortana via VAPI.

## Usage

```bash
/root/clawd/skills/vapi-call/vapi-call +15551234567 "Hey, this is Cortana calling on behalf of Ben"
```

- First argument: phone number (with country code)
- Second argument (optional): custom greeting message

## CRITICAL RULES

- ALWAYS use this script for outbound calls. It passes the correct assistantId and phoneNumberId.
- NEVER construct your own curl calls to https://api.vapi.ai/call with inline assistant objects.
- NEVER pass raw twilioAccountSid/twilioAuthToken in API calls - use phoneNumberId instead.
- If you bypass this script, calls will connect but without the real Cortana assistant (no voice, no tools, no personality) and Twilio will play a "trial account" message.

## Config

- VAPI Assistant ID: 899db371-3ca9-44f6-8ad3-a70131af4987
- VAPI Phone Number ID: 3d76fe66-e37e-4c9c-af92-695690631c9b
- From number: +15164713637
- Ben's number: +15168706749
