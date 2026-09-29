# FDE Deployment Brief: Automated Export Customs Clearance & Tariff Reconciliation Pilot

> [!WARNING]
> **Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation**

**Target Enterprise**: Agro-Industrial del Este S.A. (AIDESA)  
**Pilot Identifier**: `pilot-2026-customs-recon` | **Status**: `PilotStatus.PROPOSED` | **Provenance**: `ProvenanceType.DERIVED`  
**Document Date**: September 29, 2026 | **Prepared By**: Forward Deployed Engineering (FDE)  

> **Executive Mandate**: This briefing document establishes the operational reality, economic equation, human governance boundary, and measurable acceptance criteria for a 30-day pilot deployment.

---

## 1. Operational Problem
*What is happening?*  

In the Export documentation review, SOFIA clearance pack compilation, and Mercosur NCM tariff classification workflow at Agro-Industrial del Este S.A. (AIDESA), manual execution creates severe latency and operational friction.

**Operational Baseline Focus Areas (Pending Field Calibration):**
- **Manual Prep Time Minutes**: `[ Pending field validation — see Section 4 ]`
- **Customs Error Rate Pct**: `[ Pending field validation — see Section 4 ]`
- **Border Dwell Hours**: `[ Pending field validation — see Section 4 ]`
- **Annual Delay Penalties Usd**: `[ Pending field validation — see Section 4 ]`
- ⚠️ Manual cycle time and administrative touch time per decision
- ⚠️ Current exception frequency across annual export shipment volume
- ⚠️ Direct cost per exception (truck demurrage, re-inspection fees, lightering, and delay penalties)

## 2. Empirical Evidence
*How do we know?*  

**Measurement & Audit Methodology**: Audit logs comparing timestamp of packing list availability vs SOFIA clearance receipt; weekly customs rectification tracker.

| Evidence ID | Source / System | Type | Provenance | Confidence | Empirical Claim |
|:---|:---|:---|:---|:---:|:---|
| `EVI-REF-01` | **Operational Field Telemetry & Disruption Log** | `ERP_RECORD` | `ProvenanceType.DERIVED` | 95% | *"Historical operational logs confirm Head of Customs Compliance & Foreign Trade (Jefe de Comercio Exterior) executes manual validations with elevated exception rate."* |

## 3. Decision Loop
*What decision is currently being made manually?*  

- **Manual Decision Point**: `Authorize dispatch and generate customs submission pack for dry grain / meal outbound trucks`
- **Accountable Decision Owner**: **Head of Customs Compliance & Foreign Trade (Jefe de Comercio Exterior)**
- **Operational Trigger**: Truck weigh-out event at facility terminal scale (scale_ticket_closed)
- **Escalation Trigger Model**: Evaluated on-demand via operator review sweep or automated hourly cron sweep calling `POST /api/decisions/check-escalations` (timeout threshold: 2.0 hours; does not rely on an unmonitored background daemon in local-first mode).

## 4. Economic Impact & ROI Equation
*What does the problem cost, and what does the solution yield?*  

> [!NOTE]
> **Values pending field validation — see operator interview.**
> Baseline figures, economic costs, and ROI projections are intentionally omitted in this calibration document to prevent anchoring bias during operator discovery interviews.

