"""Source Evidence abstraction grounding the operational model in physical reality."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from fde_workbench.domain.provenance import ProvenanceType


class EvidenceSourceType(str, Enum):
    """Classification of raw operational evidence sources."""
    ERP_RECORD = "ERP_RECORD"
    SPREADSHEET = "SPREADSHEET"
    EMAIL_MESSAGE = "EMAIL_MESSAGE"
    CONTRACT_DOCUMENT = "CONTRACT_DOCUMENT"
    CUSTOMS_DOCUMENT = "CUSTOMS_DOCUMENT"
    INTERVIEW_STATEMENT = "INTERVIEW_STATEMENT"
    TELEMETRY_STREAM = "TELEMETRY_STREAM"
    REGULATORY_GAZETTE = "REGULATORY_GAZETTE"
    PHYSICAL_INSPECTION = "PHYSICAL_INSPECTION"


class EvidenceRecord(BaseModel):
    """
    Formal Source Evidence model.
    Establishes the evidence foundation supporting operational events and decisions:
    Evidence -> Operational Event -> Decision -> Outcome
    """
    id: str = Field(..., description="Unique evidence ID, e.g. 'evi-2026-001'")
    source: str = Field(..., description="Specific system or origin, e.g. 'SAP_B1_EXPORT', 'PREFECTURA_NAVAL_GAUGE'")
    source_type: EvidenceSourceType = Field(..., description="Category of evidence artifact")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when evidence was observed or recorded")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Verification confidence score (0.0 to 1.0)")
    provenance: ProvenanceType = Field(default=ProvenanceType.SYNTHETIC, description="Origin provenance classification")
    extracted_claim: str = Field(..., description="Specific, concise factual finding extracted from this evidence")
    raw_payload_snippet: Optional[str] = Field(default=None, description="Verbatim textual extract, table row, quote, or sensor readout")
    references_entity_ids: List[str] = Field(default_factory=list, description="IDs of domain entities linked to this evidence")
    references_event_ids: List[str] = Field(default_factory=list, description="IDs of operational events directly supported by this evidence")
    references_decision_ids: List[str] = Field(default_factory=list, description="IDs of decisions informed by this evidence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or technical attributes")
