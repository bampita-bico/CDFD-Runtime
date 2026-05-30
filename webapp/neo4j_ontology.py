"""
Ontology + Decision Layer — Neo4j backend (Palantir-style).

Graph schema:
  (:Field {id, label, requires_restricted_access})
  (:Patient)-[:HAS_SYSTEM]->(:BiologicalSystem)-[:IN_FIELD]->(:Field)
  (:BiologicalSystem)-[:INTERACTS_WITH {strength}]->(:BiologicalSystem)
  (:BiologicalSystem)-[:HAS_BIOMARKER]->(:Biomarker)
  (:BiologicalSystem)-[:HAS_STATE]->(:SystemState {psi, classification, timestamp})
  (:Biomarker)-[:DRIVES_FLUX|:DRIVES_CONSTRAINT]->(:BiologicalSystem)
"""

import os
import time
from typing import Any

from runtime.decision import classify_operating_state

# Twelve major modelling fields (domain split — not a single cluttered graph namespace)
ONTOLOGY_FIELDS: dict[str, dict[str, Any]] = {
    "medicine": {"label": "Medicine", "requires_restricted_access": True},
    "physics": {"label": "Physics", "requires_restricted_access": False},
    "chemistry": {"label": "Chemistry", "requires_restricted_access": False},
    "biology": {"label": "Biology", "requires_restricted_access": False},
    "climate": {"label": "Climate", "requires_restricted_access": False},
    "geology": {"label": "Geology", "requires_restricted_access": False},
    "finance": {"label": "Finance", "requires_restricted_access": False},
    "economics": {"label": "Economics", "requires_restricted_access": False},
    "ecology": {"label": "Ecology", "requires_restricted_access": False},
    "neuroscience": {"label": "Neuroscience", "requires_restricted_access": False},
    "social_systems": {"label": "Social systems", "requires_restricted_access": False},
    "technology": {"label": "Technology", "requires_restricted_access": False},
    "sports_markets": {"label": "Sports markets", "requires_restricted_access": False},
}


def list_fields() -> list[dict[str, Any]]:
    return [
        {"id": fid, **meta}
        for fid, meta in ONTOLOGY_FIELDS.items()
    ]

# ── Neo4j driver (optional — falls back gracefully if unavailable) ─────────────
try:
    from neo4j import GraphDatabase
    _NEO4J_AVAILABLE = True
except ImportError:
    _NEO4J_AVAILABLE = False

_NEO4J_URI  = os.environ.get("NEO4J_URI",      "bolt://localhost:7687")
_NEO4J_USER = os.environ.get("NEO4J_USER",     "neo4j")
_NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "cdfd_secret")

_driver = None


def _get_driver():
    global _driver
    if not _NEO4J_AVAILABLE:
        return None
    if _driver is None:
        try:
            _driver = GraphDatabase.driver(_NEO4J_URI, auth=(_NEO4J_USER, _NEO4J_PASS))
        except Exception:
            return None
    return _driver


def _run(cypher: str, **params) -> list[dict]:
    driver = _get_driver()
    if driver is None:
        return []
    try:
        with driver.session() as session:
            result = session.run(cypher, **params)
            return [dict(r) for r in result]
    except Exception:
        return []


# ── Schema bootstrap ──────────────────────────────────────────────────────────

def ensure_schema():
    """Create indexes and constraints on first startup."""
    _run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE")
    _run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:BiologicalSystem) REQUIRE s.id IS UNIQUE")
    _run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Biomarker) REQUIRE b.id IS UNIQUE")
    _run("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Field) REQUIRE f.id IS UNIQUE")
    _run("CREATE INDEX IF NOT EXISTS FOR (s:SystemState) ON (s.timestamp)")
    seed_fields()


def seed_fields():
    """MERGE twelve Field nodes for multi-domain graphs."""
    for fid, meta in ONTOLOGY_FIELDS.items():
        _run(
            """
            MERGE (f:Field {id: $id})
            SET f.label = $label,
                f.requires_restricted_access = $rc
            """,
            id=fid,
            label=meta["label"],
            rc=bool(meta["requires_restricted_access"]),
        )


# ── Patient / System helpers ──────────────────────────────────────────────────

def upsert_patient(patient_id: str, meta: dict | None = None) -> dict:
    meta = meta or {}
    _run(
        "MERGE (p:Patient {id: $id}) SET p += $meta RETURN p",
        id=patient_id, meta=meta
    )
    return {"patient_id": patient_id}


