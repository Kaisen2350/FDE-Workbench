# Paraguay Export Economy — Forward Deployed Engineer (FDE) Workbench (Phase 1)

> **Mission**: An engineering and research workbench for a Forward Deployed Engineer (FDE) to model the operational reality of Paraguayan export-oriented enterprises, identify mission-critical workflows and bottlenecks, and translate those findings into platform-agnostic AI agent deployment specifications.

---

## Scope & Non-Goals

- **NOT a SaaS product**: No billing layer, multi-tenancy, or commercial subscriptions.
- **NOT an autonomous agent**: No unsupervised execution or black-box agents.
- **NOT a production customer system**: Does not connect to live customer databases, send emails, or make external API calls.
- **Purpose**: Establishes the **deterministic domain-modeling foundation** grounded in physical reality (fluvial draft levels, Mercosur road freight, customs documentation, Maquila regimes, and cash conversion cycles).

---

## Quickstart

The workbench is local-first, requires only Python 3.11 with `pydantic` and `fastapi`, and runs with zero external network dependencies.

```powershell
# 1. Launch the Workbench Web Interface
python run_workbench.py

# Alternatively via the package entrypoint:
python -m fde_workbench serve --port 8000
```

Open your browser at:
- **Workbench UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive REST API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

To run the automated test suite:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## Architecture & Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FDE WORKBENCH WEB INTERFACE                           │
│  [1.Ontology] [2.Entities] [3.Relations] [4.Events] [5.Decisions]           │
│  [6.Workflows] [7.AI Opportunities] [8.Agent Specs] [9.KPIs] [10.Company]   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST API (FastAPI)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LOCAL-FIRST IN-MEMORY GRAPH & AUDIT STORE                │
│  - Bi-directional Adjacency Lists (Incoming/Outgoing 1-hop Graph Traversal) │
│  - Append-Only Audit Trail (Entity mutation logs & state transition diffs)  │
│  - JSON Snapshot Persistence (Import / Export / Reseed)                     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Validates & Hydrates
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                  TYPED DOMAIN & ONTOLOGY LAYER (Pydantic v2)                 │
│  - 24 Core Domain Entities (Organization, Facility, Shipment, Batch...)     │
│  - Explicit Typed Relationship Triples (operates, transports, settles...)   │
│  - Operational Event Model (Expected vs Observed state diffs & impact)      │
│  - Decision Pipeline (Observation -> Context -> Decision -> Action -> Result)│
│  - AI Opportunity Framework (Bottleneck, HITL, Permissions, Failure Modes)  │
│  - Platform-Agnostic Agent Specs + Platform Adapters (Gemini, OpenAI, etc.) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Seed Data
┌──────────────────────────────────────▼──────────────────────────────────────┐
│          SYNTHETIC EXPORTER SEED: Agro-Industrial del Este S.A. (AIDESA)     │
│  - 250 Headcount across Operations, Quality, Logistics, Comex, & Finance    │
│  - 2 Facilities: Planta Villeta (River Port) & Planta Hernandarias (Maquila) │
│  - Trade Corridors: Brazil (CDE/Foz BR-277) & Argentina (Falcón & Hidrovía) │
│  - 80 Approved Suppliers & 25 International B2B Customers                   │
│  - IT Landscape: SAP B1 + Google Workspace + Trans-Chaco TMS + Spreadsheets │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Ontology: The 24 Domain Entities

