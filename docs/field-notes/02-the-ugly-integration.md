# FDE Field Note #02: I Deliberately Built the Integration I Didn't Want to Build

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/integrations/legacy_connector.py`](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/integrations/legacy_connector.py)  
> **Key Principle**: *The connective tissue between AI and 20-year-old enterprise data silos is 80% of forward-deployed engineering.*

---

In textbook AI tutorials, data arrives in clean REST JSON with camelCase fields, UTC timestamps, and pre-parsed floats.

In live enterprise environments, your AI system will be handed an export from a 2004 desktop TMS running on Windows XP:
* Semicolon-delimited rows with missing columns.
* Numbers formatted in Latin/Mercosur convention: `"42.350,00"` (periods for thousands, commas for decimals).
* Dates formatted as `"23/09/2026"`.
* Dirty string identifiers: `"CHOFER FICTICIO ALPHA (CHAPA SYN-991 / REMOLQUE 102)"`.
* Hidden quality alerts like moisture exceeding 14.0% buried in an unparsed column.

*(Note: In accordance with DoD Invariant 8, all sample rows and carrier identities in this repository are synthetic by construction. Zero customer or driver PII is committed.)*

If you feed that directly to an LLM, you are paying token costs to have a probabilistic model guess string parsing—and fail 4% of the time when a driver's name contains a semicolon or quotation mark.

I built a dedicated connector (`LegacyTMSConnector`) in the workbench to show how an FDE handles this:
1. Normalizes Latin numbers and dates deterministically in microseconds.
2. Extracts truck license plates and driver identities via regex.
3. Automatically flags physical quality anomalies (e.g. moisture > 14.0% = aflatoxin risk).
4. Emits typed `Shipment` and `Carrier` domain entities into the ontology.
5. Ties the raw payload snippet to an `EvidenceRecord` with explicit provenance (stamped `ProvenanceType.SYNTHETIC` for this reference fixture; transitioning to `CUSTOMER_OBSERVED` upon live on-site deployment).

Before your AI can reason about a workflow, you must build the plumbing that turns legacy garbage into structured ground truth.

---

**Code implementation**:
See the legacy connector and messy CSV normalization:  
👉 [https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/integrations/legacy_connector.py](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/integrations/legacy_connector.py)