def upsert_system(
    system_id: str,
    system_type: str,
    patient_id: str | None = None,
    field_id: str | None = None,
) -> dict:
    _run(
        "MERGE (s:BiologicalSystem {id: $id}) SET s.type = $type",
        id=system_id, type=system_type
    )
    if patient_id:
        _run(
            """
            MATCH (p:Patient {id: $pid}), (s:BiologicalSystem {id: $sid})
            MERGE (p)-[:HAS_SYSTEM]->(s)
            """,
            pid=patient_id, sid=system_id
        )
    if field_id and field_id in ONTOLOGY_FIELDS:
        meta = ONTOLOGY_FIELDS[field_id]
        _run(
            """
            MERGE (f:Field {id: $fid})
            SET f.label = $label, f.requires_restricted_access = $rc
            WITH f
            MATCH (s:BiologicalSystem {id: $sid})
            MERGE (s)-[:IN_FIELD]->(f)
            """,
            fid=field_id,
            label=meta["label"],
            rc=bool(meta["requires_restricted_access"]),
            sid=system_id,
        )
    return {"system_id": system_id, "field_id": field_id}


def link_system_interaction(
    from_system_id: str,
    to_system_id: str,
    strength: float = 1.0,
) -> dict:
    """Directed coupling between systems (cross-organ / cross-domain links)."""
    _run(
        """
        MATCH (a:BiologicalSystem {id: $aid}), (b:BiologicalSystem {id: $bid})
        MERGE (a)-[r:INTERACTS_WITH]->(b)
        SET r.strength = $s
        """,
        aid=from_system_id,
        bid=to_system_id,
        s=float(strength),
    )
    return {"from": from_system_id, "to": to_system_id, "strength": strength}


def explain_overload(
    patient_id: str,
    system_id: str | None = None,
    psi_threshold: float = 1.2,
) -> dict[str, Any]:
    """
    Systems whose latest Ψ exceeds threshold, with biomarkers driving flux vs constraint.
    """
    q_base = """
        MATCH (p:Patient {id: $pid})-[:HAS_SYSTEM]->(s:BiologicalSystem)
        OPTIONAL MATCH (s)-[:HAS_STATE]->(st:SystemState)
        WITH s, st ORDER BY st.timestamp DESC
        WITH s, collect(st)[0] AS latest
        WHERE latest IS NOT NULL AND latest.psi > $thr
        OPTIONAL MATCH (bf:Biomarker)-[:DRIVES_FLUX]->(s)
        OPTIONAL MATCH (bc:Biomarker)-[:DRIVES_CONSTRAINT]->(s)
        RETURN s.id AS system_id, s.type AS system_type, latest.psi AS psi,
               collect(DISTINCT bf.name) AS flux_biomarkers,
               collect(DISTINCT bc.name) AS constraint_biomarkers
        LIMIT 50
        """
    q_filter = """
        MATCH (p:Patient {id: $pid})-[:HAS_SYSTEM]->(s:BiologicalSystem)
        WHERE s.id = $sid
        OPTIONAL MATCH (s)-[:HAS_STATE]->(st:SystemState)
        WITH s, st ORDER BY st.timestamp DESC
        WITH s, collect(st)[0] AS latest
        WHERE latest IS NOT NULL AND latest.psi > $thr
        OPTIONAL MATCH (bf:Biomarker)-[:DRIVES_FLUX]->(s)
        OPTIONAL MATCH (bc:Biomarker)-[:DRIVES_CONSTRAINT]->(s)
        RETURN s.id AS system_id, s.type AS system_type, latest.psi AS psi,
               collect(DISTINCT bf.name) AS flux_biomarkers,
               collect(DISTINCT bc.name) AS constraint_biomarkers
        LIMIT 50
        """
    if system_id:
        rows = _run(q_filter, pid=patient_id, sid=system_id, thr=psi_threshold)
    else:
        rows = _run(q_base, pid=patient_id, thr=psi_threshold)
    explanations = []
    for r in rows:
        psi_v = float(r.get("psi") or 0)
        flux_bm = [x for x in (r.get("flux_biomarkers") or []) if x]
        cons_bm = [x for x in (r.get("constraint_biomarkers") or []) if x]
        guidance = classify_operating_state(
            psi_v,
            meta={
                "high_flux_biomarkers": flux_bm,
                "high_constraint_biomarkers": cons_bm,
            },
            domain="medicine",
        )
        explanations.append(
            {
                "system_id": r.get("system_id"),
                "system_type": r.get("system_type"),
                "psi": psi_v,
                "flux_biomarkers": flux_bm,
                "constraint_biomarkers": cons_bm,
                "runtime_guidance": guidance,
            }
        )
    return {"patient_id": patient_id, "threshold": psi_threshold, "explanations": explanations}


