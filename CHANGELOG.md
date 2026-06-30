# Changelog — Functional Location ODP

Ontology IRI: `https://www.inf.ufrgs.br/ontologies/odp/functional-location`
Camera-ready version: **0.8**
License: CC BY-NC 4.0 (matching the FOIS 2026 proceedings)

This file records the changes to the ontology artifact between the anonymized
version provided for double-blind review and the public camera-ready release that
accompanies the FOIS 2026 paper *"An Ontology Design Pattern for Functional
Locations in Industrial Asset Management"* (Submission 70). It complements the
paper's "Description of Changes" letter, which covers the text; this file covers the
OWL artifact and the validation material. Items are annotated with the reviewer
comment they address where applicable (R1/R2/R3, metareview).

Snapshot of the camera-ready release: 704 triples; 21 classes, 14 object properties,
10 data properties, 24 named individuals; verified consistent (0 unsatisfiable
classes) with HermiT against the bundled imports.

---

## Camera-ready release (v0.8) — changes relative to the reviewed version

### Publication and reproducibility
- **De-anonymized and published** under the stable ontology IRI above; real asset
  identifiers replaced by synthetic ones throughout the validation dataset.
- **Imports bundled with an OFFLINE catalog** (R1). The repository now ships BFO
  2020, IAO, IOF Core 202602, and the IOF Annotation Vocabulary 202602 under
  `imports/`, with a populated `catalog-v001.xml` so the ontology loads and reasons
  without network access.
- **Full SPARQL query set included** (R2). The seven competency questions ship as
  runnable queries under `cqs/` (`cq1.rq`–`cq7.rq`) plus a `verify_cqs.py` runner;
  the query in Listing 1 of the paper runs verbatim against the dataset.
- **Consistency verified with imports resolved** (R2/R3). HermiT reports zero
  unsatisfiable classes over the merged ontology + imports.

### Validation dataset (R1, R2 — "evaluation is a table only")
- **Inlet-separator position added.** A separator position (`FL_V23401_Site`, tag
  `V-23401`, code `30234.FSFS.FWSF.10.02`) with its specification and a gas-liquid
  separation function was added so that **CQ4** (locations requiring a function) and
  **CQ6** (separation equipment via subsumption) are directly demonstrable on the
  dataset rather than asserted.
- **Site coordinates added** for **CQ5** (proximity), recorded as data properties in
  the platform's local reference frame.
- **Delimiting-structure individual added** (`DeckC_Structure`) and linked via
  `hasBoundaryDeterminedBy`, instantiating the delimiter that Sections 5.2 and 7.1
  describe.
- **Cross-source integration data added** for **CQ7**: a production-loss event is
  modeled in a separate source-schema namespace (`src:`) that joins to the pattern
  only through the shared functional-location site, making explicit (per Section
  7.2) that events are source data, not part of the pattern.

### Functional-location hierarchy (ISO 14224)
- **Level-skipping defect fixed.** The maintainable-item site was previously asserted
  as `partOfSystemSite` directly to the subsystem site, skipping the equipment-unit
  level. The chain is now a clean Maintainable Item → Equipment Unit → Subsystem →
  System → Plant, and **CQ3** traverses it without a shortcut.

### Text ↔ artifact alignment (R2)
- **Property names reconciled** between the paper, Figure 1, and the OWL file:
  `hasBoundaryDeterminedBy` (the reviewed text had referred to it as "delimited by"),
  `identifies` / `identifiesLocation`, `specifiesLocation`, `requiresFunction`,
  `partOfSystemSite`.
- **Identifier relations tightened.** `identifies` (for codes) and `identifiesLocation`
  (for tags) are functional sub-properties of IAO's *is about* relation
  (`IAO_0000136`), each with a qualified cardinality of exactly one; the classes
  `FunctionalLocationCode` and `EquipmentTag` are declared mutually disjoint.

