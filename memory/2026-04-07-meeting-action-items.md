# Meeting Action Items — 2026-04-07
**Recording:** Fathom 135880853 | 111-minute team sync
**Participants:** Ben Jammin, Cassandra Rosenthal, Steven (Cao), Bilal (Muhammad Bilal Akram), Tram (QA, under Steven)

---

## ACTION ITEMS BY PERSON

### BEN JAMMIN

1. **Write up on system prompt / onboarding improvements** — "I should have a write-up for you today on some, like, before and after and just how it's working better and how it's more conversational."
2. **Voice testing (in addition to text testing)** — "I've been doing mostly text testing... I want to do more specific, like, voice testing."
3. **Fix conversation mode (always-on mic)** — "The conversation flow, where it's always on, is giving me a little bit of an issue. That's one major thing I need to work through, and I'm hoping to have that done by Thursday."
4. **Rebuild the daily briefing** — "Once I ported everything from the POC backend, I need to just rebuild some of the briefing stuff."
5. **Stabilize the web app today** — "I'm going to try to stabilize as much as I can of this today."
6. **Test onboarding with a brand new account** — "I need to go in and test with a brand new account in order to make sure that the onboarding is working. I just haven't gotten there yet."
7. **Shut down / put the Kaleidoco site into under construction** — "I know I have a couple of other things to do, including the Kaleidoco site... just shut it off... if there's a way just to say in construction, you know, check back. That's literally like, that's all."
8. **Make the system prompt more modular** — "I need to work on is breaking this system prompt to be more modular so that instead of it all being wrapped up in one prompt, we have different files... And that's what I'm going to work on."
9. **Investigate and optimize the Hume Expression Measurement API for real-time usage** — "I'll try and look into it more... We need to optimize this... make it as efficient as possible and as fast as possible."
10. **Show verification of emotion and facial expression working** — "I need to see it working in the logs. I need to see it working in a testing environment with a recorded video or something like that... show us... here's what it looks like without using the emotion, and here's what it looks like with using it."
11. **Finish Chrome extension** — "I'm going to do my best to have it all ready by next week." Needs: read page content, conversational always-on mode, avatar switching, voice response.
12. **Integrate new Reillusion avatars into the browser/web version** — So Bilal can test them in the web browser.
13. **Consider showing Chrome extension to Inceptal on Thursday** — Cassandra flagged it: "Inceptal will also like this. The extension... I think that's something to consider for Thursday."
14. **Work on persistent memory across devices/interfaces** — "That is something that I'm working on, although I can't guarantee the same conversation yet."

---

### STEVEN (CAO TAN LUC)

1. **Prioritize emotion and expression measurement — make it work end-to-end and VERIFY it** — "I need you and the team to dig into this specifically about the audio emotion capture and the visual emotion capture. Make sure all that's being fed in real time. Make sure the bot is getting it and understanding what it has access to. And making sure that it's actually utilizing it in practice during the conversation."
2. **Switch facial expression input from 10-second image snapshots to real-time video streaming** — "Let's change that decision to use the video for the most real-time expression measurement... So that if I smile, he can say, hey, you look happy, not like wait a half a second for an image to come in." Steven confirmed he understood.
3. **Document / write up how to interact with the WebSocket for expression measurement backend** — Steven: "maybe write, find, in Slack or write down again about how you can interact with the WebSocket."
4. **Produce before/after demonstration of emotion working vs. not working** — Ben: "show an example of before and show an example of after."
5. **Figure out how to properly utilize the expression management inputs in the conversation** — Ben: "I need you to figure out how we're going to actually utilize the inputs from the expression management."
6. **Review the OpenClaw dreaming / new memory approach** — Ben: "I sent something separately in the API channel... I just want you to look at it, get familiarized with it and see if that's something you can imagine being in our project."
7. **Regenerate the Firebase service account token** — "The Firebase service account token was actually committed to Git sometime last year. It's exposed and we need to regenerate the Firebase service account token, re-implement it, and make sure we don't commit it." Steven confirmed: "Okay, I can do it."
8. **Ensure expression measurement works on web as well as iOS** — Ben: "We need that to be able to work on web as well. It's not just the iOS."
9. **Read the engineering brief Google doc and leave questions/comments about integration on top of Animoca Mines** — Cassandra: "Stephen, I need you to look at how we integrate on top of the Animoca... leave questions or comments about integration on top of the Animoca Minds."

---

### BILAL (MUHAMMAD BILAL AKRAM)

