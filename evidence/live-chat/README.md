# Live chat session (typed by me, offline)

The offline demo pipes its chat messages in by script, so the run is reproducible. This
session is the complement: I typed each message myself in `wiki chat` with Wi-Fi off,
recorded by [`scripts/live_chat.sh`](../../scripts/live_chat.sh). The air-gap check ran
before (23:08:16) and after (23:10:07): Wi-Fi off, ping blocked, HTTPS failing.

- Full transcript: [`transcript.txt`](transcript.txt), username and host redacted.
  The raw recording is [`terminal.typescript`](terminal.typescript).
- Saved session record: [`runs/chat/`](runs/chat/).
- Screenshot of the end of the session:
  [`../screenshots/live-chat-offline.png`](../screenshots/live-chat-offline.png).

| # | What I typed | Router | What happened | Check against the source |
|---|---|---|---|---|
| 1 | hi, what can you help me with? | no search (*capabilities question*) | Described real abilities (brainstorm, outlines, study plans, rewrites, note lookups) and suggested `/notes <question>` as a start. | No citations needed, none given, no refusal. ✓ |
| 2 | Draft a 3-day study plan for goodwill and contingent value rights | searched only the Goodwill and CVR sources (named both notes) | A 3-day plan, labelled "Suggestion", with citations S1–S4. | Goodwill calculation (S4) and impairment steps (S3) match the article. CVR definition and tradeability (S2) match. **Weak:** "the context of CVRs in corporate finance [S1]" cites the *See also* list, which supports nothing. **Cut off** at the 450-token reply limit ("Let me know if you want me to"). |
| 3 | make that shorter | no search (*follow-up*) | Condensed the plan, kept `[S2]`–`[S4]` (labels are fixed for the session). | Same claims as turn 2, still supported. ✓ |
| 4 | What's the difference between event-driven and price-protection CVRs? | searched the CVR source | Event-driven: compensate for future developments, protect the acquirer from paying for an uncertain product [S5]. Price-protection: share-based payment, hedge the acquired company against a fall in the acquirer's shares [S5]. Ended with a labelled "Suggestion". | Correct and cited. **One conflation:** "help bridge negotiations by ensuring payment is averaged … or setting a floor [S6]" joins two parts of the article. "Helps bridge this negotiation" is said of *event-driven* CVRs; the averaged price and floor belong to *price-protection*. |
| 5 | /sources | — | Printed the original passages S5 and S6 in full. | Lets me verify turn 4 directly, which is how I found the conflation. ✓ |

**Verdict.** The mode boundaries behave as designed:

- no notes search for a capabilities question;
- retrieval limited to the named notes;
- a follow-up answered from the conversation;
- citations on facts drawn from the notes, and ideas labelled as suggestions.

Two sentences were weakly or wrongly cited, the same "true facts, wrong join" pattern
described in the README reflection.
