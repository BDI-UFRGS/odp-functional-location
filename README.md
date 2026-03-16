# Functional Location Ontology Design Pattern (FL-ODP)

![Status](https://img.shields.io/badge/status-active-success.svg)
![Version](https://img.shields.io/badge/version-0.5-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Alignment](https://img.shields.io/badge/alignment-BFO%20%7C%20IOF%20%7C%20IDO--compatible-green)
![Language](https://img.shields.io/badge/language-EN%20%7C%20PT--BR-orange)

A modular Ontology Design Pattern (ODP) for modeling **Functional Locations** (*Locais de Instalação*) as persistent spatial sites in industrial asset management systems.

This ontology addresses the **persistence problem** in industrial maintenance: how to maintain semantic continuity of operational data (time-series, maintenance records, production loss reports) when physical equipment is replaced, while preserving organizational hierarchies compliant with **ISO 14224**.

## The Problem

In industrial data systems, the distinction between the **position** (where equipment goes) and the **occupant** (the physical equipment) is routinely collapsed. When a separator vessel is replaced after 5 years of service, hundreds of maintenance records, sensor time-series, and safety analyses are associated with the position — not with the specific vessel. Existing approaches either treat positions as opaque strings (losing semantic structure), model them as equipment properties (breaking on replacement), or represent them as information artifacts (losing spatial semantics).

## The Pattern

The FL-ODP separates four independently persistent concerns, all anchored to the same `bfo:Site`:

```
Equipment Tag ──denotes──→ ┌─────────────────────┐ ←──denotes── FL Code
  (SEP-V001)                │  FunctionalLocation  │           (31242.FGAS.4110.02.01)
                            │     (bfo:Site)        │
FL Specification ──specifies→└─────────────────────┘ ←──installedAt── Equipment
  (engineering reqs)              persistent anchor          (transient physical asset)
```

| ODP Element | BFO Grounding | IDO Grounding | Role |
|:---|:---|:---|:---|
| **FunctionalLocation** | `bfo:Site` | `lis:Site` | Persistent spatial position |
| **FunctionalLocationCode** | `iao:Identifier` | `lis:InformationObject` | Hierarchical address (ISO 14224) |
| **EquipmentTag** | `iao:Identifier` | `lis:InformationObject` | Functional designation (naming convention) |
| **FunctionalLocationSpecification** | `iao:DirectiveIE` | `lis:Specified` | Engineering requirements |
| **Equipment** | `iof:PieceOfEquipment` | `lis:PhysicalObject` | Transient physical asset |

### Why `bfo:Site`?

The choice of `bfo:Site` as the grounding category results from a systematic elimination of alternatives:

| BFO Category | Persists when empty? | Spatial queries? | Hierarchy? | Relative to plant? | Verdict |
|:---|:---:|:---:|:---:|:---:|:---|
| `MaterialEntity` | No | Yes | Yes | Yes | Fails persistence |
| `Role` | No | No | No | — | Fails persistence, spatial, hierarchy |
| `ICE` | Yes | No | Partial | — | Fails spatial queries |
| `SpatialRegion` | Yes | Yes | Yes | No | Fails for floating units |
| **`Site`** | **Yes** | **Yes** | **Yes** | **Yes** | **All satisfied** |

A site's boundaries are determined *in relation to* material entities (nozzles, deck frames) but not *by coincidence with* the equipment that occupies it.

### Two Identifiers, One Location

A critical design decision: **neither the equipment tag nor the FL code links directly to the physical equipment**. Both denote the functional location (the position). The connection to equipment is *mediated* through the site:

```
Tag "SEP-V001" ──identifiesLocation──→ FL Site ←──installedAt── Physical Separator
Code "31242.FGAS.4110.02.01" ──identifies──→ FL Site
```

When engineers say "valve SEP-V001", they mean "the equipment *currently installed at* the position denoted by SEP-V001." The `hasTag` property chain formalizes this pragmatic shorthand:

```
hasTag ⊑ installedAt ∘ identifiesLocation⁻¹
```

## Key Features

- **ISO 14224 Compliance:** Five-level hierarchy (Plant → System → Subsystem → Equipment Unit → Maintainable Item) with restricting axioms enforcing level constraints.
- **Temporal Continuity:** Datasets (`TimeStampedMeasuredDataset`) and maintenance notes are indexed by the *Site*, not the *Equipment*, ensuring data persists across replacements.
- **Spatial Reasoning:** Relative coordinates (X, Y, Z) anchored to material reference frames.
- **Equipment Universals:** COPPP-style primitive classes with necessary conditions (not defined classes) — classification requires domain expert assertion.
- **Upper-Ontology Agnostic:** Formal mapping to IDO (`lis:Site`, `lis:Specified`, `lis:InformationObject`) enables adoption by both BFO/IOF and IDO/ISO 23726-3 ecosystems.
- **Bilingual:** Full IOF Annotation Vocabulary compliance with annotations in English and Brazilian Portuguese (*Português Brasileiro*).
- **IOF Annotations:** Aristotelian natural language definitions, semi-formal definitions, first-order logic definitions, usage notes, explanatory notes, and maturity levels for all classes and properties.

## Logical Axioms

The ontology includes restricting axioms beyond simple taxonomy:

| Class | Restriction | Rationale |
|:---|:---|:---|
| `FunctionalLocation` | `hasBoundaryDeterminedBy some MaterialEntity` | Definitional — makes it a site |
| `FunctionalLocationCode` | `identifies exactly 1 FunctionalLocation` | Code uniqueness |
| `EquipmentTag` | `identifiesLocation exactly 1 FunctionalLocation` | Tag uniqueness |
| `FunctionalLocationSpecification` | `specifiesLocation some FunctionalLocation` | Spec must have a location |
| `Equipment` | `installedAt max 1 FunctionalLocation` | One place at a time |
| `SystemSite` | `partOfSystemSite some PlantSite` | ISO 14224 Level 2 → Level 1 |
| `SubsystemSite` | `partOfSystemSite some SystemSite` | ISO 14224 Level 3 → Level 2 |
| `EquipmentUnitSite` | `partOfSystemSite some SubsystemSite` | ISO 14224 Level 4 → Level 3 |
| `MaintainableItemSite` | `partOfSystemSite some EquipmentUnitSite` | ISO 14224 Level 5 → Level 4 |
| `SeparationEquipment` | `bears some SeparationFunction` | Necessary condition (universal) |
| Hierarchy levels | `AllDisjointClasses` | Five-way disjointness |

**Deliberately NOT restricted:** FL does not require a tag or code (design phase); specification does not require a function (can constrain physical parameters only); equipment does not require `installedAt` (can be in warehouse).

## Competency Questions

| CQ | Question | Mechanism |
|:---|:---|:---|
| CQ1 | Which equipment is currently installed at FL `31242.FGAS.4110.02.01`? | Single join via site |
| CQ2 | Retrieve all maintenance records for an FL across 10 years and 3 equipment replacements | Join via persistent site — no application logic needed |
| CQ3 | List all FLs within the Gas Processing subsystem | Recursive `partOfSystemSite` |
| CQ4 | Which FLs require gas-liquid separation function? | Via specification |
| CQ5 | Which equipment is within 10m of an FL? | Coordinate data on site |
| CQ6 | List all separation equipment in the production system | Equipment universal + hierarchy |
| CQ7 | Cross-source integration for a production loss event | Multi-source join via site |

## Usage Example

Instantiating a sensor replacement scenario (Turtle syntax):

```turtle
@prefix fl: <https://www.inf.ufrgs.br/ontologies/odp/functional-location#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# The persistent site
fl:FL_PT23424_Site a fl:MaintainableItemSite ;
    fl:partOfSystemSite fl:InletSeparator_Site ;
    fl:hasCoordinateX "145.4"^^xsd:double ;
    fl:hasCoordinateY "67.8"^^xsd:double ;
    fl:hasCoordinateZ "12.6"^^xsd:double .

# Two identifiers — both denote the SITE, not the equipment
fl:Tag_PT23424 a fl:EquipmentTag ;
    fl:identifiesLocation fl:FL_PT23424_Site .

fl:Code_PT23424 a fl:FunctionalLocationCode ;
    fl:identifies fl:FL_PT23424_Site .

# Specification — prescribes requirements at the position
fl:Spec_PT23424 a fl:FunctionalLocationSpecification ;
    fl:specifiesLocation fl:FL_PT23424_Site ;
    fl:requiresFunction fl:PressureSensingFunction_1 .

# Equipment replacements — three sensors, same site
fl:Sensor_v1 a fl:Sensor ;
    fl:installedAt fl:FL_PT23424_Site ;
    fl:installedDate "2015-01-01T00:00:00"^^xsd:dateTime ;
    fl:removedDate "2017-06-15T10:30:00"^^xsd:dateTime .

fl:Sensor_v2 a fl:Sensor ;
    fl:installedAt fl:FL_PT23424_Site ;
    fl:installedDate "2017-06-16T08:00:00"^^xsd:dateTime ;
    fl:removedDate "2022-03-10T14:20:00"^^xsd:dateTime .

fl:Sensor_v3 a fl:Sensor ;
    fl:installedAt fl:FL_PT23424_Site ;
    fl:installedDate "2022-03-11T09:15:00"^^xsd:dateTime .
    # No removedDate → currently installed

# Time series — indexed by SITE, not by sensor
fl:TS_Pressure a fl:TimeStampedMeasuredDataset ;
    fl:indexedBySite fl:FL_PT23424_Site ;
    fl:storedAt "influxdb://p74/pressure/pt23424"^^xsd:anyURI .

# Maintenance note — anchored to SITE
fl:WO_2023 a fl:MaintenanceNote ;
    fl:performedAt fl:FL_PT23424_Site ;
    fl:noteText "Pressure anomaly detected at PT-23424" ;
    fl:noteTimestamp "2023-05-15T14:30:00"^^xsd:dateTime .
```

## Repository Structure

```
fl-odp/
├── fl-odp.ttl                  # Main ontology file (Turtle)
├── README.md                   # This file
├── LICENSE                     # MIT License
└── figures/
    └── odp-diagram.png         # Pattern diagram
```

## Alignment & Dependencies

This ontology imports and extends:

| Dependency | Role |
|:---|:---|
| [Basic Formal Ontology (BFO) 2020](http://purl.obolibrary.org/obo/bfo.owl) | Upper-level categories (Site, MaterialEntity, Function) |
| [Information Artifact Ontology (IAO)](http://purl.obolibrary.org/obo/iao.owl) | Identifier, InformationContentEntity |
| [IOF Core](https://spec.industrialontologies.org/ontology/core/Core/) | MaintainableMaterialItem, annotation vocabulary |
| [IOF Maintenance](https://spec.industrialontologies.org/ontology/maintenance/Maintenance/) | MaintenanceActivity |

**IDO compatibility** is demonstrated through a formal element-level mapping (see paper Section 5) but IDO is not imported — the pattern can be adopted as an IDO extension module.

## Related Work

This ODP is developed as part of the **COPPP** (Core Ontology for Petroleum Production Plants) doctoral research. It addresses a gap explicitly acknowledged by:

- **IOF-Maint** (Woods et al., 2024) — simplifies FLs to strings, noting full modeling as future work
- **IDO Working Draft** (Section 7.7) — editor's note acknowledges the "front office" persistence problem
- **IMF** (DNV) — provides conceptual separation but no OWL axioms

## Contributors

Nicolau Santos · Mara Abel · Haroldo Rojas · Rafael Petry · Regis Romeu · Cauã Antunes · Joel Carbonera · Fabrício Rodrigues

All contributors are affiliated with the **INF-UFRGS-ENERGIA** research group at the Institute of Informatics, Universidade Federal do Rio Grande do Sul (UFRGS), Porto Alegre, Brazil.

## Citation

*Paper in preparation. Citation details will be added upon submission.*

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
