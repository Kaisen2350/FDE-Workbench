"""FastAPI REST API server for the FDE Workbench."""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum, ONTOLOGY_METADATA, CRITICAL_PATH_NARRATIVE
from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.domain.evidence import EvidenceRecord, EvidenceSourceType
from fde_workbench.domain.discovery import DiscoveryIntake, DiscoveryTransformationEngine
from fde_workbench.domain.relationships import ALLOWED_RELATIONSHIPS
from fde_workbench.domain.events import EventSeverity, EventStatus
from fde_workbench.domain.adapters import ADAPTERS
from fde_workbench.domain.adapters.gemini_adapter import GeminiEnterpriseAdapter
from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.storage.snapshot import export_store_to_dict, import_store_from_dict
from fde_workbench.synthetic.generator import seed_synthetic_company

# Create global store and seed synthetic company
store = WorkbenchStore()
seed_synthetic_company(store)

app = FastAPI(
    title="Paraguay Export Economy FDE Workbench",
    description="Deterministic domain modeling, operational events, decisions, and platform-agnostic agent specifications for Paraguayan exporters.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ontology")
def get_ontology():
    """Returns ontology metadata, 24 entity definitions, critical path narrative, and relationship rules."""
    return {
        "metadata": ONTOLOGY_METADATA,
        "critical_path_narrative": CRITICAL_PATH_NARRATIVE,
        "allowed_relationships": [
            {
                "source_type": src.value,
                "relation_type": rel.value,
                "target_type": tgt.value,
                "description": desc,
            }
            for src, rel, tgt, desc in ALLOWED_RELATIONSHIPS
        ],
    }