def cross_system_influence(patient_id: str, max_hops: int = 3) -> dict[str, Any]:
    """Bounded INTERACTS_WITH walks from each patient system."""
    hops = max(1, min(int(max_hops), 6))
    rows = _run(
        """
        MATCH (p:Patient {id: $pid})-[:HAS_SYSTEM]->(s:BiologicalSystem)
        MATCH path = (s)-[:INTERACTS_WITH*1.."""
        + str(hops)
        + """]->(t:BiologicalSystem)
        RETURN s.id AS origin, t.id AS target,
               length(path) AS hops,
               reduce(acc = 1.0, r IN relationships(path) | acc * coalesce(r.strength, 1.0)) AS effective_strength
        LIMIT 200
        """,
        pid=patient_id,
    )
    return {"patient_id": patient_id, "max_hops": hops, "paths": rows}


def record_biomarker(system_id: str, name: str, value: float, role: str = "flux") -> dict:
    """
    role: 'flux' (drives Φ) or 'constraint' (drives C)
    """
    bm_id = f"{system_id}:{name}"
    _run(
        "MERGE (b:Biomarker {id: $id}) SET b.name = $name, b.value = $val",
        id=bm_id, name=name, val=value
    )
    rel = "DRIVES_FLUX" if role == "flux" else "DRIVES_CONSTRAINT"
    _run(
        f"""
        MATCH (s:BiologicalSystem {{id: $sid}}), (b:Biomarker {{id: $bid}})
        MERGE (b)-[:{rel}]->(s)
        """,
        sid=system_id, bid=bm_id
    )
    return {"biomarker_id": bm_id, "role": role}


def record_state(system_id: str, psi: float, classification: str, meta: dict | None = None) -> dict:
    ts = time.time()
    _run(
        """
        MATCH (s:BiologicalSystem {id: $sid})
        CREATE (st:SystemState {psi: $psi, classification: $cls,
                                timestamp: $ts, meta: $meta})
        CREATE (s)-[:HAS_STATE]->(st)
        """,
        sid=system_id, psi=psi, cls=classification, ts=ts, meta=str(meta or {})
    )
    return {"system_id": system_id, "psi": psi, "classification": classification, "timestamp": ts}


def get_patient_graph(patient_id: str) -> dict:
    rows = _run(
        """
        MATCH (p:Patient {id: $pid})-[:HAS_SYSTEM]->(s:BiologicalSystem)
        OPTIONAL MATCH (s)-[:HAS_STATE]->(st:SystemState)
        OPTIONAL MATCH (b:Biomarker)-[:DRIVES_FLUX|DRIVES_CONSTRAINT]->(s)
        RETURN s.id AS system, s.type AS type,
               st.psi AS psi, st.classification AS classification,
               collect(b.name) AS biomarkers
        ORDER BY st.timestamp DESC
        """,
        pid=patient_id
    )
    return {"patient_id": patient_id, "systems": rows}


# ── Decision layer ────────────────────────────────────────────────────────────

# The graph layer uses the runtime's neutral operating-state classifier. It does
# not define a separate deployment rule table.


# ── What-If projection ────────────────────────────────────────────────────────

def whatif(base_phi: float, base_C: float, overrides: dict) -> dict:
    """
    Project Ψ under parameter overrides without running the full engine.
    Overrides: {"phi_delta": float, "C_delta": float, "phi_scale": float, "C_scale": float}
    Returns neutral runtime guidance for the projected state.
    """
    phi = base_phi * overrides.get("phi_scale", 1.0) + overrides.get("phi_delta", 0.0)
    C   = base_C   * overrides.get("C_scale",   1.0) + overrides.get("C_delta",   0.0)
    phi = max(phi, 1e-9)
    C   = max(C,   1e-9)
    psi = phi / C
    guidance = classify_operating_state(psi, domain="whatif")
    guidance["projected_phi"] = phi
    guidance["projected_C"] = C
    return guidance
