"""Deterministic generator for synthetic Paraguayan export manufacturer: Agro-Industrial del Este S.A. (AIDESA)."""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum
from fde_workbench.domain.entities import (
    Organization,
    Facility,
    Supplier,
    Customer,
    Product,
    Material,
    Order,
    PurchaseOrder,
    Shipment,
    Carrier,
    Warehouse,
    Invoice,
    Payment,
    Contract,
    Document,
    CustomsDeclaration,
    RegulatoryObligation,
    EmployeeRole,
    Machine,
    ProductionBatch,
    QualityEvent,
    OperationalEvent,
    Decision,
    KPI,
)
from fde_workbench.domain.relationships import Relationship
from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.domain.evidence import EvidenceRecord, EvidenceSourceType
from fde_workbench.domain.events import OperationalEventRecord, EventSeverity, EventStatus
from fde_workbench.domain.decisions import DecisionRecord, DecisionOption, AuthorizedAction, DecisionOutcome, DecisionStatus
from fde_workbench.domain.ai_opportunities import (
    AIOpportunity,
    DeploymentComplexity,
    FDEPrioritization,
    EconomicLeverage,
    OperationalCharacteristics,
    DeploymentFeasibility,
    StrategicValue,
)
from fde_workbench.domain.agent_specs import AgentSpecification, ToolDefinition
from fde_workbench.domain.pilots import PilotSpecification, PilotEconomicModel, PilotStatus


