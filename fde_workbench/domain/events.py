"""Operational event abstraction modeling real-world supply chain deviations."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.provenance import ProvenanceType


class EventSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventStatus(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    DECISION_PENDING = "DECISION_PENDING"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"


class OperationalEventRecord(BaseModel):
    """Event model satisfying the operational reality abstraction."""
    id: str = Field(..., description="Unique event identifier, e.g. 'evt-2026-001'")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of event occurrence/detection")
    entity_id: str = Field(..., description="Target entity ID experiencing the event")
    entity_type: EntityTypeEnum = Field(..., description="Target entity type")
    event_type: str = Field(..., description="e.g. shipment_delayed, customs_doc_missing, river_draft_restriction")
    source: str = Field(..., description="Source of truth: TMS, ERP, VUE_PORTAL, RIVER_GAUGE, QUALITY_LAB, SPREADSHEET")
    provenance: ProvenanceType = Field(default=ProvenanceType.SYNTHETIC, description="Origin classification")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of Evidence records supporting this operational event")
    severity: EventSeverity = Field(default=EventSeverity.MEDIUM)
    expected_state: Dict[str, Any] = Field(default_factory=dict, description="Operational baseline or planned state")
    observed_state: Dict[str, Any] = Field(default_factory=dict, description="Observed reality or failure state")
    operational_impact: str = Field(..., description="Human/operational consequence on throughput or continuity")
    financial_impact: float = Field(default=0.0, description="Estimated direct financial loss or cost exposure in USD")
    currency: str = Field(default="USD")
    required_decision: Optional[str] = Field(default=None, description="Type of decision or action demanded")
    status: EventStatus = Field(default=EventStatus.DETECTED)
    history: List[Dict[str, Any]] = Field(default_factory=list, description="State transition log")

    def transition_to(self, new_status: EventStatus, note: str, actor: str = "System"):
        """Record state transition in history."""
        self.history.append({
            "from_status": self.status.value,
            "to_status": new_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "actor": actor,
            "note": note,
        })
        self.status = new_status


# Predefined event types catalog for Paraguayan export supply chains
STANDARD_EVENT_TYPES = {
    "shipment_delayed": {
        "description": "Barge convoy or truck dispatch running behind planned schedule",
        "typical_sources": ["TMS_GPS", "RIVER_PILOT_LOG", "CARRIER_DISPATCH"],
        "default_severity": EventSeverity.HIGH,
    },
    "customs_document_missing": {
        "description": "Required export document (MIC/DTA, CRT, VUE authorization, or Phytosanitary certificate) missing or invalid at border",
        "typical_sources": ["VUE_PORTAL", "CUSTOMS_BROKER_DRIVE", "DNIT_SYSTEM"],
        "default_severity": EventSeverity.CRITICAL,
    },
    "production_delayed": {
        "description": "Processing run stalled due to raw material starvation or equipment fault",
        "typical_sources": ["SCADA_ERP", "MAINTENANCE_LOG", "PLANT_SUPERVISOR"],
        "default_severity": EventSeverity.MEDIUM,
    },
    "inventory_below_threshold": {
        "description": "Stock of key input (grain, packaging, hexane) fallen below safety buffer",
        "typical_sources": ["SAP_B1_INVENTORY", "SILO_RADAR_SENSOR"],
        "default_severity": EventSeverity.HIGH,
    },
    "quality_failure": {
        "description": "Laboratory assay deviation (high moisture, aflatoxin, foreign matter) violating contract specs",
        "typical_sources": ["LAB_LIMS", "WEIGHBRIDGE_SAMPLE"],
        "default_severity": EventSeverity.HIGH,
    },
    "payment_delayed": {
        "description": "Cross-border export receivable wire delayed beyond credit term limit",
        "typical_sources": ["SWIFT_PORTAL", "TREASURY_EXCEL", "BCRA_CLEARING"],
        "default_severity": EventSeverity.MEDIUM,
    },
    "order_changed": {
        "description": "Customer modified delivery destination, quantity, or shipping date mid-fulfillment",
        "typical_sources": ["COMMERCIAL_GMAIL", "CRM_ERP"],
        "default_severity": EventSeverity.MEDIUM,
    },
    "supplier_disruption": {
        "description": "Upstream vendor unable to deliver contracted grain or logistics service",
        "typical_sources": ["SUPPLIER_PORTAL", "COMMODITY_BROKER"],
        "default_severity": EventSeverity.HIGH,
    },
    "river_draft_restriction": {
        "description": "Paraguay River water level drop restricting permissible barge convoy draft (calado)",
        "typical_sources": ["PREFECTURA_NAVAL_GAUGE", "HYDROLOGY_BULLETIN"],
        "default_severity": EventSeverity.CRITICAL,
    },
}
