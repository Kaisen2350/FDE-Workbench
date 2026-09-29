# FDE Curriculum Module 1: Physical Reality & Domain Ontologies

> *"Enterprise paperwork is an aspiration; physical constraints are the truth. An FDE models what moves, what stalls, and what burns capital."*

---

## 1. The Core FDE Premise: Why Traditional Schemas Fail

Most software engineering teams approach enterprise systems by inspecting relational databases or SaaS APIs (ERP tables, CRM records). In complex operations (logistics corridors, agro-industrial manufacturing, cross-border trade), **paperwork is a lagging and often misleading representation of reality**:

* A Bill of Lading says 1,500 MT of grain was loaded, but the hydrometric river gauge dropped 40 cm overnight, meaning the barge convoy will run aground at *Paso Queso* if dispatched at full draft.
* A Customs Export Declaration (`VUE`) is marked "Ready", but the physical weighbridge scale ticket shows a 450 kg discrepancy with the packing list, guaranteeing a mandatory red-channel physical inspection and a 36-hour border dwell penalty.

A Forward Deployed Engineer (FDE) builds an **operational ontology grounded in physical truth and explicit provenance**.

```
┌────────────────────────────────────────────────────────┐
│             TRADITIONAL CRUD MODEL                     │
│  Shipment (id, status, created_at)                     │
│  ❌ Ignores physical draft, customs DNA, axle weight   │
└────────────────────────────────────────────────────────┘
                           VS
┌────────────────────────────────────────────────────────┐
│             FDE OPERATIONAL ONTOLOGY                   │
│  Shipment (river_draft_ft, convoy_size, route, ... )   │
│  ├── Grounded by: Hydrometric Gauge Evidence           │
│  ├── Constrained by: SENACSA / DNIT / Mercosur Rules   │
│  └── Bound to: OperationalEvent & 5-Stage Decision     │
└────────────────────────────────────────────────────────┘
```

---

## 2. The 24-Entity Operational Taxonomy

In the `fde-workbench`, we model the physical reality of export enterprises through 24 strongly typed domain entities (defined in `fde_workbench/models/` using Pydantic v2):

| Category | Domain Entities | Operational Role |
|---|---|---|
| **Commercial Actors** | `Organization`, `Supplier`, `Customer`, `Carrier` | Enterprise participants, counterparties, and freight operators across corridors |
| **Physical Infrastructure** | `Facility`, `Warehouse`, `Machine` | Crushing mills, river ports, silo batteries, and weighbridges with throughput bounds |
| **Commodities & Batches** | `Product`, `Material`, `ProductionBatch` | Raw inputs, refined goods, specifications, and lab assays (moisture, protein, aflatoxin) |
| **Commercial Commitments** | `Order`, `PurchaseOrder`, `Contract`, `Invoice`, `Payment` | Sales agreements, Incoterms 2020 definitions, Swift MT103 wires, and settlement schedules |
| **Logistics & Transport** | `Shipment` | Push-convoys on Hidrovía (16-barge units) and bitren trucks on BR-277 with mode parameters |
| **Regulatory & Compliance** | `CustomsDeclaration`, `Document`, `RegulatoryObligation` | VUE, DUA, MIC/DTA, phytosanitary certs (SENAVE), animal health (SENACSA), and SEPRELAD GRC |
| **Human & Operational Execution** | `EmployeeRole`, `OperationalEvent`, `Decision`, `QualityEvent`, `KPI` | 250 headcount roles, real-world disruptions, 5-stage decision gates, and financial telemetry |

### The Curated Critical Path
To avoid cognitive paralysis when embedding with executive sponsors, the ontology exposes a high-leverage **6-step Critical Path**:

$$\text{Order} \longrightarrow \text{Shipment} \longrightarrow \text{CustomsDeclaration} \longrightarrow \text{OperationalEvent} \longrightarrow \text{Decision} \longrightarrow \text{Outcome}$$

---

## 3. Explicit Data Provenance

In enterprise deployments, data purity is a myth. Unlabeled data leads to hallucinated automations and catastrophic operational decisions. Every entity, claim, and evidence node in our workbench carries an explicit provenance tag:

```python
class ProvenanceType(str, Enum):
    SYNTHETIC = "SYNTHETIC"                 # Deterministic baseline data modeling physical reality
    CUSTOMER_OBSERVED = "CUSTOMER_OBSERVED" # Direct on-site telemetry (weighbridge, terminal logs)
    PUBLIC_SOURCE = "PUBLIC_SOURCE"         # Official bulletins (Prefectura Naval, DNIT tariffs)
    CUSTOMER_PROVIDED = "CUSTOMER_PROVIDED" # Unverified claims from customer interviews
    DERIVED = "DERIVED"                     # Programmatically computed state transitions
```

**The FDE Rule of Evidence**: An operational action can never be authorized based solely on `CUSTOMER_PROVIDED` assertions without corroboration from `CUSTOMER_OBSERVED` or `PUBLIC_SOURCE` evidence.

---

## 4. Directed Operational Relationships

Entities connect via validated operational verbs that enforce business rules. An `Organization` cannot "transport" a `Product`; a `Carrier` transports a `Shipment` which contains `Product`:

```python
# Validated Triples in fde_workbench.domain.relationships
ORGANIZATION  --[OPERATES]-->       FACILITY
ORGANIZATION  --[BUYS_FROM]-->      SUPPLIER
ORDER         --[GENERATES]-->      SHIPMENT
SHIPMENT      --[TRANSPORTS]-->     PRODUCT
SHIPMENT      --[HANDLED_BY]-->     CARRIER
INVOICE       --[ASSOCIATED_WITH]-> ORDER
```

The underlying graph engine maintains bi-directional adjacency indexing (`incoming_edges` and `outgoing_edges`) enabling instant 1-hop traversal across the entire trade corridor.

---

## 5. Hands-on Lab: Inspecting & Querying the Domain Graph

### 1. Launch the Workbench Server
```bash
python run_workbench.py
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to inspect the 24 entities, bi-directional edge drawer, and critical path toggle.

### 2. Programmatic Graph Query (Python)
```python
from fde_workbench.storage.store import store
from fde_workbench.domain.ontology import EntityTypeEnum, RelationTypeEnum

# Query all shipments handled by river carriers
shipments = store.get_entities_by_type(EntityTypeEnum.SHIPMENT)
for s in shipments:
    if s.attributes.get("transport_mode") == "RIVER":
        print(f"Barge Convoy: {s.id} | Draft: {s.attributes.get('draft_ft')} ft | Destination: {s.attributes.get('destination')}")
```

### 3. Verify Graph Constraints
Execute the ontology validation test suite:
```bash
python -m unittest tests/test_ontology.py -v
```

---

## Key Takeaways for the FDE
1. **Model physics before paperwork**: Build schemas around real-world friction (water depth, border queues, assay variance).
2. **Tag provenance at ingestion**: Distinguish verified facts from unverified stakeholder claims.
3. **Establish a critical path narrative**: Use the 6-step core spine to explain system value to C-level decision-makers.
