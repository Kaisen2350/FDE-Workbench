# Architecture & Control: Customs Reconciliation Pilot

> **Architectural Doctrine**: $\text{FDE Control Plane} \longrightarrow \text{Platform Adapter} \longrightarrow \text{Customer Environment}$

---

## 1. Systems Topology & Integration Pattern

```
┌────────────────────────────────────────────────────────┐
│            ENTERPRISE SYSTEMS OF RECORD                │
│  [SAP Business One]      [Trans-Chaco TMS]     [SOFIA] │
│      (Orders/Invoices)        (Truck Telemetry) (VUE)  │
└───────────────────────────┬────────────────────────────┘
                            │ Pull raw records / events
┌───────────────────────────▼────────────────────────────┐
│              FDE OPERATIONAL CONTROL PLANE             │
│  • Pydantic v2 Ingestion & Normalization Engine        │
│  • Provenance Tagging (CUSTOMER_OBSERVED / DERIVED)    │
│  • 24-Entity Operational Ontology Graph                │
└───────────────────────────┬────────────────────────────┘
                            │ Dispatches reconciliation request
┌───────────────────────────▼────────────────────────────┐
│               PLATFORM ADAPTER LAYER                   │
│  • Azure AI Foundry (GPT-4o) / Vertex AI / Databricks  │
│  • Strict JSON Schema Tool Calling                     │
│  • Pre-compiles NCM Tariff Code & Weight Reconciliation│
└───────────────────────────┬────────────────────────────┘
                            │ Returns Reconciliation Draft
┌───────────────────────────▼────────────────────────────┐
│          DETERMINISTIC VERIFICATION & GATING           │
│  • Non-Authoritative Agent Gate: State is NOT changed  │
│  • Discrepancy Diff: Tolerance check (< 0.5% weight)   │
│  • Mandatory Human Authorization Gate:                 │
│      Role: Jefe de Comercio Exterior                   │
│      Action: Sign-off & Submission Authorization       │
│  • Cryptographic SHA-256 Audit Trail Entry             │
└────────────────────────────────────────────────────────┘
```

---

## 2. Invariant Rules & Security Perimeters

1. **Non-Authoritative Agent Output**: The model's proposed tariff classification and reconciliation diff cannot submit to the DNIT / SOFIA customs portal without a signed human cryptographic token.
2. **Tolerance Gating**: If gross weight recorded at the weighbridge scale differs by $>0.5\%$ from the sales invoice, the system automatically triggers a `QualityEvent` and holds the transaction in `DECISION_PENDING`.
3. **Escalation Sweeps**: If a customs reconciliation hold is not addressed within **2.0 hours**, the escalation engine flags `status: ESCALATED` and alerts the Director of Logistics.
4. **Instant Rollback**: If an exception occurs during the pilot, the operator toggles the fallback switch in the Workbench UI, reverting the workflow instantly to manual Excel/SAP paper processing with zero data loss.
