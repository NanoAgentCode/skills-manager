# Ontology Worked Reference

Use this reference when `Ontology` means a knowledge-representation or semantic-web ontology. Treat it as an accuracy guardrail and question map, not as fixed prose. Refresh current LLM/Agent claims when live research is available. Translate and restructure the material into Simplified Chinese for the final document; do not return these English headings or paragraphs verbatim.

## Contents

1. Mental model and boundary
2. Core concepts
3. Why use an ontology
4. Construction methods
5. Scenarios and non-fit cases
6. Common confusions
7. Relationship with LLMs and agents
8. Primary references

## Mental Model And Boundary

An ontology is a shared, explicit model of a domain's kinds of things, their properties and relationships, and—when formalized—the axioms that constrain their meaning and support inference. It is best understood as a semantic contract, not merely a hierarchy, a graph database, or a vocabulary list.

Keep these layers separate:

```text
domain questions -> conceptual ontology -> formal axioms -> representation language
                -> instance data / knowledge graph -> validation and reasoning -> applications
```

OWL is one language for expressing ontologies; RDF is a graph data model used by OWL and other vocabularies; a knowledge graph may instantiate or use an ontology but does not require one; SHACL describes and validates RDF graph shapes and is not interchangeable with OWL semantics.

## Core Concepts

| Concept | Role | Relationship |
|---|---|---|
| Domain and scope | Set the modeled reality and intended decisions | Prevent an ontology from becoming an unbounded encyclopedia |
| Competency question | A question the ontology must be able to answer | Drives scope, concepts, relations, and acceptance tests |
| Class or concept | Represents a category such as `Person` or `Organization` | Classes organize individuals and may form subsumption hierarchies |
| Individual or instance | Represents a particular thing | May belong to one or more classes |
| Property or relation | Connects individuals or values | Object properties link things; data properties link things to literals |
| Axiom | States formal semantic commitments | Covers subclass, equivalence, disjointness, domain, range, cardinality, and other constraints depending on the language |
| Annotation | Adds labels, definitions, provenance, or notes | Improves human use without necessarily changing logical meaning |
| Identifier / IRI | Gives a concept or entity a stable identity | Enables linking, reuse, and integration across systems |
| Reasoner | Derives entailments or checks logical consistency | Operates over formal semantics; it is not the ontology itself |
| Alignment and mapping | Relate terms across ontologies | Support integration while preserving local models |
| Versioning and governance | Control change and ownership | Keep downstream data and applications synchronized with semantic changes |

Clarify modeling assumptions. OWL commonly uses open-world reasoning and does not infer falsity from missing facts. Database-style completeness or closed-world validation often needs explicit constraints, application rules, or SHACL.

## Why Use An Ontology

Tie each benefit to a problem:

| Problem | Ontology mechanism | Potential benefit | Cost or caveat |
|---|---|---|---|
| Teams use the same word differently | Shared definitions and identifiers | Semantic interoperability | Requires agreement and governance |
| Heterogeneous data has incompatible structures | Mappings to a common conceptual model | Integration and reuse | Mapping quality becomes critical |
| Meaning is hidden in code or documents | Explicit relations and axioms | Inspectable, machine-actionable knowledge | Formalization takes domain expertise |
| Applications need derived facts | Formal semantics plus a reasoner | Consistent inference | Expressivity can increase reasoning cost |
| Models and vocabularies evolve independently | Modular reuse, imports, and versioning | Controlled change | Downstream compatibility must be managed |

Do not recommend an ontology when a small, stable application only needs a local enum, JSON Schema, relational schema, or simple taxonomy and there is no cross-system semantic problem.

## Construction Methods

Recognize method families, then choose by project needs:

- **Ontology Development 101:** a pragmatic iterative guide covering scope, reuse, term enumeration, class hierarchy, properties, facets, and instances. Use for a first domain ontology or small team.
- **METHONTOLOGY:** a structured engineering lifecycle with specification, conceptualization, formalization, implementation, integration, evaluation, documentation, and maintenance activities. Use when process rigor and traceable artifacts matter.
- **NeOn:** a scenario-based methodology for networks of ontologies, emphasizing reuse, reengineering, merging, collaboration, and evolution. Use for distributed or multi-ontology programs.
- **Pattern-based or agile ontology engineering:** reuse ontology design patterns and build only enough semantics to answer prioritized competency questions. Use for iterative product delivery.
- **Ontology learning / LLM-assisted construction:** extract terms, types, taxonomies, relations, or candidate axioms from corpora. Use as a candidate-generation accelerator, not as an autonomous authority.

Translate the chosen method into this practical loop:

```text
1. Define stakeholders, scope, and competency questions.
2. Search for reusable ontologies, vocabularies, and identifiers.
3. Collect terms and representative data/examples.
4. Model classes, relations, and identity rules; choose top-down, bottom-up, or middle-out development.
5. Add only the axioms required by competency questions and quality goals.
6. Encode in the chosen language and profile.
7. Verify syntax, logical consistency, unintended entailments, and constraint conformance.
8. Validate competency questions and terminology with domain experts.
9. Publish documentation, ownership, versioning, mappings, and change policy.
10. Monitor usage and evolve through reviewed change proposals.
```

