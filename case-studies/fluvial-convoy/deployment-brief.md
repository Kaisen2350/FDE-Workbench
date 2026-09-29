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

**Observed Operational Baseline:**
- **Convoy Draft Utilization Pct**: `81.4`
- **Alijo Lightering Incidents Annual**: `4.0`
- **Avg Immersion Safety Margin Inches**: `24.0`
- **Annual Lost Freight And Alijo Usd**: `164000.0`
- ⚠️ Manual cycle time: 45.0 minutes per decision
- ⚠️ Current exception rate: 8.0% across 240 annual decisions
- ⚠️ Direct cost per exception: $18,500.00 in demurrage, re-inspection, and delay penalties

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

```text
Baseline Annual Cost:          $  377,400.00  (Labor: $7,200.00 + Exceptions: $355,200.00)
Target Annual Post-Pilot:      $   46,000.00
--------------------------------------------------------------------------------
Addressable Annual Savings:    $  331,400.00 / year
Implementation Cost:           $   22,000.00  (One-time engineering & deployment)
Annual Software License:       $   24,000.00  (Subscription runtime)
Total 1st-Year Investment:     $   46,000.00  (Implementation + License)
--------------------------------------------------------------------------------
Net 1st-Year ROI ($):          $  285,400.00  (Savings - Total Investment)
ROI %:                                 620.4%  (Net 1st-Year ROI / Total Investment * 100)
Capital Payback Period:                  0.8 months
Pilot Batch Measured Value:    $   33,140.00  (During controlled pilot scope)
```

### Assumptions Ledger
| Parameter | Baseline Value | Unit | Operational Source / Rationale |
|:---|:---:|:---|:---|
| `annual_decision_volume` | **240** | decisions/year | *240 push-boat convoy barge departures/year from Villeta terminal along Hidrovía Paraguay-Paraná.* |
| `manual_effort_minutes_per_decision` | **45.0** | minutes/decision | *45.0 minutes manual calculation per convoy across barge hydrostatic tables, draft gauges, and shoal forecasts.* |
| `hourly_labor_cost_usd` | **40.0** | USD/hour | *$40.00 blended rate for Senior Terminal Operations Director and Naval Logistics Captain.* |
| `current_error_or_exception_rate` | **8.0%** | percentage | *8.0% historical rate of convoy grounding risk or sub-optimal loading resulting in emergency alijo (lightering).* |
| `cost_per_exception_usd` | **18500.0** | USD/exception | *$18,500 direct cost per lightering incident (chartering auxiliary crane barge, lost days, demurrage penalties).* |
| `target_manual_effort_minutes` | **10.0** | minutes/decision | *10.0 minutes review and sign-off on AI-optimized multi-barge draft distribution plan.* |
| `target_exception_rate` | **1.0%** | percentage | *1.0% residual risk under conservative hydrological safety margin constraints.* |
| `pilot_decision_volume` | **24** | decisions in pilot | *24 push-boat convoy dispatches during 60-day low-water window.* |
| `pilot_implementation_cost_usd` | **22000.0** | USD one-off | *$22,000 fixed FDE deployment covering telemetry pipeline integration and sonar depth calibration.* |
| `annual_software_subscription_usd` | **24000.0** | USD/year | *$24,000 annual subscription for hydrographic simulation and multi-sensor predictive draft model.* |
| `working_capital_acceleration_days` | **2.0** | days | *2.0 days faster river transit cycle time resulting from elimination of grounding delays.* |
| `annual_working_capital_financial_value_usd` | **15000.0** | USD/year carrying value | *$15,000 financial savings on tied-up fluvial freight inventory.* |

### Sensitivity Analysis (±20% Sensitivity Range)
| Scenario | Volume | Touch Time | Residual Errors | Annual Savings | Net 1st-Year ROI ($) | Net ROI (%) | Payback |
|:---|:---:|:---|:---|:---:|:---:|:---:|:---:|
| **Low (Conservative -20%)** | 192 | 12.0m | 1.2% | $257,760.00 | $211,760.00 | **460.3%** | 1.0 mo |
| **Mid (Base Case)** | 240 | 10.0m | 1.0% | $331,400.00 | $285,400.00 | **620.4%** | 0.8 mo |
| **High (Optimistic +20%)** | 288 | 8.0m | 0.8% | $408,720.00 | $362,720.00 | **788.5%** | 0.6 mo |

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
- **Deployment Boundary**: 6 consecutive outbound push-convoys (approx. 72 total barge transits) during low-water season (24 decisions / shipments)
- **FDE Engineering Effort**: 3 weeks integration + 2 weeks shadow verification

## 10. Success & Acceptance Criteria
*What measurable result constitutes success?*  

**Target KPI Outcomes:**
- **Convoy Draft Utilization Pct**: `92.5`
- **Alijo Lightering Incidents Annual**: `0.0`
- **Avg Immersion Safety Margin Inches**: `13.5`
- **Annual Lost Freight And Alijo Usd**: `32000.0`

**Rigorous Acceptance Criteria for Production Graduation:**
- [ ] **Zero barge groundings or emergency lighterings (alijo)**
- [ ] **>= 8% increase in cargo payload per convoy without safety violations**
- [ ] **100% compliance with Naval Prefecture draft advisories**

## 11. Enterprise Platform Options
*Which technology stacks can run this blueprint?*  

The pilot blueprint is **platform-agnostic**. The operational domain logic remains identical across any of the following enterprise execution substrates:

| Platform Ecosystem | Core Engine / Models | Tool Execution Mechanism | Grounding Data Substrate |
|:---|:---|:---|:---|
| **Google Cloud / Gemini Enterprise** **(Selected)** | `Vertex AI Agent Engine (gemini-2.5-flash / gemini-2.5-pro)` | Typed OpenAPI 3.0 / GenAI SDK function declarations | Vertex AI Search over regulatory customs tariffs & SOPs |
| **Microsoft Azure AI Foundry** | `Azure OpenAI Service (GPT-4o / 4o-mini) + Semantic Kernel` | Native C# / Python Semantic Kernel Plugins with RequiresConsent policy | Azure AI Search with integrated vector index |
| **OpenAI Enterprise** | `Assistants API v2` | Strict JSON Schema function calling (strict: true) | File Search vector storage over transit documents |
| **Databricks Mosaic AI** | `Mosaic AI Agent Framework & Model Serving` | Unity Catalog three-tier registered functions (catalog.schema.tool) | Unity Catalog Vector Search |

## 12. Expansion Path & Flywheel Leverage
*What adjacent workflow becomes possible if the pilot works?*  

**Immediate Expansion Horizon**:  
Dynamic Fleet Routing & Fuel Consumption Optimization across Lower Paraná

**FDE Flywheel**: *Deploy Pilot -> Measure Hard Dollar ROI -> Expand to Adjacent Workflows -> Compound Enterprise Moat.*
