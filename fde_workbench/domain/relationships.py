"""Explicit, typed graph relationships connecting domain entities."""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from pydantic import BaseModel, Field

from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum


class Relationship(BaseModel):
    """Explicit directed graph edge connecting two entities."""
    id: str = Field(..., description="Unique edge identifier, e.g. 'rel-org-operates-fac-01'")
    relation_type: RelationTypeEnum = Field(..., description="Relationship type enum")
    source_id: str = Field(..., description="Source entity ID")
    source_type: EntityTypeEnum = Field(..., description="Source entity type")
    target_id: str = Field(..., description="Target entity ID")
    target_type: EntityTypeEnum = Field(..., description="Target entity type")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary edge metadata (e.g. Incoterm, capacity)")

    def as_triple(self) -> Tuple[str, str, str]:
        return (self.source_id, self.relation_type.value, self.target_id)

    def as_type_triple(self) -> Tuple[EntityTypeEnum, RelationTypeEnum, EntityTypeEnum]:
        return (self.source_type, self.relation_type, self.target_type)


# Defined valid relationship schemas matching prompt requirements and operational reality
ALLOWED_RELATIONSHIPS: List[Tuple[EntityTypeEnum, RelationTypeEnum, EntityTypeEnum, str]] = [
    # Core Organization relationships
    (EntityTypeEnum.ORGANIZATION, RelationTypeEnum.OPERATES, EntityTypeEnum.FACILITY, "Organization operates an industrial/port facility"),
    (EntityTypeEnum.ORGANIZATION, RelationTypeEnum.BUYS_FROM, EntityTypeEnum.SUPPLIER, "Organization procures commodities/inputs from supplier"),
    (EntityTypeEnum.ORGANIZATION, RelationTypeEnum.SELLS_TO, EntityTypeEnum.CUSTOMER, "Organization sells export goods to foreign customer"),
    (EntityTypeEnum.ORGANIZATION, RelationTypeEnum.PRODUCES, EntityTypeEnum.PRODUCT, "Organization manufactures or processes product"),
    (EntityTypeEnum.ORGANIZATION, RelationTypeEnum.OWNS, EntityTypeEnum.MACHINE, "Organization owns physical plant machinery"),
    (EntityTypeEnum.ORGANIZATION, RelationTypeEnum.OWNS, EntityTypeEnum.WAREHOUSE, "Organization owns or leases storage warehouse/silo"),

    # Order relationships
    (EntityTypeEnum.ORDER, RelationTypeEnum.CONTAINS, EntityTypeEnum.PRODUCT, "Sales order specifies product and quantities"),
    (EntityTypeEnum.ORDER, RelationTypeEnum.FULFILLED_BY, EntityTypeEnum.PRODUCTION_BATCH, "Sales order is allocated output from batch"),
    (EntityTypeEnum.ORDER, RelationTypeEnum.GENERATES, EntityTypeEnum.SHIPMENT, "Sales order initiates dispatch shipment"),
    (EntityTypeEnum.ORDER, RelationTypeEnum.GENERATES, EntityTypeEnum.INVOICE, "Sales order billing generates commercial export invoice"),

    # Shipment relationships
    (EntityTypeEnum.SHIPMENT, RelationTypeEnum.TRANSPORTS, EntityTypeEnum.PRODUCT, "Shipment physically moves product payload"),
    (EntityTypeEnum.SHIPMENT, RelationTypeEnum.HANDLED_BY, EntityTypeEnum.CARRIER, "Shipment contracted to barge or road freight carrier"),
    (EntityTypeEnum.SHIPMENT, RelationTypeEnum.REQUIRES, EntityTypeEnum.CUSTOMS_DECLARATION, "Shipment requires VUE, DUA, or MIC/DTA declaration"),
    (EntityTypeEnum.SHIPMENT, RelationTypeEnum.DELIVERS_TO, EntityTypeEnum.CUSTOMER, "Shipment final destination is customer premises/port"),
    (EntityTypeEnum.SHIPMENT, RelationTypeEnum.ORIGINATES_FROM, EntityTypeEnum.FACILITY, "Shipment departs from origin facility dock"),
    (EntityTypeEnum.SHIPMENT, RelationTypeEnum.ACCOMPANIED_BY, EntityTypeEnum.DOCUMENT, "Shipment accompanied by physical/digital documents"),

    # Product and Batch relationships
    (EntityTypeEnum.PRODUCT, RelationTypeEnum.REQUIRES, EntityTypeEnum.MATERIAL, "Product recipe requires specific raw materials"),
    (EntityTypeEnum.PRODUCTION_BATCH, RelationTypeEnum.CONSUMES, EntityTypeEnum.MATERIAL, "Batch execution consumes raw materials"),
    (EntityTypeEnum.PRODUCTION_BATCH, RelationTypeEnum.OCCURS_AT, EntityTypeEnum.FACILITY, "Batch manufactured at specific physical plant"),
    (EntityTypeEnum.PRODUCTION_BATCH, RelationTypeEnum.PRODUCES, EntityTypeEnum.PRODUCT, "Batch produces finished product lots"),

    # Inbound and procurement relationships
    (EntityTypeEnum.PURCHASE_ORDER, RelationTypeEnum.CONTAINS, EntityTypeEnum.MATERIAL, "Purchase order specifies raw commodity inputs"),
    (EntityTypeEnum.PURCHASE_ORDER, RelationTypeEnum.ASSOCIATED_WITH, EntityTypeEnum.SUPPLIER, "Purchase order issued to vendor"),

    # Financial settlement relationships
    (EntityTypeEnum.INVOICE, RelationTypeEnum.ASSOCIATED_WITH, EntityTypeEnum.ORDER, "Invoice settles commercial export contract"),
    (EntityTypeEnum.PAYMENT, RelationTypeEnum.SETTLES, EntityTypeEnum.INVOICE, "Payment transaction extinguishes invoice debt"),

    # Regulatory and Compliance
    (EntityTypeEnum.CUSTOMS_DECLARATION, RelationTypeEnum.SATISFIES, EntityTypeEnum.REGULATORY_OBLIGATION, "Customs clearance fulfills statutory obligation"),

    # Operational events & decisions
    (EntityTypeEnum.OPERATIONAL_EVENT, RelationTypeEnum.AFFECTS, EntityTypeEnum.SHIPMENT, "Event impacts specific shipment"),
    (EntityTypeEnum.OPERATIONAL_EVENT, RelationTypeEnum.AFFECTS, EntityTypeEnum.FACILITY, "Event impacts facility operations"),
    (EntityTypeEnum.OPERATIONAL_EVENT, RelationTypeEnum.AFFECTS, EntityTypeEnum.MACHINE, "Event impacts physical machine"),
    (EntityTypeEnum.OPERATIONAL_EVENT, RelationTypeEnum.AFFECTS, EntityTypeEnum.PRODUCTION_BATCH, "Event impacts batch execution"),
    (EntityTypeEnum.OPERATIONAL_EVENT, RelationTypeEnum.AFFECTS, EntityTypeEnum.ORDER, "Event impacts commercial order delivery"),
    (EntityTypeEnum.DECISION, RelationTypeEnum.RESOLVES, EntityTypeEnum.OPERATIONAL_EVENT, "Decision mitigates operational event"),
    (EntityTypeEnum.EMPLOYEE_ROLE, RelationTypeEnum.AUTHORIZES, EntityTypeEnum.DECISION, "Role exercises authorization on decision"),
]

_ALLOWED_SET: Set[Tuple[EntityTypeEnum, RelationTypeEnum, EntityTypeEnum]] = {
    (src, rel, tgt) for src, rel, tgt, _ in ALLOWED_RELATIONSHIPS
}


def is_valid_relationship(source_type: EntityTypeEnum, relation_type: RelationTypeEnum, target_type: EntityTypeEnum) -> bool:
    """Validate whether an edge satisfies ontology schema constraints."""
    # Strict validation with allowance for generic EVENT / DECISION links
    if (source_type, relation_type, target_type) in _ALLOWED_SET:
        return True
    if relation_type == RelationTypeEnum.AFFECTS and source_type in (EntityTypeEnum.OPERATIONAL_EVENT, EntityTypeEnum.QUALITY_EVENT):
        return True
    if relation_type == RelationTypeEnum.RESOLVES and source_type == EntityTypeEnum.DECISION:
        return True
    return False
