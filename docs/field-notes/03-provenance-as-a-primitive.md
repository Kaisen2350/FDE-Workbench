# FDE Field Note #03: Why Provenance is an Engineering Primitive

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/domain/provenance.py`](https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/domain/provenance.py)  
> **Key Principle**: *An enterprise system that treats stakeholder claims and empirical sensor data as equal will fail catastrophically.*

---

One of the quickest ways an applied AI pilot loses executive credibility is hallucinated confidence.

When an AI system makes an operational recommendation, the first question from the VP of Operations or Head of Customs Compliance is:
*"Where did that number come from?"*

If your system treats all facts as equal, you have a design flaw:
* A customer stating in an interview: *"Our trucks take 10 minutes to clear"* is a claim.
* A báscula weighbridge scale log recording `scale_ticket_closed` at 14:22 and customs gate exit at 17:10 is an empirical observation.
* An official hydrometric water level bulletin published by the Prefectura Naval is a verified public source.

In the FDE Workbench, **data provenance is a first-class enum on every entity, evidence record, and decision**:

```python
class ProvenanceType(str, Enum):
    SYNTHETIC = "SYNTHETIC"                 # Deterministic baseline data modeling physical reality
    CUSTOMER_OBSERVED = "CUSTOMER_OBSERVED" # Direct on-site telemetry (scale tickets, logs)
    PUBLIC_SOURCE = "PUBLIC_SOURCE"         # Official bulletins (customs tariffs, hydrometric gauges)
    CUSTOMER_PROVIDED = "CUSTOMER_PROVIDED" # Self-reported claims from customer interviews
    DERIVED = "DERIVED"                     # Programmatically computed state transitions
```

**The FDE Rule of Evidence**:
The control plane refuses to authorize irreversible financial actions or submit official customs filings based solely on `CUSTOMER_PROVIDED` assertions without corroboration from `CUSTOMER_OBSERVED` or `PUBLIC_SOURCE` data.

Synthetic data isn't a weakness if provenance is explicit. And customer claims aren't truth until telemetry confirms them.

---

**Code implementation**:
See how provenance is modeled across entities and evidence:  
👉 [https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/domain/provenance.py](https://github.com/[your-username]/fde-workbench/blob/main/fde_workbench/domain/provenance.py)
