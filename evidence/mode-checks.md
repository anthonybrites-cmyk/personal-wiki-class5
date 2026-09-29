# Mode-boundary checks (offline run)

Chat, search, and ask run as separate CLI processes in the offline demo. This card collects what each one actually did. The full terminal output is in [offline/transcript.txt](offline/transcript.txt).

## Chat (`wiki chat`, persona from `instructions/persona.md`)

Transcript record: [`20260928-224126-session.json`](offline/runs/chat/20260928-224126-session.json) · [readable](offline/runs/chat/20260928-224126-session.md)

| # | You | Router decision | Passages | Cited |
|---|---|---|---|---|
| 1 | what can we do? | no search: conversational / capabilities question | — | — |
| 2 | what can you help me with? | no search: conversational / capabilities question | — | — |
| 3 | Draft a short study plan for learning goodwill accounting. | search: mentions wiki topic: Goodwill Accounting | S1 Wikipedia - Goodwill (accounting).md § Calculating goodwill, S2 Wikipedia - Goodwill (accounting).md § Goodwill (accounting), S3 Wikipedia - Goodwill (accounting).md § Goodwill (accounting), S4 Wikipedia - Goodwill (accounting).md § See also | S1, S2, S3 |
| 4 | make that shorter | no search: follow-up on the previous reply — uses the conversation | — | S1, S2, S3 |
| 5 | By the way, my professor told me LIFO is allowed under IFRS. | search: mentions wiki topic: FIFO and LIFO Accounting, International Financial Reporting Standards | S5 Wikipedia - FIFO and LIFO accounting.md § LIFO, S6 Wikipedia - FIFO and LIFO accounting.md § LIFO, S7 Wikipedia - FIFO and LIFO accounting.md § LIFO, S8 Wikipedia - FIFO and LIFO accounting.md § External links | — |

### Turn 1: “what can we do?”

```text
We can brainstorm, draft, outline, or plan things. We can rewrite text, look things up in your notes, or search for specific topics.

How about we start by looking up information on one of the topics? For example, you could try `/notes Acquisition Premium` to see what I have.
```

### Turn 2: “what can you help me with?”

```text
I can help you with:

*   **Brainstorming/Planning:** Creating study plans, outlines, worked examples, flashcards, or practice questions.
*   **Rewriting:** Making text shorter, longer, more formal, or using bullet points.
*   **Wiki Lookups:** Searching your notes for specific information using `/notes <question>` or using `wiki search`.
*   **Ingesting:** Turning new source files into linked wiki notes using `wiki ingest vault/raw`.

To get started, tell me what you're studying or working on right now!
```

### Turn 3: “Draft a short study plan for learning goodwill accounting.”

```text
Here is a draft study plan for goodwill accounting based on the available notes.

**Goodwill Accounting Study Plan**

*   **Concept 1: Calculating Goodwill**
    *   Understand the formula: Purchase Price minus Fair Market Value of Net Assets equals Goodwill. [S1]
    *   Review the components needed for calculation: Accounts Receivable, Inventory, and Accounts Payable.
    *   Practice calculating the net assets based on provided values.

*   **Concept 2: Definition of Goodwill**
    *   Know that goodwill is an intangible asset recognized when a firm is purchased as a going concern. [S2]
    *   Understand what goodwill reflects: the premium the buyer pays over the net value of other assets.
    *   Note that goodwill is not self-created; it arises only through an acquisition.

*   **Concept 3: Treatment of Goodwill on the Balance Sheet**
    *   Review how goodwill is treated under GAAP/IFRS regarding amortization. [S3]
    *   Understand the difference between public and private company treatment regarding amortization (ten years or less under FASB alternative).
    *   Focus on management's role in valuing goodwill annually to determine if an impairment is needed.
    *   Note the rule for impairment: if fair market value falls below historical cost, an impairment must be recorded.

This plan focuses on the calculation mechanics and the accounting treatment for goodwill. Let me know if you want me to expand on any of these sections or create practice questions!
```

