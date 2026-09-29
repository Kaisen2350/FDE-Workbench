# FDE Field Note #03: Why Provenance is an Engineering Primitive

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/domain/provenance.py`](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/provenance.py)  
> **Key Principle**: *An enterprise system that treats stakeholder claims and empirical sensor data as equal will fail catastrophically.*

---

One of the quickest ways an applied AI pilot loses executive credibility is hallucinated confidence.

When an AI system makes an operational recommendation, the first question from the VP of Operations or Head of Customs Compliance is:
*"Where did that number come from?"*

If your system treats all facts as equal, you have a design flaw:
* A customer stating in an interview: *"Our trucks take 10 minutes to clear"* is a claim.
* A báscula weighbridge scale log recording `scale_ticket_closed` at 14:22 and customs gate exit at 17:10 is an empirical observation.
* An official hydrometric water level bulletin published by the Prefectura Naval is a verified public source.

In the FDE Workbench, **data provenance is an active engineering primitive**, not just an audit tag:

```python
class ProvenanceType(str, Enum):
    SYNTHETIC = "SYNTHETIC"                 # Synthetic fixture modeled after legacy enterprise patterns
    CUSTOMER_PROVIDED = "CUSTOMER_PROVIDED" # Customer-supplied unverified claim or questionnaire
    CUSTOMER_OBSERVED = "CUSTOMER_OBSERVED" # Actually observed on-site in customer environment
    PUBLIC_SOURCE = "PUBLIC_SOURCE"         # Verified official bulletins (customs, hydrometric gauges)
    DERIVED = "DERIVED"                     # Programmatically computed state transitions
```

**Provenance governs what the system is allowed to believe and subsequently do:**
1. A recommendation derived from `SYNTHETIC` fixtures is strictly labeled as a reference workload or modeled hypothesis.
2. The control plane refuses to trigger irreversible external mutations or official customs filings based solely on `CUSTOMER_PROVIDED` assertions without corroboration from `CUSTOMER_OBSERVED` or `PUBLIC_SOURCE` evidence.
3. Every state transition links backward to a verified `EvidenceRecord`, preserving the chain of belief.

Synthetic data isn't a weakness if provenance is explicit. And customer claims aren't truth until telemetry confirms them.

---

**Code implementation**:
See how provenance is modeled across entities and evidence:  
👉 [https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/provenance.py](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/provenance.py)