def seed_synthetic_company(store: WorkbenchStore) -> Dict[str, Any]:
    """Populate the store with complete synthetic company matching all prompt requirements."""
    store.clear()
    now = datetime.utcnow()

    # ==========================================
    # 1. CORE ORGANIZATION
    # ==========================================
    aidesa = Organization(
        id="org-aidesa",
        name="Agro-Industrial del Este S.A. (AIDESA)",
        ruc="80099412-4",
        legal_form="Sociedad Anónima (S.A.)",
        headcount=250,
        export_regime="Régimen General de Exportación & Maquila Ley 1064/97",
        system_of_record="SAP_B1",
        tags=["paraguay", "exporter", "agribusiness", "maquila", "hidrovia"],
        attributes={
            "founding_year": 2011,
            "annual_export_volume_mt": 420000.0,
            "annual_revenue_usd": 185000000.0,
            "bank_accounts": ["Banco Continental (USD)", "Banco Itaú Paraguay (USD/PYG)", "Sudameris (Trade Finance)"],
            "tax_compliance_status": "CERTIFICADO_CUMPLIMIENTO_TRIBUTARIO_VALIDO",
            "seprelad_registration": "SUJETO_OBLIGADO_REG_2026_091",
        },
    )
    store.add_entity(aidesa)

    # ==========================================
    # 2. FACILITIES (2 Facilities)
    # ==========================================
    fac_villeta = Facility(
        id="fac-villeta",
        name="Planta Fluvial & Puerto Villeta",
        facility_type="RIVER_PORT_AND_CRUSHING_MILL",
        department="Central",
        city="Villeta",
        throughput_capacity_tpd=2800.0,
        has_barge_dock=True,
        has_rail_spur=False,
        coordinates={"lat": -25.5142, "lng": -57.5621},
        system_of_record="SAP_B1",
        tags=["facility", "port", "crushing", "river"],
        attributes={
            "port_code": "PYVIL",
            "berth_length_meters": 180.0,
            "barge_loader_capacity_tph": 800.0,
            "paraguay_river_km": 1590.0,
            "weighbridges": 3,
        },
    )
    store.add_entity(fac_villeta)
    store.add_relationship(Relationship(
        id="rel-aidesa-operates-villeta",
        relation_type=RelationTypeEnum.OPERATES,
        source_id=aidesa.id,
        source_type=EntityTypeEnum.ORGANIZATION,
        target_id=fac_villeta.id,
        target_type=EntityTypeEnum.FACILITY,
    ))

    fac_hernandarias = Facility(
        id="fac-hernandarias",
        name="Planta Industrial Hernandarias (Maquila)",
        facility_type="MAQUILA_ASSEMBLY_AND_PACKAGING",
        department="Alto Paraná",
        city="Hernandarias",
        throughput_capacity_tpd=1200.0,
        has_barge_dock=False,
        has_rail_spur=False,
        coordinates={"lat": -25.4019, "lng": -54.6412},
        system_of_record="SAP_B1",
        tags=["facility", "maquila", "packaging", "border"],
        attributes={
            "maquila_cnime_program_id": "MAQ-2026-088",
            "distance_to_brazil_border_km": 14.5,
            "container_dock_bays": 6,
            "automated_bagging_lines": 2,
        },
    )
    store.add_entity(fac_hernandarias)
    store.add_relationship(Relationship(
        id="rel-aidesa-operates-hernandarias",
        relation_type=RelationTypeEnum.OPERATES,
        source_id=aidesa.id,
        source_type=EntityTypeEnum.ORGANIZATION,
        target_id=fac_hernandarias.id,
        target_type=EntityTypeEnum.FACILITY,
    ))

    # ==========================================
    # 3. WAREHOUSES & MACHINES
    # ==========================================
    wh_silos_villeta = Warehouse(
        id="wh-villeta-silos",
        name="Batería de Silos Villeta (60k MT)",
        facility_id=fac_villeta.id,
        storage_type="GRAIN_SILO",
        capacity_metric_tons=60000.0,
        current_occupancy_metric_tons=41500.0,
        is_bonded_fiscal=True,
        system_of_record="SAP_B1",
        tags=["warehouse", "silo", "bonded"],
    )
    store.add_entity(wh_silos_villeta)
    store.add_relationship(Relationship(
        id="rel-aidesa-owns-wh-villeta",
        relation_type=RelationTypeEnum.OWNS,
        source_id=aidesa.id,
        source_type=EntityTypeEnum.ORGANIZATION,
        target_id=wh_silos_villeta.id,
        target_type=EntityTypeEnum.WAREHOUSE,
    ))

    wh_fiscal_cde = Warehouse(
        id="wh-cde-bonded",
        name="Depósito Fiscal Hernandarias",
        facility_id=fac_hernandarias.id,
        storage_type="BONDED_FISCAL",
        capacity_metric_tons=15000.0,
        current_occupancy_metric_tons=8900.0,
        is_bonded_fiscal=True,
        system_of_record="SAP_B1",
        tags=["warehouse", "bonded", "border"],
    )
    store.add_entity(wh_fiscal_cde)

    machine_crusher = Machine(
        id="mach-crusher-01",
        name="Línea de Molienda Bühler 120 TPH",
        machine_code="CRUSH-B120",
        facility_id=fac_villeta.id,
        rated_capacity_tph=120.0,
        status="RUNNING",
        operating_hours=480,
        system_of_record="SAP_B1",
        tags=["machine", "milling"],
    )
    store.add_entity(machine_crusher)
    store.add_relationship(Relationship(
        id="rel-aidesa-owns-mach-crusher",
        relation_type=RelationTypeEnum.OWNS,
        source_id=aidesa.id,
        source_type=EntityTypeEnum.ORGANIZATION,
        target_id=machine_crusher.id,
        target_type=EntityTypeEnum.MACHINE,
    ))

    # ==========================================
    # 4. PRODUCTS & MATERIALS
    # ==========================================
    prod_soymeal = Product(
        id="prod-soymeal-pellets",
        name="Harina de Soja Peletizada 46.5% Prot.",
        ncm_code="2304.00.10",
        unit_of_measure="MT",
        standard_packaging="Granel / Big Bags 1000kg",
        target_margin_pct=15.2,
        system_of_record="SAP_B1",
        tags=["product", "export", "soymeal"],
        attributes={"min_protein_pct": 46.5, "max_moisture_pct": 12.0, "max_fiber_pct": 3.8},
    )
    prod_soyoil = Product(
        id="prod-soyoil-crude",
        name="Aceite Crudo de Soja Desgomado",
        ncm_code="1507.10.00",
        unit_of_measure="MT",
        standard_packaging="A Granel Fluvial / Flexitank",
        target_margin_pct=18.0,
        system_of_record="SAP_B1",
        tags=["product", "export", "soyoil"],
    )
    prod_beef = Product(
        id="prod-beef-chilled",
        name="Cortes Vacunos Envasados al Vacío (Hilton/Mercosur)",
        ncm_code="0202.30.00",
        unit_of_measure="MT",
        standard_packaging="Cajas 25kg / Contenedor Reefer",
        target_margin_pct=22.5,
        system_of_record="SAP_B1",
        tags=["product", "export", "beef"],
    )
    store.add_entity(prod_soymeal)
    store.add_entity(prod_soyoil)
    store.add_entity(prod_beef)

    store.add_relationship(Relationship(
        id="rel-aidesa-produces-soymeal",
        relation_type=RelationTypeEnum.PRODUCES,
        source_id=aidesa.id,
        source_type=EntityTypeEnum.ORGANIZATION,
        target_id=prod_soymeal.id,
        target_type=EntityTypeEnum.PRODUCT,
    ))
    store.add_relationship(Relationship(
        id="rel-aidesa-produces-soyoil",
        relation_type=RelationTypeEnum.PRODUCES,
        source_id=aidesa.id,
        source_type=EntityTypeEnum.ORGANIZATION,
        target_id=prod_soyoil.id,
        target_type=EntityTypeEnum.PRODUCT,
    ))

    mat_soybeans = Material(
        id="mat-soybeans-raw",
        name="Soja en Grano Base Zafra 2026",
        material_code="MAT-SOJA-GRA",
        unit_of_measure="MT",
        reorder_point_tons=5000.0,
        current_inventory_tons=28400.0,
        max_moisture_tolerance_pct=14.0,
        system_of_record="SAP_B1",
        tags=["material", "raw_commodity"],
    )
    mat_polybags = Material(
        id="mat-polybags-50kg",
        name="Bolsas de Polipropileno 50kg con Liner",
        material_code="MAT-PKG-BAG50",
        unit_of_measure="UNIT",
        reorder_point_tons=20000.0,
        current_inventory_tons=75000.0,
        system_of_record="SAP_B1",
        tags=["material", "packaging"],
    )
    store.add_entity(mat_soybeans)
    store.add_entity(mat_polybags)

    store.add_relationship(Relationship(
        id="rel-prod-soymeal-requires-soybeans",
        relation_type=RelationTypeEnum.REQUIRES,
        source_id=prod_soymeal.id,
        source_type=EntityTypeEnum.PRODUCT,
        target_id=mat_soybeans.id,
        target_type=EntityTypeEnum.MATERIAL,
    ))

    # ==========================================
    # 5. EMPLOYEES / ROLES (Total 250 Headcount)
    # ==========================================
    role_distribution = [
        ("role-plant-ops", "Operador de Planta & Silos", "Planta y Silos", 120, 5000.0, ["Monitoreo de molienda", "Carga de silos", "Romaneo de báscula"]),
        ("role-maint", "Técnico de Mantenimiento Electromecánico", "Mantenimiento e Ingeniería", 30, 15000.0, ["Mantenimiento preventivo Bühler", "Inspección de bombas de vapor", "Calibración de básculas"]),
        ("role-logistics-dispatch", "Despachante de Cargas & Coordinador TMS", "Logística y Despacho", 25, 30000.0, ["Asignación de cupos de camiones", "Coordinación de barcazas", "Planilla de calado"]),
        ("role-quality-lab", "Analista de Laboratorio & Control de Calidad", "Calidad y Laboratorio", 20, 10000.0, ["Análisis de humedad y proteína", "Pruebas de aflatoxinas", "Liberación de lote"]),
        ("role-customs-compliance", "Especialista en Comercio Exterior & Aduana", "Comex y Aduanas", 15, 50000.0, ["Emisión de VUE y DUA", "Carga de MIC/DTA en VUE", "Despacho con DNA/DNIT"]),
        ("role-finance-treasury", "Analista de Tesorería & Finanzas Multidivisa", "Finanzas y Tesorería", 18, 75000.0, ["Conciliación SWIFT MT103", "Gestión de transferencias SML Mercosur", "Flujo de caja"]),
        ("role-commercial-trader", "Trader de Granos y Subproductos", "Comercial", 12, 150000.0, ["Negociación de contratos FOB/CIF", "Fijación Chicago CBOT", "Atención a clientes Brasil/Argentina"]),
        ("role-executive", "Dirección General & Gerencia de Operaciones", "Dirección", 10, 500000.0, ["Autorizaciones de excepciones", "Resolución de eventos críticos", "Estrategia"]),
    ]

    total_headcount_verified = 0
    for r_id, title, dept, count, limit, resp in role_distribution:
        total_headcount_verified += count
        role_ent = EmployeeRole(
            id=r_id,
            name=f"{title} ({count} colaboradores)",
            title=title,
            department=dept,
            headcount_in_role=count,
            approval_threshold_usd=limit,
            key_responsibilities=resp,
            system_of_record="GOOGLE_WORKSPACE",
            tags=["employee_role", dept.lower().replace(" ", "_")],
        )
        store.add_entity(role_ent)

    # ==========================================
    # 6. SUPPLIERS (Exactly 80 Suppliers)
    # ==========================================
    supplier_regions = [
        ("Alto Paraná", 25, "GRAIN_PRODUCER"),
        ("Itapúa", 20, "GRAIN_PRODUCER"),
        ("San Pedro", 10, "GRAIN_PRODUCER"),
        ("Chaco (Boquerón / Pdte. Hayes)", 12, "LIVESTOCK_AND_FEED"),
        ("Ciudad del Este", 6, "PACKAGING_AND_CONSUMABLES"),
        ("Asunción / Villeta", 7, "FLUVIAL_AND_LOGISTICS_SERVICES"),
    ]

    supplier_counter = 1
    for region, count, stype in supplier_regions:
        for i in range(1, count + 1):
            s_id = f"sup-{supplier_counter:03d}"
            name = f"Agropecuaria {region.split()[0]} Lote {i:02d} {'S.A.' if i % 2 == 0 else 'S.R.L.'}"
            sup_ent = Supplier(
                id=s_id,
                name=name,
                supplier_type=stype,
                ruc=f"80{supplier_counter:05d}-1",
                department=region,
                reliability_score=round(0.85 + (supplier_counter % 15) * 0.01, 2),
                payment_terms_days=30 if stype == "GRAIN_PRODUCER" else 15,
                currency="USD" if stype == "GRAIN_PRODUCER" else "PYG",
                system_of_record="SAP_B1",
                tags=["supplier", stype.lower(), region.lower().replace(" ", "_")],
            )
            store.add_entity(sup_ent)
            store.add_relationship(Relationship(
                id=f"rel-aidesa-buys-from-{s_id}",
                relation_type=RelationTypeEnum.BUYS_FROM,
                source_id=aidesa.id,
                source_type=EntityTypeEnum.ORGANIZATION,
                target_id=sup_ent.id,
                target_type=EntityTypeEnum.SUPPLIER,
            ))
            supplier_counter += 1

    # ==========================================
    # 7. CUSTOMERS (Exactly 25 Customers)
    # ==========================================
    customer_destinations = [
        ("Cascavel (PR)", "Brazil", "Nutrição Animal Cascavel Ltda.", "FOB Villeta"),
        ("Chapecó (SC)", "Brazil", "Cooperativa Agroindustrial do Oeste S.A.", "DPU Foz do Iguaçu"),
        ("Maringá (PR)", "Brazil", "Paraná Proteínas e Óleos Vegetais S.A.", "CIF Paranaguá"),
        ("Toledo (PR)", "Brazil", "Frigorífico e Rações Toledo Ltda.", "DPU Foz do Iguaçu"),
        ("Curitiba (PR)", "Brazil", "Moinhos e Exportadora Curitibana S.A.", "CIF Paranaguá"),
        ("São Paulo (SP)", "Brazil", "AgroTrading Paulista S.A.", "FOB Villeta"),
        ("Campinas (SP)", "Brazil", "NutriAgro Campinas Alimentos Ltda.", "FOB Villeta"),
        ("Londrina (PR)", "Brazil", "Avícola Norte Paranaense S.A.", "DPU Foz do Iguaçu"),
        ("Castro (PR)", "Brazil", "Leite e Suínos Castro Cooperativa", "DPU Foz do Iguaçu"),
        ("Joinville (SC)", "Brazil", "Exportadora Catarinense de Proteína Ltda.", "CIF Paranaguá"),
        ("Uberlândia (MG)", "Brazil", "Triângulo Rações e Fórmulas S.A.", "FOB Villeta"),
        ("Passo Fundo (RS)", "Brazil", "Gaúcha Grãos e Subprodutos Ltda.", "DPU Foz do Iguaçu"),
        ("Dourados (MS)", "Brazil", "Fronteira Oeste Agronegócios Ltda.", "FOB Villeta"),
        ("Santos (SP)", "Brazil", "Terminal Portuário Exportador Santos S.A.", "FOB Villeta"),
        ("Paranaguá (PR)", "Brazil", "Paranaguá Bulk Terminal Logistics S.A.", "CIF Paranaguá"),
        ("Rosario (SF)", "Argentina", "Molinos Fluviales del Paraná S.A.", "FOB Villeta"),
        ("San Lorenzo (SF)", "Argentina", "Terminal Portuaria San Lorenzo S.A.", "FOB Villeta"),
        ("Buenos Aires", "Argentina", "Agropecuaria Rioplatense S.A.", "FOB Villeta"),
        ("Santa Fe (SF)", "Argentina", "Procesadora y Aceitera Santafesina S.A.", "FOB Villeta"),
        ("Pergamino (BA)", "Argentina", "NutriSemillas Pergamino S.R.L.", "FOB Villeta"),
        ("Córdoba (CBA)", "Argentina", "Proteínas del Centro S.A.", "DPU Clorinda"),
        ("San Nicolás (BA)", "Argentina", "Fluvial Muelle San Nicolás S.A.", "FOB Villeta"),
        ("Zárate (BA)", "Argentina", "Delta Logística Fluvial Zárate S.A.", "FOB Villeta"),
        ("Junín (BA)", "Argentina", "Raciones y Harinas Junín S.A.", "DPU Clorinda"),
        ("Bahía Blanca (BA)", "Argentina", "Exportadora Atlántica Sur S.A.", "FOB Villeta"),
    ]

    for idx, (dest_city, country, cust_name, incoterm) in enumerate(customer_destinations, start=1):
        c_id = f"cust-{idx:03d}"
        cust_ent = Customer(
            id=c_id,
            name=cust_name,
            country=country,
            destination_city=dest_city,
            tax_id_foreign=f"{'CNPJ-14.88' if country == 'Brazil' else 'CUIT-30-71'}{idx:06d}-1",
            default_incoterm=incoterm,
            credit_limit_usd=1200000.0 + (idx * 50000.0),
            payment_terms_days=45 if country == "Brazil" else 60,
            system_of_record="SAP_B1",
            tags=["customer", country.lower(), dest_city.split()[0].lower()],
        )
        store.add_entity(cust_ent)
        store.add_relationship(Relationship(
            id=f"rel-aidesa-sells-to-{c_id}",
            relation_type=RelationTypeEnum.SELLS_TO,
            source_id=aidesa.id,
            source_type=EntityTypeEnum.ORGANIZATION,
            target_id=cust_ent.id,
            target_type=EntityTypeEnum.CUSTOMER,
        ))

    # ==========================================
    # 8. CARRIERS (Fluvial & Terrestrial)
    # ==========================================
    carrier_fluvial = Carrier(
        id="carrier-hidrovias-sur",
        name="Hidrovías del Sur Fluvial S.A.",
        transport_mode="FLUVIAL",
        fleet_size=36,
        dinatran_registry="DINATRAN-FLUV-094",
        insurance_policy_usd=12000000.0,
        system_of_record="TMS",
        tags=["carrier", "fluvial", "barge", "hidrovia"],
    )
    carrier_road = Carrier(
        id="carrier-trans-mercosur",
        name="Expreso Trans-Mercosur Bitrenes S.R.L.",
        transport_mode="TERRESTRIAL",
        fleet_size=65,
        dinatran_registry="DINATRAN-ROD-882",
        insurance_policy_usd=4000000.0,
        system_of_record="TMS",
        tags=["carrier", "terrestrial", "truck", "bitren"],
    )
    store.add_entity(carrier_fluvial)
    store.add_entity(carrier_road)

    # ==========================================
    # 9. PRODUCTION BATCH, ORDER, SHIPMENT, INVOICE, PAYMENT
    # ==========================================
    batch_01 = ProductionBatch(
        id="batch-2026-pellet-081",
        name="Lote Molienda Villeta Soja #081",
        batch_number="BATCH-2026-PELLET-081",
        product_id=prod_soymeal.id,
        facility_id=fac_villeta.id,
        output_quantity_mt=2400.0,
        protein_assay_pct=46.8,
        moisture_assay_pct=11.6,
        quality_status="APPROVED",
        system_of_record="SAP_B1",
        tags=["batch", "approved", "villeta"],
    )
    store.add_entity(batch_01)
    store.add_relationship(Relationship(
        id="rel-batch-occurs-at-villeta",
        relation_type=RelationTypeEnum.OCCURS_AT,
        source_id=batch_01.id,
        source_type=EntityTypeEnum.PRODUCTION_BATCH,
        target_id=fac_villeta.id,
        target_type=EntityTypeEnum.FACILITY,
    ))
    store.add_relationship(Relationship(
        id="rel-batch-produces-soymeal",
        relation_type=RelationTypeEnum.PRODUCES,
        source_id=batch_01.id,
        source_type=EntityTypeEnum.PRODUCTION_BATCH,
        target_id=prod_soymeal.id,
        target_type=EntityTypeEnum.PRODUCT,
    ))
    store.add_relationship(Relationship(
        id="rel-batch-consumes-soybeans",
        relation_type=RelationTypeEnum.CONSUMES,
        source_id=batch_01.id,
        source_type=EntityTypeEnum.PRODUCTION_BATCH,
        target_id=mat_soybeans.id,
        target_type=EntityTypeEnum.MATERIAL,
    ))

    # Order to Argentine Customer (Rosario)
    order_arg = Order(
        id="ord-2026-exp-042",
        name="Export Order EXP-2026-042 (Rosario)",
        order_number="EXP-2026-042",
        customer_id="cust-016",
        incoterm="FOB Villeta",
        destination_port_or_border="Puerto de Rosario / Hidrovía",
        quantity_ordered_mt=2400.0,
        total_amount_usd=936000.0,
        delivery_deadline=now + timedelta(days=12),
        status="IN_FULFILLMENT",
        system_of_record="SAP_B1",
        tags=["order", "argentina", "fluvial"],
    )
    store.add_entity(order_arg)
    store.add_relationship(Relationship(
        id="rel-ord-contains-soymeal",
        relation_type=RelationTypeEnum.CONTAINS,
        source_id=order_arg.id,
        source_type=EntityTypeEnum.ORDER,
        target_id=prod_soymeal.id,
        target_type=EntityTypeEnum.PRODUCT,
    ))
    store.add_relationship(Relationship(
        id="rel-ord-fulfilled-by-batch01",
        relation_type=RelationTypeEnum.FULFILLED_BY,
        source_id=order_arg.id,
        source_type=EntityTypeEnum.ORDER,
        target_id=batch_01.id,
        target_type=EntityTypeEnum.PRODUCTION_BATCH,
    ))

    # Shipment for Argentine Order
    shipment_barge = Shipment(
        id="shp-2026-fluv-019",
        name="Convoy Barcazas HB-104 (Villeta -> Rosario)",
        shipment_code="SHP-2026-FLUV-019",
        transport_mode="FLUVIAL",
        origin_facility_id=fac_villeta.id,
        destination="Puerto Rosario, Santa Fe, Argentina",
        carrier_id=carrier_fluvial.id,
        weight_net_tons=2400.0,
        vessel_or_truck_id="Empujador Don Tito / Barcazas HB-104 y HB-105",
        corridor="Hidrovía Paraguay-Paraná",
        estimated_departure=now - timedelta(days=1),
        estimated_arrival=now + timedelta(days=7),
        status="DELAYED",
        system_of_record="TMS",
        tags=["shipment", "fluvial", "delayed", "hidrovia"],
    )
    store.add_entity(shipment_barge)
    store.add_relationship(Relationship(
        id="rel-ord-generates-shipment-barge",
        relation_type=RelationTypeEnum.GENERATES,
        source_id=order_arg.id,
        source_type=EntityTypeEnum.ORDER,
        target_id=shipment_barge.id,
        target_type=EntityTypeEnum.SHIPMENT,
    ))
    store.add_relationship(Relationship(
        id="rel-shipment-transports-soymeal",
        relation_type=RelationTypeEnum.TRANSPORTS,
        source_id=shipment_barge.id,
        source_type=EntityTypeEnum.SHIPMENT,
        target_id=prod_soymeal.id,
        target_type=EntityTypeEnum.PRODUCT,
    ))
    store.add_relationship(Relationship(
        id="rel-shipment-handled-by-hidrovias",
        relation_type=RelationTypeEnum.HANDLED_BY,
        source_id=shipment_barge.id,
        source_type=EntityTypeEnum.SHIPMENT,
        target_id=carrier_fluvial.id,
        target_type=EntityTypeEnum.CARRIER,
    ))

    # Customs Declaration & Regulatory
    reg_senave = RegulatoryObligation(
        id="reg-senave-phyto",
        name="Certificado Fitosanitario de Exportación SENAVE",
        agency="SENAVE",
        statute_code="Ley 123/91 Sanidad Vegetal & Res. SENAVE 448/21",
        compliance_status="COMPLIANT",
        system_of_record="VUE_PORTAL",
        tags=["regulatory", "senave", "phytosanitary"],
    )
    store.add_entity(reg_senave)

    customs_dec = CustomsDeclaration(
        id="cdec-vue-2026-8819",
        name="Declaración VUE / DUA #26099-VUE-8819",
        declaration_type="VUE_PERMIT",
        customs_office="Aduana de Villeta (Código 003)",
        customs_broker_name="Agencia Aduanera del Plata S.A.",
        channel="VERDE",
        submission_date=now - timedelta(days=2),
        cleared_date=now - timedelta(days=1),
        status="CLEARED",
        system_of_record="VUE_PORTAL",
        tags=["customs", "vue", "cleared"],
    )
    store.add_entity(customs_dec)
    store.add_relationship(Relationship(
        id="rel-shipment-requires-customs-dec",
        relation_type=RelationTypeEnum.REQUIRES,
        source_id=shipment_barge.id,
        source_type=EntityTypeEnum.SHIPMENT,
        target_id=customs_dec.id,
        target_type=EntityTypeEnum.CUSTOMS_DECLARATION,
    ))
    store.add_relationship(Relationship(
        id="rel-customs-dec-satisfies-senave",
        relation_type=RelationTypeEnum.SATISFIES,
        source_id=customs_dec.id,
        source_type=EntityTypeEnum.CUSTOMS_DECLARATION,
        target_id=reg_senave.id,
        target_type=EntityTypeEnum.REGULATORY_OBLIGATION,
    ))

    # Invoice & Payment
    inv_01 = Invoice(
        id="inv-exp-2026-0042",
        name="Factura de Exportación 001-002-0045192 (USD 936k)",
        invoice_number="001-002-0045192",
        timbrado_dnit="16489201",
        order_id=order_arg.id,
        currency="USD",
        subtotal=936000.0,
        total_amount=936000.0,
        payment_status="PENDING",
        due_date=now + timedelta(days=45),
        system_of_record="SAP_B1",
        tags=["invoice", "export", "usd"],
    )
    store.add_entity(inv_01)
    store.add_relationship(Relationship(
        id="rel-ord-generates-invoice",
        relation_type=RelationTypeEnum.GENERATES,
        source_id=order_arg.id,
        source_type=EntityTypeEnum.ORDER,
        target_id=inv_01.id,
        target_type=EntityTypeEnum.INVOICE,
    ))
    store.add_relationship(Relationship(
        id="rel-inv-associated-with-order",
        relation_type=RelationTypeEnum.ASSOCIATED_WITH,
        source_id=inv_01.id,
        source_type=EntityTypeEnum.INVOICE,
        target_id=order_arg.id,
        target_type=EntityTypeEnum.ORDER,
    ))

    # ==========================================
    # 9.5. SOURCE EVIDENCE (GROUNDING OPERATIONAL REALITY)
    # ==========================================
    evi_gauge = EvidenceRecord(
        id="evi-2026-001",
        source="PREFECTURA_NAVAL_GAUGE_KM1530",
        source_type=EvidenceSourceType.TELEMETRY_STREAM,
        timestamp=now - timedelta(hours=14, minutes=30),
        confidence=0.98,
        provenance=ProvenanceType.SYNTHETIC,
        extracted_claim="Paraguay River water depth at Paso Queso gauge (km 1530) measured 8.4 ft, falling below the 10.0 ft safe navigation threshold for 16-barge convoys.",
        raw_payload_snippet="BOLETIN_HIDROMETRICO_DIARIO: FECHA 2026-09-18 06:00 | ESTACION: PASO QUESO KM 1530 | CALADO_MAX_PIES: 8.4 | ALERTA: ESTIAJE_CRITICO",
        references_entity_ids=[shipment_barge.id, fac_villeta.id],
        references_event_ids=["evt-2026-001"],
        references_decision_ids=["dec-2026-001"],
    )
    store.add_evidence(evi_gauge)

    evi_customs = EvidenceRecord(
        id="evi-2026-002",
        source="DNIT_VUE_CUSTOMS_PORTAL",
        source_type=EvidenceSourceType.CUSTOMS_DOCUMENT,
        timestamp=now - timedelta(hours=6, minutes=15),
        confidence=0.99,
        provenance=ProvenanceType.SYNTHETIC,
        extracted_claim="Export transit manifest MIC/DTA rejected with error NCM_EX_CODE_MISMATCH against registered Maquila tariff exemption.",
        raw_payload_snippet="VUE_WS_RESP: STATUS=REJECTED | DUA=026-EXP-08819 | ERR=NCM_EX_CODE_MISMATCH [Declared: 2304.00.10.00 vs Approved: 2304.00.10.Ex01]",
        references_entity_ids=[fac_hernandarias.id],
        references_event_ids=["evt-2026-002"],
        references_decision_ids=["dec-2026-002"],
    )
    store.add_evidence(evi_customs)

    evi_scale = EvidenceRecord(
        id="evi-2026-003",
        source="TOLEDO_BASCULA_SCALE_VILLETA",
        source_type=EvidenceSourceType.PHYSICAL_INSPECTION,
        timestamp=now - timedelta(hours=3, minutes=15),
        confidence=0.96,
        provenance=ProvenanceType.SYNTHETIC,
        extracted_claim="Weighbridge automatic NIR grain sampler recorded 15.7% moisture on inbound truck lot vs 14.0% contractual maximum.",
        raw_payload_snippet="ROMANEO_FISCAL_TICKET: #88412 | BRUTO: 48,200 KG | TARA: 14,100 KG | NETO: 34,100 KG | HUMEDAD: 15.7% | MAT_EXTRAÑA: 1.4%",
        references_entity_ids=[mat_soybeans.id, "sup-001"],
        references_event_ids=["evt-2026-003"],
    )
    store.add_evidence(evi_scale)

    evi_swift = EvidenceRecord(
        id="evi-2026-004",
        source="BANCO_CONTINENTAL_SWIFT_PORTAL",
        source_type=EvidenceSourceType.ERP_RECORD,
        timestamp=now - timedelta(hours=2, minutes=20),
        confidence=0.94,
        provenance=ProvenanceType.SYNTHETIC,
        extracted_claim="Expected SWIFT MT103 wire transfer of USD 185,000 overdue by 5 business days due to Central Bank of Argentina (BCRA) foreign exchange authorization hold.",
        raw_payload_snippet="SWIFT_INQUIRY: REF_INV=FAC-2026-001 | MT103_STATUS=PENDING_CENTRAL_BANK_CLEARING | CORRESPONDENT=BANCO_NACION_ARG | AMOUNT=USD 185,000",
        references_entity_ids=[inv_01.id],
        references_event_ids=["evt-2026-004"],
    )
    store.add_evidence(evi_swift)

    evi_whatsapp = EvidenceRecord(
        id="evi-2026-005",
        source="CUSTOMS_BROKER_DISPATCH_WHATSAPP",
        source_type=EvidenceSourceType.INTERVIEW_STATEMENT,
        timestamp=now - timedelta(hours=7, minutes=10),
        confidence=0.91,
        provenance=ProvenanceType.SYNTHETIC,
        extracted_claim="Customs broker statement confirms 3 refrigerated containers of beef halted at Puerto Falcón border post due to missing SENACSA Annex III health certificate.",
        raw_payload_snippet="\"Licenciado, Aduana Clorinda rechazó el ingreso de los 3 camiones reefer. Falta el Anexo III firmado de SENACSA. Los motores tienen combustible para 5 horas más nomás.\"",
        references_entity_ids=["cust-021"],
        references_event_ids=["evt-2026-005-escalation"],
        references_decision_ids=["dec-2026-005-escalated"],
    )
    store.add_evidence(evi_whatsapp)

    # ==========================================
    # 10. OPERATIONAL EVENTS & DECISIONS (Including Escalation Path)
    # ==========================================
    # Event 1: River Draft Restriction (Paso Queso)
    evt_river = OperationalEventRecord(
        id="evt-2026-001",
        timestamp=now - timedelta(hours=14),
        entity_id=shipment_barge.id,
        entity_type=EntityTypeEnum.SHIPMENT,
        event_type="river_draft_restriction",
        source="PREFECTURA_NAVAL_GAUGE",
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_gauge.id],
        severity=EventSeverity.CRITICAL,
        expected_state={"permissible_draft_ft": 10.5, "convoy_actual_draft_ft": 10.2, "status": "NAVIGABLE"},
        observed_state={"permissible_draft_ft": 8.4, "convoy_actual_draft_ft": 10.2, "deficit_inches": 21.6, "critical_pass": "Paso Queso (km 1530)"},
        operational_impact="Convoy HB-104 cannot pass without grounding. Convoy anchored upstream at Villeta anchorage zone.",
        financial_impact=42000.0,
        currency="USD",
        required_decision="Lighten barge load into auxiliary craft vs Reroute balance via terrestrial trucks via Puerto Falcón",
        status=EventStatus.DECISION_PENDING,
    )
    store.add_event(evt_river)

    dec_river = DecisionRecord(
        decision_id="dec-2026-001",
        timestamp=now - timedelta(hours=10),
        triggering_event_id=evt_river.id,
        decision_owner="role-executive",
        status=DecisionStatus.EXECUTED,
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_gauge.id],
        context={
            "customer": "cust-016 (Molinos Fluviales del Paraná)",
            "contractual_penalty_delay_per_day_usd": 3500.0,
            "river_forecast_next_7_days": "DROPPING_FURTHER_2_INCHES",
            "available_local_truck_capacity_tons": 1200.0,
        },
        options=[
            DecisionOption(
                option_id="OPT-RIVER-A",
                title="Lighten barge load (Alijo de Carga) into shallow-draft hopper barges",
                description="Charter 2 shallow-draft 7-ft hoppers to transfer 600 MT, allowing main convoy to clear Paso Queso.",
                pros=["Maintains fluvial economy of scale", "Delivery to same discharge dock"],
                cons=["Alijo crane charter cost", "36 hour transfer operation"],
                cost_estimate_usd=18500.0,
                delay_hours_estimate=36.0,
                risk_level="MEDIUM",
            ),
            DecisionOption(
                option_id="OPT-RIVER-B",
                title="Reroute priority 800 MT via road freight through Puerto Falcón / Clorinda",
                description="Discharge 800 MT back to Villeta silo, dispatch 30 bitren trucks across Falcón bridge.",
                pros=["Guarantees arrival within 48h", "Bypasses all river draft risk"],
                cons=["Higher freight rate per ton ($38 vs $18 fluvial)", "Border crossing queue risk"],
                cost_estimate_usd=31000.0,
                delay_hours_estimate=48.0,
                risk_level="HIGH",
            ),
        ],
        recommendation="Execute Option A (Alijo de Carga) as river drops remain localized and charter crane is mobilizable within 12 hours.",
        authorization_required=True,
        authorized_action=AuthorizedAction(
            action_type="CHARTER_ALIJO_BARGE",
            target_entity_id=shipment_barge.id,
            parameters={"charter_barge_code": "BARCAZA-HO-09", "transfer_metric_tons": 650.0, "contractor": "Hidrovías del Sur"},
            authorized_by="role-executive",
            authorized_at=now - timedelta(hours=8),
        ),
        outcome=DecisionOutcome(
            observed_result="Alijo completed successfully. Convoy draft reduced to 8.2 ft, cleared Paso Queso safely with 0 grounding incidents.",
            actual_latency_hours=28.5,
            financial_delta_usd=-19200.0,
            kpi_impact="Fluvial Convoy OTIF maintained within contract window",
            verified=True,
        ),
    )
    store.add_decision(dec_river)

    # Event 2: Missing Customs Transit Document (Puente de la Amistad - Ciudad del Este)
    evt_customs = OperationalEventRecord(
        id="evt-2026-002",
        timestamp=now - timedelta(hours=6),
        entity_id=fac_hernandarias.id,
        entity_type=EntityTypeEnum.FACILITY,
        event_type="customs_document_missing",
        source="VUE_PORTAL",
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_customs.id],
        severity=EventSeverity.HIGH,
        expected_state={"document": "MIC_DTA_ELECTRONICO", "status": "TRANSMITTED_TO_RECEITA_FEDERAL_BRASIL"},
        observed_state={"document": "MIC_DTA_ELECTRONICO", "status": "REJECTED_SYNTAX_ERROR", "error_code": "NCM_EX_CODE_MISMATCH"},
        operational_impact="12 trucks carrying 320 MT bagged protein held at Ciudad del Este customs yard before Friendship Bridge.",
        financial_impact=14800.0,
        currency="USD",
        required_decision="Authorize customs broker emergency re-filing with amended NCM exemption code",
        status=EventStatus.RESOLVED,
    )
    store.add_event(evt_customs)

    dec_customs = DecisionRecord(
        decision_id="dec-2026-002",
        timestamp=now - timedelta(hours=4),
        triggering_event_id=evt_customs.id,
        decision_owner="role-customs-compliance",
        status=DecisionStatus.EXECUTED,
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_customs.id],
        context={
            "affected_shipment_ids": ["shp-truck-cde-01", "shp-truck-cde-02"],
            "receita_federal_shift_cutoff": "20:00 local time",
            "layover_penalty_per_truck_per_day": 350.0,
        },
        options=[
            DecisionOption(
                option_id="OPT-CUST-A",
                title="Emergency re-rectification on VUE portal with legal counsel validation",
                description="Customs broker re-submits VUE manifest with corrected NCM 2304.00.10 Ex 01 tariff designation.",
                pros=["Direct clearance without returning trucks", "Fastest if cleared before shift change"],
                cons=["Requires urgent DNA administrator signature"],
                cost_estimate_usd=1200.0,
                delay_hours_estimate=4.0,
                risk_level="LOW",
            ),
        ],
        recommendation="Submit rectified VUE electronic declaration immediately with customs broker direct expedited counter-signature.",
        authorization_required=True,
        authorized_action=AuthorizedAction(
            action_type="SUBMIT_AMENDED_VUE",
            target_entity_id=evt_customs.entity_id,
            parameters={"rectified_ncm": "2304.00.10.Ex01", "broker": "Despachos Aduaneros del Este"},
            authorized_by="role-customs-compliance",
            authorized_at=now - timedelta(hours=3),
        ),
        outcome=DecisionOutcome(
            observed_result="Receita Federal accepted rectified MIC/DTA. All 12 trucks cleared across Friendship Bridge at 18:45.",
            actual_latency_hours=3.5,
            financial_delta_usd=-1400.0,
            kpi_impact="Customs Dwell reduced by 24h compared to manual overnight demurrage",
            verified=True,
        ),
    )
    store.add_decision(dec_customs)

    # Event 3: Grain Moisture Assay Deviation
    evt_moisture = OperationalEventRecord(
        id="evt-2026-003",
        timestamp=now - timedelta(hours=3),
        entity_id=mat_soybeans.id,
        entity_type=EntityTypeEnum.MATERIAL,
        event_type="quality_failure",
        source="WEIGHBRIDGE_SAMPLE",
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_scale.id],
        severity=EventSeverity.MEDIUM,
        expected_state={"moisture_pct_max": 14.0, "foreign_matter_max": 1.0},
        observed_state={"moisture_pct_actual": 15.7, "foreign_matter_actual": 1.4, "supplier": "sup-001 (Agropecuaria Alto Paraná)"},
        operational_impact="Grain cannot enter main storage silo 1 without preliminary drying pass in gas drying tower.",
        financial_impact=5400.0,
        currency="USD",
        required_decision="Apply standard CAPPRO moisture table price deduction and route to secondary drying silo",
        status=EventStatus.RESOLVED,
    )
    store.add_event(evt_moisture)

    # Event 4: Delayed Foreign Exchange Wire from Argentina
    evt_payment = OperationalEventRecord(
        id="evt-2026-004",
        timestamp=now - timedelta(hours=2),
        entity_id=inv_01.id,
        entity_type=EntityTypeEnum.INVOICE,
        event_type="payment_delayed",
        source="SWIFT_PORTAL",
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_swift.id],
        severity=EventSeverity.MEDIUM,
        expected_state={"invoice_due_date": (now - timedelta(days=5)).isoformat(), "wire_received": True},
        observed_state={"wire_received": False, "bcra_approval_pending_status": "SEPA_SIRA_HOLD", "days_overdue": 5},
        operational_impact="Delayed working capital inflow impacts local farmer crop payout schedule.",
        financial_impact=8200.0,
        currency="USD",
        required_decision="Draw on sudameris trade finance revolving credit line to bridge grain settlement liquidity",
        status=EventStatus.DETECTED,
    )
    store.add_event(evt_payment)

    # Event 5: Unattended Border Hold Escalation Scenario (Demonstrates Decision Timeout & Escalation)
    evt_escalation = OperationalEventRecord(
        id="evt-2026-005-escalation",
        timestamp=now - timedelta(hours=7),
        entity_id="cust-021", # Córdoba importer
        entity_type=EntityTypeEnum.CUSTOMER,
        event_type="customs_document_missing",
        source="VUE_PORTAL",
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_whatsapp.id],
        severity=EventSeverity.HIGH,
        expected_state={"status": "CLEARED_AT_PUERTO_FALCON", "border_dwell_hours": 2.0},
        observed_state={"status": "HELD_AT_BORDER", "border_dwell_hours": 7.2, "missing_document": "SENACSA_EXPORT_PERMIT_ANNEX_III"},
        operational_impact="3 reefer containers of chilled beef stranded at Puerto Falcón / Clorinda crossing. Refrigerator gen-sets running low on diesel fuel.",
        financial_impact=26500.0,
        currency="USD",
        required_decision="Authorize emergency SENACSA electronic stamp amendment and dispatch fuel replenishment truck",
        status=EventStatus.DECISION_PENDING,
    )
    store.add_event(evt_escalation)

    # Create decision that timed out (created 6.5 hours ago, threshold 4.0h)
    dec_escalated = DecisionRecord(
        decision_id="dec-2026-005-escalated",
        timestamp=now - timedelta(hours=6, minutes=30),
        triggering_event_id=evt_escalation.id,
        decision_owner="role-customs-compliance",
        status=DecisionStatus.DECISION_PENDING,
        provenance=ProvenanceType.SYNTHETIC,
        evidence_ids=[evi_whatsapp.id],
        escalation_timeout_hours=4.0,
        escalation_target_role="role-executive",
        context={
            "cargo_type": "Vacuno Enfriado al Vacío (Reefer Containers)",
            "gen_set_fuel_hours_remaining": 5.0,
            "cold_chain_spoilage_exposure_usd": 68000.0,
            "border_post": "Puerto Falcón / Clorinda (Argentina)",
        },
        options=[
            DecisionOption(
                option_id="OPT-ESCAL-A",
                title="Executive emergency SENACSA liaison & border fuel dispatch",
                description="General Manager contacts SENACSA Director directly for digital signature bypass, while logistics dispatches diesel to border.",
                pros=["Saves $68k cold chain meat cargo", "Solves gen-set fuel emergency within 2 hours"],
                cons=["Requires C-level political intervention", "Fuel dispatch road permit cost"],
                cost_estimate_usd=3200.0,
                delay_hours_estimate=2.0,
                risk_level="HIGH",
            ),
            DecisionOption(
                option_id="OPT-ESCAL-B",
                title="Wait for standard morning SENACSA shift change",
                description="Await normal office hours at Asunción central lab to re-issue certificate.",
                pros=["Standard administrative procedure"],
                cons=["Gen-sets will exhaust fuel overnight", "Risk total meat spoilage"],
                cost_estimate_usd=68000.0,
                delay_hours_estimate=14.0,
                risk_level="CRITICAL",
            ),
        ],
        recommendation="Option A must be authorized immediately by Executive Management to prevent refrigerated beef spoilage.",
        authorization_required=True,
    )
    # Pre-aged decision scenario: created 6.5 hours ago with 4.0h threshold.
    # Seeded in DECISION_PENDING state without pre-escalating, so check_all_escalations()
    # demonstrates the live state transition and cryptographic audit log link end-to-end!
    store.add_decision(dec_escalated)

    # ==========================================
    # 11. AI OPPORTUNITY MODELS & FDE PRIORITIZATION
    # ==========================================
    opp_customs = AIOpportunity(
        id="opp-01-customs-recon",
        title="Automated Cross-Border Customs Document Reconciliation Agent",
        workflow="Cross-Border Export Customs Clearance (Mercosur / VUE / DNA / Receita Federal)",
        bottleneck="Manual verification across 4 disparate systems (SAP B1 Invoice, DNA VUE, Carrier CRT, Paper Packing List) causing 16+ hour dwell times at border crossings.",
        business_impact="$380,000 annual loss in truck driver demurrage, border parking fees, and customer late delivery penalties.",
        entities_involved=[EntityTypeEnum.SHIPMENT, EntityTypeEnum.CUSTOMS_DECLARATION, EntityTypeEnum.DOCUMENT, EntityTypeEnum.INVOICE, EntityTypeEnum.ORDER],
        data_required=["SAP B1 Export Invoice XML", "VUE Portal Export Permit JSON", "Carrier CRT PDF / EDI", "Physical Weight Ticket (Romaneo)"],
        decision_involved="Authorize truck border departure vs Hold for document amendment prior to leaving plant gates.",
        proposed_ai_intervention="Deterministic entity extraction and cross-reconciliation across NCM codes, gross/net weights, Incoterms, and RUC/CNPJ tax IDs before trucks depart the facility.",
        human_in_the_loop_requirement="Mandatory customs broker validation and digital signature confirmation before transmitting rectified filings to DNA/Receita Federal.",
        permissions_required=["SAP_B1:READ_INVOICES", "VUE_PORTAL:READ_DECLARATION", "TMS:READ_SHIPMENT", "SLACK_GMAIL:NOTIFY_BROKER"],
        failure_modes=[
            "Hallucinated NCM tariff code causing customs seizure",
            "Currency conversion rounding error creating invoice-declaration mismatch",
            "Missed phytosanitary expiration date",
        ],
        kpi="Customs Border Dwell Time (Hours)",
        deployment_complexity=DeploymentComplexity.LOW,
        estimated_payoff_annual_usd=320000.0,
        provenance=ProvenanceType.SYNTHETIC,
        prioritization=FDEPrioritization(
            economic_leverage=EconomicLeverage(
                revenue_impact=7,
                cost_impact=9,
                working_capital_impact=8,
                risk_exposure=8,
            ),
            operational_characteristics=OperationalCharacteristics(
                frequency=9,
                decision_complexity=6,
                current_manual_effort=9,
                latency_sensitivity=9,
                cross_system_fragmentation=8,
            ),
            deployment_feasibility=DeploymentFeasibility(
                data_availability=9,
                integration_complexity=8,
                security_sensitivity=9,
                human_approval_clarity=9,
                change_management_readiness=8,
            ),
            strategic_value=StrategicValue(
                repeatability=10,
                adjacent_workflows_count=8,
                cross_customer_applicability=10,
                reusable_ip_potential=9,
            ),
            pilot_recommendation="HIGH_PRIORITY_PILOT",
            prioritization_rationale="Prime candidate for initial FDE pilot: Extremely high frequency, structured VUE/SAP data inputs, clear single broker approval checkpoint, and $320k annual savings.",
        ),
    )
    store.add_opportunity(opp_customs)

    opp_river = AIOpportunity(
        id="opp-02-hydrovia-draft",
        title="Predictive River Level & Fluvial Convoy Draft Optimizer",
        workflow="Fluvial Barge Logistics Dispatch & River Convoys (Hidrovía Paraguay-Paraná)",
        bottleneck="Static loading charts fail to account for 3-5 day river level drops at Paso Queso and Carpinchero, forcing emergency alijo operations or underloading barges by 25%.",
        business_impact="$650,000 annual lost freight capacity and unplanned emergency transfer crane charters.",
        entities_involved=[EntityTypeEnum.FACILITY, EntityTypeEnum.SHIPMENT, EntityTypeEnum.CARRIER, EntityTypeEnum.OPERATIONAL_EVENT],
        data_required=["Prefectura Naval hydrometric gauge readings", "Weather/precipitation radar Chaco basin", "Barge hull immersion curves (cm/ton)"],
        decision_involved="Maximum permissible convoy loading tonnage and draft limit authorization for outgoing 16-barge push-convoys.",
        proposed_ai_intervention="Physics-grounded hydrologic predictive model forecasting navigable draft 7 days ahead and prescribing exact per-barge tonnages to maximize cargo without grounding.",
        human_in_the_loop_requirement="Fluvial Fleet Captain & Logistics Director joint sign-off before closing barge hatches and clearing port authority departure.",
        permissions_required=["TMS:READ_BARGE_FLEET", "WEATHER_API:READ_TELEMETRY", "ERP:UPDATE_SHIPMENT_PLAN"],
        failure_modes=[
            "Optimistic water level prediction leading to convoy grounding and river blockage",
            "Overly conservative draft prescription resulting in wasted vessel deadweight",
        ],
        kpi="Fluvial Convoy Draft Capacity Utilization (%)",
        deployment_complexity=DeploymentComplexity.MEDIUM,
        estimated_payoff_annual_usd=520000.0,
        provenance=ProvenanceType.SYNTHETIC,
        prioritization=FDEPrioritization(
            economic_leverage=EconomicLeverage(
                revenue_impact=9,
                cost_impact=9,
                working_capital_impact=7,
                risk_exposure=10,
            ),
            operational_characteristics=OperationalCharacteristics(
                frequency=7,
                decision_complexity=8,
                current_manual_effort=8,
                latency_sensitivity=9,
                cross_system_fragmentation=7,
            ),
            deployment_feasibility=DeploymentFeasibility(
                data_availability=7,
                integration_complexity=7,
                security_sensitivity=9,
                human_approval_clarity=8,
                change_management_readiness=7,
            ),
            strategic_value=StrategicValue(
                repeatability=9,
                adjacent_workflows_count=9,
                cross_customer_applicability=9,
                reusable_ip_potential=10,
            ),
            pilot_recommendation="HIGH_PRIORITY_PILOT",
            prioritization_rationale="High economic leverage and critical vessel grounding risk avoidance. Core vertical IP for Paraguayan fluvial logistics.",
        ),
    )
    store.add_opportunity(opp_river)

    opp_quality = AIOpportunity(
        id="opp-03-grain-intake-arbitrage",
        title="Automated Grain Intake Assay & CAPPRO Penalty Arbitrage Agent",
        workflow="Raw Commodity Procurement & Weighbridge Receiving (Villeta Silo Intake)",
        bottleneck="Paper weighbridge romaneos and manual spreadsheet calculations of moisture/foreign matter penalty deductions create supplier disputes and slow truck intake.",
        business_impact="$140,000 annual overpayment from unapplied contractual quality deductions and silo bottleneck delays.",
        entities_involved=[EntityTypeEnum.PURCHASE_ORDER, EntityTypeEnum.MATERIAL, EntityTypeEnum.QUALITY_EVENT, EntityTypeEnum.SUPPLIER],
        data_required=["Toledo Weighbridge scale telemetry", "Perten NIR lab moisture/protein readings", "SAP B1 Purchase Order contractual penalty tables"],
        decision_involved="Accept with calculated automated discount vs Route to drying tower vs Reject delivery.",
        proposed_ai_intervention="Instant contractual penalty calculation and generation of digital Romaneo signed via SMS/WhatsApp with delivery driver at scale.",
        human_in_the_loop_requirement="Plant Chemist approval on rejections above 16% moisture.",
        permissions_required=["SCALE:READ_WEIGHT", "LIMS:READ_ASSAY", "SAP_B1:WRITE_PURCHASE_INVOICE_DISCOUNT"],
        failure_modes=["Incorrect moisture table formula application leading to supplier litigation"],
        kpi="Grain Intake Processing Time per Truck (Minutes)",
        deployment_complexity=DeploymentComplexity.LOW,
        estimated_payoff_annual_usd=140000.0,
        provenance=ProvenanceType.SYNTHETIC,
        prioritization=FDEPrioritization(
            economic_leverage=EconomicLeverage(
                revenue_impact=5,
                cost_impact=7,
                working_capital_impact=6,
                risk_exposure=5,
            ),
            operational_characteristics=OperationalCharacteristics(
                frequency=10,
                decision_complexity=5,
                current_manual_effort=9,
                latency_sensitivity=6,
                cross_system_fragmentation=6,
            ),
            deployment_feasibility=DeploymentFeasibility(
                data_availability=8,
                integration_complexity=8,
                security_sensitivity=9,
                human_approval_clarity=8,
                change_management_readiness=8,
            ),
            strategic_value=StrategicValue(
                repeatability=8,
                adjacent_workflows_count=6,
                cross_customer_applicability=8,
                reusable_ip_potential=7,
            ),
            pilot_recommendation="PHASE_2_EXPANSION",
            prioritization_rationale="Solid operational ROI with high daily frequency, but lower aggregate cost exposure ($140k/yr) than customs clearance ($380k/yr) and river draft ($650k/yr).",
        ),
    )
    store.add_opportunity(opp_quality)

    # ==========================================
    # 12. PLATFORM-AGNOSTIC AGENT SPECIFICATIONS
    # ==========================================
    agent_customs = AgentSpecification(
        spec_id="spec-customs-recon-agent",
        title="Cross-Border Customs Reconciliation Agent",
        version="1.0.0",
        objective="Ensure 100% pre-departure consistency across commercial invoices, VUE declarations, CRTs, and packing lists to achieve zero-dwell border crossings.",
        trigger="Event: Shipment ready for dispatch at Facility gate (Planta Villeta or Planta Hernandarias)",
        inputs=[
            "SAP Business One Export Invoice Document (OINV)",
            "Ventanilla Única de Exportación (VUE) Declaration JSON",
            "Carta de Porte Internacional (CRT) PDF/JSON",
            "Báscula Fiscal Certified Romaneo Ticket",
        ],
        entities=[
            EntityTypeEnum.SHIPMENT,
            EntityTypeEnum.CUSTOMS_DECLARATION,
            EntityTypeEnum.DOCUMENT,
            EntityTypeEnum.INVOICE,
            EntityTypeEnum.ORDER,
        ],
        context=(
            "You are operating within the Paraguayan Export Economy regulatory framework governing trade with Mercosur (Brazil and Argentina). "
            "You must cross-validate that: (1) NCM codes on Factura de Exportación match VUE and CRT exact digits; (2) Gross and Net weights on weighbridge "
            "romaneo match declared transport weight within a 0.5% scale tolerance; (3) Exporter RUC (AIDESA: 80099412-4) and foreign Importer CNPJ/CUIT "
            "are valid and unflagged by SEPRELAD/Receita Federal; (4) Incoterm (e.g. FOB Villeta vs DPU Foz) correctly aligns with freight charges in CRT Campo 15."
        ),
        tools=[
            ToolDefinition(
                name="read_erp_export_invoice",
                description="Fetches invoice line items, NCM codes, quantities, and timbrado metadata from SAP Business One.",
                input_schema={"type": "object", "properties": {"invoice_id": {"type": "string"}}, "required": ["invoice_id"]},
                read_only=True,
                required_permissions=["ERP:READ"],
            ),
            ToolDefinition(
                name="read_vue_declaration",
                description="Queries DNA VUE portal for declaration status, channel assignment, and authorized weight/product details.",
                input_schema={"type": "object", "properties": {"vue_declaration_id": {"type": "string"}}, "required": ["vue_declaration_id"]},
                read_only=True,
                required_permissions=["VUE:READ"],
            ),
            ToolDefinition(
                name="read_weighbridge_romaneo",
                description="Fetches certified gross, tare, and net weights from plant weighbridge system.",
                input_schema={"type": "object", "properties": {"shipment_id": {"type": "string"}}, "required": ["shipment_id"]},
                read_only=True,
                required_permissions=["SCALE:READ"],
            ),
            ToolDefinition(
                name="flag_customs_discrepancy",
                description="Generates an alert in FDE Workbench and notifies customs compliance manager with structured mismatch details.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "shipment_id": {"type": "string"},
                        "discrepancy_type": {"type": "string"},
                        "expected_value": {"type": "string"},
                        "observed_value": {"type": "string"},
                        "suggested_action": {"type": "string"},
                    },
                    "required": ["shipment_id", "discrepancy_type", "expected_value", "observed_value"],
                },
                read_only=False,
                required_permissions=["WORKBENCH:WRITE_EVENT"],
            ),
        ],
        permissions=["SAP_B1:READ", "VUE_PORTAL:READ", "TMS:READ", "WORKBENCH:WRITE_EVENT"],
        reasoning_requirements="Deterministic arithmetic and regex string match on legal identifiers. Zero tolerance for approximate matching on tax IDs or tariff subheadings.",
        human_approval_requirements="Any discrepancy blocking departure requires explicit written authorization from Role: Customs Compliance Specialist prior to gate pass issuance.",
        actions=[
            "Issue Green-Gate Pass if 100% fields reconcile",
            "Hold Truck at Plant Depot if discrepancy > tolerance",
            "Generate pre-filled VUE rectification petition for customs broker",
        ],
        failure_modes=[
            "OCR extraction failure on physical CRT stamp",
            "VUE portal API timeout",
            "False negative on Mercosur bilateral tariff exemption",
        ],
        evaluation_criteria=[
            "100% precision on detecting NCM code mismatches",
            "Zero false gate clearances that result in border red-channel inspections",
            "< 30 seconds reconciliation execution time per shipment",
        ],
        kpis=["Customs Border Dwell Time (Hours)", "Red Channel Inspection Rate (%)"],
    )
    store.add_agent_spec(agent_customs)

    agent_hydrovia = AgentSpecification(
        spec_id="spec-hydrovia-draft-agent",
        title="Fluvial Barge Loading & River Draft Optimization Agent",
        version="1.0.0",
        objective="Prescribe exact tonnage allocations across barge convoys to achieve maximum cargo payload without exceeding critical river draft thresholds.",
        trigger="Schedule: Daily at 06:00 and on new hydrology report publication",
        inputs=[
            "Prefectura General Naval Hydrometric Gauge Daily Telemetry",
            "Villeta Silo Inventory & Crushing Mill Output Forecast",
            "Carrier Fluvial Fleet Convoy Manifests",
        ],
        entities=[
            EntityTypeEnum.FACILITY,
            EntityTypeEnum.SHIPMENT,
            EntityTypeEnum.CARRIER,
            EntityTypeEnum.OPERATIONAL_EVENT,
        ],
        context=(
            "You calculate navigable draft for 12-16 barge push-convoys navigating the Paraguay-Paraná river corridor from Villeta (km 1590) "
            "downstream to Rosario/Nueva Palmira. Critical river passes include Paso Queso, Paso Carpinchero, and Angostura. "
            "Safety margin must remain at minimum 12 inches under-keel clearance (UKC) above river bed."
        ),
        tools=[
            ToolDefinition(
                name="get_hydrometric_levels",
                description="Fetches water gauge levels at Asunción, Villeta, Alberdi, and Pilar stations.",
                input_schema={"type": "object", "properties": {"station_code": {"type": "string"}}},
                read_only=True,
                required_permissions=["HYDROLOGY:READ"],
            ),
            ToolDefinition(
                name="calculate_barge_immersion",
                description="Calculates barge draft in feet and inches based on metric tons loaded.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "barge_type": {"type": "string"},
                        "cargo_metric_tons": {"type": "number"},
                    },
                    "required": ["barge_type", "cargo_metric_tons"],
                },
                read_only=True,
                required_permissions=["MATH:EXEC"],
            ),
        ],
        permissions=["HYDROLOGY:READ", "TMS:READ", "SAP_B1:READ"],
        reasoning_requirements="Hydrodynamic equations combining hydrostatic immersion curves with river stage forecasts. Safety margin strictly non-negotiable.",
        human_approval_requirements="Fluvial Fleet Captain and Operations Director joint digital sign-off on loading manifest.",
        actions=[
            "Publish Daily Loading Plan per Barge Convoy",
            "Trigger Alijo Alert when draft deficit forecast exceeds 18 inches",
        ],
        failure_modes=["Failure to predict sudden flash drought or upstream Itaipú dam discharge reduction"],
        evaluation_criteria=["Zero barge groundings in 12-month rolling window", "Average convoy draft within 3 inches of safe limit"],
        kpis=["Fluvial Convoy Draft Capacity Utilization (%)", "Demurrage Cost per MT ($)"],
    )
    store.add_agent_spec(agent_hydrovia)

    # ==========================================
    # 13. KPIS (Operational & Financial Reality)
    # ==========================================
    kpi_ccc = KPI(
        id="kpi-cash-conversion-cycle",
        name="Cash Conversion Cycle (CCC)",
        category="FINANCIAL",
        metric_code="CCC_DAYS",
        current_value=48.2,
        target_value=35.0,
        unit_of_measure="Days",
        trend="DEGRADING",
        system_of_record="SAP_B1",
        tags=["kpi", "financial", "cash"],
        attributes={"notes": "Prolonged by Argentine foreign exchange wire authorizations and river convoy transit delays."},
    )
    kpi_dwell = KPI(
        id="kpi-border-dwell",
        name="Customs Border Dwell Time",
        category="LOGISTICS",
        metric_code="BORDER_DWELL_HOURS",
        current_value=16.8,
        target_value=6.0,
        unit_of_measure="Hours",
        trend="DEGRADING",
        system_of_record="TMS",
        tags=["kpi", "logistics", "customs", "border"],
        attributes={"notes": "Average truck waiting hours at Ciudad del Este / Foz do Iguaçu customs checkpoint."},
    )
    kpi_draft = KPI(
        id="kpi-fluvial-draft-utilization",
        name="Fluvial Convoy Draft Capacity Utilization",
        category="LOGISTICS",
        metric_code="DRAFT_UTILIZATION_PCT",
        current_value=81.4,
        target_value=95.0,
        unit_of_measure="Percentage",
        trend="IMPROVING",
        system_of_record="TMS",
        tags=["kpi", "logistics", "fluvial", "hidrovia"],
        attributes={"notes": "Percentage of theoretical barge deadweight utilized safely under current river levels."},
    )
    kpi_otif = KPI(
        id="kpi-otif-export",
        name="On-Time In-Full Export Delivery (OTIF)",
        category="OPERATIONS",
        metric_code="OTIF_PCT",
        current_value=89.2,
        target_value=96.0,
        unit_of_measure="Percentage",
        trend="STABLE",
        system_of_record="SAP_B1",
        tags=["kpi", "commercial", "otif"],
    )
    kpi_moisture = KPI(
        id="kpi-moisture-rejection",
        name="Grain Intake Quality Penalty/Rejection Rate",
        category="QUALITY",
        metric_code="REJECTION_PCT",
        current_value=3.8,
        target_value=1.5,
        unit_of_measure="Percentage",
        trend="STABLE",
        system_of_record="SAP_B1",
        tags=["kpi", "quality", "grain"],
    )

    store.add_kpi(kpi_ccc)
    store.add_kpi(kpi_dwell)
    store.add_kpi(kpi_draft)
    store.add_kpi(kpi_otif)
    store.add_kpi(kpi_moisture)

    # ==========================================
    # 14. CANONICAL FDE PILOT SPECIFICATIONS
    # ==========================================
    econ_customs = PilotEconomicModel(
        annual_decision_volume=1800,
        manual_effort_minutes_per_decision=14.0,
        hourly_labor_cost_usd=25.0,
        current_error_or_exception_rate=0.065,
        cost_per_exception_usd=850.0,
        target_manual_effort_minutes=3.0,
        target_exception_rate=0.015,
        pilot_decision_volume=100,
        pilot_implementation_cost_usd=15000.0,
        annual_software_subscription_usd=18000.0,
        working_capital_acceleration_days=3.5,
        annual_working_capital_financial_value_usd=22000.0,
        assumptions_ledger={
            "annual_decision_volume": "1,800 outbound export trucks/year derived from AIDESA annual volume of 480k MT divided by ~27 MT per truckload.",
            "manual_effort_minutes_per_decision": "14.0 minutes average time spent by foreign trade clerks reconciling SAP B1 invoices, báscula slips, and SENAVE certificates.",
            "hourly_labor_cost_usd": "$25.00 fully-burdened hourly cost (salary, social charges, overhead) for Paraguayan foreign trade documentation analysts.",
            "current_error_or_exception_rate": "6.5% baseline error rate based on historical customs rejection and Canal Rojo audit logs.",
            "cost_per_exception_usd": "$850.00 average cost per exception including border truck demurrage ($250/day x 2 days), customs rectification fees, and administrative rework.",
            "target_manual_effort_minutes": "3.0 minutes human verification and click-to-transmit time in assisted dashboard.",
            "target_exception_rate": "1.5% residual exception rate accounting for rare physical scale discrepancies or tariff classification edge cases.",
            "pilot_decision_volume": "100 consecutive outbound shipments through Ciudad del Este border post during 30-day evaluation.",
            "pilot_implementation_cost_usd": "$15,000 fixed fee for 2 weeks FDE integration, prompt tuning, and SAP B1 connector deployment.",
            "annual_software_subscription_usd": "$18,000 annual runtime subscription for Vertex AI inference, embeddings, and enterprise support.",
            "working_capital_acceleration_days": "3.5 days reduction in border clearance dwell time accelerating letter-of-credit presentation.",
            "annual_working_capital_financial_value_usd": "$22,000 carrying cost savings on $4.5M rolling export receivables at 6.0% cost of capital.",
        },
    )

    pilot_customs = PilotSpecification(
        pilot_id="pilot-2026-customs-recon",
        opportunity_id="opp-2026-001",
        agent_spec_id="agent-customs-compliance",
        title="Automated Export Customs Clearance & Tariff Reconciliation Pilot",
        customer="Agro-Industrial del Este S.A. (AIDESA)",
        workflow="Export documentation review, SOFIA clearance pack compilation, and Mercosur NCM tariff classification",
        decision="Authorize dispatch and generate customs submission pack for dry grain / meal outbound trucks",
        decision_owner="Head of Customs Compliance & Foreign Trade (Jefe de Comercio Exterior)",
        baseline_kpi={
            "manual_prep_time_minutes": 14.0,
            "customs_error_rate_pct": 6.5,
            "border_dwell_hours": 16.8,
            "annual_delay_penalties_usd": 99450.0,
        },
        target_kpi={
            "manual_prep_time_minutes": 3.0,
            "customs_error_rate_pct": 1.5,
            "border_dwell_hours": 6.0,
            "annual_delay_penalties_usd": 22950.0,
        },
        measurement_method="Audit logs comparing timestamp of packing list availability vs SOFIA clearance receipt; weekly customs rectification tracker.",
        data_sources=[
            "SAP Business One ERP (OINV, DLN1, OITM)",
            "DNA SOFIA Customs XML API",
            "Villeta & CDE Terminal Truck Scale Weight Slips (Báscula)",
            "SENAVE Phytosanitary Inspection Reports",
        ],
        required_integrations=[
            "SAP Business One Service Layer (Read-Only)",
            "DNA SOFIA Staging Sandbox (SOAP/XML Read-Only)",
            "Postgres / Shared SMB Scale Ticket Folder",
        ],
        trigger="Truck weigh-out event at facility terminal scale (scale_ticket_closed)",
        inputs=[
            "Commercial Invoice (Factura de Exportación)",
            "SENAVE Phytosanitary Certificate",
            "Bill of Lading / CRT (Carta de Porte por Carretera)",
            "Packing List with calibrated moisture & net weights",
        ],
        context=(
            "Mercosur trade corridor through Ciudad del Este / Foz do Iguaçu. Discrepancies between declared weight "
            "on CRT and scale ticket trigger physical red-channel customs inspection (Canal Rojo) causing 36-72 hour "
            "border demurrage."
        ),
        recommended_action=(
            "Pre-validate 4-way document cross-check, flag NCM classification mismatches, and prepare pre-filled "
            "SOFIA export dispatch declaration."
        ),
        human_approval_required="Jefe de Comercio Exterior must click 'Approve for SOFIA Transmission' in dashboard. Agent NEVER submits directly to DNA production.",
        authorized_actions=[
            "Generate reconciled customs pack PDF",
            "Post draft document bundle to SAP B1 staging table",
            "Emit alert to customs broker on discrepancy > 0.5%",
        ],
        supported_platforms=[
            "gemini_enterprise",
            "microsoft_azure_ai_foundry",
            "openai_assistants",
            "databricks_mosaic_ai",
        ],
        selected_platform="gemini_enterprise",
        pilot_duration="30 days",
        pilot_scope="100 consecutive outbound soy meal and oil export trucks passing through Ciudad del Este border",
        failure_modes=[
            "OCR / Document extraction confidence < 92% on stamped scale slips",
            "SOFIA schema divergence or unannounced DNA customs server downtime",
            "Complex multi-modal transit shipments with transit bond changes",
        ],
        rollback_condition=(
            "If 2 consecutive shipments incur customs documentation discrepancies or manual intervention time exceeds baseline "
            "(15 mins), pilot pauses to manual operator review immediately."
        ),
        safety_constraints=[
            "No write access to production DNA SOFIA customs system",
            "Read-only access to SAP Business One financial journal entries",
            "All data stored and processed within encrypted regional boundary with no LLM model training on customer commercial data",
        ],
        acceptance_criteria=[
            ">= 95% of test shipments processed in < 3 minutes",
            "Zero Canal Rojo (red-channel) inspections caused by clerical documentation discrepancy",
            "100% human sign-off recorded with tamper-evident audit hash (within current database session)",
        ],
        economic_model=econ_customs,
        implementation_effort="2 weeks configuration + 1 week shadow testing",
        deployment_dependencies=[
            "SAP B1 Service Layer API credentials",
            "SOFIA testing environment digital certificate",
            "Sample historical dataset of 200 completed export files",
        ],
        status=PilotStatus.PROPOSED,
        expansion_path="Automated Fluvial Barge Convoy Transit Manifests (Villeta to Nueva Palmira)",
        provenance=ProvenanceType.DERIVED,
    )

    econ_fluvial = PilotEconomicModel(
        annual_decision_volume=240,
        manual_effort_minutes_per_decision=45.0,
        hourly_labor_cost_usd=40.0,
        current_error_or_exception_rate=0.08,
        cost_per_exception_usd=18500.0,
        target_manual_effort_minutes=10.0,
        target_exception_rate=0.01,
        pilot_decision_volume=24,
        pilot_implementation_cost_usd=22000.0,
        annual_software_subscription_usd=24000.0,
        working_capital_acceleration_days=2.0,
        annual_working_capital_financial_value_usd=15000.0,
        assumptions_ledger={
            "annual_decision_volume": "240 push-boat convoy barge departures/year from Villeta terminal along Hidrovía Paraguay-Paraná.",
            "manual_effort_minutes_per_decision": "45.0 minutes manual calculation per convoy across barge hydrostatic tables, draft gauges, and shoal forecasts.",
            "hourly_labor_cost_usd": "$40.00 blended rate for Senior Terminal Operations Director and Naval Logistics Captain.",
            "current_error_or_exception_rate": "8.0% historical rate of convoy grounding risk or sub-optimal loading resulting in emergency alijo (lightering).",
            "cost_per_exception_usd": "$18,500 direct cost per lightering incident (chartering auxiliary crane barge, lost days, demurrage penalties).",
            "target_manual_effort_minutes": "10.0 minutes review and sign-off on AI-optimized multi-barge draft distribution plan.",
            "target_exception_rate": "1.0% residual risk under conservative hydrological safety margin constraints.",
            "pilot_decision_volume": "24 push-boat convoy dispatches during 60-day low-water window.",
            "pilot_implementation_cost_usd": "$22,000 fixed FDE deployment covering telemetry pipeline integration and sonar depth calibration.",
            "annual_software_subscription_usd": "$24,000 annual subscription for hydrographic simulation and multi-sensor predictive draft model.",
            "working_capital_acceleration_days": "2.0 days faster river transit cycle time resulting from elimination of grounding delays.",
            "annual_working_capital_financial_value_usd": "$15,000 financial savings on tied-up fluvial freight inventory.",
        },
    )

    pilot_fluvial = PilotSpecification(
        pilot_id="pilot-2026-fluvial-draft",
        opportunity_id="opp-2026-002",
        agent_spec_id="agent-fluvial-hydrology",
        title="Hidrovía Dynamic Convoy Draft & Loading Allocation Pilot",
        customer="Agro-Industrial del Este S.A. (AIDESA)",
        workflow="Daily barge loading plan, convoy draft optimization, and critical river pass immersion calculation",
        decision="Authorize metric tons loaded per barge and approve push-boat convoy formation at Villeta terminal",
        decision_owner="Fluvial Fleet Captain & Terminal Operations Director",
        baseline_kpi={
            "convoy_draft_utilization_pct": 81.4,
            "alijo_lightering_incidents_annual": 4.0,
            "avg_immersion_safety_margin_inches": 24.0,
            "annual_lost_freight_and_alijo_usd": 164000.0,
        },
        target_kpi={
            "convoy_draft_utilization_pct": 92.5,
            "alijo_lightering_incidents_annual": 0.0,
            "avg_immersion_safety_margin_inches": 13.5,
            "annual_lost_freight_and_alijo_usd": 32000.0,
        },
        measurement_method="Comparison of actual hydrographic sonar survey readings vs predicted draft at Paso Queso; post-voyage barge outturn manifests.",
        data_sources=[
            "Prefectura General Naval Hydrometric Gauge Network",
            "Asunción & Villeta Daily Gauge Reports",
            "Terminal Villeta Silo Weighbridge & Conveyor Belt Telemetry",
            "Hidrovías del Sur Push-Boat Convoy GPS & Sonar Feeds",
        ],
        required_integrations=[
            "Naval Prefecture Hydrographic Bulletin RSS/PDF scraper",
            "TMS Fluvial Dispatch module",
            "Villeta Terminal Silo PLC / SCADA interface (Read-Only)",
        ],
        trigger="Daily 06:00 AM hydrometric water level publication and convoy arrival notification",
        inputs=[
            "Daily river stage readings at Asunción, Villeta, Alberdi, Pilar, Corrientes",
            "Grain batch moisture and specific gravity assays",
            "Barge hydrostatic immersion tables (feet/inch per 100 MT)",
        ],
        context=(
            "Low water levels on the Paraguay-Paraná river (Paso Queso, Paso Carpinchero) severely restrict allowable barge draft. "
            "Underloading leaves money on the table (dead freight), while overloading risks grounding, canal blockage, "
            "and catastrophic lightering (alijo) costs."
        ),
        recommended_action=(
            "Compute optimal cargo distribution across 12-barge convoy to maximize payload while maintaining strict 12-inch "
            "under-keel clearance at bottleneck passes."
        ),
        human_approval_required="Fleet Captain and Terminal Operations Director joint digital sign-off before conveyor belt loading commences.",
        authorized_actions=[
            "Publish Convoy Loading Plan to Terminal Villeta SCADA",
            "Issue Navigational Advisory to Tugboat Master",
            "Alert Commercial Desk on available incremental spot freight capacity",
        ],
        supported_platforms=[
            "gemini_enterprise",
            "microsoft_azure_ai_foundry",
            "openai_assistants",
            "databricks_mosaic_ai",
        ],
        selected_platform="gemini_enterprise",
        pilot_duration="45 days",
        pilot_scope="6 consecutive outbound push-convoys (approx. 72 total barge transits) during low-water season",
        failure_modes=[
            "Sudden unpredicted river level drop (> 15 cm in 12 hours) due to Itaipú dam flow modulation",
            "Inaccurate barge tare weights causing immersion discrepancy",
        ],
        rollback_condition=(
            "If any barge draft exceeds target maximum minus 6 inches safety buffer, or captain flags navigation safety concern, "
            "immediately revert to conservative static tables."
        ),
        safety_constraints=[
            "Strict 12-inch under-keel clearance (UKC) invariant — model cannot override safety threshold",
            "Loading speed capped at terminal conveyor maximum",
        ],
        acceptance_criteria=[
            "Zero barge groundings or emergency lighterings (alijo)",
            ">= 8% increase in cargo payload per convoy without safety violations",
            "100% compliance with Naval Prefecture draft advisories",
        ],
        economic_model=econ_fluvial,
        implementation_effort="3 weeks integration + 2 weeks shadow verification",
        deployment_dependencies=[
            "Barge hydrostatic calibration curves",
            "Prefectura Naval gauge telemetry API/feed",
            "Terminal Villeta loading master coordination",
        ],
        status=PilotStatus.PROPOSED,
        expansion_path="Dynamic Fleet Routing & Fuel Consumption Optimization across Lower Paraná",
        provenance=ProvenanceType.DERIVED,
    )

    store.add_pilot(pilot_customs)
    store.add_pilot(pilot_fluvial)

    return {
        "status": "SUCCESS",
        "company": aidesa.name,
        "headcount": total_headcount_verified,
        "facility_count": 2,
        "supplier_count": supplier_counter - 1,
        "customer_count": len(customer_destinations),
        "product_count": 3,
        "material_count": 2,
        "event_count": len(store.list_events()),
        "decision_count": len(store.list_decisions()),
        "opportunity_count": len(store.list_opportunities()),
        "agent_spec_count": len(store.list_agent_specs()),
        "kpi_count": len(store.list_kpis()),
        "evidence_count": store.count_evidence(),
        "pilot_count": store.count_pilots(),
    }