### Assumptions Ledger (Field Calibration)
| Parameter | Unit | Operational Prompt | Field Calibrated Value |
|:---|:---:|:---|:---:|
| **Annual decision volume** (`annual_decision_volume`) | decisions/year | *Annual outbound export volume (shipments / convoy departures per year)* | baseline: `_____` |
| **Manual effort minutes per decision** (`manual_effort_minutes_per_decision`) | minutes/decision | *Active manual touch time required per decision (not counting waiting time)* | baseline: `_____` |
| **Hourly labor cost usd** (`hourly_labor_cost_usd`) | USD/hour | *Fully-loaded hourly cost of the role performing this work (salary, benefits, overhead)* | baseline: `_____` |
| **Current error or exception rate** (`current_error_or_exception_rate`) | percentage | *Historical rate of serious clerical or physical exceptions requiring rework* | baseline: `_____` |
| **Cost per exception usd** (`cost_per_exception_usd`) | USD/exception | *Average direct & indirect cost per exception incident (demurrage, lightering, penalties)* | baseline: `_____` |
| **Target manual effort minutes** (`target_manual_effort_minutes`) | minutes/decision | *Estimated hands-on review time required with pre-compiled draft* | baseline: `_____` |
| **Target exception rate** (`target_exception_rate`) | percentage | *Target residual exception rate under automated pre-validation* | baseline: `_____` |
| **Pilot decision volume** (`pilot_decision_volume`) | decisions in pilot | *Planned shipment / convoy sample size for controlled pilot evaluation* | baseline: `_____` |
| **Pilot implementation cost usd** (`pilot_implementation_cost_usd`) | USD one-off | *One-off deployment engineering and connector integration fee* | baseline: `_____` |
| **Annual software subscription usd** (`annual_software_subscription_usd`) | USD/year | *Annual software runtime, model inference, and infrastructure subscription* | baseline: `_____` |
| **Working capital acceleration days** (`working_capital_acceleration_days`) | days | *Days reduction in clearance dwell time or fluvial cycle time* | baseline: `_____` |
| **Annual working capital financial value usd** (`annual_working_capital_financial_value_usd`) | USD/year carrying value | *Annual financial carrying cost savings on accelerated receivables or inventory* | baseline: `_____` |

## 5. Proposed AI Intervention
*What should AI actually do?*  

Pre-validate 4-way document cross-check, flag NCM classification mismatches, and prepare pre-filled SOFIA export dispatch declaration.

**Operational Context**: Mercosur trade corridor through Ciudad del Este / Foz do Iguaçu. Discrepancies between declared weight on CRT and scale ticket trigger physical red-channel customs inspection (Canal Rojo) causing 36-72 hour border demurrage.

**Processed Document Inputs:**
- `📄 Commercial Invoice (Factura de Exportación)`
- `📄 SENAVE Phytosanitary Certificate`
- `📄 Bill of Lading / CRT (Carta de Porte por Carretera)`
- `📄 Packing List with calibrated moisture & net weights`

## 6. Human Authority & Governance
*What remains under strict human control?*  

> [!IMPORTANT]
> **Mandatory Human-in-the-Loop Sign-Off**:  
> Jefe de Comercio Exterior must click 'Approve for SOFIA Transmission' in dashboard. Agent NEVER submits directly to DNA production.

**Permitted Agent Actions (Read-Only & Drafting):**
- `✓ Generate reconciled customs pack PDF`
- `✓ Post draft document bundle to SAP B1 staging table`
- `✓ Emit alert to customs broker on discrepancy > 0.5%`

**Rollback Condition / Kill Switch**:  
*If 2 consecutive shipments incur customs documentation discrepancies or manual intervention time exceeds baseline, pilot pauses to manual operator review immediately.*

**Safety Invariants:**
- 🛡️ No write access to production DNA SOFIA customs system
- 🛡️ Read-only access to SAP Business One financial journal entries
- 🛡️ All data stored and processed within encrypted regional boundary with no LLM model training on customer commercial data
- 🛡️ Audit guarantee: All human actions logged to append-only SHA-256 hash-chain (tamper-evident within current seeded database session; resets on database reseed).
- 🛡️ Decision timeout governance: Pending decisions escalate via on-demand sweep or scheduled cron webhook, maintaining determinism without unmonitored background daemons.

## 7. Required Data & Telemetry
*What systems and data are needed?*  

**Systems of Record & Feeds:**
- 💾 SAP Business One ERP (OINV, DLN1, OITM)
- 💾 DNA SOFIA Customs XML API
- 💾 Villeta & CDE Terminal Truck Scale Weight Slips (Báscula)
- 💾 SENAVE Phytosanitary Inspection Reports