1. **Organization**: Exporter entity (e.g. AIDESA S.A., RUC 80099412-4).
2. **Facility**: Industrial plants and ports (Planta Fluvial Villeta, Planta Maquila Hernandarias).
3. **Supplier**: 80 grain/feed producers, livestock farms, packaging, and barge lines.
4. **Customer**: 25 international buyers (Brazilian poultry feed integrators, Argentine crushers).
5. **Product**: High-protein soybean meal pellets 46.5%, crude degummed soy oil, chilled beef.
6. **Material**: Raw unprocessed soybeans, bulk yellow corn, 50kg polybags, flexitanks.
7. **Order**: Commercial export sales contracts with Incoterms (FOB Villeta, CIF Paranaguá, DPU Foz).
8. **PurchaseOrder**: Inbound commodity and packaging procurement commitments.
9. **Shipment**: 16-barge push convoys on the Hidrovía; double-trailer bitren trucks across CDE.
10. **Carrier**: Fluvial barge lines (Hidrovías del Sur) and terrestrial trucking fleets.
11. **Warehouse**: Silo batteries (60k MT at Villeta) and bonded fiscal depots (Hernandarias).
12. **Invoice**: Official export invoices (Factura de Exportación en USD, Timbrado DNIT).
13. **Payment**: International Swift MT103 wires, Mercosur SML payments, SIPAP transfers.
14. **Contract**: Master sales contracts, Incoterms 2020 definitions, and demurrage schedules.
15. **Document**: Bill of Lading (B/L), Carta de Porte Internacional (CRT), Romaneo, Packing List.
16. **CustomsDeclaration**: VUE (Ventanilla Única de Exportación), DUA, and MIC/DTA transit permits.
17. **RegulatoryObligation**: SENACSA animal health, SENAVE phytosanitary, Maquila CNIME, SEPRELAD.
18. **EmployeeRole**: Headcount distribution across 8 functional areas totaling exactly 250 roles.
19. **Machine**: Grain crushers (Bühler 120 TPH), expellers, weighbridges, barge loading spouts.
20. **ProductionBatch**: Industrial runs with recorded laboratory moisture/protein assays.
21. **QualityEvent**: High moisture (>14%), aflatoxin detection, broken container seals.
22. **OperationalEvent**: Fluvial river draft drops, customs border bridge delays, machine faults.
23. **Decision**: Managerial resolution evaluating trade-offs, recommendations, and authorized actions.
24. **KPI**: Cash Conversion Cycle, Border Dwell Time, Fluvial Draft Capacity, OTIF Delivery.

---

## Operational Event Model

An `OperationalEventRecord` captures physical reality rather than paperwork:
- `timestamp`: Event occurrence or detection time.
- `entity_id` & `entity_type`: Affected target entity.
- `event_type`: e.g. `river_draft_restriction`, `customs_document_missing`, `quality_failure`.
- `source`: Source of truth (`PREFECTURA_NAVAL_GAUGE`, `VUE_PORTAL`, `WEIGHBRIDGE_SCALE`, `TMS`).
- `severity`: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
- `expected_state`: Baseline planned state (e.g. permissible draft 10.5 ft).
- `observed_state`: Real-world observation (e.g. permissible draft 8.4 ft at Paso Queso).
- `operational_impact`: Human/physical disruption description.
- `financial_impact`: Quantified loss/exposure in USD.
- `required_decision`: Nature of the decision demanded.
- `status`: `DETECTED`, `TRIAGED`, `DECISION_PENDING`, `MITIGATED`, `RESOLVED`.

---

## Decision Pipeline: Observation to Outcome

Enforces the core tradecraft sequence:
$$\text{OBSERVATION} \longrightarrow \text{CONTEXT} \longrightarrow \text{DECISION} \longrightarrow \text{AUTHORIZED ACTION} \longrightarrow \text{OUTCOME}$$

1. **Observation**: Triggered directly by an `OperationalEventRecord`.
2. **Context**: Relevant operational state, customer constraints, penalty clauses, and local alternatives.
3. **Decision & Options**: Multi-option trade-off matrix evaluating cost, latency, and risk, yielding a formal recommendation.
4. **Authorized Action**: Mandatory human authorization capturing who approved what, when, and with what parameters.
5. **Outcome**: Verified post-execution measurement checking actual latency, financial delta, and KPI impact.

---

## AI Opportunity Model & Platform-Agnostic Agent Specs

### AI Opportunity
Connects operational bottlenecks to high-leverage AI interventions:
- `workflow` & `bottleneck`
- `business_impact` & estimated annual payoff
- `proposed_ai_intervention`
- `human_in_the_loop_requirement`
- `permissions_required`
- `failure_modes` & guardrails
- `deployment_complexity` (`LOW`, `MEDIUM`, `HIGH`)

