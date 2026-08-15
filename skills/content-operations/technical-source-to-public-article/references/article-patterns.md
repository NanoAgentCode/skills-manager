# Article Patterns And Quality Rubric

Read this reference when planning a full source-to-article transformation or judging a completed draft.

## Choose One Primary Pattern

| Pattern | Best fit | Narrative spine | Main failure to avoid |
|---|---|---|---|
| Problem -> mechanism -> consequence | A system or method solves a clear problem | What breaks, how the mechanism works, what changes, where it stops working | Turning the mechanism into a feature list |
| Common belief -> evidence -> revised model | The source corrects a misconception | Familiar belief, conflicting evidence, better explanation, practical implication | Exaggerating a nuance into a “myth busted” claim |
| Change -> why now -> who is affected | A release, standard, or ecosystem shift matters | Previous state, new evidence, enabling conditions, impact, adoption limits | Rewriting release notes as promotional news |
| Comparison -> decision axes -> recommendation | Readers must choose among approaches | Shared goal, consistent axes, tradeoffs, scenario-based choice | Declaring one universal winner |
| Concrete journey -> underlying system | A case, request, or event reveals a larger mechanism | Observable journey, hidden components, failure points, reusable lesson | Treating one anecdote as representative evidence |

Use a secondary pattern only when it strengthens the same central argument.

## Public Explanation Test

For every essential technical concept, verify four items:

1. **Plain-language role** — what job does it perform?
2. **Relationship** — what does it consume, produce, constrain, or coordinate?
3. **Mechanism** — why does that relationship create the claimed behavior?
4. **Boundary** — when does the explanation stop being true or useful?

Delete a definition that never becomes useful later in the article.

## Evidence Test

Inspect each sentence containing a number, comparison, causal verb, superlative, prediction, security claim, capability claim, or statement about the current ecosystem. It must have one of:

- a source that directly supports it;
- cautious wording that accurately reflects limited evidence;
- an explicit label as interpretation;
- removal from the publication draft.

Do not let a citation at the end of a long paragraph appear to support several unrelated claims.

## Editorial Scorecard

Score each dimension from 0 to 2. Revise any dimension scoring 0 and aim for at least 14 of 16.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Reader promise | Missing | Implied | Explicit and fulfilled |
| Central argument | Source dump | Partly coherent | One clear through-line |
| Fidelity | Distorted or unsupported | Minor ambiguity | Claims and limits preserved |
| Mechanism | Labels only | Partial explanation | Causal steps are understandable |
| Accessibility | Jargon-heavy | Mostly readable | Terms introduced at point of need |
| Evidence traceability | Unclear | Mixed | Material claims map cleanly to sources |
| Structure | Source-shaped | Serviceable | Reader-shaped progression |
| Ending | Repetition | Summary | Decision, implication, or next step |

## Final Compression Pass

Remove repeated setup, synonymous bullet points, throat-clearing, unsupported adjectives, and details that do not change the reader's mental model. Keep caveats that affect decisions even when they reduce narrative smoothness.
