"""SQLite-backed deterministic graph repository and tamper-evident audit store."""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum
from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.domain.evidence import EvidenceRecord, EvidenceSourceType
from fde_workbench.domain.entities import BaseEntity, KPI, ENTITY_TYPE_TO_CLASS
from fde_workbench.domain.relationships import Relationship
from fde_workbench.domain.events import OperationalEventRecord, EventSeverity, EventStatus
from fde_workbench.domain.decisions import DecisionRecord
from fde_workbench.domain.ai_opportunities import AIOpportunity
from fde_workbench.domain.agent_specs import AgentSpecification

GENESIS_HASH = "0" * 64


class WorkbenchStore:
    """
    SQLite-backed graph repository with tamper-evident cryptographic hash-chain audit log.
    Preserves exact same public interface as the in-memory store.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default database file in workspace
            workspace_dir = Path(__file__).resolve().parent.parent.parent
            self.db_path = str(workspace_dir / "workbench.db")
        else:
            self.db_path = db_path

        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    system_of_record TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    relation_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(relation_type);")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_id);")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    triggering_event_id TEXT NOT NULL,
                    decision_owner TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dec_event ON decisions(triggering_event_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dec_status ON decisions(status);")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id TEXT PRIMARY KEY,
                    workflow TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_specs (
                    spec_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence (
                    id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    extracted_claim TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_source_type ON evidence(source_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidence_provenance ON evidence(provenance);")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_seq ON audit_log(sequence);")

    # --- TAMPER-EVIDENT AUDIT TRAIL ---

    def log_audit(self, action: str, entity_id: str, details: Dict[str, Any]):
        """Append-only tamper-evident cryptographic hash-chain entry."""
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("SELECT sequence, entry_hash FROM audit_log ORDER BY sequence DESC LIMIT 1;")
            last_row = cursor.fetchone()

            if last_row:
                seq = last_row["sequence"] + 1
                prev_hash = last_row["entry_hash"]
            else:
                seq = 1
                prev_hash = GENESIS_HASH

            ts = datetime.utcnow().isoformat()
            canonical_details = json.dumps(details, sort_keys=True, separators=(",", ":"))
            content = f"{seq}:{ts}:{action}:{entity_id}:{canonical_details}:{prev_hash}".encode("utf-8")
            entry_hash = hashlib.sha256(content).hexdigest()

            cursor.execute("""
                INSERT INTO audit_log (sequence, timestamp, action, entity_id, details_json, prev_hash, entry_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (seq, ts, action, entity_id, canonical_details, prev_hash, entry_hash))

    def verify_audit_chain(self) -> Dict[str, Any]:
        """
        Walks the entire cryptographic hash-chain from sequence 1 to HEAD.
        Verifies every prev_hash and recomputes SHA-256 for each entry.
        Flags any tampering, deletion, or modification.
        """
        cursor = self._conn.cursor()
        cursor.execute("SELECT sequence, timestamp, action, entity_id, details_json, prev_hash, entry_hash FROM audit_log ORDER BY sequence ASC;")
        rows = cursor.fetchall()

        if not rows:
            return {"valid": True, "total_entries": 0, "head_hash": None}

        expected_prev_hash = GENESIS_HASH
        for idx, row in enumerate(rows, start=1):
            if row["sequence"] != idx:
                return {
                    "valid": False,
                    "corrupted_sequence": row["sequence"],
                    "reason": f"Sequence gap or reordering: expected {idx}, got {row['sequence']}",
                }

            if row["prev_hash"] != expected_prev_hash:
                return {
                    "valid": False,
                    "corrupted_sequence": row["sequence"],
                    "reason": f"Mismatched prev_hash at sequence {row['sequence']}: expected {expected_prev_hash}, got {row['prev_hash']}",
                }

            # Canonical details verification
            try:
                parsed_details = json.loads(row["details_json"])
                canonical_details = json.dumps(parsed_details, sort_keys=True, separators=(",", ":"))
            except Exception:
                canonical_details = row["details_json"]

            content = f"{row['sequence']}:{row['timestamp']}:{row['action']}:{row['entity_id']}:{canonical_details}:{row['prev_hash']}".encode("utf-8")
            recalculated_hash = hashlib.sha256(content).hexdigest()

            if recalculated_hash != row["entry_hash"]:
                return {
                    "valid": False,
                    "corrupted_sequence": row["sequence"],
                    "reason": f"Tampered entry_hash at sequence {row['sequence']}: recalculated {recalculated_hash} != stored {row['entry_hash']}",
                }

            expected_prev_hash = row["entry_hash"]

        return {
            "valid": True,
            "total_entries": len(rows),
            "head_hash": rows[-1]["entry_hash"],
        }

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT sequence, timestamp, action, entity_id, details_json, prev_hash, entry_hash
            FROM audit_log ORDER BY sequence DESC LIMIT ?;
        """, (limit,))
        results = []
        for r in cursor.fetchall():
            results.append({
                "sequence": r["sequence"],
                "timestamp": r["timestamp"],
                "action": r["action"],
                "entity_id": r["entity_id"],
                "details": json.loads(r["details_json"]),
                "prev_hash": r["prev_hash"],
                "entry_hash": r["entry_hash"],
            })
        return results

    # --- ENTITIES ---

    def _deserialize_entity(self, row: sqlite3.Row) -> BaseEntity:
        payload = json.loads(row["payload_json"])
        ent_type = EntityTypeEnum(row["entity_type"])
        cls = ENTITY_TYPE_TO_CLASS.get(ent_type, BaseEntity)
        return cls.model_validate(payload)

    def add_entity(self, entity: BaseEntity) -> BaseEntity:
        payload_str = entity.model_dump_json()
        now_iso = datetime.utcnow().isoformat()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("SELECT id FROM entities WHERE id = ?;", (entity.id,))
            exists = cursor.fetchone() is not None

            cursor.execute("""
                INSERT INTO entities (id, entity_type, name, system_of_record, payload_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    entity_type = excluded.entity_type,
                    name = excluded.name,
                    system_of_record = excluded.system_of_record,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at;
            """, (
                entity.id,
                entity.entity_type.value,
                entity.name,
                entity.system_of_record,
                payload_str,
                now_iso,
                now_iso,
            ))

        self.log_audit("UPDATE_ENTITY" if exists else "CREATE_ENTITY", entity.id, {
            "type": entity.entity_type.value,
            "name": entity.name,
        })
        return entity

    def get_entity(self, entity_id: str) -> Optional[BaseEntity]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM entities WHERE id = ?;", (entity_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._deserialize_entity(row)

    def list_entities(
        self,
        entity_type: Optional[EntityTypeEnum] = None,
        search: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[BaseEntity]:
        query = "SELECT * FROM entities WHERE 1=1"
        params = []
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type.value)
        if search:
            query += " AND (LOWER(name) LIKE ? OR LOWER(id) LIKE ? OR LOWER(payload_json) LIKE ?)"
            term = f"%{search.lower()}%"
            params.extend([term, term, term])

        query += " ORDER BY name ASC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return [self._deserialize_entity(row) for row in cursor.fetchall()]

    def count_entities(self, entity_type: Optional[EntityTypeEnum] = None) -> int:
        cursor = self._conn.cursor()
        if entity_type:
            cursor.execute("SELECT COUNT(*) FROM entities WHERE entity_type = ?;", (entity_type.value,))
        else:
            cursor.execute("SELECT COUNT(*) FROM entities;")
        return cursor.fetchone()[0]

    def delete_entity(self, entity_id: str) -> bool:
        cursor = self._conn.cursor()
        cursor.execute("SELECT entity_type FROM entities WHERE id = ?;", (entity_id,))
        row = cursor.fetchone()
        if not row:
            return False
        ent_type = row["entity_type"]

        with self._conn:
            cursor.execute("DELETE FROM entities WHERE id = ?;", (entity_id,))
            cursor.execute("DELETE FROM relationships WHERE source_id = ? OR target_id = ?;", (entity_id, entity_id))

        self.log_audit("DELETE_ENTITY", entity_id, {"type": ent_type})
        return True

    # --- RELATIONSHIPS ---

    def _deserialize_rel(self, row: sqlite3.Row) -> Relationship:
        meta = json.loads(row["metadata_json"]) if row["metadata_json"] else {}
        return Relationship(
            id=row["id"],
            relation_type=RelationTypeEnum(row["relation_type"]),
            source_id=row["source_id"],
            source_type=EntityTypeEnum(row["source_type"]),
            target_id=row["target_id"],
            target_type=EntityTypeEnum(row["target_type"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
            metadata=meta,
        )

    def add_relationship(self, rel: Relationship) -> Relationship:
        meta_json = json.dumps(rel.metadata)
        now_iso = rel.created_at.isoformat() if rel.created_at else datetime.utcnow().isoformat()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO relationships (id, relation_type, source_id, source_type, target_id, target_type, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    relation_type = excluded.relation_type,
                    source_id = excluded.source_id,
                    source_type = excluded.source_type,
                    target_id = excluded.target_id,
                    target_type = excluded.target_type,
                    metadata_json = excluded.metadata_json;
            """, (
                rel.id,
                rel.relation_type.value,
                rel.source_id,
                rel.source_type.value,
                rel.target_id,
                rel.target_type.value,
                meta_json,
                now_iso,
            ))

        self.log_audit("CREATE_RELATIONSHIP", rel.id, {
            "source": rel.source_id,
            "relation": rel.relation_type.value,
            "target": rel.target_id,
        })
        return rel

    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM relationships WHERE id = ?;", (rel_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._deserialize_rel(row)

    def list_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationTypeEnum] = None,
        limit: int = 500,
    ) -> List[Relationship]:
        query = "SELECT * FROM relationships WHERE 1=1"
        params = []
        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)
        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)
        if relation_type:
            query += " AND relation_type = ?"
            params.append(relation_type.value)

        query += " ORDER BY created_at DESC LIMIT ?;"
        params.append(limit)

        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return [self._deserialize_rel(row) for row in cursor.fetchall()]

    def delete_relationship(self, rel_id: str) -> bool:
        cursor = self._conn.cursor()
        cursor.execute("SELECT source_id, target_id FROM relationships WHERE id = ?;", (rel_id,))
        row = cursor.fetchone()
        if not row:
            return False

        with self._conn:
            cursor.execute("DELETE FROM relationships WHERE id = ?;", (rel_id,))

        self.log_audit("DELETE_RELATIONSHIP", rel_id, {"source": row["source_id"], "target": row["target_id"]})
        return True

    def get_entity_connections(self, entity_id: str) -> Dict[str, Any]:
        """Returns 1-hop connected graph around an entity."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM relationships WHERE source_id = ?;", (entity_id,))
        outgoing = [self._deserialize_rel(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM relationships WHERE target_id = ?;", (entity_id,))
        incoming = [self._deserialize_rel(row) for row in cursor.fetchall()]

        connected_ids = {r.target_id for r in outgoing} | {r.source_id for r in incoming}
        connected_entities = {}
        for cid in connected_ids:
            ent = self.get_entity(cid)
            if ent:
                connected_entities[cid] = ent

        return {
            "entity_id": entity_id,
            "outgoing": outgoing,
            "incoming": incoming,
            "connected_entities": connected_entities,
        }

    # --- EVENTS ---

    def add_event(self, event: OperationalEventRecord) -> OperationalEventRecord:
        payload_str = event.model_dump_json()
        now_iso = event.timestamp.isoformat() if event.timestamp else datetime.utcnow().isoformat()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO events (id, entity_id, entity_type, event_type, severity, status, payload_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    entity_id = excluded.entity_id,
                    entity_type = excluded.entity_type,
                    event_type = excluded.event_type,
                    severity = excluded.severity,
                    status = excluded.status,
                    payload_json = excluded.payload_json,
                    timestamp = excluded.timestamp;
            """, (
                event.id,
                event.entity_id,
                event.entity_type.value,
                event.event_type,
                event.severity.value,
                event.status.value,
                payload_str,
                now_iso,
            ))

        self.log_audit("RECORD_EVENT", event.id, {
            "event_type": event.event_type,
            "severity": event.severity.value,
            "entity_id": event.entity_id,
        })
        return event

    def get_event(self, event_id: str) -> Optional[OperationalEventRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM events WHERE id = ?;", (event_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return OperationalEventRecord.model_validate(json.loads(row["payload_json"]))

    def list_events(
        self,
        severity: Optional[EventSeverity] = None,
        status: Optional[EventStatus] = None,
        entity_id: Optional[str] = None,
    ) -> List[OperationalEventRecord]:
        query = "SELECT payload_json FROM events WHERE 1=1"
        params = []
        if severity:
            query += " AND severity = ?"
            params.append(severity.value)
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)

        query += " ORDER BY timestamp DESC;"
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return [OperationalEventRecord.model_validate(json.loads(row["payload_json"])) for row in cursor.fetchall()]

    # --- DECISIONS ---

    def add_decision(self, decision: DecisionRecord) -> DecisionRecord:
        payload_str = decision.model_dump_json()
        now_iso = decision.timestamp.isoformat() if decision.timestamp else datetime.utcnow().isoformat()
        status_val = decision.status.value if hasattr(decision, "status") and hasattr(decision.status, "value") else str(getattr(decision, "status", "DECISION_PENDING"))
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO decisions (decision_id, triggering_event_id, decision_owner, status, payload_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET
                    triggering_event_id = excluded.triggering_event_id,
                    decision_owner = excluded.decision_owner,
                    status = excluded.status,
                    payload_json = excluded.payload_json,
                    timestamp = excluded.timestamp;
            """, (
                decision.decision_id,
                decision.triggering_event_id,
                decision.decision_owner,
                status_val,
                payload_str,
                now_iso,
            ))

        self.log_audit("RECORD_DECISION", decision.decision_id, {
            "event_id": decision.triggering_event_id,
            "owner": decision.decision_owner,
            "status": status_val,
        })
        return decision

    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM decisions WHERE decision_id = ?;", (decision_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return DecisionRecord.model_validate(json.loads(row["payload_json"]))

    def list_decisions(self, event_id: Optional[str] = None) -> List[DecisionRecord]:
        query = "SELECT payload_json FROM decisions WHERE 1=1"
        params = []
        if event_id:
            query += " AND triggering_event_id = ?"
            params.append(event_id)
        query += " ORDER BY timestamp DESC;"
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return [DecisionRecord.model_validate(json.loads(row["payload_json"])) for row in cursor.fetchall()]

    # --- AI OPPORTUNITIES ---

    def add_opportunity(self, opp: AIOpportunity) -> AIOpportunity:
        payload_str = opp.model_dump_json()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO opportunities (id, workflow, payload_json)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    workflow = excluded.workflow,
                    payload_json = excluded.payload_json;
            """, (opp.id, opp.workflow, payload_str))

        self.log_audit("RECORD_OPPORTUNITY", opp.id, {"title": opp.title, "kpi": opp.kpi})
        return opp

    def list_opportunities(self) -> List[AIOpportunity]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM opportunities ORDER BY id ASC;")
        return [AIOpportunity.model_validate(json.loads(row["payload_json"])) for row in cursor.fetchall()]

    # --- AGENT SPECIFICATIONS ---

    def add_agent_spec(self, spec: AgentSpecification) -> AgentSpecification:
        payload_str = spec.model_dump_json()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO agent_specs (spec_id, title, payload_json)
                VALUES (?, ?, ?)
                ON CONFLICT(spec_id) DO UPDATE SET
                    title = excluded.title,
                    payload_json = excluded.payload_json;
            """, (spec.spec_id, spec.title, payload_str))

        self.log_audit("RECORD_AGENT_SPEC", spec.spec_id, {"title": spec.title})
        return spec

    def list_agent_specs(self) -> List[AgentSpecification]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM agent_specs ORDER BY spec_id ASC;")
        return [AgentSpecification.model_validate(json.loads(row["payload_json"])) for row in cursor.fetchall()]

    def get_agent_spec(self, spec_id: str) -> Optional[AgentSpecification]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM agent_specs WHERE spec_id = ?;", (spec_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return AgentSpecification.model_validate(json.loads(row["payload_json"]))

    # --- SOURCE EVIDENCE ---

    def add_evidence(self, evidence: EvidenceRecord) -> EvidenceRecord:
        payload_str = evidence.model_dump_json()
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO evidence (id, source, source_type, provenance, confidence, extracted_claim, payload_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source = excluded.source,
                    source_type = excluded.source_type,
                    provenance = excluded.provenance,
                    confidence = excluded.confidence,
                    extracted_claim = excluded.extracted_claim,
                    payload_json = excluded.payload_json,
                    timestamp = excluded.timestamp;
            """, (
                evidence.id,
                evidence.source,
                evidence.source_type.value,
                evidence.provenance.value,
                evidence.confidence,
                evidence.extracted_claim,
                payload_str,
                evidence.timestamp.isoformat(),
            ))

        self.log_audit("RECORD_EVIDENCE", evidence.id, {
            "source": evidence.source,
            "source_type": evidence.source_type.value,
            "provenance": evidence.provenance.value,
            "extracted_claim": evidence.extracted_claim[:100],
        })
        return evidence

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM evidence WHERE id = ?;", (evidence_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return EvidenceRecord.model_validate(json.loads(row["payload_json"]))

    def list_evidence(
        self,
        source_type: Optional[EvidenceSourceType] = None,
        provenance: Optional[ProvenanceType] = None,
        entity_id: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
    ) -> List[EvidenceRecord]:
        query = "SELECT payload_json FROM evidence WHERE 1=1"
        params: List[Any] = []
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type.value if hasattr(source_type, "value") else str(source_type))
        if provenance:
            query += " AND provenance = ?"
            params.append(provenance.value if hasattr(provenance, "value") else str(provenance))

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor = self._conn.cursor()
        cursor.execute(query, params)
        records = [EvidenceRecord.model_validate(json.loads(row["payload_json"])) for row in cursor.fetchall()]

        if entity_id:
            records = [e for e in records if entity_id in e.references_entity_ids]

        return records

    def count_evidence(
        self,
        source_type: Optional[EvidenceSourceType] = None,
        provenance: Optional[ProvenanceType] = None,
    ) -> int:
        query = "SELECT COUNT(*) as cnt FROM evidence WHERE 1=1"
        params: List[Any] = []
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type.value if hasattr(source_type, "value") else str(source_type))
        if provenance:
            query += " AND provenance = ?"
            params.append(provenance.value if hasattr(provenance, "value") else str(provenance))

        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()["cnt"]

    def delete_evidence(self, evidence_id: str) -> bool:
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM evidence WHERE id = ?;", (evidence_id,))
            deleted = cursor.rowcount > 0
        if deleted:
            self.log_audit("DELETE_EVIDENCE", evidence_id, {})
        return deleted

    # --- KPIS ---

    def add_kpi(self, kpi: KPI) -> KPI:
        self.add_entity(kpi)
        return kpi

    def list_kpis(self) -> List[KPI]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM entities WHERE entity_type = ? ORDER BY name ASC;", (EntityTypeEnum.KPI.value,))
        return [KPI.model_validate(json.loads(row["payload_json"])) for row in cursor.fetchall()]

    # --- RESET / CLEAR ---

    def clear(self):
        with self._conn:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM entities;")
            cursor.execute("DELETE FROM relationships;")
            cursor.execute("DELETE FROM events;")
            cursor.execute("DELETE FROM decisions;")
            cursor.execute("DELETE FROM opportunities;")
            cursor.execute("DELETE FROM agent_specs;")
            cursor.execute("DELETE FROM evidence;")
            cursor.execute("DELETE FROM audit_log;")

    # Compatibility properties for snapshot export
    @property
    def _evidence(self) -> Dict[str, EvidenceRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT payload_json FROM evidence;")
        return {
            json.loads(r["payload_json"])["id"]: EvidenceRecord.model_validate(json.loads(r["payload_json"]))
            for r in cursor.fetchall()
        }

    @property
    def _entities(self) -> Dict[str, BaseEntity]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM entities;")
        return {r["id"]: self._deserialize_entity(r) for r in cursor.fetchall()}

    @property
    def _relationships(self) -> Dict[str, Relationship]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM relationships;")
        return {r["id"]: self._deserialize_rel(r) for r in cursor.fetchall()}

    @property
    def _events(self) -> Dict[str, OperationalEventRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM events;")
        return {r["id"]: OperationalEventRecord.model_validate(json.loads(r["payload_json"])) for r in cursor.fetchall()}

    @property
    def _decisions(self) -> Dict[str, DecisionRecord]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM decisions;")
        return {r["decision_id"]: DecisionRecord.model_validate(json.loads(r["payload_json"])) for r in cursor.fetchall()}

    @property
    def _opportunities(self) -> Dict[str, AIOpportunity]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM opportunities;")
        return {r["id"]: AIOpportunity.model_validate(json.loads(r["payload_json"])) for r in cursor.fetchall()}

    @property
    def _agent_specs(self) -> Dict[str, AgentSpecification]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM agent_specs;")
        return {r["spec_id"]: AgentSpecification.model_validate(json.loads(r["payload_json"])) for r in cursor.fetchall()}

    @property
    def _kpis(self) -> Dict[str, KPI]:
        return {k.id: k for k in self.list_kpis()}