### Platform-Agnostic Agent Specifications
Specifies an agent blueprint without vendor lock-in:
- `objective`, `trigger`, `inputs`, `entities`, `context`
- `tools` (typed schema, read-only vs state-mutating, permissions)
- `reasoning_requirements` & `human_approval_requirements`
- `actions`, `failure_modes`, `evaluation_criteria`, `kpis`

### Enterprise Platform Adapters
The workbench includes compilers that export native manifests on demand:
- **Google Cloud / Gemini Enterprise**: Generates Vertex AI system instructions, function declarations, grounding datastore configs, and guardrail policies.
- **OpenAI**: Generates Assistants API instructions, strict function tools, and metadata.
- **Microsoft Azure AI Foundry**: Generates Semantic Kernel plugins, responsible AI policies, and prompt templates.
- **Databricks Mosaic AI**: Generates Unity Catalog tool bindings, MLflow experiment bindings, and serving endpoint configurations.

---

## Synthetic Company: Agro-Industrial del Este S.A. (AIDESA)

- **Headcount**: Exactly **250 employees** distributed across:
  - Plant & Silos (120)
  - Maintenance & Engineering (30)
  - Logistics, Scale & Dispatch (25)
  - Quality Control & Laboratory (20)
  - Comex, Customs & Regulatory (15)
  - Finance, Treasury & Foreign Exchange (18)
  - Commercial & Grain Trading (12)
  - Executive & Operations Direction (10)
- **Facilities**:
  1. *Planta Fluvial Villeta*: km 1590 on Paraguay River, 2,800 TPD crushing mill, barge loading dock, 60k MT silos.
  2. *Planta Maquila Hernandarias*: Alto Paraná near Friendship Bridge to Brazil, packaging and export assembly under Ley de Maquila 1064/97.
- **Corridors**:
  - *Brazil*: Terrestrial bitren highway PY-02 / BR-277 to Cascavel, Curitiba, and Port of Paranaguá.
  - *Argentina*: Fluvial barge push-convoys down Hidrovía Paraná-Paraguay to Rosario/San Lorenzo, and road freight via Puerto Falcón / Clorinda.
- **Network**: Exactly **80 suppliers** and **25 international customers**.
- **IT Systems**: SAP Business One, Google Workspace, Trans-Chaco TMS, Spreadsheets.

---

## 10-View Inspection Interface

1. **Ontology**: Schema browser, 24 entity definitions with Paraguayan context, and relationship rules.
2. **Entities**: Searchable, filterable directory with side-drawer attribute and graph inspector.
3. **Relationships**: Directed edge browser with source, relation, and target links.
4. **Operational Events**: Feed of real-world disruptions comparing expected baseline vs observed reality.
5. **Decisions**: 5-stage pipeline inspector (`Observation ➔ Context ➔ Decision ➔ Action ➔ Outcome`).
6. **Workflows**: Lifecycle trace chains for fluvial and terrestrial export corridors.
7. **AI Opportunities**: High-leverage bottleneck analysis cards with human-in-the-loop gates.
8. **Agent Specifications**: Platform-agnostic blueprints with live live adapter compilation to Gemini, OpenAI, Azure, and Databricks.
9. **KPIs**: Metrics telemetry (Cash Conversion Cycle, Customs Dwell Time, Fluvial Draft Capacity, OTIF).
10. **Synthetic Company**: Enterprise dossier, 250-headcount distribution, IT landscape, and reset controls.

---

## CLI Reference

```powershell
# Start workbench web interface
python -m fde_workbench serve --host 127.0.0.1 --port 8000

# Generate synthetic dataset and verify counts
python -m fde_workbench seed --export aidesa_snapshot.json

# Export snapshot
python -m fde_workbench export my_snapshot.json

# Import snapshot
python -m fde_workbench import my_snapshot.json
```
