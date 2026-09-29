# FDE Deployment Brief: Hidrovía Dynamic Convoy Draft & Loading Allocation Pilot

> [!WARNING]
> **Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation**

**Target Enterprise**: Agro-Industrial del Este S.A. (AIDESA)  
**Pilot Identifier**: `pilot-2026-fluvial-draft` | **Status**: `PilotStatus.PROPOSED` | **Provenance**: `ProvenanceType.DERIVED`  
**Document Date**: September 29, 2026 | **Prepared By**: Forward Deployed Engineering (FDE)  

> **Executive Mandate**: This briefing document establishes the operational reality, economic equation, human governance boundary, and measurable acceptance criteria for a 30-day pilot deployment.

---

## 1. Operational Problem
*What is happening?*  

In the Daily barge loading plan, convoy draft optimization, and critical river pass immersion calculation workflow at Agro-Industrial del Este S.A. (AIDESA), manual execution creates severe latency and operational friction.

**Operational Baseline Focus Areas (Pending Field Calibration):**
- **Convoy Draft Utilization Pct**: `[ Pending field validation — see Section 4 ]`
- **Alijo Lightering Incidents Annual**: `[ Pending field validation — see Section 4 ]`
- **Avg Immersion Safety Margin Inches**: `[ Pending field validation — see Section 4 ]`
- **Annual Lost Freight And Alijo Usd**: `[ Pending field validation — see Section 4 ]`
- ⚠️ Manual cycle time and administrative touch time per decision
- ⚠️ Current exception frequency across annual export shipment volume
- ⚠️ Direct cost per exception (truck demurrage, re-inspection fees, lightering, and delay penalties)

## 2. Empirical Evidence
*How do we know?*  

**Measurement & Audit Methodology**: Comparison of actual hydrographic sonar survey readings vs predicted draft at Paso Queso; post-voyage barge outturn manifests.

| Evidence ID | Source / System | Type | Provenance | Confidence | Empirical Claim |
|:---|:---|:---|:---|:---:|:---|
| `EVI-REF-01` | **Operational Field Telemetry & Disruption Log** | `ERP_RECORD` | `ProvenanceType.DERIVED` | 95% | *"Historical operational logs confirm Fluvial Fleet Captain & Terminal Operations Director executes manual validations with elevated exception rate."* |

## 3. Decision Loop
*What decision is currently being made manually?*  

- **Manual Decision Point**: `Authorize metric tons loaded per barge and approve push-boat convoy formation at Villeta terminal`
- **Accountable Decision Owner**: **Fluvial Fleet Captain & Terminal Operations Director**
- **Operational Trigger**: Daily 06:00 AM hydrometric water level publication and convoy arrival notification
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

Compute optimal cargo distribution across 12-barge convoy to maximize payload while maintaining strict 12-inch under-keel clearance at bottleneck passes.

**Operational Context**: Low water levels on the Paraguay-Paraná river (Paso Queso, Paso Carpinchero) severely restrict allowable barge draft. Underloading leaves money on the table (dead freight), while overloading risks grounding, canal blockage, and catastrophic lightering (alijo) costs.

**Processed Document Inputs:**
- `📄 Daily river stage readings at Asunción, Villeta, Alberdi, Pilar, Corrientes`
- `📄 Grain batch moisture and specific gravity assays`
- `📄 Barge hydrostatic immersion tables (feet/inch per 100 MT)`

## 6. Human Authority & Governance
*What remains under strict human control?*  

> [!IMPORTANT]
> **Mandatory Human-in-the-Loop Sign-Off**:  
> Fleet Captain and Terminal Operations Director joint digital sign-off before conveyor belt loading commences.

**Permitted Agent Actions (Read-Only & Drafting):**
- `✓ Publish Convoy Loading Plan to Terminal Villeta SCADA`
- `✓ Issue Navigational Advisory to Tugboat Master`
- `✓ Alert Commercial Desk on available incremental spot freight capacity`

**Rollback Condition / Kill Switch**:  
*If any barge draft exceeds target maximum minus 6 inches safety buffer, or captain flags navigation safety concern, immediately revert to conservative static tables.*

**Safety Invariants:**
- 🛡️ Strict 12-inch under-keel clearance (UKC) invariant — model cannot override safety threshold
- 🛡️ Loading speed capped at terminal conveyor maximum
- 🛡️ Audit guarantee: All human actions logged to append-only SHA-256 hash-chain (tamper-evident within current seeded database session; resets on database reseed).
- 🛡️ Decision timeout governance: Pending decisions escalate via on-demand sweep or scheduled cron webhook, maintaining determinism without unmonitored background daemons.

## 7. Required Data & Telemetry
*What systems and data are needed?*  

**Systems of Record & Feeds:**
- 💾 Prefectura General Naval Hydrometric Gauge Network
- 💾 Asunción & Villeta Daily Gauge Reports
- 💾 Terminal Villeta Silo Weighbridge & Conveyor Belt Telemetry
- 💾 Hidrovías del Sur Push-Boat Convoy GPS & Sonar Feeds

**Required Integration Connectors:**
- 🔌 Naval Prefecture Hydrographic Bulletin RSS/PDF scraper
- 🔌 TMS Fluvial Dispatch module
- 🔌 Villeta Terminal Silo PLC / SCADA interface (Read-Only)

## 8. Architecture & Integration Pattern
*How will it integrate into customer infrastructure?*  

- **Integration Pattern**: **Sidecar Decision Engine with Human-in-the-Loop Gate**
- **Ingestion (Read Path)**: Read-only ingestion from ERP/TMS/Documents via webhook or poll
- **Evaluation (Reasoning)**: Deterministic validation against domain ontology + LLM fuzzy cross-document extraction
- **Execution (Action Path)**: Pre-filled rectification draft posted to operator queue; zero direct external mutation without human broker sign-off

## 9. Pilot Scope & Duration
*What gets deployed first?*  

- **Calendar Duration**: **45 days**
- **Deployment Boundary**: Consecutive outbound push-convoys (approx. 72 total barge transits) during low-water season (Pilot decision volume pending field validation — see Section 4)
- **FDE Engineering Effort**: 3 weeks integration + 2 weeks shadow verification

## 10. Success & Acceptance Criteria
*What measurable result constitutes success?*  

**Target KPI Outcomes (Thresholds Pending Field Calibration):**
- **Convoy Draft Utilization Pct**: `[ Target threshold pending field validation — see Section 4 ]`
- **Alijo Lightering Incidents Annual**: `[ Target threshold pending field validation — see Section 4 ]`
- **Avg Immersion Safety Margin Inches**: `[ Target threshold pending field validation — see Section 4 ]`
- **Annual Lost Freight And Alijo Usd**: `[ Target threshold pending field validation — see Section 4 ]`

**Rigorous Acceptance Criteria for Production Graduation (Qualitative Framework):**
- [ ] **Zero barge groundings or emergency lighterings (alijo)**
- [ ] **Material percentage increase (target % pending field calibration) in cargo payload per convoy without safety violations**
- [ ] **100% compliance with Naval Prefecture draft advisories**

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
Dynamic Fleet Routing & Fuel Consumption Optimization across Lower Paraná

**FDE Flywheel**: *Deploy Pilot -> Measure Hard Dollar ROI -> Expand to Adjacent Workflows -> Compound Enterprise Moat.*
