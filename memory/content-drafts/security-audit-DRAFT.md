# Content Draft: Your Bot Is Leaking Your Secrets
**Status:** Draft
**Type:** Story + Steal This Prompt
**Lane:** DIY/Template (Wednesday) or Operator Lessons (Friday)

---

You're handing your AI bot API keys, passwords, and OAuth tokens. Do you know where they end up?

Your OpenClaw bot needs access to things. Twitter, Stripe, Google, Telegram, whatever you've connected. That means secrets are floating around your system. In config files. In scripts your bot wrote. In conversation logs. Maybe even in files that sync to the cloud.

I asked my bot to audit itself today. It found 12 of my API keys sitting in plain text across 18 files. Keys that could've been used to hijack my accounts, post on my behalf, or run up charges on my payment processor.

Five minutes later, every secret was locked down. One secure file. Every script patched. A scanner installed that blocks anything from ever being saved with a secret in it again.

Steal this prompt:

"Run a full security audit on this system. Search every file you have access to for hardcoded API keys, tokens, passwords, bot tokens, OAuth secrets, and credentials. Check config files, scripts, logs, and anything else that might contain sensitive values. For each finding, tell me what was exposed, where, and how severe it is. Then help me move everything to a single secure .env file and set up protections so this can't happen again."

You gave your bot the keys to your digital life. Make sure it's not leaving them under the doormat.
