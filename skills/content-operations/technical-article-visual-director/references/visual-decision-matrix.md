# Visual Decision Matrix And Plan Schema

Read this reference when deciding which visuals to keep, selecting a production method, or writing `visual-plan.md`.

## Decision Matrix

| Reader need | Preferred form | Production method | Evidence requirement | Avoid |
|---|---|---|---|---|
| Understand components and relationships | Architecture, layer, or relationship diagram | Deterministic vector or code-native diagram | Names and edges traceable to source | Decorative pseudo-architecture |
| Follow steps or state changes | Flow, sequence, or timeline | Deterministic diagram | Step order and branches verified | Compressing uncertain steps into a false linear flow |
| Compare alternatives | Matrix, aligned panels, or decision tree | Table/vector/layout tool | Same comparison axes for every option | Visual ranking unsupported by the article |
| Interpret quantities | Bar, line, scatter, distribution, or small multiple | Data chart | Original data, units, date, and source | Reconstructing values from prose or distorted axes |
| Grasp an abstract idea | Editorial metaphor or conceptual illustration | Image generation or illustration | Must not introduce factual labels or entities | Presenting metaphor as literal system behavior |
| Recognize the article promise | Cover or hero | Illustration/layout; channel-specific cover skill if available | Theme must match the article's actual thesis | Clickbait unrelated to the conclusion |
| See an actual interface or output | Annotated screenshot | Authorized capture plus redaction | Real state and provenance | Invented UI, private data, irrelevant chrome |

When two forms could work, choose the one requiring fewer invented details and less reader decoding.

## Visual Value Filter

Retain a candidate only if it scores at least 4 of 6 and has no evidence failure.

| Criterion | Score 1 when true |
|---|---|
| Removes a real comprehension bottleneck | 0/1 |
| Communicates relationships faster than prose | 0/1 |
| Supports the article's central argument | 0/1 |
| Has sufficient source evidence | 0/1 |
| Adds a distinct function not served by another figure | 0/1 |
| Remains readable at the target channel size | 0/1 |

Always retain a lower-scoring item only when the user explicitly requires it, and note the tradeoff.

## Default Ratios

Treat these as starting points, not platform guarantees:

- inline explanatory diagram: `4:3` or `3:2`;
- wide architecture or timeline: `16:9`;
- square section illustration: `1:1`;
- portrait social card: `4:5`;
- WeChat cover: delegate exact sizing to `wechat-cover` when available.

Confirm current platform specifications when exact dimensions matter.

## Visual Plan Schema

Use one table row per asset:

```markdown
| ID | Placement anchor | Reader question | Type | Essential content | Method | Ratio | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| fig-01 | After “为什么旧方案失效” | 失效发生在哪一层？ | Layer diagram | Client, gateway, cache, origin; failure edge | Deterministic SVG | 4:3 | Architecture source section 2 | planned |
```

Allowed status values:

- `planned`: accepted but not started;
- `produced`: file exists and was inspected;
- `brief-only`: production capability or evidence is unavailable;
- `blocked-evidence`: the article does not support a factual visual;
- `rejected`: intentionally removed from the set.

Under the table, give each retained asset a brief:

```markdown
### fig-01 — Failure path

- Filename: `images/fig-01-failure-path.svg`
- Placement: after the paragraph beginning “当缓存键发生漂移……”
- Composition: left-to-right four-layer flow; highlight only the failing edge in red
- Exact labels: Client, Gateway, Cache, Origin
- Caption intent: the cache key mismatch bypasses the expected hit path
- Alt-text intent: communicate the four stages and the bypass edge
- Acceptance: all edges match the source architecture; readable at 680 px width
```

For generated illustration briefs, add a positive visual prompt plus explicit exclusions. For charts, add the data file, field mapping, units, filters, and source line. For diagrams, add nodes, edges, groups, and any uncertainty that must remain visible.
