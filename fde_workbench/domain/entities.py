"""Typed domain entities modeling the operational reality of Paraguayan export companies."""

from datetime import datetime
from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel, Field

from fde_workbench.domain.ontology import EntityTypeEnum


class BaseEntity(BaseModel):
    """Base model for all 24 entities in the Paraguay Export Economy Ontology."""
    id: str = Field(..., description="Unique entity identifier, e.g. 'org-aidesa' or 'shp-2026-081'")
    entity_type: EntityTypeEnum = Field(..., description="Entity classification in the ontology")
    name: str = Field(..., description="Human-readable business name")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="Entity schema/revision version")
    system_of_record: str = Field(default="MANUAL", description="Source system: SAP_B1, TMS, GOOGLE_WORKSPACE, VUE_PORTAL, SPREADSHEET")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific structured attributes")
    tags: List[str] = Field(default_factory=list, description="Categorization tags, e.g. ['hidrovia', 'brazil_corridor', 'maquila']")

    def get_attr(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)


class Organization(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.ORGANIZATION
    ruc: str = Field(default="", description="Registro Único del Contribuyente (Fiscal tax ID in Paraguay)")
    legal_form: str = Field(default="S.A.", description="Sociedad Anónima, S.R.L., etc.")
    headcount: int = Field(default=250)
    export_regime: str = Field(default="General / Maquila Ley 1064", description="Export regime under Paraguayan law")
    primary_corridors: List[str] = Field(default_factory=lambda: ["Brazil - Terrestrial", "Argentina - Fluvial"])


class Facility(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.FACILITY
    facility_type: str = Field(default="PROCESSING_PLANT", description="RIVER_PORT, PROCESSING_PLANT, DEPOT, MAQUILA_ASSEMBLY")
    department: str = Field(default="Central", description="Paraguayan Department: Central, Alto Paraná, Chaco, etc.")
    city: str = Field(default="Villeta")
    throughput_capacity_tpd: float = Field(default=2500.0, description="Tons per day")
    has_barge_dock: bool = Field(default=False)
    has_rail_spur: bool = Field(default=False)
    coordinates: Dict[str, float] = Field(default_factory=lambda: {"lat": -25.51, "lng": -57.56})


class Supplier(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.SUPPLIER
    supplier_type: str = Field(default="GRAIN_PRODUCER", description="GRAIN_PRODUCER, PACKAGING, CHEMICALS, FUEL, SERVICES")
    ruc: str = Field(default="")
    department: str = Field(default="Alto Paraná")
    reliability_score: float = Field(default=0.92, description="Historical delivery reliability 0.0-1.0")
    payment_terms_days: int = Field(default=30)
    currency: str = Field(default="USD")


class Customer(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.CUSTOMER
    country: str = Field(default="Brazil", description="Brazil, Argentina, Uruguay, Chile, etc.")
    destination_city: str = Field(default="Cascavel")
    tax_id_foreign: str = Field(default="", description="CNPJ (Brazil) or CUIT (Argentina)")
    default_incoterm: str = Field(default="FOB Villeta")
    credit_limit_usd: float = Field(default=1500000.0)
    payment_terms_days: int = Field(default=45)


class Product(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.PRODUCT
    ncm_code: str = Field(default="2304.00.10", description="Mercosur Common Nomenclature / HS Code")
    unit_of_measure: str = Field(default="MT", description="Metric Tons, Kilograms, Liters")
    standard_packaging: str = Field(default="Bulk / 50kg Polypropylene Bags")
    shelf_life_days: int = Field(default=365)
    target_margin_pct: float = Field(default=14.5)


class Material(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.MATERIAL
    material_code: str = Field(default="MAT-SOJA-01")
    unit_of_measure: str = Field(default="MT")
    reorder_point_tons: float = Field(default=1500.0)
    current_inventory_tons: float = Field(default=3400.0)
    max_moisture_tolerance_pct: float = Field(default=14.0)


class Order(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.ORDER
    order_number: str = Field(default="EXP-ORD-2026-001")
    customer_id: str = Field(default="")
    incoterm: str = Field(default="FOB Villeta")
    destination_port_or_border: str = Field(default="Puerto Villeta / Hidrovía")
    quantity_ordered_mt: float = Field(default=1200.0)
    total_amount_usd: float = Field(default=468000.0)
    delivery_deadline: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="IN_FULFILLMENT", description="PENDING, IN_FULFILLMENT, SHIPPED, DELIVERED, CANCELLED")


class PurchaseOrder(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.PURCHASE_ORDER
    po_number: str = Field(default="PO-2026-042")
    supplier_id: str = Field(default="")
    material_id: str = Field(default="")
    quantity_ordered_mt: float = Field(default=2500.0)
    total_amount_usd: float = Field(default=925000.0)
    delivery_scheduled_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="DELIVERED", description="ISSUED, IN_TRANSIT, RECEIVED, REJECTED")


class Shipment(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.SHIPMENT
    shipment_code: str = Field(default="SHP-2026-081")
    transport_mode: str = Field(default="FLUVIAL", description="FLUVIAL (Barge), TERRESTRIAL (Truck), MULTIMODAL")
    origin_facility_id: str = Field(default="")
    destination: str = Field(default="Rosario, Argentina")
    carrier_id: str = Field(default="")
    weight_net_tons: float = Field(default=1500.0)
    vessel_or_truck_id: str = Field(default="Barcaza HB-104 / Convoy San Roque")
    corridor: str = Field(default="Hidrovía Paraguay-Paraná")
    estimated_departure: datetime = Field(default_factory=datetime.utcnow)
    estimated_arrival: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="IN_TRANSIT", description="PREPARING, LOADING, IN_TRANSIT, AT_BORDER, DELIVERED, DELAYED")


class Carrier(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.CARRIER
    transport_mode: str = Field(default="FLUVIAL", description="FLUVIAL, TERRESTRIAL, MARITIME")
    fleet_size: int = Field(default=24, description="Number of barges or trucks")
    dinatran_registry: str = Field(default="DINATRAN-PY-8841")
    insurance_policy_usd: float = Field(default=5000000.0)
    reliability_rating: float = Field(default=0.88)


class Warehouse(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.WAREHOUSE
    facility_id: str = Field(default="")
    storage_type: str = Field(default="GRAIN_SILO", description="GRAIN_SILO, FLAT_WAREHOUSE, BONDED_FISCAL, COLD_ROOM")
    capacity_metric_tons: float = Field(default=45000.0)
    current_occupancy_metric_tons: float = Field(default=31200.0)
    is_bonded_fiscal: bool = Field(default=False, description="Authorized fiscal deposit under DNIT customs control")


class Invoice(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.INVOICE
    invoice_number: str = Field(default="001-002-0045192")
    timbrado_dnit: str = Field(default="16489201")
    order_id: str = Field(default="")
    currency: str = Field(default="USD")
    subtotal: float = Field(default=468000.0)
    tax_amount: float = Field(default=0.0, description="Export invoices are zero-rated for Paraguayan IVA")
    total_amount: float = Field(default=468000.0)
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(default_factory=datetime.utcnow)
    payment_status: str = Field(default="PENDING", description="PENDING, PARTIALLY_PAID, PAID, OVERDUE")


class Payment(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.PAYMENT
    payment_reference: str = Field(default="SWIFT-MT103-2026-992")
    invoice_id: str = Field(default="")
    amount: float = Field(default=468000.0)
    currency: str = Field(default="USD")
    channel: str = Field(default="SWIFT_WIRE", description="SWIFT_WIRE, MERCOSUR_SML, SIPAP_LOCAL")
    fx_rate_to_pyg: float = Field(default=7550.0)
    settlement_date: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = Field(default=True)


class Contract(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.CONTRACT
    contract_number: str = Field(default="CTR-EXP-2026-FOSFA")
    governing_rules: str = Field(default="FOSFA 54 / Paraguayan Civil Code")
    arbitration_city: str = Field(default="Asunción / Montevideo")
    demurrage_usd_per_day: float = Field(default=3500.0)
    valid_until: datetime = Field(default_factory=datetime.utcnow)


class Document(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.DOCUMENT
    doc_type: str = Field(default="CRT", description="CRT, BILL_OF_LADING, ROMANEO, PACKING_LIST, CERT_ORIGIN")
    document_number: str = Field(default="CRT-BR-PY-2026-00412")
    file_format: str = Field(default="PDF")
    file_location: str = Field(default="Google Drive / Export Archive / 2026")
    is_signed: bool = Field(default=True)


class CustomsDeclaration(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.CUSTOMS_DECLARATION
    declaration_type: str = Field(default="MIC_DTA", description="VUE_PERMIT, DUA_EXPORT, MIC_DTA")
    customs_office: str = Field(default="Aduana de Ciudad del Este (Puente de la Amistad)")
    customs_broker_name: str = Field(default="Despachos Aduaneros del Este S.R.L.")
    inspection_channel: str = Field(default="VERDE", description="VERDE (Immediate release), NARANJA (Document inspection), ROJO (Physical inspection)")
    submission_date: datetime = Field(default_factory=datetime.utcnow)
    cleared_date: Optional[datetime] = None
    status: str = Field(default="CLEARED", description="DRAFT, SUBMITTED, HELD, CLEARED, REJECTED")


class RegulatoryObligation(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.REGULATORY_OBLIGATION
    agency: str = Field(default="SENAVE", description="SENAVE (Phytosanitary), SENACSA (Animal Health), DNIT, SEPRELAD, CNIME")
    statute_code: str = Field(default="Resolución SENAVE 448/21")
    mandatory_inspection: bool = Field(default=True)
    compliance_status: str = Field(default="COMPLIANT", description="COMPLIANT, PENDING_INSPECTION, VIOLATION, EXPIRED")
    expiration_date: datetime = Field(default_factory=datetime.utcnow)


class EmployeeRole(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.EMPLOYEE_ROLE
    title: str = Field(default="Logistics Dispatch Manager")
    department: str = Field(default="Operations & Logistics", description="Operations, Trade, Quality, Customs, Finance, Executive")
    headcount_in_role: int = Field(default=6)
    approval_threshold_usd: float = Field(default=50000.0)
    key_responsibilities: List[str] = Field(default_factory=lambda: ["Truck slot allocation", "Customs broker dispatch", "TMS entry"])


class Machine(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.MACHINE
    machine_code: str = Field(default="CRUSH-MILL-02")
    facility_id: str = Field(default="")
    rated_capacity_tph: float = Field(default=120.0, description="Tons per hour")
    status: str = Field(default="RUNNING", description="RUNNING, IDLE, MAINTENANCE, FAULTED")
    maintenance_interval_hours: int = Field(default=500)
    operating_hours: int = Field(default=384)


class ProductionBatch(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.PRODUCTION_BATCH
    batch_number: str = Field(default="BATCH-2026-PELLET-08")
    product_id: str = Field(default="")
    facility_id: str = Field(default="")
    output_quantity_mt: float = Field(default=850.0)
    protein_assay_pct: float = Field(default=46.5, description="Contractual min typically 46.0%")
    moisture_assay_pct: float = Field(default=11.8, description="Contractual max typically 12.5%")
    quality_status: str = Field(default="APPROVED", description="PENDING_LAB, APPROVED, RECONDITION, REJECTED")


class QualityEvent(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.QUALITY_EVENT
    parameter_tested: str = Field(default="Moisture Percentage")
    target_threshold: float = Field(default=14.0)
    observed_value: float = Field(default=15.4)
    disposition: str = Field(default="PRICE_DISCOUNT_APPLIED", description="ACCEPTED_NORM, PRICE_DISCOUNT_APPLIED, RECONDITION, REJECTED")
    penalty_amount_usd: float = Field(default=8500.0)


class OperationalEvent(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.OPERATIONAL_EVENT
    event_type: str = Field(default="shipment_delayed")
    source: str = Field(default="TMS")
    severity: str = Field(default="HIGH")
    expected_state: Dict[str, Any] = Field(default_factory=dict)
    observed_state: Dict[str, Any] = Field(default_factory=dict)
    operational_impact: str = Field(default="")
    financial_impact: float = Field(default=0.0)
    currency: str = Field(default="USD")
    required_decision: Optional[str] = Field(default=None)
    status: str = Field(default="DETECTED")


class Decision(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.DECISION
    triggering_event_id: str = Field(default="")
    decision_owner: str = Field(default="Operations Director")
    context_summary: str = Field(default="")
    options_summary: List[str] = Field(default_factory=list)
    recommendation: str = Field(default="")
    authorization_required: bool = Field(default=True)
    authorized_action_summary: Optional[str] = Field(default=None)
    outcome_summary: Optional[str] = Field(default=None)


class KPI(BaseEntity):
    entity_type: EntityTypeEnum = EntityTypeEnum.KPI
    category: str = Field(default="LOGISTICS", description="LOGISTICS, FINANCIAL, QUALITY, COMPLIANCE")
    metric_code: str = Field(default="CUSTOMS_DWELL_HOURS")
    current_value: float = Field(default=18.5)
    target_value: float = Field(default=8.0)
    unit_of_measure: str = Field(default="Hours")
    trend: str = Field(default="IMPROVING", description="IMPROVING, STABLE, DEGRADING")


ENTITY_TYPE_TO_CLASS: Dict[EntityTypeEnum, Type[BaseEntity]] = {
    EntityTypeEnum.ORGANIZATION: Organization,
    EntityTypeEnum.FACILITY: Facility,
    EntityTypeEnum.SUPPLIER: Supplier,
    EntityTypeEnum.CUSTOMER: Customer,
    EntityTypeEnum.PRODUCT: Product,
    EntityTypeEnum.MATERIAL: Material,
    EntityTypeEnum.ORDER: Order,
    EntityTypeEnum.PURCHASE_ORDER: PurchaseOrder,
    EntityTypeEnum.SHIPMENT: Shipment,
    EntityTypeEnum.CARRIER: Carrier,
    EntityTypeEnum.WAREHOUSE: Warehouse,
    EntityTypeEnum.INVOICE: Invoice,
    EntityTypeEnum.PAYMENT: Payment,
    EntityTypeEnum.CONTRACT: Contract,
    EntityTypeEnum.DOCUMENT: Document,
    EntityTypeEnum.CUSTOMS_DECLARATION: CustomsDeclaration,
    EntityTypeEnum.REGULATORY_OBLIGATION: RegulatoryObligation,
    EntityTypeEnum.EMPLOYEE_ROLE: EmployeeRole,
    EntityTypeEnum.MACHINE: Machine,
    EntityTypeEnum.PRODUCTION_BATCH: ProductionBatch,
    EntityTypeEnum.QUALITY_EVENT: QualityEvent,
    EntityTypeEnum.OPERATIONAL_EVENT: OperationalEvent,
    EntityTypeEnum.DECISION: Decision,
    EntityTypeEnum.KPI: KPI,
}
