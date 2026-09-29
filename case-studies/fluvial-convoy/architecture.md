# Architecture & Control: Fluvial Convoy Draft Optimizer

> **Architectural Doctrine**: $\text{FDE Control Plane} \longrightarrow \text{Platform Adapter} \longrightarrow \text{Customer Environment}$

---

## 1. Systems Topology & Integration Pattern

```
┌────────────────────────────────────────────────────────┐
│             PHYSICAL RIVER & TERMINAL FEEDS            │
│  [Prefectura Naval Gauges]       [Terminal Báscula]    │
│    (Hydrometric Bulletins)      (Draft Survey Tickets) │
└───────────────────────────┬────────────────────────────┘
                            │ Continuous ingestion
┌───────────────────────────▼────────────────────────────┐
│              FDE OPERATIONAL CONTROL PLANE             │
│  • Pydantic v2 OperationalEvent Ingestion Engine       │
│  • Provenance Tagging (PUBLIC_SOURCE / OBSERVED)       │
│  • Dynamic River Pass Critical Constraint Engine       │
└───────────────────────────┬────────────────────────────┘
                            │ Dispatches stowage optimization
┌───────────────────────────▼────────────────────────────┐
│               PLATFORM ADAPTER LAYER                   │
│  • Google Cloud Vertex AI / Azure AI Foundry / OpenAI  │
│  • Safe Dynamic Loading Allocation & Draft Calculation │
└───────────────────────────┬────────────────────────────┘
                            │ Returns Advisory Loading Plan
┌───────────────────────────▼────────────────────────────┐
│          DETERMINISTIC VERIFICATION & GATING           │
│  • Hard Under-Keel Clearance Gate (UKC >= 1.5 ft)      │
│  • If Predicted UKC < 1.5 ft -> Refuse Automated Plan  │
│  • Mandatory Human Authority Gate:                     │
│      Role: Capitán de Flota / Terminal Director        │
│      Action: Written Sign-Off on Stowage Plan          │
│  • Cryptographic SHA-256 Audit Trail Entry             │
└────────────────────────────────────────────────────────┘
```

---

## 2. Invariant Rules & Maritime Safety

1. **Under-Keel Clearance (UKC) Invariant**: Software mathematically enforces a minimum under-keel safety clearance of 1.5 feet ($0.45\text{ m}$) below the lowest predicted gauge at critical passes (*Paso Queso*). If water levels predict a clearance $<1.5\text{ ft}$, the allocation is hard-rejected and lightering is scheduled.
2. **Deterministic Governance**: AI proposes allocation; Fleet Captain confirms. No push-boat throttle is engaged without authenticated human dispatch approval.
3. **Audit Trail**: Every hydrometric observation, draft computation, and captain sign-off is logged into the append-only SHA-256 cryptographic chain.