### CQ1 semantics (R2's direct question)
- "Currently installed" is realized as a **query-time filter over `removedDate`**, not
  a TBox cardinality restriction. Each item is `installedAt` at most one location;
  no location-side cardinality restricts concurrent occupants. Three sequential
  sensor instances at one position demonstrate the behavior.

### Equipment modeling
- **Intermediate `Equipment` class removed.** Specific equipment types (`Sensor`,
  `Valve`, `SeparationEquipment`) now specialize `iof:MaterialArtifact` **directly**,
  following IOF Core guidance not to subclass the defined class `iof:PieceOfEquipment`.
  Types are modeled as primitive universals carrying necessary function-bearing
  conditions, with **CQ6** supported through subsumption-based retrieval.
- `installedAt`, `installedDate`, `removedDate`, `hasTag`, and `hostedBy` were
  repointed accordingly; the existing `FunctionalLocation`-disjoint-with-
  `iof:MaterialArtifact` axiom carries the equipment/location disjointness.

### Spatial grounding (R2)
- **`hasBoundaryDeterminedBy` range widened** from `bfo:Object` (`BFO_0000030`) to
  `bfo:MaterialEntity` (`BFO_0000040`), and likewise the `FunctionalLocation`
  existential restriction, aligning the axiom with the first-order-logic annotation
  and the Section 5.2 discussion.

### Upper-ontology version and modularity
- **Reconciled to IOF Core release 202602** (latest): the annotation vocabulary moved
  to the `annotation/` namespace (`maturity` replacing `maturityLevel`; the
  `Provisional`/`Released` individuals under the `individual/` namespace), and IOF
  classes are referenced under the `construct/` namespace.
- **IOF Maintenance decoupled** into an optional extension, `odp-fl-maint.ttl`. The
  core no longer hard-imports the IOF Maintenance module; an adopter who wants the
  maintenance bridge (`performedAtLocation`, domain `iof:MaintenanceActivity`) imports
  the extension. This keeps maintenance records in the source/application layer, as
  Section 7.2 states.

### Metadata
- The ontology description was corrected from "four concerns" to the **five** pattern
  elements, with the correct grounding terms (`iao:CentrallyRegisteredIdentifier`,
  `iao:DirectiveInformationEntity`, `bfo:Site`, `iof:MaterialArtifact`).

---

## Repository contents

| Path | Description |
|------|-------------|
| `odp-fl.ttl` | Core ontology (v0.8). |
| `odp-fl-maint.ttl` | Optional IOF-Maintenance bridge extension (v0.1). |
| `imports/` | Bundled BFO 2020, IAO, IOF Core 202602, IOF Annotation Vocabulary 202602 (and IOF Maintenance 202602 for the extension). |
| `catalog-v001.xml` | OWL import → local file mappings for offline loading. |
| `cqs/cq1.rq … cq7.rq` | The seven competency-question queries. |
| `verify_cqs.py` | Runs the query set against the ontology. |

---

## Embedded version log (from the ontology's `skos:historyNote`)

- **v0.1** — Initial pattern.
- **v0.2** — Added specification class.
- **v0.3** — Corrected `EquipmentTag` semantics (denotes the functional location, not the equipment).
- **v0.4** — Full IOF annotation compliance; bilingual EN/PT-BR annotations.
- **v0.5** — Added restricting logical axioms (cardinality, existential restrictions, hierarchy-level constraints, disjointness), function universals, and equipment-type universals (primitive classes with necessary conditions).
- **v0.6** — Reconciled to IOF Core release 202602 (annotation-vocabulary namespace, `maturity`, `individual`-namespace status individuals, `construct`-namespace classes).
- **v0.7** — Widened `hasBoundaryDeterminedBy` range and the `FunctionalLocation` existential to `bfo:MaterialEntity`; decoupled the IOF Maintenance dependency into the optional `odp-fl-maint.ttl` extension.
- **v0.8** — Removed the intermediate `Equipment` class; equipment types specialize `iof:MaterialArtifact` directly; repointed the installation/tag properties accordingly.
