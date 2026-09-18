"""Deterministic snapshot export and import for FDE Workbench store."""

import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.entities import ENTITY_TYPE_TO_CLASS, BaseEntity
from fde_workbench.domain.relationships import Relationship
from fde_workbench.domain.events import OperationalEventRecord
from fde_workbench.domain.decisions import DecisionRecord
from fde_workbench.domain.ai_opportunities import AIOpportunity
from fde_workbench.domain.agent_specs import AgentSpecification


def export_store_to_dict(store: WorkbenchStore) -> Dict[str, Any]:
    """Serialize the entire in-memory store state to a deterministic JSON dictionary."""
    return {
        "version": "1.0.0",
        "exported_at": datetime.utcnow().isoformat(),
        "summary": {
            "entity_count": len(store._entities),
            "relationship_count": len(store._relationships),
            "event_count": len(store._events),
            "decision_count": len(store._decisions),
            "opportunity_count": len(store._opportunities),
            "agent_spec_count": len(store._agent_specs),
        },
        "entities": [e.model_dump(mode="json") for e in store._entities.values()],
        "relationships": [r.model_dump(mode="json") for r in store._relationships.values()],
        "events": [ev.model_dump(mode="json") for ev in store._events.values()],
        "decisions": [d.model_dump(mode="json") for d in store._decisions.values()],
        "opportunities": [o.model_dump(mode="json") for o in store._opportunities.values()],
        "agent_specs": [s.model_dump(mode="json") for s in store._agent_specs.values()],
        "audit_trail": store.get_audit_trail(limit=500),
    }


def import_store_from_dict(store: WorkbenchStore, data: Dict[str, Any]):
    """Hydrate in-memory store from a serialized JSON dictionary."""
    store.clear()

    # Hydrate entities using their respective typed Pydantic classes
    for ent_data in data.get("entities", []):
        ent_type_val = ent_data.get("entity_type")
        try:
            ent_type = EntityTypeEnum(ent_type_val)
            cls = ENTITY_TYPE_TO_CLASS.get(ent_type, BaseEntity)
            entity = cls.model_validate(ent_data)
            store.add_entity(entity)
        except Exception:
            entity = BaseEntity.model_validate(ent_data)
            store.add_entity(entity)

    # Hydrate relationships
    for rel_data in data.get("relationships", []):
        rel = Relationship.model_validate(rel_data)
        store.add_relationship(rel)

    # Hydrate events
    for ev_data in data.get("events", []):
        ev = OperationalEventRecord.model_validate(ev_data)
        store.add_event(ev)

    # Hydrate decisions
    for dec_data in data.get("decisions", []):
        dec = DecisionRecord.model_validate(dec_data)
        store.add_decision(dec)

    # Hydrate opportunities
    for opp_data in data.get("opportunities", []):
        opp = AIOpportunity.model_validate(opp_data)
        store.add_opportunity(opp)

    # Hydrate agent specs
    for spec_data in data.get("agent_specs", []):
        spec = AgentSpecification.model_validate(spec_data)
        store.add_agent_spec(spec)


def save_snapshot_to_file(store: WorkbenchStore, file_path: str):
    data = export_store_to_dict(store)
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_snapshot_from_file(store: WorkbenchStore, file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    import_store_from_dict(store, data)
