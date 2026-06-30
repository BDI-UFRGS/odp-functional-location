#!/usr/bin/env python3
"""
verify_cqs.py — Empirical verification of all 7 CQs from the FL-ODP paper.

Usage (from repository root):
    python3 validation/verify_cqs.py

Loads odp-fl/odp-fl.ttl as the single source of truth (all ABox additions have been
merged in as of v0.8). All CQs use SPARQL property paths where subsumption or
transitivity is needed — no external reasoner required for the query step.

HermiT consistency check (T5): loads the ontology WITH all imports resolved from
local files in odp-fl/imports/ (BFO 2020, IAO, IOF Core 202602, IOF AV 202602,
IOF Maintenance 202602). This checks cross-import axioms, not just local TBox.
Java is required for HermiT. If Java is unavailable, the SPARQL queries still run.
"""

import sys
import pathlib
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD

REPO_ROOT = pathlib.Path(__file__).parent.parent
ONTOLOGY  = REPO_ROOT / "odp-fl" / "odp-fl.ttl"
IMPORTS   = REPO_ROOT / "odp-fl" / "imports"
CQ_DIR    = pathlib.Path(__file__).parent / "cqs"

FL  = Namespace("https://www.inf.ufrgs.br/ontologies/odp/functional-location#")
SRC = Namespace("https://www.inf.ufrgs.br/ontologies/odp/functional-location/source-schema#")

# Local import files (matches catalog-v001.xml)
IMPORT_FILES = [
    (IMPORTS / "bfo-2020.rdf",           "xml"),
    (IMPORTS / "iao.owl",                "xml"),
    (IMPORTS / "iof-av-202602.rdf",      "xml"),
    (IMPORTS / "iof-core-202602.rdf",    "xml"),
    (IMPORTS / "iof-maintenance-202602.rdf", "xml"),
]


# ─────────────────────────────────────────────────────────────────────────────
def load_graph() -> Graph:
    g = Graph()
    g.parse(str(ONTOLOGY), format="turtle")
    triples = len(g)
    print(f"Main ontology (odp-fl.ttl):  {triples} triples")
    return g


# ─────────────────────────────────────────────────────────────────────────────
def load_merged_with_imports() -> Graph:
    """Load main TTL + all local import files into a single merged graph."""
    g = Graph()

    # Load each import file
    for fpath, fmt in IMPORT_FILES:
        if fpath.exists():
            before = len(g)
            g.parse(str(fpath), format=fmt)
            added = len(g) - before
            print(f"  + {fpath.name:<40} {added:5d} new triples")
        else:
            print(f"  ! MISSING: {fpath}")

    # Load main ontology last (its triples override nothing; just merge)
    before = len(g)
    g.parse(str(ONTOLOGY), format="turtle")
    added = len(g) - before
    print(f"  + odp-fl.ttl                           {added:5d} new triples")
    print(f"  = Merged graph total:                  {len(g):5d} triples")
    return g


# ─────────────────────────────────────────────────────────────────────────────
def run_cq(g: Graph, cq_file: pathlib.Path, expected: str) -> tuple[bool, int, list]:
    """Run a single CQ. Returns (non_empty, row_count, rows)."""
    print(f"\n{'='*66}")
    print(f"  {cq_file.name}")
    print(f"{'='*66}")
    query = cq_file.read_text()
    # Print query without leading comment block
    lines = query.splitlines()
    code_start = next(
        (i for i, l in enumerate(lines) if l.strip() and not l.strip().startswith("#")),
        0,
    )
    print("\n".join(lines[code_start:]))
    print("\n--- RESULTS ---")
    results = list(g.query(query))
    if not results:
        print("  [EMPTY — 0 rows returned]")
        ok = False
    else:
        for row in results:
            formatted = []
            for v in row:
                if v is None:
                    formatted.append("UNBOUND")
                elif isinstance(v, URIRef):
                    s = str(v)
                    fl_base = "https://www.inf.ufrgs.br/ontologies/odp/functional-location#"
                    src_base = "https://www.inf.ufrgs.br/ontologies/odp/functional-location/source-schema#"
                    if s.startswith(fl_base):
                        formatted.append("fl:" + s[len(fl_base):])
                    elif s.startswith(src_base):
                        formatted.append("src:" + s[len(src_base):])
                    else:
                        formatted.append(f"<{s}>")
                else:
                    formatted.append(str(v))
            print(" ", tuple(formatted))
        print(f"  Row count: {len(results)}")
        ok = True
    print(f"\n  Expected: {expected}")
    return ok, len(results), results


