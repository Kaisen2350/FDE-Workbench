# FDE Curriculum Module 2: Enterprise Discovery & Operator Calibration

> *"If you ask an enterprise client what they want built, they will describe faster horses or automated spreadsheets. An FDE maps the friction, calibrates the numbers against live operators, and prioritizes by economic leverage."*

---

## 1. The FDE Discovery Philosophy

Forward Deployed Engineering begins before writing code. When entering an enterprise:
1. **Never accept reported metrics as ground truth**: Self-reported cycle times are almost always understated; error rates are underreported due to organizational shame or lack of instrumentation.
2. **Distinguish complaints from bottlenecks**: A process that causes loud frustration may have minimal economic impact, while a silent reconciliation delay may tie up \$30M in working capital.
3. **Calibrate without confirmation bias**: Showing an operator your financial model produces compliance; asking open-ended operational questions produces calibration.

---

## 2. Canonical Discovery Intake Schema

The intake process is formalized in a structured JSON dossier schema (`DiscoveryIntake`), modeled in `fde_workbench/domain/discovery.py`:

```json
{
  "company_profile": {
    "name": "Agro-Industrial del Este S.A. (AIDESA)",
    "headcount": 250,
    "facilities": ["Planta Fluvial Villeta", "Planta Maquila Hernandarias"],
    "systems_of_record": ["SAP Business One", "Trans-Chaco TMS", "VUE / SOFIA"]
  },
  "critical_workflows": [
    "Fluvial Push-Convoy Export Clearing (Hidrovía)",
    "Terrestrial Bitren Border Clearance (CDE - Foz do Iguaçu)"
  ],
  "bottlenecks": [
    "Low-water river draft gauge variance causing unexpected lightering",
    "Border customs documentation mismatches and dwell time penalties"
  ]
}
```

The intake is programmatically compiled by the **`DiscoveryTransformationEngine`**, which parses the intake JSON, instantiates entities, generates relationships, and infers high-impact AI candidate opportunities.

```bash
python -m fde_workbench discover --intake aidesa_discovery_intake.json
```

---

## 3. The Operator Interview & Calibration Kit

The greatest risk in enterprise pilot scoping is that your economic model is based on "placeholders dressed up as facts." The FDE uses the **Operator Calibration Kit** (`docs/OPERATOR_INTERVIEW_KIT.md`) to stress-test every assumption with front-line practitioners.

### The Cardinal Rule of Discovery
> **Do not lead with the model's numbers.**  
> If you say, *"We estimate customs exceptions happen 6.5% of the time and cost \$850, is that right?"*, the operator will nod.  
> If you ask, *"Out of 100 outbound trucks, how many get stuck in red channel, and what does the detention bill actually look like when that happens?"*, you will get the unvarnished reality.

### The Assumption-Stripped Leave-Behind Pattern
When leaving materials with enterprise sponsors, generate an **Assumption-Stripped Brief**:
- Shows the workflow sequence.
- Shows the decision points and approval gates.
- Shows the *structure* of the economic equations ($Cost = Labor + Exceptions + Drag$).
- **Strips all numerical values**, leaving blanks for the operator to fill in from their actual accounts.

```bash
# Generate the assumption-stripped calibration brief via CLI
python run_workbench.py pilot calibration-brief pilot-2026-customs-recon --export docs/briefs/calibration-customs.md
```

---

## 4. Multi-Dimensional FDE Opportunity Prioritization

Rather than assigning an arbitrary "AI score", an FDE scores enterprise opportunities across **4 distinct operational dimensions** (1–10 scale):

```
┌────────────────────────────────────────────────────────────┐
│              4-DIMENSIONAL FDE EVALUATION                  │
├────────────────────────────────────────────────────────────┤
│ 1. Economic Leverage      (Annual Payoff, Cash Drag, ROI)  │
│ 2. Operational Dynamics   (Volume, Telemetry, Error Cost)  │
│ 3. Deployment Feasibility (System Friction, HITL, Regs)   │
│ 4. Strategic Value        (Executive Buy-in, Corridor DNA) │
└────────────────────────────────────────────────────────────┘
```

```python
# Evaluated in fde_workbench.domain.prioritization
score = (
    0.35 * economic_leverage +
    0.25 * operational_dynamics +
    0.20 * deployment_feasibility +
    0.20 * strategic_value
)
```

Opportunities that exceed the threshold and demonstrate actionable feasibility are designated as **`candidate_for_pilot: true`**, advancing to formal `PilotSpecification` authoring.

---

## 5. Hands-on Lab: Running Discovery & Prioritization

### 1. Ingest an Enterprise Intake Dossier
```bash
python -m fde_workbench discover --intake aidesa_discovery_intake.json
```

### 2. Inspect Inferred Opportunities in the Workbench UI
* Launch `python run_workbench.py`
* Navigate to **Tab 9: AI Opportunities**
* Observe the 4-dimensional score breakdown bars and candidate flags.

### 3. Generate a Calibration Script for a Fleet Captain
```bash
python run_workbench.py pilot calibration-brief pilot-2026-fluvial-draft --export calibration_script.md
```
Open `calibration_script.md` and verify that the numeric placeholders are completely stripped, ready for a discovery session.

---

## Key Takeaways for the FDE
1. **Requirements are extracted, not received**: Front-line operators know the friction; executives know the pain. An FDE bridges the two.
2. **Use the assumption-stripped pattern**: Protect your models from confirmation bias.
3. **Prioritize along 4 dimensions**: Economic leverage alone is useless if deployment friction is insurmountable.
