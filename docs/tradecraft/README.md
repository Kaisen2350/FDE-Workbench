# Forward Deployed Engineering (FDE) — Field Tradecraft & Operational Patterns

> **Applied FDE Tradecraft**: A field-tested engineering sequence bridging physical operations, typed domain ontologies, human calibration, deterministic control planes, and enterprise platform substrates.

---

## The FDE Deployment Loop

```mermaid
flowchart TD
    A["<b>1. PHYSICAL REALITY</b><br/>Fluvial draft, border dwell, physical assets"] --> B["<b>2. DOMAIN ONTOLOGY</b><br/>24 typed entities, explicit provenance"]
    B --> C["<b>3. OPERATOR DISCOVERY</b><br/>Assumption-stripped interview protocols"]
    C --> D["<b>4. DETERMINISTIC CONTROL</b><br/>State gates & SHA-256 audit chain"]
    D --> E["<b>5. EVALUATION & OBSERVABILITY</b><br/>Accuracy, safety, p95 latency, cost/task"]
    E --> F["<b>6. AUDITABLE ECONOMIC BRIDGE</b><br/>10-step formula linking friction to EBITDA"]
    F --> G["<b>7. MULTI-PLATFORM SUBSTRATES</b><br/>Gemini · Azure · OpenAI · Databricks"]
    G --> H["<b>8. FIELD DEPLOYMENT & FEEDBACK</b><br/>Human authority sign-off & telemetry loop"]
    H -.-> A
```

| Tradecraft Guide | Core Operational Question | Key Field Artifacts | Executable Verification |
|---|---|---|---|
| [**01. Physical Reality & Domain Ontologies**](01-domain-ontologies.md) | *How do we model real-world physical friction instead of lagging paperwork?* | 24-Entity Taxonomy, Provenance Enums, Critical Path | `tests/test_ontology.py` |
| [**02. Discovery Intake & Operator Calibration**](02-operator-discovery.md) | *How do we extract ground truth from operators without confirmation bias?* | Intake Dossier, Operator Interview Kit, 4D Prioritization | `python -m fde_workbench discover` |
| [**03. Deterministic Control & Governance**](03-deterministic-control.md) | *Why must agent-reported completion be non-authoritative?* | 5-Stage Decision Pipeline, SHA-256 Audit Chain, Escalations | `python -m fde_workbench verify-audit` |
| [**04. The Economic Bridge & ROI Equations**](04-economic-bridges.md) | *How do we translate operational friction into an auditable financial equation?* | 10-Step Economic Model, 12-Section Briefs, Payback Period | `python run_workbench.py pilot economics` |
| [**05. Multi-Platform Enterprise Substrates**](05-platform-adapters.md) | *How do we deploy to Azure, Gemini, OpenAI, or Databricks without rewriting logic?* | Google Vertex AI, Azure AI Foundry, OpenAI, Databricks Mosaic | `tests/test_adapters.py` |

---

## Synthetic Deployment Cases

* [**Customs Reconciliation Case**](../../case-studies/customs-reconciliation/README.md) — *223.5% Net ROI, 1.7 mo Payback on BR-277 border corridor.*
* [**Fluvial Convoy Allocation Case**](../../case-studies/fluvial-convoy/README.md) — *620.4% Net ROI, 0.8 mo Payback under low-water draft restrictions.*
