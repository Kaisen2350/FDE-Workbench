"""Versioned ontology definitions and metamodel for the Paraguay Export Economy."""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class EntityTypeEnum(str, Enum):
    """The 24 domain entities representing operational reality."""
    ORGANIZATION = "organization"
    FACILITY = "facility"
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    PRODUCT = "product"
    MATERIAL = "material"
    ORDER = "order"
    PURCHASE_ORDER = "purchase_order"
    SHIPMENT = "shipment"
    CARRIER = "carrier"
    WAREHOUSE = "warehouse"
    INVOICE = "invoice"
    PAYMENT = "payment"
    CONTRACT = "contract"
    DOCUMENT = "document"
    CUSTOMS_DECLARATION = "customs_declaration"
    REGULATORY_OBLIGATION = "regulatory_obligation"
    EMPLOYEE_ROLE = "employee_role"
    MACHINE = "machine"
    PRODUCTION_BATCH = "production_batch"
    QUALITY_EVENT = "quality_event"
    OPERATIONAL_EVENT = "operational_event"
    DECISION = "decision"
    KPI = "kpi"


class RelationTypeEnum(str, Enum):
    """Explicit relationship types connecting domain entities."""
    OPERATES = "operates"
    BUYS_FROM = "buys_from"
    SELLS_TO = "sells_to"
    PRODUCES = "produces"
    OWNS = "owns"
    CONTAINS = "contains"
    FULFILLED_BY = "fulfilled_by"
    GENERATES = "generates"
    TRANSPORTS = "transports"
    HANDLED_BY = "handled_by"
    REQUIRES = "requires"
    DELIVERS_TO = "delivers_to"
    CONSUMES = "consumes"
    OCCURS_AT = "occurs_at"
    ASSOCIATED_WITH = "associated_with"
    SETTLES = "settles"
    SATISFIES = "satisfies"
    ORIGINATES_FROM = "originates_from"
    ACCOMPANIED_BY = "accompanied_by"
    AFFECTS = "affects"
    RESOLVES = "resolves"
    AUTHORIZES = "authorizes"


class EntitySchemaDefinition(BaseModel):
    name: str
    category: str
    description: str
    key_attributes: List[str]
    paraguayan_context: str


class RelationSchemaDefinition(BaseModel):
    source_type: EntityTypeEnum
    relation_type: RelationTypeEnum
    target_type: EntityTypeEnum
    description: str


class OntologyVersionInfo(BaseModel):
    name: str
    version: str
    description: str
    domain: str
    entity_count: int
    relationship_types_count: int
    entities: Dict[str, EntitySchemaDefinition]
    allowed_relations: List[RelationSchemaDefinition]


