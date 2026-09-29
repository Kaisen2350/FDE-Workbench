# FDE Curriculum Module 3: Deterministic Control Planes & Governance

> *"Autonomous AI agents making unverified modifications to production enterprise systems is an engineering fantasy. In the real world, models propose; deterministic control planes verify, gate, and log."*

---

## 1. The Autonomous Agent Fallacy

Enterprise executives and compliance officers do not want "autonomous agents" running loose in their supply chains. If an LLM hallucinates a customs tariff code or dispatches a 16-barge convoy into a shallow river pass, the liability rests entirely on the enterprise.

The FDE implements a **Deterministic Control Plane**:
1. **Agent-reported completion is non-authoritative**: An AI model stating *"I have completed the customs clearance"* cannot transition the system state. Only deterministic verification (e.g. valid digital signature, verified hash, schema pass) can transition a task from `EXECUTING` to `VERIFIED`.
2. **Strict Human-in-the-Loop (HITL) Authority Gates**: The AI drafts; an authorized human role signs off.
3. **Rollback Conditions**: Every automated intervention must specify an instantaneous, deterministic rollback mechanism.

```
┌─────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│  AI Engine      │ ----> │ Deterministic Gate   │ ----> │ Enterprise System    │
│  (Probabilistic)│ Draft │ (State Machine, Auth)│ Exec  │ (SAP, TMS, Bank Wire)│
└─────────────────┘       └──────────────────────┘       └──────────────────────┘
                                     │
                           Refuses if unverified /
                           outside bounds
```

---

## 2. The 5-Stage Decision Pipeline

In the `fde-workbench`, every managerial resolution follows an immutable 5-stage state machine:

$$\text{OBSERVATION} \longrightarrow \text{CONTEXT} \longrightarrow \text{DECISION} \longrightarrow \text{AUTHORIZED ACTION} \longrightarrow \text{OUTCOME}$$

```python
class DecisionStatusEnum(str, Enum):
    OBSERVED = "OBSERVED"             # Raw operational anomaly detected
    TRIAGED = "TRIAGED"               # Operational context and constraints hydrated
    DECISION_PENDING = "DECISION_PENDING" # Trade-offs evaluated, options prepared
    ESCALATED = "ESCALATED"           # Timeout breached without human action
    AUTHORIZED = "AUTHORIZED"         # Named human authority approved action
    EXECUTED = "EXECUTED"             # Physical / digital action dispatched
    OUTCOME_VERIFIED = "OUTCOME_VERIFIED" # Measured post-intervention financial & operational delta
```

### Stage Breakdown
1. **Observation**: Triggered directly by an `OperationalEventRecord` (e.g., river draft drops to 8.4 ft).
2. **Context**: Gathers relevant contracts, demurrage schedules, and alternate routes.
3. **Decision Options**: Multi-option matrix evaluating cost, latency delta, and risk rating.
4. **Authorized Action**: Mandatory recording of `authorized_by_role` (e.g., `Jefe de Comercio Exterior`), timestamp, and explicit parameters.
5. **Outcome**: Verifies the post-execution state diff against expected baselines.

---

## 3. Cryptographic Tamper-Evident Audit Hash-Chain

To satisfy institutional auditors, GRC/AML mandates (SEPRELAD/GAFILAT), and forensic reviews, the storage layer implements a SHA-256 cryptographic hash-chain across all state mutations:

$$\text{block\_hash}_n = \text{SHA256}(\text{prev\_hash}_{n-1} + \text{timestamp} + \text{action} + \text{entity\_type} + \text{entity\_id} + \text{canonical\_json\_payload})$$

```python
# Implemented in fde_workbench.storage.store
def verify_audit_chain(self) -> dict:
    prev_hash = "GENESIS"
    for entry in self.get_audit_log():
        expected_hash = compute_sha256(prev_hash, entry.data)
        if entry.hash != expected_hash:
            raise AuditTamperingError(f"Bit-flip or deletion detected at entry {entry.id}")
        prev_hash = entry.hash
    return {"status": "VALID", "total_verified": len(entries)}
```

Any direct SQLite edit, deletion, or bit-flip invalidates the cryptographic chain from that point forward.

---

## 4. Decision Timeout & Escalation Engine

Delays in operational decisions compound exponentially (e.g. demurrage bills accrual). The workbench includes a deterministic **Escalation Engine**:
- Evaluates pending decisions against an `escalation_timeout_hours` SLA.
- Automatically transitions unacknowledged tasks to `ESCALATED`.
- Assigns the incident to an escalated target role (e.g., escalating from *Customs Coordinator* to *VP of Operations*).

```bash
# Trigger an escalation sweep via CLI
python -m fde_workbench verify-audit
```

---

## 5. Hands-on Lab: Verifying the Control Plane

### 1. Verify Cryptographic Integrity
Run the audit chain verification tool:
```bash
python -m fde_workbench verify-audit
```
Expected output:
```text
Cryptographic Audit Chain: VALID (100% Tamper-Free within current seeded session)
  Total Verified Entries: 281
  Head Hash:              de0ad1801142bdcb7995ddced0d72d1b5238972b2c2d31996921872036114f21
```

### 2. Run the Deterministic Test Suite
Execute the 72 unit tests proving zero unverified transitions:
```bash
python -m unittest tests/test_events_and_decisions.py tests/test_storage_hardening.py -v
```

---

## Key Takeaways for the FDE
1. **Autonomous agents are toys; deterministic control planes are products**: In enterprise operations, safety and auditability trump autonomy.
2. **Cryptographic auditability wins enterprise trust**: Prove that data has not been modified or fabricated.
3. **Enforce SLAs in software**: Use deterministic escalation sweeps to prevent decision paralysis.
