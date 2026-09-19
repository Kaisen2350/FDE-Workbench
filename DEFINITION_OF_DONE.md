# Definition of Done (DoD)
## FDE Reasoning & Control Plane — Phase 3.7 Boundary Specification

> **Purpose**: This document establishes the permanent, non-negotiable architectural and verification invariants of the Forward Deployed Engineering (FDE) Reasoning and Control Plane. It marks the formal conclusion of internal synthesis, hardening, and verification passes (Phases 1, 2, 3, 3.5, 3.6, and 3.7). Future engineering effort beyond Phase 3.7 is strictly driven by live customer pilot engagements and field feedback, rather than speculative internal expansion.

---

## The 6 Core Invariants

### Invariant 1: Automated Test Suite & Zero-Regression Baseline
* **Standard**: 100% test pass rate across all domain, synthetic generator, SQLite storage, API, and platform adapter test suites.
* **Current Measure**: **69 tests passing** (`Ran 69 tests in ~1.8s`, `OK`).
* **Enforcement Rule**: Any PR, commit, or modification that breaks or skips any of the 69 tests violates the Definition of Done.
* **Verification Command**:
  ```powershell
  python -m unittest discover -s tests -p "test_*.py" -v
  ```

---

### Invariant 2: Cryptographic Tamper-Evident Audit Chain
* **Standard**: Every operational event, entity mutation, decision lifecycle transition, and escalation is recorded in an append-only, SHA-256 hash-chained audit ledger.
* **Scope & Bound**: Tamper-evident guarantee covers all state transitions within the current active database session from initial genesis block (`0` * 64). Explicit database re-seeding safely re-initializes the genesis block.
* **Current Measure**: **281 verified entries**, unbroken hash-chain, head hash verified.
* **Enforcement Rule**: `verify_audit_chain()` must return `valid: True` and `broken_at: None`.
* **Verification Command**:
  ```powershell
  python run_workbench.py verify-audit
  ```

---

### Invariant 3: Four Enterprise Platform Adapters Grounded in Live Public Documentation
* **Standard**: Agent specifications compile into valid enterprise manifests across 4 platforms, validated against real public schemas fetched live:
  1. **Google Cloud / Vertex AI**:
     * **Live URL**: `https://ai.google.dev/api/generate-content#FunctionDeclaration` & `https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/Tool#FunctionDeclaration`
     * **Constraint**: `FunctionDeclaration` requires `name` (regex `^[a-zA-Z0-9_-]{1,64}$`), `description`, and `parameters` (`type="object"`).
  2. **OpenAI Assistants API**:
     * **Live URL**: `https://platform.openai.com/docs/guides/function-calling`
     * **Constraint**: Strict tool calling mandates `strict: True`, explicit `additionalProperties: False`, and 100% parameter enumeration in `required`.
  3. **Microsoft Azure AI / Semantic Kernel**:
     * **Live URL**: `https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/`
     * **Constraint**: Plugin definitions require semantic function descriptions and human-in-the-loop authorization gates (`RequiresConsent`).
  4. **Databricks Mosaic AI Agent Framework**:
     * **Live URL**: `https://docs.databricks.com/en/generative-ai/agent-framework/create-agent.html`
     * **Constraint**: Tools require 3-tier Unity Catalog namespace (`catalog.schema.function`) and explicit scalar type declarations.
* **Enforcement Rule**: Runtime tool schemas and cloud infrastructure declarations are strictly distinguished. Negative schema tests must reject invalid manifests.

---

### Invariant 4: Settled 24-Entity Core Taxonomy
* **Standard**: The core domain ontology consists of strictly **24 entity classes** in `EntityTypeEnum`.
* **Discipline Rule**: Domain entities must not be arbitrarily proliferated. Specifically:
  * `BargeConvoy` is an instance of `Shipment` with `transport_mode="RIVER"`, not a 25th entity class.
  * Operational events (`OperationalEvent`) and Decisions (`Decision`) are first-class control plane primitives that link entities without inflating the core entity taxonomy.
* **Verification**: `len(EntityTypeEnum) == 24` is enforced by domain assertions.

---

### Invariant 5: Deterministic Decision Escalation Trigger Model
* **Standard**: SLA-driven decision escalations (`DECISION_PENDING` $\to$ `ESCALATED`) are executed deterministically.
* **Trigger Model**: Escalations occur **on-demand** or via **scheduled external cron sweeps** (e.g., `POST /api/decisions/check-escalations` or CLI sweep).
* **Architectural Constraint**: In local/deterministic mode, the system runs **no autonomous background threads, hidden daemons, or unobservable polling loops**. Every state transition is traceable to an explicit invocation and is recorded in the cryptographic audit chain.
* **Demonstrated State Transition**: Seeded decision `dec-2026-005-escalated` transitions from `DECISION_PENDING` to `ESCALATED` upon sweep execution, persisting to SQLite and creating an audit record.

---

### Invariant 6: Reconciled Economic Rigor & Independent Test Grounding
* **Standard**: All economic impact calculations and pilot ROI projections strictly follow the 4-step reconciled formula chain:
  1. $\text{Total 1st-Year Investment} = \text{Implementation Cost} + \text{Annual Software License}$
  2. $\text{Net 1st-Year ROI (\$)} = \text{Addressable Annual Savings} - \text{Total 1st-Year Investment}$
  3. $\text{Net 1st-Year ROI (\%)} = \left( \frac{\text{Net 1st-Year ROI}}{\text{Total 1st-Year Investment}} \right) \times 100$
  4. $\text{Payback Period (months)} = \frac{\text{Implementation Cost}}{\text{Addressable Annual Savings} / 12}$
* **Economic Defense**:
  * Every pilot is accompanied by an explicit **Assumptions Ledger** documenting operational baselines and target metrics.
  * Every pilot features a **Tripartite Sensitivity Matrix** reporting Conservative (-20%), Base, and Aggressive (+20%) scenarios.
* **Non-Tautological Verification Rule**: Tests must **never** assert `roi_pct == net_roi / investment * 100` (formula verifying itself). Tests must assert against **independently derived numerical constants** with full step-by-step arithmetic shown in test comments.

---

## Phase 3.7 Boundary & Transition to Field Deployment

With the completion and verification of Phase 3.7:
1. **The Reasoning & Control Plane is Feature-Complete**: Ontology, synthetic seed generator, SQLite persistence, audit hash chaining, decision escalation, economic modeling, and enterprise adapters are fully hardened.
2. **End of Speculative Passes**: No further internal synthetic refactorings or speculative model additions will be undertaken without real customer inputs.
3. **Next Phase (Phase 4)**: Deployment of Pilot 1 (`pilot-aidesa-customs-001`) and Pilot 2 (`pilot-capexa-fluvial-002`) into real customer environments, connecting live ERP connectors (SAP B1 Service Layer) and customs/telemetry APIs.
