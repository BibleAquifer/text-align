---
name: review-alignment
description: Review a generated chapter (or verse range) of a text-align alignment for substantive errors. Use when the user asks to review, check, or spot-check an alignment, e.g. "review Titus 2 in CUV" or "look at John 3:1-10 for OENGB". Judges whether links are defensible, not whether they match the prompt exactly.
---

# review-alignment

Semantic review of one chapter of a generated alignment. Complements `score-alignment`
(mechanical signals); this catches wrong links, unjustified NEQs, and missed content words.

## Inputs

- `config` — a name from `configs/` (e.g. `CUV`). Ask only if not given.
- `corpus` — `nt` or `ot`. Infer from the book when obvious (NT books are 40–66).
- `chapter` — `BBCCC` (e.g. `56002`); optionally a verse range. Translate book names
  ("Titus 2" → `56002`; NT book numbers start at 40 = Matthew).

## Procedure

1. Dump the chapter (read-only):
   `poetry run python scripts/dump_chapter.py --config <C> --corpus <nt|ot> --chapter <BBCCC> [--verses N-M]`
   Output per verse: source gloss stream, each record as `source -> target` (`*` = secondary),
   NEQ'd tokens, unaligned tokens.
2. Load conventions *only as background*, not as a checklist:
   - `docs/alignment-principles-nt.md` or `-ot.md` for primary / secondary / NEQ meaning.
   - `scripts/dump_chapter.py ... --prompt` for the language's base block; pull a conditional
     block with `--prompt-block TAG` only if the chapter has that construction.
   Never paste or restate prompt text into the review.
3. Judge each verse against the bar below. Do not edit data, configs, or prompts.

## The bar: defensible, not prompt-exact

Report a link only if a Greek/Hebrew-literate reviewer would call it **wrong or indefensible**:

- source word linked to a target word that does not render it
- content word NEQ'd although the target plainly renders it
- NEQ claimed where nothing in the target could correspond but a target word is left unaligned/misattached
- content-bearing source or target token left unaligned
- a supplied word made primary in a way that changes what the record claims

Do **not** report: prompt-convention deviations that are still reasonable (secondary vs. primary
on a supplied word, split vs. grouped tokens), idiomatic multi-token renderings, stylistic
choices, rendering/visualization issues, or anything you would only call a nitpick.
When a call is arguable but defensible, say so in one line — don't escalate it.

## Output

Brevity matters. Format:

```
**<book chapter> (<config>): <verdict>**   # "defensible throughout" or "N issues"
- v. N, <source> → <target>: <what's wrong, one sentence>. <suggested fix, if clear>
Arguable-but-defensible (optional, max ~3): ...
```

- Lead with the verdict. List real issues first, ordered by severity.
- One sentence per item; no restating the whole record.
- State plainly if the chapter has no substantive errors.
- Close by noting this is a model review (same model family as the aligner) and is triage,
  not a substitute for native-speaker or Greek/Hebrew review — one line, only when issues
  were found or the user is relying on it to accept a chapter.

## Notes

- OT target verse ids can differ from source verse ids (versification); records are keyed
  by target verse, so an "unaligned source" line may be incomplete there — don't flag it alone.
- Records with `[idiom]` are intentional multi-primary groupings.
- Retry-pass output replaces flagged verses in place; the header line shows which model(s) ran.
- For a whole book, run one chapter per subagent so dumps don't accumulate in the main context.
