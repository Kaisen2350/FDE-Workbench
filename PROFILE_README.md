# Felix Peña
### Forward Deployed Engineer | Applied AI · Enterprise Integration · Operational Systems

> I build the connective tissue between AI systems and operational reality.

[FDE Workbench](https://github.com/kaisen2350/fde-workbench) · [Case Studies](https://github.com/kaisen2350/fde-workbench/tree/main/case-studies) · [Field Tradecraft](https://github.com/kaisen2350/fde-workbench/tree/main/docs/tradecraft) · [Contact](#contact)

---

## Proof Architecture

* **01 — Discover**: Turn ambiguous operator problems into typed requirements and assumption-stripped calibration protocols.
* **02 — Model**: Represent physical and operational reality explicitly (river draft, axle weight, customs DNA, explicit provenance).
* **03 — Integrate**: Ingest messy legacy systems (dirty TMS exports, Spanish dates/commas) into strongly typed domain entities.
* **04 — Control**: *"Agent-reported completion is non-authoritative."* Enforce deterministic state gates, human authority boundaries, and SHA-256 audit trails.
* **05 — Evaluate**: Benchmark across 50 realistic operational edge cases, measuring task success, schema validity, and enforcing 0 unauthorized actions.
* **06 — Observe**: Fine-grained span telemetry tracking p50/p95 latency and token costs, cleanly separated from compliance audit chains.
* **07 — Economize**: Bridge technical cycle-time reductions directly to EBITDA savings, working capital acceleration, and payback months.
* **08 — Deploy**: Decouple domain control planes from enterprise cloud execution substrates (Vertex AI, Azure AI, OpenAI, Databricks).

---

## Selected Work

* [**FDE Workbench (Flagship Monorepo)**](https://github.com/kaisen2350/fde-workbench)  
  Executable control plane for deploying AI into messy operational environments. Built in Python 3.11 / Pydantic v2 / FastAPI with **78 automated tests**, **6 deterministic verification gates**, and zero external network coupling.
* [**Synthetic Deployment Case 1: Customs Reconciliation**](https://github.com/kaisen2350/fde-workbench/tree/main/case-studies/customs-reconciliation)  
  BR-277 border corridor: 4-way document cross-check and SOFIA dispatch reconciliation. **223.5% Net 1st-Year ROI**, **1.7-month payback**.
* [**Synthetic Deployment Case 2: Fluvial Convoy Draft Optimizer**](https://github.com/kaisen2350/fde-workbench/tree/main/case-studies/fluvial-convoy)  
  Paraguay River Hidrovía: Dynamic draft allocation under shallow pass restrictions (*Paso Queso*). **620.4% Net 1st-Year ROI**, **0.8-month payback**.
* [**Legacy Enterprise TMS Connector**](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/integrations/legacy_connector.py)  
  Connective tissue normalizing messy Latin CSV exports (comma decimals, Spanish dates, noisy carrier plates) into typed domain entities.
* [**AI Evaluation Harness & Observability Telemetry**](https://github.com/kaisen2350/fde-workbench/tree/main/fde_workbench/evals)  
  Benchmark evaluation across 50 operational cases tracking task accuracy, p95 latency, token cost, and enforcing **0 unauthorized actions**.

---

## The FDE Deployment Loop

```mermaid
flowchart LR
    A["<b>1. Discover</b><br/>Calibration"] --> B["<b>2. Model</b><br/>Ontology"]
    B --> C["<b>3. Integrate</b><br/>Legacy Silos"]
    C --> D["<b>4. Control</b><br/>State Gates"]
    D --> E["<b>5. Evaluate</b><br/>Benchmarks"]
    E --> F["<b>6. Observe</b><br/>Telemetry"]
    F --> G["<b>7. Economize</b><br/>EBITDA Bridge"]
    G --> H["<b>8. Deploy</b><br/>Adapters"]
```

---

## 60-Second Quickstart

```bash
# Clone & run deterministic test suite (78 tests, all green)
git clone https://github.com/kaisen2350/fde-workbench.git
cd fde-workbench
pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py" -v

# Run AI evaluation harness & safety invariants
python run_workbench.py eval

# Inspect live observability & latency telemetry
python run_workbench.py telemetry

# Calculate enterprise pilot economics
python run_workbench.py pilot economics pilot-2026-fluvial-draft

# Launch local control plane UI
python run_workbench.py
```

---

## Contact
- **Email**: [kaisentrading@gmail.com](mailto:kaisentrading@gmail.com)
- **LinkedIn**: [linkedin.com/in/felixpenamelgarejo](https://www.linkedin.com/in/felixpenamelgarejo/)
- **Location**: Asunción, Paraguay / Available globally for embedded enterprise engagements