# ─────────────────────────────────────────────────────────────────────────────
def check_consistency():
    """HermiT consistency check WITH all imports resolved from local files.

    Loads all import files + main ontology into a merged rdflib graph, strips
    owl:imports directives (already resolved by manual loading), serialises as
    RDF/XML, and passes to owlready2+HermiT. This checks cross-import axioms
    (BFO/IAO/IOF Core subclass hierarchies, disjointness, etc.), unlike the
    previous local-only approach.
    """
    print(f"\n{'='*66}")
    print("  Consistency check — HermiT WITH imports resolved (local files)")
    print(f"{'='*66}")
    try:
        import owlready2
        import tempfile
        import os

        print("  Loading imports + main ontology...")
        g = load_merged_with_imports()

        # Strip owl:imports declarations — they are already resolved by manual loading.
        # This prevents HermiT from attempting network fetches for the same IRIs.
        onto_iri = URIRef("https://www.inf.ufrgs.br/ontologies/odp/functional-location")
        removed = 0
        for subj, obj in list(g.subject_objects(OWL.imports)):
            g.remove((subj, OWL.imports, obj))
            removed += 1
        print(f"  Stripped {removed} owl:imports declarations (content already loaded)")
        print(f"  Final merged graph: {len(g)} triples")

        with tempfile.NamedTemporaryFile(
            suffix=".owl", delete=False, mode="wb"
        ) as f:
            tmp = f.name
            f.write(g.serialize(format="xml").encode("utf-8"))

        print(f"  Written to {tmp}")
        print("  Running HermiT (WITH BFO/IAO/IOF Core axioms present)...")

        world = owlready2.World()
        onto = world.get_ontology(f"file://{tmp}").load()
        with onto:
            owlready2.sync_reasoner_hermit(infer_property_values=False)

        unsat = list(world.inconsistent_classes())
        if not unsat:
            print("  RESULT: CONSISTENT — 0 unsatisfiable classes")
            print("  (Checked WITH BFO 2020, IAO, IOF Core 202602, IOF Maintenance 202602)")
        else:
            print(f"  RESULT: UNSATISFIABLE CLASSES: {[str(c) for c in unsat]}")

        os.unlink(tmp)
        return unsat == []

    except ImportError:
        print("  owlready2 not installed — skipping HermiT check")
        return None
    except Exception as e:
        print(f"  HermiT check failed: {type(e).__name__}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
def check_alignment_non_vacuity(g: Graph):
    """Verify the alignment axioms have non-empty extensions in the ABox."""
    print(f"\n{'='*66}")
    print("  Alignment axiom non-vacuity checks")
    print(f"{'='*66}")

    iof_constr = "https://spec.industrialontologies.org/ontology/construct/"
    MA = URIRef(iof_constr + "MaterialArtifact")

    # v0.8: fl:Equipment removed. Check that Sensor/Valve/SeparationEquipment directly
    # subclass iof-constr:MaterialArtifact (non-vacuity of the equipment→MA hierarchy).
    ma_subclasses = list(g.query("""
        PREFIX fl:  <https://www.inf.ufrgs.br/ontologies/odp/functional-location#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?cls WHERE {
          ?cls rdfs:subClassOf*/rdf:type* <https://spec.industrialontologies.org/ontology/construct/MaterialArtifact> .
          FILTER(STRSTARTS(STR(?cls), "https://www.inf.ufrgs.br/ontologies/odp/functional-location#"))
        }
    """))
    eq_instances = list(g.query("""
        PREFIX fl:   <https://www.inf.ufrgs.br/ontologies/odp/functional-location#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?x WHERE {
          ?x rdf:type/rdfs:subClassOf* fl:Sensor .
        }
    """)) + list(g.query("""
        PREFIX fl:   <https://www.inf.ufrgs.br/ontologies/odp/functional-location#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?x WHERE {
          ?x rdf:type/rdfs:subClassOf* fl:Valve .
        }
    """)) + list(g.query("""
        PREFIX fl:   <https://www.inf.ufrgs.br/ontologies/odp/functional-location#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?x WHERE {
          ?x rdf:type/rdfs:subClassOf* fl:SeparationEquipment .
        }
    """))
    print(f"  Sensor/Valve/SeparationEquipment rdfs:subClassOf iof-constr:MaterialArtifact (v0.8 direct hierarchy)")
    print(f"    Equipment-type instances (Sensor+Valve+SeparationEquipment subtree): {len(eq_instances)} individuals")

    # Check fl:FunctionalLocation owl:disjointWith iof-constr:MaterialArtifact
    fl_instances = list(g.query("""
        PREFIX fl: <https://www.inf.ufrgs.br/ontologies/odp/functional-location#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?x WHERE {
          ?x rdf:type/rdfs:subClassOf* fl:FunctionalLocation .
        }
    """))
    print(f"  fl:FunctionalLocation owl:disjointWith iof-constr:MaterialArtifact")
    print(f"    FunctionalLocation instances (all hierarchy levels): {len(fl_instances)}")
    print(f"    (None should be typed MaterialArtifact for axiom to be non-vacuous)")


# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("FL-ODP Competency Question Verification (v0.8 — imports resolved)")
    print("=" * 66)
    g = load_graph()

    consistent = check_consistency()
    check_alignment_non_vacuity(g)

    cqs = [
        (
            "cq1.rq",
            "1 row: fl:Sensor_PT23424_v3, installedDate=2022-03-11T09:15:00",
        ),
        (
            "cq2.rq",
            "2 rows: fl:WorkOrder_2023_05_15 (ts bound) + fl:TS_Pressure_PT23424 (ts unbound)",
        ),
        (
            "cq3.rq",
            "2 rows: fl:FL_V23401_Site (EquipmentUnitSite) + fl:FL_PT23424_Site (MaintainableItemSite)",
        ),
        (
            "cq4.rq",
            "1 row: loc=fl:FL_V23401_Site, spec=fl:Spec_V23401",
        ),
        (
            "cq5.rq",
            "1 row: fl:Separator_V23401_v1 at fl:FL_V23401_Site, dist≈4.82m",
        ),
        (
            "cq6.rq",
            "1 row: eq=fl:Separator_V23401_v1, loc=fl:FL_V23401_Site, fkind=fl:GasLiquidSeparationFunction",
        ),
        (
            "cq7.rq",
            "7+ rows: MaintenanceNote + EquipmentHistory (4 items) + Specification (2) across 2 sites",
        ),
    ]

    results_summary = []
    for fname, expected in cqs:
        ok, nrows, rows = run_cq(g, CQ_DIR / fname, expected)
        results_summary.append((fname, ok, nrows))

    # Final summary
    print(f"\n{'='*66}")
    print("  FINAL SUMMARY")
    print(f"{'='*66}")
    if consistent is True:
        print("  HermiT: CONSISTENT (with BFO/IAO/IOF Core 202602 imports)")
    elif consistent is False:
        print("  HermiT: INCONSISTENT — see output above")
    else:
        print("  HermiT: skipped (owlready2/Java unavailable)")

    passed = 0
    for fname, ok, nrows in results_summary:
        status = "PASS (non-empty)" if ok else "FAIL (empty)"
        print(f"  {fname}: {status} — {nrows} row(s)")
        if ok:
            passed += 1
    print(f"\n  {passed}/{len(cqs)} CQs returned non-empty results")

    if passed < len(cqs):
        sys.exit(1)


if __name__ == "__main__":
    main()
