# Live session: typed by hand, offline

On 2026-09-29 I turned Wi-Fi off and typed every command myself in a recorded shell
([`scripts/live_session.sh`](../../scripts/live_session.sh)). The shell uses a neutral
`offline-demo $` prompt, so no username or computer name is recorded. The air-gap check
ran at the start (08:27:01) and again when I typed `exit` (08:30:43): Wi-Fi off, ping
blocked, HTTPS failing both times.

- Full transcript: [`transcript.txt`](transcript.txt). The raw recording is
  [`terminal.typescript`](terminal.typescript).
- Every saved record: [`runs/`](runs/).
- Screenshot of the chat part and the closing check:
  [`../screenshots/live-session-offline.png`](../screenshots/live-session-offline.png).

| # | What I typed | What happened | Checked against the source |
|---|---|---|---|
| 1 | `./wiki --help` | Commands, the three modes, examples, configuration, and required inputs | ✓ |
| 2 | `./wiki status` | Both models `cached ✓`, *network now: offline (no DNS)*, 3 sources, 14 notes, 61 passages | ✓ matches the README |
| 3 | `./wiki ingest vault/raw --force` | Gemma re-drafted all 3 articles in 26.8 s. All three notes stayed **kept-reviewed**: no duplicates, and the reviewed text was unchanged (fresh drafts went to `runs/ingest-drafts/`). The source check rejected a topic Gemma invented, "FASB" for the CVR article, which never names FASB. | ✓ |
| 4 | `./wiki search "LIFO reserve"` | 4 original passages with `path § section (lines)` and scores, no answer, no model loaded | S1–S3 are the right LIFO passages. **Weak:** S4 is the CVR article's *See also* list, with no keyword match (bm25 0.00) and a cosine of 0.475, just over the 0.45 cut-off. |
| 5 | `./wiki ask "What was the total cost of sales for November under LIFO in the Foo Co. example?"` | "Under LIFO, the total cost of sales for November would be $11,800 [S2]": quote and claim verified | ✓ S2 says exactly that |
| 6 | `./wiki ask "Who founded the Save LIFO Coalition?"` | "The Save LIFO Coalition argues in favor of the retention of the LIFO method [S1]", marked **citations verified** | ✗ **The known limitation.** The notes never say who founded it. Gemma answered a related question with a true, cited sentence, and the harness's value-question rule does not cover "who" questions (see the README reflection). |
| 7 | `./wiki ask "In what year was the Save LIFO Coalition founded?"` | "The notes do not contain information about the year the Save LIFO Coalition was founded." Reported as **insufficient evidence**. | ✓ The same missing fact, asked as a year, is refused. |
| 8a | chat: `what can we do?` | No search; described its real abilities; suggested `/notes <question>` | ✓ |
| 8b | chat: `Summarize goodwill impairment in 3 bullets` | **Router bug.** Classed as a follow-up to the previous reply (it contains "summarize" and "bullets"), so it did not search; Gemma suggested `/notes goodwill impairment`. | ✗ See "Bug found" below. |
| 8c | chat: `/notes goodwill impairment` (my workaround) | Searched the goodwill article; three cited bullets | Bullets 2 and 3 match the article. The private-company point drops "in the United States". **Bullet 1 is wrong:** it says goodwill is reduced "to equal the carrying value"; the article says it is reduced so that *the carrying value equals the fair value*. |
| 8d | chat: `make that shorter` | No search; condensed from the conversation, kept `[S1]`/`[S2]` | ✓ The shorter wording ("requiring a reduction of the goodwill") is correct. |

## Bug found in this session, and the fix

The chat router checked for follow-up verbs ("summarize", "shorter", "bullets", …) before
checking whether the message names a wiki topic. So a new request that happened to use
one of those words was treated as a rewrite of the previous reply.

**Fix** ([`harness/router.py`](../../harness/router.py)): a message only counts as a
follow-up if it names no wiki topic, or if it points back at the last reply ("that",
"it", "this", …). I re-ran every chat message from the three recorded sessions (offline
demo, live chat, this session) through the new rule. Only this message changes; "make
that shorter" is still a follow-up in all three.

**Rerun** (online, after the fix, labelled as such):
[`after-router-fix/transcript-online.txt`](after-router-fix/transcript-online.txt).

- "Summarize goodwill impairment in 3 bullets" now searches the notes on its own
  (*mentions wiki topic: Goodwill Accounting, Impairment Testing*) and cites them.
- This time the carrying-value point is stated correctly.
- "make that shorter" still uses the conversation.
