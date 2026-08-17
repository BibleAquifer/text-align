# Presentation Outline — Alignment Pipeline (20 slides, ~40 min)

Diagrams referenced in slides 2 and 18: `docs/alignment-pipeline-diagrams.html`.

## 1 — Title
Word-Level Alignment: Translation → Source
*(subtitle: how we align Bible translations to Greek/Hebrew with LLMs)*

## 2 — The Pipeline
[visual: `alignment-pipeline-diagrams.html`, pipeline-overview figure]
- Tokenized TSVs
- refine-alignment
- score-alignment / retry-alignment
- render-alignment
- compare-alignment

## 3 — What This Produces
[visual: full-screen screenshot, BSB verse, minimal text on slide]
- SBL Reverse Interlinear style
- Target word above its source word(s)
- Translation order, not source order

## 4 — Reading the Symbols
- → / ← — non-anchor, source shown in adjacent cell
- ▸N / ◂N — separated from anchor, N = source index
- • — no source correspondent
- ≠ — confirmed non-equivalent (NEQ)
- ‹ … › — phrase behind one target word

## 5 — Primary, Secondary, NEQ, Idiom
- Primary — direct lexical/semantic link
- Secondary — grammatically implied, no separate source word
- NEQ — positive claim of *no* correspondence, not a shrug
- Idiom — phrase-to-phrase, treated as one unit

## 6 — Core Principles
- Always translation → source
- Same spec, both testaments
- Generous alignment: include grammatically implied words
- Every record needs ≥1 primary link per side

## 7 — NT Detail: Articles
- Greek article ↔ English "the": not always 1:1
- Rules decide primary vs. secondary vs. NEQ
- One construction, several possible outcomes

## 8 — OT Detail: Word-Part Tokens
[visual: table row, e.g. בְּבֵיתוֹ → prep + noun + suffix]
- Hebrew words split into morphemes
- Each part aligns independently
- Prefixes, suffixes, articles all separately tagged

## 9 — Why LLM, Not Statistical
- eflomal, fast_align, embeddings: co-occurrence & similarity
- Good at "these tend to correspond"
- Can't judge primary vs. secondary, NEQ, idiom — that's grammar, not statistics
- LLM reasons per verse; statistical methods aggregate a corpus
*(short paragraph, if room: statistical methods are fast and cheap — the LLM trade is judgment for cost/latency)*

## 10 — Prompt Architecture
- One config per target language
- Base rules + conditional grammar blocks
- Blocks injected only when the verse needs them
- Same architecture, 6 languages so far

## 11 — Phenomenon Detection
- Scans real Greek/Hebrew morphology per batch
- Passive voice, participles, infinitives, ἵνα, conditionals…
- Triggers only the relevant guidance
- Keeps prompt lean, targeted

## 12 — Structured Output
- Forced function/tool calling, not free text
- Strict JSON schema = spec-conformant by construction
- Tokens referenced by number, not copied as text
- Bad output caught immediately, not silently wrong

## 13 — Data Substrate
- Tokenized target TSVs + Greek/Hebrew source TSVs
- Shared token ID scheme
- refine-alignment: one chapter, blank slate, per call

## 14 — Multiple LLM Providers
- OpenAI · Anthropic · Google · OpenRouter · Gloo · Ollama
- Swappable per run

## 15 — Why Score Quality
- First-pass LLM output isn't uniformly good
- Need automated triage before expensive re-alignment

## 16 — Five Quality Signals
- Source coverage
- Target coverage
- NEQ overuse
- Token "smearing" (over-grouping)
- Per-verse deviation from chapter norm

## 17 — retry-alignment
- Flagged verses re-aligned blank slate
- Optionally with a stronger model
- Falls back to cheap re-pass if too much of the chapter is flagged

## 18 — The Recommended Loop
[visual: `alignment-pipeline-diagrams.html`, retry-loop figure]
- Cheap model → clean → score → retry (better model)

## 19 — Cost Awareness
- Retry cost estimated before spending
- Per-verse and total caps

## 20a — compare-alignment
- Checks our output against Biblica's independent alignment
- Precision / recall / F1 over links
- Measures *divergence*, not correctness

## 20b — Wrap-up
[visual: pipeline diagram from slide 2, now filled in]
- Questions

---

*Note: slides 20a/20b make this 21 total. Either split compare-alignment and
wrap-up across two slides (21 total), or fold "Cost Awareness" (19) into the
retry-loop slide (18) as a sub-bullet to land back at 20.*
