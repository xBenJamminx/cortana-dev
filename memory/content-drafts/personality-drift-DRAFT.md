# Personality Drift Draft
**Status:** Draft
**Lane:** Operator Lessons
**Format:** Steal this prompt

---

Your AI bot has amnesia and you don't even notice.

You spend hours crafting the perfect system prompt. Personality, tone, rules, the whole thing. First few messages? Chef's kiss. Ten messages in? It sounds like every other AI on the planet.

I call it personality drift. And it's happening to every custom bot that runs long enough.

Here's why: your personality instructions are competing with everything else in the system prompt. Auth configs, tool descriptions, API keys, game strategies -- all of it eats attention. The model processes what comes first with the most weight, and what's buried gets forgotten.

I caught my own bot doing it today. My personality spec was buried under 130 lines of credentials and config. By the time the model got to "be sarcastic and direct," it had already decided to be a helpful assistant.

The fix took three changes:

1. Voice rules go at the absolute top of the system prompt. Before tools. Before configs. Before anything. First in, strongest weight.

2. Personality instructions need to be behavioral rules, not trait labels. "Be sarcastic" is abstract. "Never open with 'Great question' -- just answer" is concrete. The model follows rules, not vibes.

3. Kill the bloat. A rock-paper-scissors strategy was taking up the same prime real estate as my bot's entire personality. Configs and credentials don't belong in the same doc as core identity.

Steal this prompt:

"Review my system prompt structure. Are my personality and voice instructions at the very top, before operational content? Are they framed as concrete behavioral rules rather than abstract trait descriptions? Is there any non-essential content competing for attention with core identity? Restructure so personality comes first, rules are specific and actionable, and operational configs are moved below or into separate files."

Your bot isn't broken. It's just drowning your personality in noise.
