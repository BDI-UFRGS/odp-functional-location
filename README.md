# Functional Location Ontology Design Pattern (ODP)

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Alignment](https://img.shields.io/badge/alignment-BFO%20%7C%20IOF-green)

A modular Ontology Design Pattern (ODP) for modeling **Functional Locations (FL)** as persistent spatial sites in industrial asset management systems. 

This ontology addresses the **persistence problem** in industrial maintenance: maintaining semantic continuity of operational data (e.g., time-series, maintenance notes) when physical equipment is replaced, while preserving strict organizational hierarchies compliant with **ISO 14224**.

## 📖 Overview

In many industrial ontologies, the distinction between the "hole" (the functional position) and the "filler" (the physical equipment) is often blurred. This ODP strictly separates them using **Basic Formal Ontology (BFO)**:

* **Functional Location (`fl:FunctionalLocation`):** A persistent `bfo:Site`. It exists independently of the equipment.
* **Equipment (`fl:Equipment`):** A transient `bfo:MaterialEntity`. It is installed at a location for a specific time interval.

### Key Features
* **ISO 14224 Compliance:** Native support for the 5-level hierarchy (Plant → System → Subsystem → Equipment Unit → Maintainable Item).
* **Temporal Continuity:** Data sets (`fl:TimeStampedMeasuredDataset`) are indexed by the *Site*, not the *Equipment*, ensuring historical data remains accessible across equipment lifecycles.
* **Spatial Reasoning:** Supports relative coordinates (X, Y, Z) for site definition.

## 🧩 Core Classes & Properties

### Main Classes
| Class | Description | BFO Mapping |
| :--- | :--- | :--- |
| `FunctionalLocation` | A persistent spatial position where equipment can be installed. | `bfo:Site` |
| `Equipment` | Physical asset (Pump, Valve, Sensor) that has a finite lifespan at a location. | `bfo:MaterialEntity` |
| `FunctionalLocationCode` | The hierarchical identifier code (e.g., `30234.FSFS...`). | `iao:InformationContentEntity` |
| `MaintenanceNote` | Textual notes anchored to the location. | `iao:InformationContentEntity` |

### Key Properties
* `installedAt`: Connects Equipment to a Functional Location (temporally bounded).
* `partOfSystemSite`: Defines the transitive hierarchy (e.g., Subsystem is part of System).
* `indexedBySite`: Links time-series data to the persistent location.
* `hasCoordinateX/Y/Z`: Defines spatial position relative to a reference frame.

## 🚀 Competency Questions (CQs)

This ODP was designed to answer the following competency questions:

1.  **CQ1:** Which physical equipment is *currently* installed at Functional Location X?
2.  **CQ2:** How can I retrieve the complete pressure history of a specific pipe section, spanning multiple sensors installed over 10 years?
3.  **CQ3:** What are all the maintainable items located within "Gas Dehydration System"?
4.  **CQ6:** Which maintenance notes are associated with this location, regardless of which specific valve was installed at the time?

## 💻 Usage Example

Here is how to instantiate a sensor replacement scenario using this ODP (Turtle syntax):

```turtle
@prefix fl: [https://w3id.org/iof/odp/functional-location#](https://w3id.org/iof/odp/functional-location#) .
@prefix xsd: [http://www.w3.org/2001/XMLSchema#](http://www.w3.org/2001/XMLSchema#) .

# 1. The Persistent Site (Functional Location)
fl:FL_PT23424_Site rdf:type fl:MaintainableItemSite ;
    fl:partOfSystemSite fl:InletSeparator_Site ;
    rdfs:label "Functional Location PT-23424" .

# 2. The Old Sensor (Removed in 2022)
fl:Sensor_v2 rdf:type fl:Sensor ;
    fl:installedAt fl:FL_PT23424_Site ;
    fl:installedDate "2017-06-16T08:00:00"^^xsd:dateTime ;
    fl:removedDate   "2022-03-10T14:20:00"^^xsd:dateTime .

# 3. The New Sensor (Current)
fl:Sensor_v3 rdf:type fl:Sensor ;
    fl:installedAt fl:FL_PT23424_Site ;
    fl:installedDate "2022-03-11T09:15:00"^^xsd:dateTime .
    # No removedDate implies currently installed

# 4. Time Series Data (Linked to the Site, not the Sensor)
fl:TS_Pressure_History rdf:type fl:TimeStampedMeasuredDataset ;
    fl:indexedBySite fl:FL_PT23424_Site ;
    fl:storedAt "influxdb://p74/pressure/pt23424"^^xsd:anyURI .
```

## 📚 Alignment & Dependencies

This ontology imports and extends:

- Basic Formal Ontology (BFO) 2020
- IOF Core
- IOF Maintenance

## 👥 Contributors (for now)

- Nicolau Santos (UFRGS)
- Haroldo Rojas
- Mara Abel
- Fabrício Rodrigues
- Regis Romeu
- Cauã Antunes
- Rafael Petry
- Joel Carbonera

Affiliation: UFRGS Institute of Informatics

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
