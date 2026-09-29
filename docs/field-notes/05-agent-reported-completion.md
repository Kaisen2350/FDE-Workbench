# FDE Field Note #05: “Agent-Reported Completion Is Non-Authoritative”

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/domain/decisions.py`](https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/domain/decisions.py)  
> **Key Principle**: *An AI model stating "I have finished the task" is not evidence that the operation was executed.*

---

The internet is flooded with demos of "autonomous agents" that book flights, send emails, or reconcile invoices end-to-end.

In regulated enterprise environments—customs clearance, maritime navigation, bank wires, GRC compliance—autonomous unverified execution is an engineering liability.

If an LLM hallucinates an NCM tariff code or miscalculates permissible convoy draft, who is liable when the barge convoy runs aground or the export truck is impounded?

In the FDE Workbench, we enforce one core invariant across all workflows:

> **Agent-reported completion is non-authoritative.**

An agent can:
- Propose a reconciliation diff
- Draft a customs declaration pack
- Calculate optimal draft allocation across barge hulls
- Emit a tolerance alert

An agent **cannot**:
- Transition system state from `DECISION_PENDING` to `AUTHORIZED`
- Submit transactions to production government portals (SOFIA/VUE)
- Disown the tamper-evident audit log

### The 5-Stage Gated Decision Pipeline
```
[Observation] ➔ [Context] ➔ [Decision Options] ➔ [Authorized Action] ➔ [Outcome]
                                                        │
                                            Named Human Role (HITL)
                                            Sign-Off Token Required
```

1. **State Machine Rule**: Only deterministic verification (a cryptographic signature, valid schema validation pass, or authorized human token from the *Jefe de Comercio Exterior*) transitions state.
2. **Cryptographic Trail**: Every decision state change appends to an immutable SHA-256 hash-chain ledger.
3. **Deterministic Escalation**: If a decision sits unacknowledged past an SLA (e.g. 2.0 hours for customs), the system automatically transitions to `ESCALATED` and alerts executive leadership.

Agents propose. Control systems gate, verify, and log.

---

**Code implementation**:
See the 5-stage decision state machine and escalation engine:  
👉 [https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/domain/decisions.py](https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/domain/decisions.py)
