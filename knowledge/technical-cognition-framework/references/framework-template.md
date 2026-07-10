# Technical Cognition Framework Template

Use this template for a full framework. Adapt the depth and headings to the user's goal; do not fill sections with generic text merely to preserve the template. Render the final document in Simplified Chinese, including headings, tables, conclusions, and caveats. Keep English only for source titles, URLs, code identifiers, proper nouns, and the parenthesized original term on first mention.

## Depth Modes

| Mode | Use for | Expected shape |
|---|---|---|
| Snapshot | First contact or short answer | Mental model, 3-5 concepts, one use case, one key distinction |
| Full framework | A question cluster or systematic study | All seven dimensions plus synthesis and sources |
| Decision | Technology selection or architecture choice | Full framework with alternatives, fit criteria, costs, and recommendation |
| Design | Building or integrating the technology | Decision mode plus lifecycle, artifacts, validation, governance, and prototype plan |

## Seven-Dimension Question Matrix

| Dimension | Questions to answer | Required output |
|---|---|---|
| Definition | What is it? What is it not? At which abstraction layer does it live? | One-sentence model, precise definition, boundary |
| Concepts | What are the minimum primitives? How do they compose? | Concept map or relationship table |
| Motivation | Which failure mode does it address? Why are simpler tools insufficient? | Problem-mechanism-benefit-cost chain |
| Methods | How is it designed, built, validated, and evolved? | Lifecycle plus method selection criteria |
| Scenarios | Where does the mechanism create value? Where is it overkill? | Fit and non-fit cases with constraints |
| Distinctions | What is confused with it? Are those concepts alternatives or layers? | Same-axis comparison matrix |
| LLM/Agent | What does it provide to AI systems, and what can AI systems provide back? | Bidirectional integration and responsibility split |

## Concept Skeleton

Use only the rows needed for the topic.

| Concept | Plain-language role | Relationship | Layer | Example |
|---|---|---|---|---|
| ... | ... | ... | Concept / representation / implementation / runtime / governance | ... |

After the table, explain the two or three relationships that unlock the rest of the topic.

## Motivation Chain

```text
Current failure mode:
Why existing/simple approaches fail:
Mechanism introduced by the technology:
Observable benefit:
New cost or risk:
Adoption threshold:
```

## Method Comparison

| Method | Best fit | Main artifacts | Validation | Strength | Cost or failure mode |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Turn the selected method into a concrete loop:

```text
scope -> requirements -> reuse/research -> conceptual design -> implementation
      -> verification -> user validation -> release -> versioning/governance
```

## Scenario Test

For every scenario, complete this sentence:

> Because the problem has ___, the technology's ___ mechanism produces ___, provided that ___.

Reject scenarios that only say the technology is "widely used" without explaining the mechanism.

## Confusion Matrix

| Concept | Primary purpose | Abstraction | Semantics | Inference/validation | Runtime role | Relationship to topic |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | Alternative / layer / complement / implementation |

## LLM and Agent Integration

```text
Topic -> LLM: context, grounding, retrieval, generation constraints, evaluation
Topic -> Agent: state, memory, planning, tool/data contracts, policy, interoperability
LLM/Agent -> Topic: extraction, construction, mapping, enrichment, maintenance, interaction
Deterministic boundary: schema/type checks, validation, reasoning, authorization, provenance
```

State which arrows are supported by evidence, which are architectural proposals, and which do not apply.

## Evidence Ledger

| Claim | Source type | Freshness need | Confidence or caveat |
|---|---|---|---|
| Definition | Standard, specification, or foundational paper | Low | Note competing definitions |
| Current capability | Official documentation or current benchmark | High | Include date/version |
| Ecosystem adoption | Primary usage data or multiple independent sources | High | Avoid popularity inference from anecdotes |
| Recommendation | Synthesis from requirements and evidence | Contextual | Label as analysis |

## Final Synthesis

Close with:

1. the minimum correct mental model in two or three sentences;
2. a short `use / do not use / investigate next` decision;
3. a progressive learning or prototype path.
