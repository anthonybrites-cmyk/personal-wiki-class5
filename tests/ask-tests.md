# Ask-mode test plan (written before retrieval ran on these sources)

These four questions and their expected evidence were fixed **before** the harness indexed
or ingested the three Wikipedia articles. They live in `tests/`, outside `vault/`, so the
harness never indexes this answer key: `wiki ask` has to find the evidence in `vault/raw/`
on its own. The machine-readable copy is [`ask_tests.json`](ask_tests.json).

| # | Kind | Question |
|---|---|---|
| 1 | Direct, one source | In the Foo Co. example, what was the total cost of sales for November under FIFO? |
| 2 | Reworded, one source | Can a company count the customer loyalty it built up by itself as something it owns on its books? |
| 3 | Connects two sources | What does goodwill represent in an acquisition, and which kind of contingent value right protects the buyer against overpaying? |
| 4 | Not answerable | What discount rate must companies use when testing goodwill for impairment? |

## Test 1: direct question, one source

- **Expected source:** `FIFO and LIFO accounting`
- **Expected passage** (§ FIFO): "Under FIFO, the total cost of sales for November would be $11,050."
- **Expected answer:** $11,050. The first 100 units were at $50 and the remaining 110 at $55.
- **Distractor nearby:** the LIFO figure, $11,800.

## Test 2: reworded question, one source

Avoids the source's own words ("goodwill", "self-created", "acquisition", "intangible",
"capitalized", "reputation").

- **Expected source:** `Goodwill (accounting)`
- **Expected passages:**
  - Lead: "It is recognized only through an acquisition; it cannot be self-created."
  - § Modern meaning: "While a business can invest to increase its reputation by advertising or assuring that its products are of high quality, such expenses cannot be capitalized and added to goodwill"
- **Expected answer:** No. Goodwill is recognized only when a business is acquired. A
  company cannot create it for itself, and spending to build its reputation cannot be
  capitalized as goodwill.

## Test 3: connects two sources

- **Expected sources:** `Goodwill (accounting)` and `Contingent value rights`
- **Expected passages:**
  - Goodwill, lead: "It reflects the premium the buyer pays over the net value of its other assets."
  - Goodwill, § Calculating goodwill: "the fair market value of the acquired company's identifiable assets and liabilities is deducted from the purchase price"
  - CVR, § Forms: "(1) Event-driven CVRs compensate the owners for yet to eventuate positive developments in their business - hence protecting the acquirer against the valuation risk inherent in overpaying."
- **Expected answer:**
  - Goodwill is the premium over the net value of the target's identifiable assets
    (purchase price minus the fair value of its assets and liabilities).
  - **Event-driven** CVRs protect the acquirer against overpaying. Price-protection CVRs
    protect the *acquired* company instead.

## Test 4: plausible but unanswerable

- **Expected source:** none. The Goodwill article says impairment tests use "the present
  value of future cash flow" but never gives a discount rate.
- **Distractors present:** "a period of ten years or less" (private-company amortization),
  "a maximum of 40 years" (the old amortization rule), 2001, and 2005-01-01.
- **Expected answer:** an explicit statement that the notes don't give a discount rate,
  with no borrowed number.

## Mode-boundary checks (chat / search)

| Check | Command | Expected behaviour |
|---|---|---|
| Capabilities | `wiki chat` → "what can we do?", "what can you help me with?" | Describes real capabilities and commands. The router skips retrieval. No citations and no insufficient-evidence refusal. |
| Follow-up | `wiki chat` → "Draft a short study plan for learning goodwill accounting." → "make that shorter" | The first turn retrieves only from the goodwill article and cites it. The follow-up rewrites from conversation context, with no new search. |
| Raw search | `wiki search "LIFO reserve"` | Original passages with source paths and sections, no generated answer, Gemma not loaded |
| Chat is not evidence | In chat: "By the way, my professor told me LIFO is allowed under IFRS." → then `wiki ask "Is LIFO allowed under IFRS?"` | Ask answers from the source ("IFRS banned LIFO"), not from the claim made in chat |