@app.get("/api/entities")
def list_entities(
    type: Optional[str] = Query(None, description="Entity type filter"),
    search: Optional[str] = Query(None, description="Search term across name, id, or tags"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    type_enum = None
    if type:
        try:
            type_enum = EntityTypeEnum(type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid entity type: {type}")

    total_in_type = store.count_entities(type_enum)
    total_overall = store.count_entities()
    entities = store.list_entities(entity_type=type_enum, search=search, limit=limit, offset=offset)

    return {
        "total_overall": total_overall,
        "total_filtered": total_in_type,
        "count": len(entities),
        "limit": limit,
        "offset": offset,
        "entities": [e.model_dump(mode="json") for e in entities],
    }


@app.get("/api/entities/{entity_id}")
def get_entity_detail(entity_id: str):
    entity = store.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    connections = store.get_entity_connections(entity_id)
    return {
        "entity": entity.model_dump(mode="json"),
        "outgoing_relationships": [r.model_dump(mode="json") for r in connections["outgoing"]],
        "incoming_relationships": [r.model_dump(mode="json") for r in connections["incoming"]],
        "connected_entities": {k: v.model_dump(mode="json") for k, v in connections["connected_entities"].items()},
    }


@app.get("/api/relationships")
def list_relationships(
    source_id: Optional[str] = Query(None),
    target_id: Optional[str] = Query(None),
    relation_type: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=1000),
):
    rel_type_enum = None
    if relation_type:
        try:
            rel_type_enum = RelationTypeEnum(relation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid relation type: {relation_type}")

    rels = store.list_relationships(source_id=source_id, target_id=target_id, relation_type=rel_type_enum, limit=limit)
    return {
        "count": len(rels),
        "relationships": [r.model_dump(mode="json") for r in rels],
    }


@app.get("/api/events")
def list_events(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
):
    sev_enum = EventSeverity(severity) if severity else None
    stat_enum = EventStatus(status) if status else None
    events = store.list_events(severity=sev_enum, status=stat_enum, entity_id=entity_id)
    return {
        "count": len(events),
        "events": [e.model_dump(mode="json") for e in events],
    }


@app.get("/api/decisions")
def list_decisions(event_id: Optional[str] = Query(None)):
    decisions = store.list_decisions(event_id=event_id)
    results = []
    for d in decisions:
        dump = d.model_dump(mode="json")
        dump["pipeline_stages"] = d.get_pipeline_stages()
        results.append(dump)
    return {
        "count": len(results),
        "decisions": results,
    }


@app.get("/api/audit/verify")
def verify_audit():
    """Verifies the cryptographic hash-chain of the append-only audit trail."""
    return store.verify_audit_chain()


@app.get("/api/workflows")
def list_workflows():
    """Synthesizes high-level operational lifecycle traces across entities and events."""
    return {
        "workflows": [
            {
                "id": "wf-critical-path-narrative",
                "title": "★ Critical Path Narrative: Order ➔ Outcome",
                "description": "The primary operational narrative spine of the FDE Workbench: walking directly from commercial order placement through multi-modal dispatch, customs clearance, physical operational disruption, managerial decision, to verified operational outcome.",
                "corridor": "Primary Operational Spine (Featured)",
                "is_featured": True,
                "nodes": [
                    {"step": 1, "entity_type": "order", "entity_id": "ord-2026-exp-042", "name": "1. Order (EXP-2026-042)", "action": "FOB Villeta contract commitment"},
                    {"step": 2, "entity_type": "shipment", "entity_id": "shp-2026-fluv-019", "name": "2. Shipment (Convoy HB-104)", "action": "Fluvial barge convoy dispatch"},
                    {"step": 3, "entity_type": "customs_declaration", "entity_id": "cdec-vue-2026-8819", "name": "3. CustomsDeclaration (VUE #8819)", "action": "VUE / SENAVE export clearance"},
                    {"step": 4, "entity_type": "operational_event", "entity_id": "evt-2026-001", "name": "4. OperationalEvent (River Draft Deficit)", "action": "Disruption: 8.4ft draft at Paso Queso"},
                    {"step": 5, "entity_type": "decision", "entity_id": "dec-2026-001", "name": "5. Decision (Alijo Lightering)", "action": "Authorized action: charter shallow hoppers"},
                    {"step": 6, "entity_type": "outcome", "entity_id": "out-2026-001", "name": "6. Outcome (Cleared Safely)", "action": "Verified: $19,200 saved, zero grounding"},
                ],
                "active_bottleneck": "Paraguay River low draft restricting permissible barge convoy loading.",
            },
            {
                "id": "wf-export-fluvial-argentina",
                "title": "Fluvial Export Execution to Argentina (Rosario)",
                "description": "Commercial export order fulfillment via Villeta crushing mill, Hidrovía river barge convoys, and international customs clearance.",
                "corridor": "Hidrovía Paraguay-Paraná (Fluvial)",
                "is_featured": False,
                "nodes": [
                    {"step": 1, "entity_type": "customer", "entity_id": "cust-016", "name": "Molinos Fluviales del Paraná", "action": "Contract Order FOB Villeta"},
                    {"step": 2, "entity_type": "order", "entity_id": "ord-2026-exp-042", "name": "Order EXP-2026-042 (2400 MT)", "action": "Order allocation"},
                    {"step": 3, "entity_type": "production_batch", "entity_id": "batch-2026-pellet-081", "name": "Lote Molienda Villeta #081", "action": "Processing & lab release"},
                    {"step": 4, "entity_type": "customs_declaration", "entity_id": "cdec-vue-2026-8819", "name": "Declaración VUE/DUA", "action": "VUE clearance"},
                    {"step": 5, "entity_type": "shipment", "entity_id": "shp-2026-fluv-019", "name": "Convoy Barcazas HB-104", "action": "Fluvial navigation"},
                    {"step": 6, "entity_type": "operational_event", "entity_id": "evt-2026-001", "name": "River Draft Deficit (Paso Queso)", "action": "Operational disruption"},
                    {"step": 7, "entity_type": "decision", "entity_id": "dec-2026-001", "name": "Alijo de Carga Authorization", "action": "Managerial resolution"},
                    {"step": 8, "entity_type": "invoice", "entity_id": "inv-exp-2026-0042", "name": "Factura Exportación $936k", "action": "Billing & Swift MT103"},
                ],
                "active_bottleneck": "Critical low water draft on Paraguay River km 1530 requiring load transfers.",
            },
            {
                "id": "wf-export-terrestrial-brazil",
                "title": "Cross-Border Maquila Dispatch to Brazil (Cascavel / Curitiba)",
                "description": "Finished protein products packaged under Maquila regime in Hernandarias dispatched via Friendship Bridge (Puente de la Amistad) to Brazilian feed integrators.",
                "corridor": "Highway PY-02 / BR-277 (Terrestrial Bitren)",
                "nodes": [
                    {"step": 1, "entity_type": "facility", "entity_id": "fac-hernandarias", "name": "Planta Maquila Hernandarias", "action": "Packaging & palletizing"},
                    {"step": 2, "entity_type": "warehouse", "entity_id": "wh-cde-bonded", "name": "Depósito Fiscal Hernandarias", "action": "Fiscal pre-clearance"},
                    {"step": 3, "entity_type": "customs_declaration", "entity_id": "cdec-mic-dta", "name": "MIC/DTA Electrónico VUE", "action": "Electronic customs filing"},
                    {"step": 4, "entity_type": "operational_event", "entity_id": "evt-2026-002", "name": "MIC/DTA Rejection at Border", "action": "Customs syntax mismatch"},
                    {"step": 5, "entity_type": "decision", "entity_id": "dec-2026-002", "name": "Expedited VUE Rectification", "action": "Broker emergency re-submission"},
                    {"step": 6, "entity_type": "carrier", "entity_id": "carrier-trans-mercosur", "name": "Expreso Trans-Mercosur", "action": "BR-277 delivery to Cascavel"},
                ],
                "active_bottleneck": "Discrepancy in electronic customs paperwork syntax between Paraguayan VUE and Brazilian Receita Federal.",
            },
        ]
    }


@app.get("/api/opportunities")
def list_opportunities():
    opps = store.list_opportunities()
    return {
        "count": len(opps),
        "opportunities": [o.model_dump(mode="json") for o in opps],
    }


@app.get("/api/agent-specs")
def list_agent_specs():
    specs = store.list_agent_specs()
    return {
        "count": len(specs),
        "agent_specifications": [s.model_dump(mode="json") for s in specs],
    }


@app.get("/api/agent-specs/{spec_id}/export/{platform}")
def export_agent_manifest(spec_id: str, platform: str):
    spec = store.get_agent_spec(spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="Agent specification not found")
    adapter = ADAPTERS.get(platform.lower())
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Supported platforms: {list(ADAPTERS.keys())}")
    
    manifest = adapter.export_manifest(spec)
    compatibility = adapter.validate_compatibility(spec)
    return {
        "platform": platform,
        "spec_id": spec_id,
        "compatibility": compatibility,
        "manifest": manifest,
    }


@app.get("/api/agent-specs/{spec_id}/scaffold/gemini")
def get_gemini_python_scaffold(spec_id: str):
    spec = store.get_agent_spec(spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="Agent specification not found")
    adapter = GeminiEnterpriseAdapter()
    scaffold = adapter.generate_python_scaffold(spec)
    return {
        "spec_id": spec_id,
        "platform": "gemini_enterprise",
        "title": spec.title,
        "python_scaffold": scaffold,
    }


# --- SOURCE EVIDENCE ENDPOINTS ---

@app.get("/api/evidence")
def list_evidence(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    provenance: Optional[str] = Query(None, description="Filter by provenance"),
    entity_id: Optional[str] = Query(None, description="Filter by referenced entity ID"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    st_enum = None
    if source_type:
        try:
            st_enum = EvidenceSourceType(source_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid source_type: {source_type}")

    prov_enum = None
    if provenance:
        try:
            prov_enum = ProvenanceType(provenance)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provenance: {provenance}")

    evidence_list = store.list_evidence(
        source_type=st_enum,
        provenance=prov_enum,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )
    total_count = store.count_evidence(source_type=st_enum, provenance=prov_enum)
    return {
        "total": total_count,
        "count": len(evidence_list),
        "evidence": [e.model_dump(mode="json") for e in evidence_list],
    }


@app.get("/api/evidence/{evidence_id}")
def get_evidence_detail(evidence_id: str):
    evidence = store.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")
    return {"evidence": evidence.model_dump(mode="json")}


@app.post("/api/evidence")
def create_evidence(evidence_data: Dict[str, Any] = Body(...)):
    try:
        evidence = EvidenceRecord.model_validate(evidence_data)
        saved = store.add_evidence(evidence)
        return {"status": "CREATED", "evidence": saved.model_dump(mode="json")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- FDE DISCOVERY ENDPOINTS ---

@app.get("/api/discovery/intake")
def get_discovery_intake():
    intake_file = Path(__file__).resolve().parent.parent.parent / "aidesa_discovery_intake.json"
    if intake_file.exists():
        with open(intake_file, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Discovery intake file not found")


@app.post("/api/discovery/intake")
def save_discovery_intake(intake_data: Dict[str, Any] = Body(...)):
    try:
        intake = DiscoveryIntake.model_validate(intake_data)
        intake_file = Path(__file__).resolve().parent.parent.parent / "aidesa_discovery_intake.json"
        with open(intake_file, "w", encoding="utf-8") as f:
            f.write(intake.model_dump_json(indent=2))
        return {"status": "SAVED", "intake_id": intake.intake_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/discovery/generate")
def generate_from_discovery_intake(intake_data: Optional[Dict[str, Any]] = Body(None)):
    if intake_data:
        try:
            intake = DiscoveryIntake.model_validate(intake_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        intake_file = Path(__file__).resolve().parent.parent.parent / "aidesa_discovery_intake.json"
        if not intake_file.exists():
            raise HTTPException(status_code=404, detail="No active intake to generate from")
        with open(intake_file, "r", encoding="utf-8") as f:
            intake = DiscoveryIntake.model_validate(json.load(f))

    summary = DiscoveryTransformationEngine.generate_operational_model(intake, store)
    return {
        "status": "SUCCESS",
        "intake_id": intake.intake_id,
        "company": intake.company_profile.name,
        "summary": summary,
    }


@app.get("/api/kpis")
def list_kpis():
    kpis = store.list_kpis()
    return {
        "count": len(kpis),
        "kpis": [k.model_dump(mode="json") for k in kpis],
    }


@app.get("/api/company")
def get_company_overview():
    org = store.get_entity("org-aidesa")
    facs = store.list_entities(entity_type=EntityTypeEnum.FACILITY)
    sups = store.list_entities(entity_type=EntityTypeEnum.SUPPLIER)
    custs = store.list_entities(entity_type=EntityTypeEnum.CUSTOMER)
    roles = store.list_entities(entity_type=EntityTypeEnum.EMPLOYEE_ROLE)

    total_headcount = sum(r.get_attr("headcount_in_role", 0) or getattr(r, "headcount_in_role", 0) for r in roles)
    if total_headcount == 0:
        total_headcount = getattr(org, "headcount", 250)

    return {
        "organization": org.model_dump(mode="json") if org else None,
        "headcount": total_headcount,
        "facilities": [f.model_dump(mode="json") for f in facs],
        "supplier_count": len(sups),
        "customer_count": len(custs),
        "roles": [r.model_dump(mode="json") for r in roles],
        "it_systems": [
            {
                "system": "SAP Business One (HANA)",
                "category": "ERP / Core Financials & Orders",
                "scope": "Order management, invoicing (Timbrado DNIT), inventory, bill of materials",
                "status": "OPERATIONAL",
            },
            {
                "system": "Google Workspace (Sheets & Drive)",
                "category": "Dispatches & Documents",
                "scope": "Truck dispatch schedule sheets, scanned MIC/DTA/CRT documents, broker email threads",
                "status": "OPERATIONAL",
            },
            {
                "system": "Trans-Chaco TMS",
                "category": "Fleet & Dispatch Logistics",
                "scope": "Truck GPS tracking, driver assignments, weighbridge slip recording",
                "status": "OPERATIONAL",
            },
            {
                "system": "Spreadsheets (Excel)",
                "category": "Critical Operational Spreadsheets",
                "scope": "River water level draft calculations, grain moisture penalty romaneos, multi-currency USD-BRL-PYG FX cash conversion",
                "status": "OPERATIONAL",
            },
        ],
        "summary": {
            "entity_count": len(store._entities),
            "relationship_count": len(store._relationships),
            "event_count": len(store._events),
            "decision_count": len(store._decisions),
            "opportunity_count": len(store._opportunities),
            "agent_spec_count": len(store._agent_specs),
        },
    }


@app.post("/api/company/reset")
def reset_synthetic_company():
    """Reseeds the synthetic company data."""
    summary = seed_synthetic_company(store)
    return {"message": "Store successfully reset and reseeded with AIDESA synthetic data", "summary": summary}


@app.get("/api/snapshot/export")
def export_snapshot():
    return export_store_to_dict(store)


@app.post("/api/snapshot/import")
def import_snapshot(payload: Dict[str, Any] = Body(...)):
    import_store_from_dict(store, payload)
    return {"message": "Snapshot imported successfully", "entity_count": len(store._entities)}


# Mount UI static directory
ui_path = Path(__file__).resolve().parent.parent / "ui"
if ui_path.exists():
    app.mount("/static", StaticFiles(directory=str(ui_path)), name="static")

    @app.get("/")
    def index():
        return FileResponse(str(ui_path / "index.html"))

    @app.get("/ui")
    def ui():
        return FileResponse(str(ui_path / "index.html"))
