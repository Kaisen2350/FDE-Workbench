# Paraguay Export Economy — FDE Workbench & Ontology

> **Mission**: Engineering, research, and operational control plane for Forward Deployed Engineers (FDE) modeling the physical reality of Paraguayan export-oriented enterprises.  
> **Key Docs**: [`README.md`](README.md), [`DESIGN.md`](DESIGN.md), [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md)

---

## 1. Domain Purpose & Operational Scope

- **Deterministic Control Plane**: Empirical evidence and physical reality (fluvial draft restrictions, Mercosur cross-border customs DNA, Maquila regimes, and cash conversion cycles).
- **Core Architecture Doctrine**:
  $$\text{FDE Control Plane} \longrightarrow \text{Platform Adapter} \longrightarrow \text{Customer Environment}$$
  Adapters exist for Google Gemini, Microsoft Azure, OpenAI, and Databricks Mosaic AI.
- **Local-First & Zero Cloud Coupling**: Runs on Python 3.11 with `pydantic` and `fastapi` with zero required external network calls.

---

## 2. Architecture & Tech Stack

```text
FDE/Ontology/
├── fde_workbench/            # Core Python package (models, ontology, adapters, web UI)
├── tests/                    # Automated test suite (unittest)
├── docs/                     # Architectural specs and deployment briefs
├── run_workbench.py          # Primary local server entrypoint
└── workbench.db              # SQLite persistence layer
```

---

## 3. Non-Negotiable Constraints & Guardrails

1. **State Machine Rule**: Agent-reported completion is non-authoritative. Only deterministic verification transitions a task from `EXECUTING` to `VERIFIED`.
2. **Deterministic Schemas**: Maintain strict Pydantic model validation. Do not bypass type validations.
3. **Evidence-First**: Every ontology node must link to grounded source evidence with explicit provenance.

---

## 4. Deterministic Verification & Completion Gates

* **Automated Unit Tests**: Execute `python -m unittest discover -s tests -p "test_*.py" -v` with 100% of tests passing.
* **Server Health Gate**: Run `python run_workbench.py` to confirm FastAPI service boots without runtime exceptions.
