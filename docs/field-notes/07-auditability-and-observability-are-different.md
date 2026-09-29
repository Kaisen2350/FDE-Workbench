# FDE Field Note #07: Auditability and Observability Are Different Systems

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/telemetry/tracer.py`](https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/telemetry/tracer.py)  
> **Key Principle**: *Auditability asks: "What happened, and can I prove it to a regulator?" Observability asks: "Why did it happen, where was the latency, and what did it cost?" Conflating the two creates systems that fail both auditors and on-call engineers.*

---

In early AI deployments, teams frequently mix up two fundamentally different operational requirements:
1. **Compliance Auditability** (forensic, immutable, tamper-evident).
2. **Runtime Observability** (granular, ephemeral, statistical).

If you dump OpenTelemetry trace JSONs into an S3 bucket, a customs inspector or financial auditor will reject it—there is no cryptographic proof that the records weren't edited retroactively. 

Conversely, if you only maintain high-level compliance event logs, your engineering team will have zero visibility when p95 latency spikes from 800 ms to 9 seconds during peak export season.

In the FDE Workbench, we cleanly decouple these into two distinct subsystems:

### 1. The Forensic Audit Plane (`audit.py`)
The audit ledger is designed for legal, regulatory, and financial scrutiny:
* It records state transitions: who authorized what action, under which evidence provenance, at what timestamp.
* Every record is cryptographically bound into an **append-only SHA-256 hash chain**:
  $$\text{Hash}_n = \text{SHA256}(\text{Record}_n + \text{Hash}_{n-1})$$
* Any retroactive tampering, database alteration, or dropped record breaks the hash chain immediately and is flagged during verification.

### 2. The Operational Observability Plane (`tracer.py`)
The telemetry system is designed for the engineers keeping the deployment running:
* **Span-level tracking**: Every operational task decomposes into fine-grained execution spans:
  $$\text{Request} \longrightarrow \text{Model Inference} \longrightarrow \text{Retrieval} \longrightarrow \text{Tool Execution} \longrightarrow \text{Decision Gate} \longrightarrow \text{Action}$$
* **Latency distributions**: Automated calculation of $\text{p50}$, $\text{p90}$, $\text{p95}$, and $\text{p99}$ latencies to identify bottlenecked tool calls.
* **Granular cost accounting**: Tracks input/output token usage per span and calculates exact financial cost per transaction based on provider rate cards.
* **Failure categorization**: Segregates schema validation errors, tool execution timeouts, and rate limits.

```text
[Telemetry Summary]
  Traces Recorded: 50
  Latency: p50=6.2ms | p90=11.4ms | p95=14.1ms | p99=18.7ms
  Total Tokens: 12,450 (In: 9,800, Out: 2,650)
  Total Incurred Cost: $0.0249
  Spans by Component:
    - retrieval: 3.1ms avg
    - model_inference: 8.4ms avg
    - decision_gate: 0.8ms avg
```

### The Unsolved Problem in the Field
The clean separation works beautifully within the boundaries of our Python control plane. 

Where it gets hard in real customer environments is **context propagation across legacy boundaries**. When a decision triggers a SOAP XML call to an AS/400 mainframe or a file write to a local SMB share, standard W3C `traceparent` headers vanish. Bridging distributed trace context across 1990s industrial plumbing remains one of the hardest practical challenges an FDE faces.

---

**Code implementation**:
See the trace collector, span tree hierarchy, and latency distribution engine:  
👉 [https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/telemetry/tracer.py](https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/telemetry/tracer.py)
