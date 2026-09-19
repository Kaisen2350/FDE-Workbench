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
from fde_workbench.domain.pilots import PilotSpecification, PilotStatus
from fde_workbench.domain.brief_generator import FDEBriefGenerator
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


@app.get("/api/ontology/critical-path")
def get_critical_path():
    """Returns the curated critical path spine, narrative, and connected entities."""
    return store.get_critical_path()


@app.get("/api/entities")
def list_entities(
    type: Optional[str] = Query(None, description="Entity type filter"),
    search: Optional[str] = Query(None, description="Search term across name, id, or tags"),
    critical_path: bool = Query(False, description="Filter for curated critical-path entities"),
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
    entities = store.list_entities(
        entity_type=type_enum,
        search=search,
        critical_path=critical_path,
        limit=limit,
        offset=offset
    )

    return {
        "total_overall": total_overall,
        "total_filtered": total_in_type,
        "count": len(entities),
        "critical_path_filtered": critical_path,
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


@app.post("/api/decisions/{decision_id}/escalate")
def escalate_decision(decision_id: str, body: Dict[str, Any] = Body(...)):
    """Escalates a decision with specified target role and reason, logging to tamper-evident audit trail."""
    escalated_to = body.get("escalated_to", "role-executive")
    reason = body.get("reason", "Manual operational escalation triggered from FDE workbench.")
    dec = store.escalate_decision(decision_id=decision_id, escalated_to=escalated_to, reason=reason)
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")
    dump = dec.model_dump(mode="json")
    dump["pipeline_stages"] = dec.get_pipeline_stages()
    return {
        "status": "ESCALATED",
        "decision": dump,
    }


@app.post("/api/decisions/check-escalations")
def check_decision_escalations():
    """
    Evaluates pending decisions against timeout threshold and transitions timed-out items to ESCALATED.
    Trigger Model: On-demand sweep (operator invocation or external cron/webhook).
    Local-first workbench intentionally does not run background daemon polling.
    """
    escalated = store.check_all_escalations()
    return {
        "trigger_model": "on_demand_or_scheduled_sweep",
        "escalated_count": len(escalated),
        "escalated_decisions": [d.model_dump(mode="json") for d in escalated],
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


# --- PILOT ENGINE ENDPOINTS ---

@app.get("/api/pilots")
def list_pilots(
    opportunity_id: Optional[str] = Query(None, description="Filter by AI opportunity ID"),
    status: Optional[str] = Query(None, description="Filter by pilot status"),
):
    pilots = store.list_pilots(opportunity_id=opportunity_id, status=status)
    return {
        "count": len(pilots),
        "pilots": [
            {
                **p.model_dump(mode="json"),
                "economics_summary": p.economic_model.summary(),
            }
            for p in pilots
        ],
    }


@app.get("/api/pilots/{pilot_id}")
def get_pilot_detail(pilot_id: str):
    pilot = store.get_pilot(pilot_id)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot specification not found")
    return {
        "pilot": pilot.model_dump(mode="json"),
        "economics_summary": pilot.economic_model.summary(),
    }


@app.get("/api/pilots/{pilot_id}/brief")
def get_pilot_brief(pilot_id: str, format: Optional[str] = Query("markdown", description="Format: 'markdown' or 'json'")):
    pilot = store.get_pilot(pilot_id)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot specification not found")
    
    brief_data = FDEBriefGenerator.generate_brief_data(pilot)
    brief_markdown = FDEBriefGenerator.generate_markdown(pilot)
    
    return {
        "pilot_id": pilot_id,
        "title": pilot.title,
        "customer": pilot.customer,
        "format": format,
        "brief_markdown": brief_markdown,
        "brief_data": brief_data,
    }


@app.get("/api/pilots/{pilot_id}/economic-bridge")
def get_pilot_economic_bridge(pilot_id: str):
    pilot = store.get_pilot(pilot_id)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot specification not found")

    econ = pilot.economic_model
    return {
        "pilot_id": pilot_id,
        "title": pilot.title,
        "customer": pilot.customer,
        "watermark": "Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation",
        "inputs": {
            "annual_decision_volume": econ.annual_decision_volume,
            "manual_effort_minutes_per_decision": econ.manual_effort_minutes_per_decision,
            "hourly_labor_cost_usd": econ.hourly_labor_cost_usd,
            "current_error_or_exception_rate": econ.current_error_or_exception_rate,
            "cost_per_exception_usd": econ.cost_per_exception_usd,
            "target_manual_effort_minutes": econ.target_manual_effort_minutes,
            "target_exception_rate": econ.target_exception_rate,
            "pilot_decision_volume": econ.pilot_decision_volume,
            "pilot_implementation_cost_usd": econ.pilot_implementation_cost_usd,
            "annual_software_subscription_usd": econ.annual_software_subscription_usd,
            "working_capital_acceleration_days": econ.working_capital_acceleration_days,
            "annual_working_capital_financial_value_usd": econ.annual_working_capital_financial_value_usd,
        },
        "total_first_year_investment_usd": econ.total_investment_usd(),
        "assumptions_ledger": econ.get_assumptions_table(),
        "sensitivity_analysis": econ.compute_sensitivity(),
        "calculation_steps": [
            {
                "step": 1,
                "name": "Baseline Annual Labor Cost",
                "formula": "Annual Volume * (Manual Minutes / 60) * Hourly Rate",
                "result_usd": round(econ.baseline_annual_labor_cost(), 2),
            },
            {
                "step": 2,
                "name": "Baseline Annual Exception & Rework Cost",
                "formula": "Annual Volume * Exception Rate * Cost Per Exception",
                "result_usd": round(econ.baseline_annual_exception_cost(), 2),
            },
            {
                "step": 3,
                "name": "Working Capital Drag / Carrying Cost",
                "formula": "Annual carrying cost of cash trapped in delay",
                "result_usd": round(econ.annual_working_capital_financial_value_usd, 2),
            },
            {
                "step": 4,
                "name": "Baseline Total Annual Cost",
                "formula": "Labor Cost + Exception Cost + Working Capital Drag",
                "result_usd": round(econ.baseline_annual_total_cost(), 2),
            },
            {
                "step": 5,
                "name": "Target Annual Cost Post-Intervention",
                "formula": "Target Labor Cost + Target Exception Cost",
                "result_usd": round(econ.target_annual_total_cost(), 2),
            },
            {
                "step": 6,
                "name": "Addressable Annual Savings",
                "formula": "Baseline Total - Target Total",
                "result_usd": round(econ.addressable_annual_savings(), 2),
            },
            {
                "step": 7,
                "name": "Savings Per Unit / Shipment",
                "formula": "Addressable Savings / Annual Volume",
                "result_usd": round(econ.savings_per_decision_unit(), 2),
            },
            {
                "step": 8,
                "name": "Pilot Batch Measured Value",
                "formula": "Pilot Volume * Savings Per Unit",
                "result_usd": round(econ.pilot_measured_value(), 2),
            },
            {
                "step": 9,
                "name": "Net First-Year Enterprise ROI ($)",
                "formula": "Addressable Savings - Total Investment (Implementation + License)",
                "result_usd": round(econ.first_year_net_roi_usd(), 2),
            },
            {
                "step": 10,
                "name": "First-Year Net ROI Percentage & Payback",
                "formula": "Net 1st-Year ROI / Total 1st-Year Investment * 100",
                "roi_percentage": round(econ.expected_roi_percentage(), 1),
                "payback_period_months": round(econ.payback_period_months(), 1),
            },
        ],
        "summary": econ.summary(),
    }


@app.get("/api/pilots/{pilot_id}/deployment-plan")
def get_pilot_deployment_plan(pilot_id: str, platform: Optional[str] = Query(None)):
    pilot = store.get_pilot(pilot_id)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot specification not found")

    target_platform = (platform or pilot.selected_platform).lower()
    adapter = ADAPTERS.get(target_platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {target_platform}. Supported: {list(ADAPTERS.keys())}")

    plan = adapter.generate_pilot_deployment_plan(pilot)
    validation = adapter.validate_deployment_plan_schema(plan)
    return {
        "pilot_id": pilot_id,
        "platform": target_platform,
        "validation": validation,
        "deployment_plan": plan,
    }


@app.get("/api/pilots/{pilot_id}/deployment-plan/validate")
def validate_pilot_deployment_plan(pilot_id: str, platform: Optional[str] = Query(None)):
    pilot = store.get_pilot(pilot_id)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot specification not found")

    target_platform = (platform or pilot.selected_platform).lower()
    adapter = ADAPTERS.get(target_platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {target_platform}. Supported: {list(ADAPTERS.keys())}")

    plan = adapter.generate_pilot_deployment_plan(pilot)
    validation = adapter.validate_deployment_plan_schema(plan)
    return {
        "pilot_id": pilot_id,
        "platform": target_platform,
        "validation": validation,
    }



@app.post("/api/pilots/{pilot_id}/platform")
def set_pilot_platform(pilot_id: str, payload: Dict[str, Any] = Body(...)):
    platform = payload.get("platform")
    if not platform:
        raise HTTPException(status_code=400, detail="Missing 'platform' in request body")
    
    target_platform = platform.lower()
    if target_platform not in ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {target_platform}. Supported: {list(ADAPTERS.keys())}")
    
    pilot = store.get_pilot(pilot_id)
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot specification not found")
    
    pilot.selected_platform = target_platform
    store.add_pilot(pilot)
    return {
        "status": "UPDATED",
        "pilot_id": pilot_id,
        "selected_platform": pilot.selected_platform,
    }


@app.post("/api/pilots/{pilot_id}/status")
def set_pilot_status(pilot_id: str, payload: Dict[str, Any] = Body(...)):
    new_status = payload.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing 'status' in request body")
    
    try:
        updated = store.update_pilot_status(pilot_id, new_status.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}. Valid: {[s.value for s in PilotStatus]}")
    
    if not updated:
        raise HTTPException(status_code=404, detail="Pilot specification not found")
    
    return {
        "status": "UPDATED",
        "pilot_id": pilot_id,
        "new_status": updated.status.value,
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
            "pilot_count": store.count_pilots(),
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