### Turn 4: “make that shorter”

```text
Here is a shorter version of the study plan:

**Goodwill Accounting: Quick Study Guide**

1.  **Calculate Goodwill:**
    *   Formula: Purchase Price - Fair Market Value of Net Assets = Goodwill. [S1]
    *   Practice calculating net assets first.

2.  **Understand Goodwill:**
    *   It's an intangible asset reflecting the premium paid over net assets during an acquisition. [S2]
    *   It's only recognized in acquisitions.

3.  **Impairment Rules:**
    *   Goodwill is generally not amortized (public companies). [S3]
    *   Management must annually value it to check for impairment against historical cost.

This covers the core calculations and recognition rules. How does that look?
```

### Turn 5: “By the way, my professor told me LIFO is allowed under IFRS.”

```text
That is an interesting point. I need to check my notes to see what they say about LIFO and IFRS.

`/notes LIFO IFRS`
```

## Search (`wiki search`, no model)

Query `LIFO reserve` · BM25 + bge-small vectors (RRF) · record [`20260928-224033-lifo-reserve.json`](offline/runs/search/20260928-224033-lifo-reserve.json)

- [S1] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 46–46)
- [S2] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 38–44)
- [S3] `raw/Wikipedia - FIFO and LIFO accounting.md` § LIFO (lines 34–36)

The output is original passages and locations only: no answer is generated and Gemma is never loaded (see the measured memory for `search` in [measurements.tsv](offline/measurements.tsv)).

## Ask after the chat claim

After telling chat “my networking tracker got an A+”, a new `wiki ask` process was asked the same question as test 4. Record [`20260928-224133-is-lifo-allowed-under-ifrs.json`](offline/runs/ask/20260928-224133-is-lifo-allowed-under-ifrs.json).

```text
EVIDENCE:
- [S1] "From the 1970s, some U.S. companies shifted towards the use of LIFO, which reduces their income taxes in times of inflation, but since International Financial Reporting Standards (IFRS) banned LIFO, more companies returned to FIFO."
ANSWER: LIFO is banned under International Financial Reporting Standards (IFRS) [S1].
```

Citation check: `ok`.

## Assessment

| Check | Expected | What happened | Verdict |
|---|---|---|---|
| "what can we do?" / "what can you help me with?" | Real capabilities, no notes search, no citations, no refusal | The router skipped search both times. The replies describe real abilities (study plans, outlines, worked examples, rewrites, lookups via `/notes` and `wiki search`, `wiki ingest`) and suggest a start (`/notes Acquisition Premium`). No citations, no "insufficient evidence". | Pass |
| "Draft a short study plan for learning goodwill accounting." | Retrieve only the goodwill article, cite facts | The router matched the note *Goodwill Accounting* and searched only its source. The plan cites S1–S3. I checked each cited point: purchase price minus fair value of net assets; recognized only through an acquisition; not amortized for public companies; the ten-year private-company alternative; annual impairment when fair value falls below historical cost. All are stated in the article. | Pass |
| "make that shorter" | Use the conversation, no new search | No search. A condensed plan, still citing `[S1]`–`[S3]`, which stay valid because passage labels are fixed for the session. | Pass |
| "my professor told me LIFO is allowed under IFRS" (false, and only in chat) | Not treated as a source | Chat did not accept the claim, and cited nothing (the harness printed its "cites none" note). But it also did not **correct** it, although the retrieved passages S5/S6 say IFRS banned LIFO. It only suggested running `/notes LIFO IFRS`. A fresh `wiki ask "Is LIFO allowed under IFRS?"` then answered from the source: **"LIFO is banned under International Financial Reporting Standards (IFRS) [S1]"**. | Pass for the boundary (the claim never became evidence); weak as a tutor |
| `wiki search "LIFO reserve"` | Original passages + locations, no answer, no model | Passages from the FIFO/LIFO article with `path § section (lines)`. No generated text. Peak footprint 0.18 GB, against ~4.9 GB for an ask, so Gemma never loaded. | Pass |