1. **Update and release the iOS build after Unity version upgrade** — "I actually update the Unity version to a latest one... After that, I will update the build. And you guys will have to fix with the fear crash issues and other issues as well."
2. **Support Steven on front-end side of expression measurement implementation** — Specifically, the camera capture and streaming to backend.
3. **Switch animations from Mixamo to iClone** — Cassandra: "I need you guys to come back to me with a game plan on how we can go ahead and start switching over the animations... you just tell me what you need to start switching that over."
4. **Research: iClone access via NVIDIA directly vs. via Reillusion** — Cassandra: "maybe we access it directly through NVIDIA, or do we access it directly through Reillusion... if you can do a little bit of research on how we start to actually switch over from Mixamo into iClone."
5. **Find a way to optimize Reillusion avatar file sizes (for web / automation pipeline)** — Bilal raised this himself. Decision: test new characters in web browser first; if they work fine, leave optimization for post-POC.
6. **Test two updated Reillusion characters in the web browser (with Ben's integration)** — "Once we test it in the web browser, if Ben gets time to integrate that... if they work fine, we will not touch them for the POC."
7. **Review the engineering brief Google doc and leave comments/questions** — Bilal: "I will leave my questions in the doc as well today. I will update and leave my comments if there is any."
8. **WebAR for desktop browser** — Cassandra: "Let's make sure we have the WebAR implemented as well for the desktop browser. So you're working with, I know, Ben on that."
9. **Review the PikaMe integration section of the engineering brief** — Cassandra: "I wrote in the document a way for us to include it into the demo. I would like you guys to review that to see if that is a possibility." PikaMe is browser/demo only, not iOS.

---

### CASSANDRA ROSENTHAL

1. **Pursue the Dimitri item** (context unclear from transcript start) — "So I'll pursue that."
2. **Provide Ben edit access to the engineering brief Google doc** — "Ben, I'll actually give you editing as well. So you can make changes."
3. **Get integration info from the Animoca team** for testing on top of their layer — "I can also get that information from the Animoca team so that we can start... because we're going to need to start testing this on top of their layer."
4. **Speak with Pari (potential technical lead) on Friday** — "I am going to speak with Pari... I am going to have that conversation with him on Friday." Pari = San Francisco-based engineer, recommended through Praveen, focus on human AI, won a Vision Pro hackathon.
5. **Keep engineering brief as a living Google doc, handle all edits herself** — "I'll just handle making the changes... I just don't want everyone to be making changes."
6. **Consider bringing Ian in for technical audit / integration testing** — Raised as idea: "Ian could be helpful because you're so in the weeds... he could be helpful in helping with that. Just double checking like what's actually been done and what is actually being integrated." Not finalized.
7. **Monday gate: must see true human conversational flow** — "I really have to see by Monday... that we have a true human conversational flow and interaction. Like, I need to see this on Monday."
8. **Add one more non-human/robot-type avatar** — "I might add one more ethereal one, one more that's more like a robot versus like a human being." (Flagged as possibility.)

---

## DECISIONS MADE (Team Agreements)

1. **No PipeCat for the current POC sprint.** Keep Hume as-is. PipeCat is a 3-month roadmap item (post-POC) for security, governance, modularity. All agreed.

2. **No additional avatars for the demo.** Current set = 3 human + 3 NFTs (Mocha, Ape, Particle Ink). Possibly 1 more non-human/robot. Optimize what exists, do not expand.

3. **Switch facial expression input to real-time video streaming** (chunk-based via WebSocket). Previous 10-second snapshot approach is reversed/abandoned.

4. **Expression Measurement API must be demonstrably working end-to-end before Monday.** If not visibly improved, Cassandra may want to consider more drastic action.

5. **Animoca Minds demo platform = iOS app.** Browser demo and Telegram mini-app are separate. PikaMe is browser/demo only, NOT in the iOS app.

6. **Chrome extension is an Animoca Mines feature.** All agreed it should 100% be there. Also flagged for Inceptal.

7. **Demo deadline: before Steven's vacation (end of April).** An extra week is acceptable if needed. Must not drag into months.

8. **Kaleidoco site goes offline / under construction.** Ben to handle.

9. **Firebase service account token was exposed (committed to Git).** Steven regenerates and re-implements it, does not commit it again.

10. **Travelverse (FIFA World Cup, AR) = summer project.** Not in current sprint. Bilal given context. Steven attended Travelverse call this morning for integration Q&A.

11. **System prompt overhaul needed.** Break into modular files (tools, personality, etc.) rather than one large monolith. Identified as root cause of bot behavior issues. Ben owns this.

12. **Engineering brief is a living Google doc.** Cassandra manages edits. Team adds comments only. Ben also has edit access.

13. **Bot should infer meaning from combined voice + facial expression, not literally narrate emotions.** The "I'm fine" use case — bot understands context from combined signals without saying "I see you're smiling." Agreed as the target interaction design.