Separate verification from validation: verification asks whether the model is internally and technically correct; validation asks whether it represents the intended domain well enough for stakeholders and applications.

## Scenarios And Non-Fit Cases

Strong-fit scenarios include cross-system semantic integration, biomedical or scientific knowledge representation, enterprise metadata and master-data alignment, semantic search, explainable rule-based inference, digital twins, data catalogs, and shared domain models for multiple applications.

For each scenario, explain which ontology mechanism is needed. A knowledge graph use case may only need a lightweight vocabulary; a regulatory reasoning use case may need formal axioms, provenance, validation, and governance.

Poor-fit cases include a single short-lived application with a stable schema, simple tagging/classification, approximate similarity search with no shared semantics, or a team unable to own semantic governance. In those cases, a taxonomy, schema, controlled vocabulary, or embedding model may be enough.

## Common Confusions

| Concept | Primary purpose | Relationship to ontology |
|---|---|---|
| Taxonomy | Classify concepts in a hierarchy | Usually narrower; may be one structural part of an ontology |
| Thesaurus / SKOS concept scheme | Manage preferred labels plus broader, narrower, and related concepts | Semi-formal knowledge organization; often lighter than an axiomatized ontology |
| Schema or data model | Define data structure, fields, and validity for an application | Can align with an ontology but usually optimizes storage or exchange rather than domain meaning |
| Knowledge graph | Store and connect entity facts in graph form | May use an ontology as its semantic layer; graph data alone is not an ontology |
| RDF | Represent information as subject-predicate-object triples | Data model and foundation for many semantic-web languages, not itself a domain ontology |
| RDFS / OWL | Express vocabularies and ontologies with increasing semantic features | Representation languages, not synonyms for the modeled ontology |
| SHACL | Describe and validate the shape of RDF graphs | Complements ontology semantics; focuses on validation constraints |
| Embedding / vector database | Represent statistical similarity and retrieve nearby vectors | Complements explicit semantics but does not replace named concepts, axioms, or governance |

## Relationship With LLMs And Agents

### Ontology To LLM/Agent

- Supply canonical terms, relations, and identifiers for normalization and grounding.
- Provide structured retrieval paths and typed context instead of relying only on chunk similarity.
- Give agents a shared domain model for memory, tool inputs/outputs, state, and cross-agent communication.
- Enable external reasoners or validators to check some generated claims and action parameters.
- Support explainability by linking outputs to explicit concepts, rules, and provenance.

Do not claim that an ontology prevents hallucination by itself. Effectiveness depends on retrieval, entity linking, prompt/context design, data quality, validation, authorization, and evaluation.

### LLM/Agent To Ontology

LLMs can propose candidate terms, term types, taxonomic relations, non-taxonomic relations, mappings, documentation, competency questions, and axioms from text. Agents can orchestrate corpus collection, extraction, review queues, reasoner runs, SHACL validation, versioning, and publication.

Keep deterministic and human gates around candidate output. Research results vary by task, axiom type, domain, model, and prompting method; current evidence does not justify treating end-to-end ontology construction as reliably autonomous.

### Reference Architecture

```text
documents/data -> LLM candidate extraction -> expert review -> ontology + constraints
              -> knowledge graph / reasoner / query layer -> agent retrieval, tools, memory
              -> provenance and feedback -> reviewed ontology evolution
```

The productive division is neuro-symbolic: use LLMs for language-heavy proposal and interaction, and use ontologies, schemas, validators, reasoners, authorization, and human governance for explicit semantics and enforceable checks.

## Primary References

- [OWL 2 Web Ontology Language Primer](https://www.w3.org/TR/owl2-primer/): classes, properties, individuals, axioms, and OWL modeling.
- [RDF 1.1 Concepts and Abstract Syntax](https://www.w3.org/TR/rdf11-concepts/): RDF graphs and triples.
- [SKOS Simple Knowledge Organization System Reference](https://www.w3.org/TR/skos-reference/): concept schemes, labels, and semantic relations for taxonomies and thesauri.
- [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/): RDF graph validation and constraints.
- [Ontology Development 101](https://protege.stanford.edu/publications/ontology_development/ontology101-noy-mcguinness.html): scope, reuse, modeling steps, and iterative ontology development.
- [METHONTOLOGY: From Ontological Art Towards Ontological Engineering](https://oa.upm.es/5484/): structured ontology-development activities and lifecycle.
- [The NeOn Methodology](https://oeg.fi.upm.es/index.php/en/methodologies/59-neon-methodology/index.html): scenario-based collaborative ontology-network development.
- [LLMs4OL: Large Language Models for Ontology Learning](https://arxiv.org/abs/2307.16648): evaluation of term typing, taxonomy discovery, and non-taxonomic relation extraction.
- [Ontology Learning with LLMs: A Benchmark Study on Axiom Identification](https://arxiv.org/abs/2512.05594): evidence that LLM axiom-identification quality varies and still requires engineering review.
