# Ingest rules (turning one source file into a wiki note)

You are writing one note for a personal Obsidian wiki from a single source file: a
reference article (for example from Wikipedia) the owner is studying from. The note must be
accurate to the source: every fact you write has to be stated in the source text you were given. Do not
add background knowledge.

Write these lines, in this order, one item per line, and nothing else:

TITLE: <the article's subject as a person would say it, 2 to 5 words, Title Case — e.g. "Depreciation Methods", "Contingent Value Rights">
ALIASES: <other short names for this document's subject, comma-separated, or none — not people and not organizations>
DESCRIPTION: <one line of at most 18 words saying what this document covers or argues>
SUMMARY: <2 or 3 plain sentences: the question it addresses, the main argument or content, the conclusion>
ORG: <a company, agency, regulator, or institution named in the source> || WHY: <its role in this document>
ORG: <another organization> || WHY: <its role>
ORG: <another organization> || WHY: <its role>
CONCEPT: <a business, finance, or accounting concept the source names, 1 to 4 words> || WHY: <how this document uses it>
CONCEPT: <another concept> || WHY: <how>
CONCEPT: <another concept> || WHY: <how>
FACT: <one specific fact or claim, with numbers and names copied exactly> || SECTION: <heading from the outline>
FACT: <another fact> || SECTION: <heading>
FACT: <another fact> || SECTION: <heading>
FACT: <another fact> || SECTION: <heading>
FACT: <another fact> || SECTION: <heading>
FACT: <another fact> || SECTION: <heading>

Rules:
- TITLE names the subject, not the file. No "Assignment", "Final", "Write-up", author names, or dates.
- Write exactly 6 FACT lines, then stop. Spread them across the whole document, beginning,
  middle and end, and include its key numbers, its recommendation or conclusion, and
  definitions it gives.
- Fill every ORG and CONCEPT line above (3 organizations, 3 concepts), using names that
  appear in the source. WHY is at most 15 words.
- An ORG is the proper name of one specific organization (like "FASB" or "Internal Revenue Service"),
  never a category of organizations (like "pharmacies"), a drug, a person, or a document.
- A CONCEPT is an established term that could have its own wiki page and could matter to
  other courses, e.g. "Acquisition Premium", "Revenue Recognition", "Market Segmentation",
  "Contingent Value Rights". Never the document itself, a person, or a whole sentence.
- If one of the existing topic notes fits, reuse its exact name.
- Copy numbers exactly. If you are not sure a detail is in the source, leave it out.