ONTOLOGY_METADATA: Dict[str, Any] = {
    "name": "Paraguay Export Economy FDE Ontology",
    "version": "1.0.0",
    "domain": "Paraguayan Export Processing, Agribusiness, Maquila, and Fluvial/Terrestrial Logistics",
    "author": "Forward Deployed Engineer (FDE) Research Workbench",
    "entity_types": [e.value for e in EntityTypeEnum],
    "relation_types": [r.value for r in RelationTypeEnum],
    "entity_definitions": {
        EntityTypeEnum.ORGANIZATION.value: {
            "name": "Organization",
            "category": "Core",
            "description": "Primary export-oriented corporation, legal entities, joint ventures, or holding companies.",
            "key_attributes": ["ruc", "country", "headcount", "annual_export_usd", "regime"],
            "paraguayan_context": "Includes RUC fiscal registration, Maquila Ley 1064/97 regime status, and SEPRELAD compliance categorization.",
        },
        EntityTypeEnum.FACILITY.value: {
            "name": "Facility",
            "category": "Physical Infrastructure",
            "description": "Physical plants, river ports, processing mills, packaging plants, or administrative campuses.",
            "key_attributes": ["location", "department", "port_code", "throughput_capacity_ton_day", "coordinates"],
            "paraguayan_context": "Critical hubs like Port of Villeta (Paraguay River km 1590) or Hernandarias Maquila Park (near Friendship Bridge to Brazil).",
        },
        EntityTypeEnum.SUPPLIER.value: {
            "name": "Supplier",
            "category": "Commercial Network",
            "description": "Upstream vendor providing agricultural raw commodities, packaging, industrial inputs, or services.",
            "key_attributes": ["ruc", "department", "commodity_type", "payment_terms_days", "reliability_rating"],
            "paraguayan_context": "Grain producers in Alto Paraná/Itapúa, Chaco livestock farms, San Pedro grain coops, packaging converters in CDE.",
        },
        EntityTypeEnum.CUSTOMER.value: {
            "name": "Customer",
            "category": "Commercial Network",
            "description": "International buyers, foreign trading houses, food processors, or Mercosur distributors.",
            "key_attributes": ["country", "jurisdiction", "cnpj_cuit", "default_incoterm", "credit_limit_usd"],
            "paraguayan_context": "Brazilian poultry feed integrators in Paraná/Santa Catarina, Argentine crushing plants in Rosario/San Lorenzo.",
        },
        EntityTypeEnum.PRODUCT.value: {
            "name": "Product",
            "category": "Asset & Output",
            "description": "Finished export goods produced or traded by the enterprise.",
            "key_attributes": ["ncm_code", "hs_code", "standard_package", "unit_of_measure", "shelf_life_days"],
            "paraguayan_context": "NCM 2304.00 (Soybean meal pellets), NCM 1507.10 (Crude soy oil), NCM 0202.30 (Chilled/frozen boneless beef cuts).",
        },
        EntityTypeEnum.MATERIAL.value: {
            "name": "Material",
            "category": "Asset & Input",
            "description": "Raw agricultural crops, industrial chemicals, packaging consumables, or spare parts.",
            "key_attributes": ["material_code", "unit", "target_inventory", "storage_condition", "unit_cost_usd"],
            "paraguayan_context": "Raw unprocessed grain (soja en grano), hexane solvent, 50kg polybags, flexitanks for containerized liquid oil.",
        },
        EntityTypeEnum.ORDER.value: {
            "name": "Order",
            "category": "Transaction",
            "description": "Commercial export sales contract order placed by international buyers.",
            "key_attributes": ["order_number", "incoterm", "delivery_deadline", "destination_port", "total_usd"],
            "paraguayan_context": "FOB Villeta fluvial loading terms, CIF Paranaguá deep-sea terms, or DPU Foz do Iguaçu terrestrial crossing.",
        },
        EntityTypeEnum.PURCHASE_ORDER.value: {
            "name": "Purchase Order",
            "category": "Transaction",
            "description": "Commercial procurement commitment for raw materials, packaging, or plant consumables.",
            "key_attributes": ["po_number", "supplier_id", "total_pyg_usd", "target_delivery_date", "moisture_penalty_clause"],
            "paraguayan_context": "Grain intake purchase contracts with Chamber of Cereals (CAPPRO) moisture/impurity deduction schedules.",
        },
        EntityTypeEnum.SHIPMENT.value: {
            "name": "Shipment",
            "category": "Logistics Execution",
            "description": "Physical movement of goods via river barge convoys, international road trucks, or multi-modal containers.",
            "key_attributes": ["shipment_type", "origin_facility", "destination_city", "weight_tons", "est_transit_days"],
            "paraguayan_context": "Fluvial 12-16 barge push-convoys down Hidrovía Paraná-Paraguay, or bitren heavy trucks across Ciudad del Este.",
        },
        EntityTypeEnum.CARRIER.value: {
            "name": "Carrier",
            "category": "Logistics Partner",
            "description": "Fluvial barge fleet operator, road freight trucking consortium, or shipping line.",
            "key_attributes": ["transport_mode", "flag", "fleet_size", "dinatran_registration", "insurance_coverage_usd"],
            "paraguayan_context": "Registered under DINATRAN (Dirección Nacional de Transporte) or Prefectura General Naval flags.",
        },
        EntityTypeEnum.WAREHOUSE.value: {
            "name": "Warehouse",
            "category": "Physical Infrastructure",
            "description": "Grain silo batteries, bulk meal warehouses, fiscal bonded yards, or cold-storage chambers.",
            "key_attributes": ["capacity_tons", "temperature_controlled", "is_bonded_fiscal", "current_utilization_pct"],
            "paraguayan_context": "Depósito Fiscal autorizada by DNIT for pre-customs clearing without triggering premature import/export duties.",
        },
        EntityTypeEnum.INVOICE.value: {
            "name": "Invoice",
            "category": "Financial",
            "description": "Commercial export invoice or inbound vendor invoice registered for tax and exchange control.",
            "key_attributes": ["invoice_number", "timbrado_dnlt", "currency", "amount_total", "due_date"],
            "paraguayan_context": "Timbrado electronic invoicing issued under DNIT (Dirección Nacional de Ingresos Tributarios) rules.",
        },
        EntityTypeEnum.PAYMENT.value: {
            "name": "Payment",
            "category": "Financial",
            "description": "Financial settlement transaction executing cross-border or domestic fund transfers.",
            "key_attributes": ["payment_ref", "channel", "origin_currency", "settlement_currency", "fx_rate"],
            "paraguayan_context": "Swift MT103 wire settlements in USD, Mercosur Local Currency Payment System (SML), or local SIPAP transfers.",
        },
        EntityTypeEnum.CONTRACT.value: {
            "name": "Contract",
            "category": "Legal & Governance",
            "description": "Master international supply contract, grain purchase agreement, or carrier charter agreement.",
            "key_attributes": ["contract_type", "governing_law", "arbitration_forum", "demurrage_rate_per_day", "valid_until"],
            "paraguayan_context": "Subject to FOSFA/GAFTA trade rules, Mercosur arbitration, or Paraguayan Civil Code.",
        },
        EntityTypeEnum.DOCUMENT.value: {
            "name": "Document",
            "category": "Information Asset",
            "description": "Physical or digital instrument accompanying cargo, financial flows, or customs releases.",
            "key_attributes": ["doc_type", "file_format", "issuing_entity", "document_hash", "is_original_required"],
            "paraguayan_context": "Bill of Lading (B/L), Carta de Porte Internacional (CRT), Romaneo de Carga, Packing List, Certificate of Origin.",
        },
        EntityTypeEnum.CUSTOMS_DECLARATION.value: {
            "name": "Customs Declaration",
            "category": "Regulatory Instrument",
            "description": "Formal electronic declaration submitted to customs authorities for export/transit authorization.",
            "key_attributes": ["declaration_number", "customs_office", "channel", "customs_broker_id", "cleared_at"],
            "paraguayan_context": "VUE (Ventanilla Única de Exportación), DUA (Declaración Única de Aduanas), MIC/DTA (Manifiesto Internacional de Carga).",
        },
        EntityTypeEnum.REGULATORY_OBLIGATION.value: {
            "name": "Regulatory Obligation",
            "category": "Compliance & GRC",
            "description": "Statutory mandate imposed by state agencies governing food safety, phytosanitary, or anti-money laundering.",
            "key_attributes": ["agency", "legal_framework", "renewal_cycle_days", "penalty_exposure_usd", "compliance_status"],
            "paraguayan_context": "SENACSA (animal safety), SENAVE (crop protection), SEPRELAD (AML/CFT Res. 70/19), CNIME (Maquila exports).",
        },
        EntityTypeEnum.EMPLOYEE_ROLE.value: {
            "name": "Employee / Role",
            "category": "Human Organization",
            "description": "Organizational position with assigned operational responsibilities, delegations, and approval thresholds.",
            "key_attributes": ["title", "department", "headcount_allocated", "approval_limit_usd", "critical_workflow"],
            "paraguayan_context": "Headcount distribution across Operations, Quality Control, Dispatch Logistics, Export Documentation, and Treasury.",
        },
        EntityTypeEnum.MACHINE.value: {
            "name": "Machine",
            "category": "Physical Infrastructure",
            "description": "Industrial production machinery, conveyors, weighbridges, expellers, or packaging lines.",
            "key_attributes": ["machine_code", "rated_capacity_tph", "operating_hours", "maintenance_cycle_hours", "status"],
            "paraguayan_context": "Bühler grain crushers, Anderson expellers, Toledo truck weighbridge (báscula fiscal), river barge loading spout.",
        },
        EntityTypeEnum.PRODUCTION_BATCH.value: {
            "name": "Production Batch",
            "category": "Operational Execution",
            "description": "Discrete manufacturing or processing run transforming raw inputs into finished export lots.",
            "key_attributes": ["batch_number", "yield_percentage", "protein_assay_pct", "moisture_assay_pct", "qa_release_status"],
            "paraguayan_context": "Crushing batch linking specific silo grain lots to export meal pellets with recorded laboratory assays.",
        },
        EntityTypeEnum.QUALITY_EVENT.value: {
            "name": "Quality Event",
            "category": "Quality & Compliance",
            "description": "Physical, chemical, or microbiological assay deviation triggering rejection, reconditioning, or penalties.",
            "key_attributes": ["parameter_tested", "threshold_max", "measured_value", "containment_action", "disposition"],
            "paraguayan_context": "Moisture above 14% at weighbridge, aflatoxin detection in corn, broken veterinary seals on chilled beef containers.",
        },
        EntityTypeEnum.OPERATIONAL_EVENT.value: {
            "name": "Operational Event",
            "category": "Operational Reality",
            "description": "Observed real-world disruption or deviation affecting supply chain continuity, time, or cost.",
            "key_attributes": ["event_type", "source", "severity", "financial_impact", "operational_impact", "status"],
            "paraguayan_context": "River water level drop at Paso Queso restricting barge draft, customs broker delay at Ciudad del Este, machine breakdown.",
        },
        EntityTypeEnum.DECISION.value: {
            "name": "Decision",
            "category": "Management Governance",
            "description": "Structured resolution evaluated, authorized, and executed in response to operational disruptions.",
            "key_attributes": ["decision_owner", "options_count", "recommendation", "authorized_action", "outcome_verified"],
            "paraguayan_context": "Rerouting river freight to terrestrial trucks via Puerto Falcón, applying moisture deductions, expediting customs clearance.",
        },
        EntityTypeEnum.KPI.value: {
            "name": "KPI",
            "category": "Performance Metrics",
            "description": "Operational, financial, and regulatory key performance indicator tracking business execution efficiency.",
            "key_attributes": ["category", "current_value", "target_value", "unit", "business_impact_notes"],
            "paraguayan_context": "Cash Conversion Cycle (days), Customs Border Dwell Time (hours), Hydrovia Fleet Draft Utilization (%), OTIF Delivery (%).",
        },
    },
}
