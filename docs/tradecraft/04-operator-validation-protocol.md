# Pre-Registered Operator Validation Protocol
### Empirical Measurement Protocol for Cross-Border Operational Reconciliation

> **Pre-Registration Timestamp**: `2026-09-29T11:30:00-03:00`  
> **Status**: **LOCKED BEFORE DATA INSPECTION**  
> **Rule**: *Zero post-hoc metric tuning. The measurement criteria, authority boundaries, and baseline categories are fixed prior to examining any external operator dataset.*

---

## 1. Context & The Inquiry Mindset

The objective of this engagement is not to sell software or confirm a pre-existing bias. It is to obtain a **falsifiable external observation** of cross-border operational friction.

### The Inquiry Opener (Non-Presumptive)
When conducting the calibration interview with a customs broker or terminal logistics manager, avoid assuming the 4-way document reconciliation problem exists. 

Open with an empirical inquiry:
> **“Walk me through the last export that got delayed at the border. Where did the time go?”**

- If document mismatch (SOFIA vs. Báscula vs. Invoice) is the true bottleneck, the operator will state it unprompted.
- If the bottleneck is elsewhere (e.g., driver tax ID corruption, manual SENAVE phytosanitary wait, banking foreign exchange clearing), the operator's response immediately redirects the integration boundary to physical reality.

---

## 2. The 4-Part Pre-Registered Protocol

### Part 1: Baseline (Pre-Intervention)
Recorded with the operator before system execution:
1. **Sample Size**: Exact record count $N \in [50, 100]$ of closed historical export dispatches.
2. **Manual Cycle Time**: Average minutes spent by human clerks reviewing, cross-referencing, and clearing one dispatch.
3. **Historical Exception Rate**: Percentage of dispatches historically flagged for red-channel physical inspection or administrative post-clearance review.
4. **Historical Rework / Escalation Time**: Average hours required to resolve a border discrepancy once flagged.
5. **Economic Bleed**: Historical carrier demurrage, driver detention fees, or customs administrative penalties per flagged incident.

### Part 2: Intervention (System Boundaries & Authority Gates)
1. **Input Schemas**: Only anonymized historical export exports (CSV / Excel) processed through local connectors.
2. **Permitted Evaluations**: Deterministic 4-way consistency checks (gross/tare/net weights, carrier tax IDs, driver licenses, NCM tariff codes).
3. **Authority Gate (Non-Negotiable)**: The system generates an advisory pre-clearance report and discrepancy alerts. **Zero automated external mutations or live portal submissions are permitted.** Authority remains 100% with the human operator.

### Part 3: Measurement (The Objective Delta)
Evaluated deterministically across the batch:
1. **Processing Latency**: Wall-clock milliseconds to normalize and evaluate the batch vs. human manual review time.
2. **Concordance Rate**: Percentage of dispatches where the system's evaluation matches the historical human decision.
3. **False-Positive Rate**: Legitimate, compliant dispatches flagged by the system as discrepant.
4. **False-Negative Rate**: Real operational or regulatory discrepancies detected by human review that the system missed.
5. **Operator Override Rate**: How frequently the human operator rejects the system's advisory recommendation upon review.
6. **Downstream Economic Consequence**: Modeled demurrage or administrative fees avoided (or incurred due to false alerts).

### Part 4: Evidence & Provenance Ladder
- Raw incoming data is labeled `CUSTOMER_PROVIDED` within the private execution environment.
- Live desk observations and verified deltas are promoted to `CUSTOMER_OBSERVED`.
- Cryptographic SHA-256 decision records and span telemetry are committed to an immutable audit ledger.
- **Hard Public Boundary**: Customer datasets, raw logs, proprietary schemas, and production traces are **never committed to any public repository**. Any public case study authored from the engagement contains only aggregate metrics, synthetic reproductions, or explicitly authorized high-level summaries.

---

## 3. Data Minimization & Quasi-Identifier Safeguards

The operator must decide what data leaves their perimeter based on the measurement question. The local minimization utility enforces these engineering constraints:

### 1. Cryptographic HMAC Salting (Defeating Rainbow Tables)
Low-entropy identifiers (Paraguayan RUCs with 6–8 digits, cédulas with 6–7 digits) are trivial to reverse if hashed with plain SHA-256. 
- The minimization script generates a **32-byte secret salt that lives only on the operator's machine**.
- RUCs and personal IDs are pseudonymized using `HMAC-SHA256(salt, value)[:16]`.
- **Salt Persistence Warning**: The operator must preserve `.operator_secret.salt` locally. If the salt is deleted, subsequent batches cannot be linked to prior runs.

### 2. Quasi-Identifier Combinations & Date Coarsening
In small samples (50–100 records), an adversary can re-identify a shipment by combining non-sensitive fields (e.g., dispatch timestamp + cargo weight + carrier route).
- Dates may be coarsened to `YYYY-MM` or date-only (`YYYY-MM-DD` stripped of time).
- Scale weights may be rounded to the nearest metric ton if precise weight delta is not the primary measurement question.

### 3. Preserving Outcome Variables via Bucketing
Zeroing monetary fields (freight value, demurrage fees) destroys the outcome variable needed for economic analysis.
- Numeric values are bucketed into ranges (e.g., `USD 500-1000`, `USD 1000-2500`) to preserve economic variance without disclosing proprietary commercial contracts.

---

## 4. Expected Output: Field Note #13

Upon completing this protocol, author **Field Note #13: What Broke When My Synthetic FDE System Met a Real Operator**:
- If the workflow held: report the measured delta (latency, concordance, false positives).
- If the workflow was invalidated: report the gap between synthetic assumptions and physical reality, and document the resulting architectural pivot.
