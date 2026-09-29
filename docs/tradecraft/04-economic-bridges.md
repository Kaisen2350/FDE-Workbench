# FDE Curriculum Module 4: The Economic Bridge & Executive Value Translation

> *"Engineers talk about latency, tokens, and model accuracy. CFOs and COOs care about working capital drag, exception expenses, and EBITDA payback. An FDE builds the mathematical bridge between the two."*

---

## 1. Why Technical Demos Fail to Close

A common failure mode of applied AI engineers is showing an impressive technical demo (e.g., an OCR model parsing a bill of lading with 98% accuracy) and expecting the enterprise to sign an agreement.

Executive buyers do not buy technology; they buy **de-risked financial outcomes**:
- How much cash does this free up from our working capital cycle?
- What happens when the model makes a mistake, and who pays for it?
- In how many months do we break even on the implementation cost?

An FDE translates operational telemetry directly into an **Auditable Economic Bridge**.

---

## 2. The 10-Step Mathematical Economic Model

In the `fde-workbench`, every pilot is evaluated using the formal `PilotEconomicModel` (`fde_workbench/domain/pilots.py`):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE 10-STEP ECONOMIC BRIDGE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Baseline Labor       = (Annual Volume × Minutes / 60) × Loaded Hourly Rate │
│ 2. Baseline Exceptions  = (Annual Volume × Exception Rate) × Incident Cost  │
│ 3. Working Capital Drag = Quantified carrying cost of delayed inventory/cash │
│ 4. Total Baseline Cost  = Labor + Exceptions + Working Capital Drag         │
│ 5. Target Cost          = Post-intervention labor + exception run-rate      │
│ 6. Addressable Savings  = Baseline Total Cost - Target Total Cost           │
│ 7. Unit Cost Delta      = Addressable Savings / Annual Volume               │
│ 8. Total 1st-Yr Invest  = Implementation Cost + Annual Software License     │
│ 9. Net 1st-Year ROI ($) = Addressable Savings - Total 1st-Year Investment   │
│10. Payback Period (mo)  = Implementation Cost / (Addressable Savings / 12)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### LaTeX Formalization
$$\text{Baseline Total} = \left(\frac{V \times M_{\text{base}}}{60} \times R\right) + (V \times E_{\text{base}} \times C_{\text{exc}}) + W_{\text{drag}}$$

$$\text{Net 1st-Year ROI (\%)} = \left(\frac{\text{Addressable Savings} - \text{Total Investment}}{\text{Total Investment}}\right) \times 100$$

$$\text{Payback Period (months)} = \frac{\text{Implementation Cost}}{\text{Addressable Savings} / 12}$$

---

## 3. Two Production Pilot Case Studies

The workbench instantiates two canonical enterprise pilots with rigorous hand-verified economics:

### Case Study A: Export Customs Clearance & Tariff Reconciler (`pilot-2026-customs-recon`)
* **Operational Scope**: Outbound soy meal and oil trucks transiting Ciudad del Este to Foz do Iguaçu (BR-277).
* **Friction**: 14 min manual doc compile per truck; 6.5% documentation mismatch exception rate causing \$850 in demurrage/storage; \$22,000 working capital drag.
* **Economic Result**:
  - Annual Volume: 2,400 shipments
  - Addressable Savings: **\$106,750 / year**
  - Investment: \$15,000 implementation + \$18,000 annual license
  - **Net 1st-Year ROI: 223.5% (\$73,750 net value)**
  - **Payback Period: 1.7 months**

### Case Study B: Hidrovía Dynamic Convoy Draft Optimizer (`pilot-2026-fluvial-draft`)
* **Operational Scope**: 16-barge push convoys during low-water river draft restrictions at critical passes (*Paso Queso*, *Paso Bermejo*).
* **Friction**: 45 min convoy planning cycle; 8.0% draft miscalculation rate causing grounding risk / emergency lightering (\$18,500/incident); \$15,000 working capital drag.
* **Economic Result**:
  - Annual Volume: 240 push-convoys
  - Addressable Savings: **\$331,400 / year**
  - Investment: \$22,000 implementation + \$24,000 annual license
  - **Net 1st-Year ROI: 620.4% (\$285,400 net value)**
  - **Payback Period: 0.8 months**

---

## 4. The 12-Section Client-Ready Deployment Brief

An FDE packages findings into an executive briefing document (`FDEBriefGenerator`) adhering to the **12-Section Standard**:

1. **Operational Problem**: Physical bottlenecks and business friction.
2. **Empirical Evidence**: Weighbridge tickets, hydrometric bulletins, customs logs.
3. **Decision Loop**: The 5-stage state transition pipeline.
4. **Economic Impact & ROI Equation**: The complete 10-step auditable bridge.
5. **Proposed AI Intervention**: Specifically what model runs where.
6. **Human Authority & Governance**: Mandatory sign-off role and rollback trigger.
7. **Required Data & Telemetry**: Systems of record (SAP B1, TMS, VUE) and APIs.
8. **Architecture & Integration Pattern**: Platform adapter topology.
9. **Pilot Scope & Duration**: Number of units tested (e.g. 100 trucks or 6 convoys).
10. **Success & Acceptance Criteria**: Quantitative gates for production cutover.
11. **Enterprise Platform Options**: Gemini, Azure, OpenAI, and Databricks specs.
12. **Expansion Path & Flywheel Leverage**: Post-pilot phase expansion.

---

## 5. Hands-on Lab: Computing Economics & Exporting Briefs

### 1. Compute Economic Bridges via CLI
```bash
python run_workbench.py pilot economics pilot-2026-customs-recon
python run_workbench.py pilot economics pilot-2026-fluvial-draft
```

### 2. Generate a Complete 12-Section Client Brief
```bash
python run_workbench.py pilot brief pilot-2026-customs-recon --export brief.md
```

### 3. Verify Mathematical Sensitivity Tests
Run unit tests verifying Low (-20%), Mid (Base), and High (+20%) scenarios:
```bash
python -m unittest tests/test_pilots.py -v
```

---

## Key Takeaways for the FDE
1. **Never pitch an algorithm without a financial equation**: Link model metrics directly to P&L savings.
2. **Always include working capital carrying costs**: Inventory held up in queues represents tied-up cash that executive leadership understands immediately.
3. **Deliver standardized 12-section briefs**: Provide the executive sponsor with everything they need to approve the pilot internally.
