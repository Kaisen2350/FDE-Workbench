"""Local-first in-memory graph repository and audit store."""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum
from fde_workbench.domain.entities import BaseEntity, KPI
from fde_workbench.domain.relationships import Relationship, is_valid_relationship
from fde_workbench.domain.events import OperationalEventRecord, EventSeverity, EventStatus
from fde_workbench.domain.decisions import DecisionRecord
from fde_workbench.domain.ai_opportunities import AIOpportunity
from fde_workbench.domain.agent_specs import AgentSpecification


class WorkbenchStore:
    """Deterministic, local-first in-memory storage engine for FDE Workbench."""

    def __init__(self):
        self._entities: Dict[str, BaseEntity] = {}
        self._by_type: Dict[EntityTypeEnum, Set[str]] = defaultdict(set)
        
        self._relationships: Dict[str, Relationship] = {}
        self._outgoing_edges: Dict[str, List[str]] = defaultdict(list)
        self._incoming_edges: Dict[str, List[str]] = defaultdict(list)

        self._events: Dict[str, OperationalEventRecord] = {}
        self._decisions: Dict[str, DecisionRecord] = {}
        self._opportunities: Dict[str, AIOpportunity] = {}
        self._agent_specs: Dict[str, AgentSpecification] = {}
        self._kpis: Dict[str, KPI] = {}

        self._audit_log: List[Dict[str, Any]] = []

    def log_audit(self, action: str, entity_id: str, details: Dict[str, Any]):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "entity_id": entity_id,
            "details": details,
        }
        self._audit_log.append(entry)

    # --- ENTITIES ---

    def add_entity(self, entity: BaseEntity) -> BaseEntity:
        is_update = entity.id in self._entities
        self._entities[entity.id] = entity
        self._by_type[entity.entity_type].add(entity.id)
        if isinstance(entity, KPI):
            self._kpis[entity.id] = entity
        self.log_audit("UPDATE_ENTITY" if is_update else "CREATE_ENTITY", entity.id, {
            "type": entity.entity_type.value,
            "name": entity.name,
        })
        return entity

    def get_entity(self, entity_id: str) -> Optional[BaseEntity]:
        return self._entities.get(entity_id)

    def list_entities(
        self,
        entity_type: Optional[EntityTypeEnum] = None,
        search: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[BaseEntity]:
        if entity_type:
            ids = self._by_type.get(entity_type, set())
            entities = [self._entities[i] for i in ids if i in self._entities]
        else:
            entities = list(self._entities.values())

        if search:
            q = search.lower()
            entities = [
                e for e in entities
                if q in e.name.lower() or q in e.id.lower() or any(q in t.lower() for t in e.tags)
            ]

        entities.sort(key=lambda x: x.name)
        return entities[offset : offset + limit]

    def count_entities(self, entity_type: Optional[EntityTypeEnum] = None) -> int:
        if entity_type:
            return len(self._by_type.get(entity_type, set()))
        return len(self._entities)

    def delete_entity(self, entity_id: str) -> bool:
        if entity_id not in self._entities:
            return False
        ent = self._entities.pop(entity_id)
        self._by_type[ent.entity_type].discard(entity_id)
        if entity_id in self._kpis:
            del self._kpis[entity_id]
        # Remove attached edges
        for rel_id in list(self._outgoing_edges.get(entity_id, [])):
            self.delete_relationship(rel_id)
        for rel_id in list(self._incoming_edges.get(entity_id, [])):
            self.delete_relationship(rel_id)
        self.log_audit("DELETE_ENTITY", entity_id, {"type": ent.entity_type.value})
        return True

    # --- RELATIONSHIPS ---

    def add_relationship(self, rel: Relationship) -> Relationship:
        self._relationships[rel.id] = rel
        self._outgoing_edges[rel.source_id].append(rel.id)
        self._incoming_edges[rel.target_id].append(rel.id)
        self.log_audit("CREATE_RELATIONSHIP", rel.id, {
            "source": rel.source_id,
            "relation": rel.relation_type.value,
            "target": rel.target_id,
        })
        return rel

    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        return self._relationships.get(rel_id)

    def list_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationTypeEnum] = None,
        limit: int = 500,
    ) -> List[Relationship]:
        results = list(self._relationships.values())
        if source_id:
            results = [r for r in results if r.source_id == source_id]
        if target_id:
            results = [r for r in results if r.target_id == target_id]
        if relation_type:
            results = [r for r in results if r.relation_type == relation_type]
        return results[:limit]

    def delete_relationship(self, rel_id: str) -> bool:
        if rel_id not in self._relationships:
            return False
        rel = self._relationships.pop(rel_id)
        if rel.source_id in self._outgoing_edges and rel_id in self._outgoing_edges[rel.source_id]:
            self._outgoing_edges[rel.source_id].remove(rel_id)
        if rel.target_id in self._incoming_edges and rel_id in self._incoming_edges[rel.target_id]:
            self._incoming_edges[rel.target_id].remove(rel_id)
        self.log_audit("DELETE_RELATIONSHIP", rel_id, {"source": rel.source_id, "target": rel.target_id})
        return True

    def get_entity_connections(self, entity_id: str) -> Dict[str, Any]:
        """Returns 1-hop connected graph around an entity."""
        outgoing = [self._relationships[r] for r in self._outgoing_edges.get(entity_id, []) if r in self._relationships]
        incoming = [self._relationships[r] for r in self._incoming_edges.get(entity_id, []) if r in self._relationships]

        connected_entity_ids = {r.target_id for r in outgoing} | {r.source_id for r in incoming}
        connected_entities = {eid: self._entities[eid] for eid in connected_entity_ids if eid in self._entities}

        return {
            "entity_id": entity_id,
            "outgoing": outgoing,
            "incoming": incoming,
            "connected_entities": connected_entities,
        }

    # --- EVENTS ---

    def add_event(self, event: OperationalEventRecord) -> OperationalEventRecord:
        self._events[event.id] = event
        self.log_audit("RECORD_EVENT", event.id, {
            "event_type": event.event_type,
            "severity": event.severity.value,
            "entity_id": event.entity_id,
        })
        return event

    def get_event(self, event_id: str) -> Optional[OperationalEventRecord]:
        return self._events.get(event_id)

    def list_events(
        self,
        severity: Optional[EventSeverity] = None,
        status: Optional[EventStatus] = None,
        entity_id: Optional[str] = None,
    ) -> List[OperationalEventRecord]:
        evts = list(self._events.values())
        if severity:
            evts = [e for e in evts if e.severity == severity]
        if status:
            evts = [e for e in evts if e.status == status]
        if entity_id:
            evts = [e for e in evts if e.entity_id == entity_id]
        evts.sort(key=lambda e: e.timestamp, reverse=True)
        return evts

    # --- DECISIONS ---

    def add_decision(self, decision: DecisionRecord) -> DecisionRecord:
        self._decisions[decision.decision_id] = decision
        self.log_audit("RECORD_DECISION", decision.decision_id, {
            "event_id": decision.triggering_event_id,
            "owner": decision.decision_owner,
        })
        return decision

    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        return self._decisions.get(decision_id)

    def list_decisions(self, event_id: Optional[str] = None) -> List[DecisionRecord]:
        decs = list(self._decisions.values())
        if event_id:
            decs = [d for d in decs if d.triggering_event_id == event_id]
        decs.sort(key=lambda d: d.timestamp, reverse=True)
        return decs

    # --- AI OPPORTUNITIES ---

    def add_opportunity(self, opp: AIOpportunity) -> AIOpportunity:
        self._opportunities[opp.id] = opp
        self.log_audit("RECORD_OPPORTUNITY", opp.id, {"title": opp.title, "kpi": opp.kpi})
        return opp

    def list_opportunities(self) -> List[AIOpportunity]:
        return list(self._opportunities.values())

    # --- AGENT SPECIFICATIONS ---

    def add_agent_spec(self, spec: AgentSpecification) -> AgentSpecification:
        self._agent_specs[spec.spec_id] = spec
        self.log_audit("RECORD_AGENT_SPEC", spec.spec_id, {"title": spec.title})
        return spec

    def list_agent_specs(self) -> List[AgentSpecification]:
        return list(self._agent_specs.values())

    def get_agent_spec(self, spec_id: str) -> Optional[AgentSpecification]:
        return self._agent_specs.get(spec_id)

    # --- KPIS ---

    def add_kpi(self, kpi: KPI) -> KPI:
        self._kpis[kpi.id] = kpi
        self.add_entity(kpi)
        return kpi

    def list_kpis(self) -> List[KPI]:
        return list(self._kpis.values())

    # --- AUDIT TRAIL ---

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:][::-1]

    def clear(self):
        """Reset store."""
        self._entities.clear()
        self._by_type.clear()
        self._relationships.clear()
        self._outgoing_edges.clear()
        self._incoming_edges.clear()
        self._events.clear()
        self._decisions.clear()
        self._opportunities.clear()
        self._agent_specs.clear()
        self._kpis.clear()
        self._audit_log.clear()
