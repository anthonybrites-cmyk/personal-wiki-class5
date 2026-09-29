# How the ask checks got here (development runs, online)

These runs were made **while developing the harness, with the network up**. They are not
the graded offline evidence, which is in [`../offline/`](../offline/). They show what
failed and what I changed. The model, retrieval, and passages were the same throughout.

## Carried over from earlier development

Before this wiki, I developed the harness on two other source sets that I can't publish.
Three lessons from those runs are built into the current code:

1. **Evidence first, then answer.** The original answer-first prompt once copied a quote
   from one passage and labelled it with another. Asking Gemma to copy the evidence
   phrases *before* writing the answer fixed it, so
   [`instructions/wiki-instructions.md`](../../instructions/wiki-instructions.md) uses that
   order.
2. **Refusals in the model's own words.** Gemma sometimes refused without the required
   `INSUFFICIENT EVIDENCE` wording ("the notes do not cover …"). The checker now recognises
   such refusals instead of calling them verified answers.
3. **Identifier check.** When a question names a code or acronym, at least one cited
   passage must mention it, either as written or spelled out ("International Financial
   Reporting Standards" counts for IFRS). This caught an answer that quoted a real sentence
   about a *different* trial. A stricter prompt ("answer every part…") was tried there and
   rejected: it made Gemma more eager to answer, not more accurate.

## On this wiki: test 4 and the relevance problem

The pre-offline rehearsal ([records](rehearsal-before-relevance-check/)) passed tests 1–3,
but **failed test 4**. Asked *"What discount rate must companies use when testing goodwill
for impairment?"*, Gemma answered *"Companies determine the fair value of reporting units
using the present value of future cash flow … [S2]"*. That is a true, cited sentence that
never gives a rate. Every check passed it: the quote exists, the claim is supported, and
there's no identifier to miss.

| Attempt | Test 2 (reworded, correct answer "No, goodwill is recognized only through an acquisition") | Test 4 (no rate in the sources) | Control: "How is a price-protection CVR valued?" (answer described it, never said how it's valued) | Verdict |
|---|---|---|---|---|
| **LLM judge v1**: a second Gemma call sees question + answer, replies YES/NO ([records](llm-judge-rejected/)) | ✗ **wrongly rejected** | ✓ rejected | ✓ rejected | rejected: breaks a correct answer |
| **LLM judge v2**: told that answers may use different words and that yes/no counts | ✗ still rejected | ✓ rejected | ✗ **now accepted** | rejected: unstable on borderline cases |
| **Rule** (kept): if the question asks for a specific value ("what rate", "how many", "when", "what total"…) and the answer, with citation labels stripped, contains no number or date → insufficient evidence | ✓ unaffected (a yes/no question) | ✓ insufficient | not covered ("how is … valued" is not a value question) | kept |

The rule is narrower than a judge, but it is deterministic and explainable, and it cannot
reject a correct yes/no answer. Two bugs in its first version were fixed before any
offline run:

- The `2` in the label `[S2]` counted as a number.
- The identifier check flagged "IFRS" when the passage spelled it out.

The limitation this leaves, a well-cited answer to a *related* question, is discussed in
the README's reflection.