**Required Integration Connectors:**
- 🔌 SAP Business One Service Layer (Read-Only)
- 🔌 DNA SOFIA Staging Sandbox (SOAP/XML Read-Only)
- 🔌 Postgres / Shared SMB Scale Ticket Folder

## 8. Architecture & Integration Pattern
*How will it integrate into customer infrastructure?*  

- **Integration Pattern**: **Sidecar Decision Engine with Human-in-the-Loop Gate**
- **Ingestion (Read Path)**: Read-only ingestion from ERP/TMS/Documents via webhook or poll
- **Evaluation (Reasoning)**: Deterministic validation against domain ontology + LLM fuzzy cross-document extraction
- **Execution (Action Path)**: Pre-filled rectification draft posted to operator queue; zero direct external mutation without human broker sign-off

## 9. Pilot Scope & Duration
*What gets deployed first?*  

- **Calendar Duration**: **30 days**
- **Deployment Boundary**: Consecutive outbound soy meal and oil export trucks passing through Ciudad del Este border (Pilot decision volume pending field validation — see Section 4)
- **FDE Engineering Effort**: 2 weeks configuration + 1 week shadow testing

## 10. Success & Acceptance Criteria
*What measurable result constitutes success?*  

**Target KPI Outcomes (Thresholds Pending Field Calibration):**
- **Manual Prep Time Minutes**: `[ Target threshold pending field validation — see Section 4 ]`
- **Customs Error Rate Pct**: `[ Target threshold pending field validation — see Section 4 ]`
- **Border Dwell Hours**: `[ Target threshold pending field validation — see Section 4 ]`
- **Annual Delay Penalties Usd**: `[ Target threshold pending field validation — see Section 4 ]`

**Rigorous Acceptance Criteria for Production Graduation (Qualitative Framework):**
- [ ] **><= validated target rate of test shipments processed in < validated target minutes**
- [ ] **Zero Canal Rojo (red-channel) inspections caused by clerical documentation discrepancy**
- [ ] **Mandatory human sign-off on all decisions recorded with tamper-evident audit hash (within current database session)**

## 11. Enterprise Platform Options
*Which technology stacks can run this blueprint?*  

The pilot blueprint is **platform-agnostic**. The operational domain logic remains identical across any of the following enterprise execution substrates:

| Platform Ecosystem | Core Engine / Models | Tool Execution Mechanism | Grounding Data Substrate |
|:---|:---|:---|:---|
| **Google Cloud / Gemini Enterprise** **(Selected)** | `Vertex AI Agent Engine (gemini-2.5-flash / gemini-2.5-pro)` | Typed OpenAPI (JSON Schema) / GenAI SDK function declarations | Vertex AI Search over regulatory customs tariffs & SOPs |
| **Microsoft Azure AI Foundry** | `Azure OpenAI Service (GPT-4o / 4o-mini) + Semantic Kernel` | Native C# / Python Semantic Kernel Plugins with RequiresConsent policy | Azure AI Search with integrated vector index |
| **OpenAI Enterprise** | `Assistants API v2` | Strict JSON Schema function calling (strict: true) | File Search vector storage over transit documents |
| **Databricks Mosaic AI** | `Mosaic AI Agent Framework & Model Serving` | Unity Catalog three-tier registered functions (catalog.schema.tool) | Unity Catalog Vector Search |

## 12. Expansion Path & Flywheel Leverage
*What adjacent workflow becomes possible if the pilot works?*  

**Immediate Expansion Horizon**:  
Automated Fluvial Barge Convoy Transit Manifests (Villeta to Nueva Palmira)

**FDE Flywheel**: *Deploy Pilot -> Measure Hard Dollar ROI -> Expand to Adjacent Workflows -> Compound Enterprise Moat.*
