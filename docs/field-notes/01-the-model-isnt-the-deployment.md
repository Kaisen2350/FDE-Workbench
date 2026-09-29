# FDE Field Note #01: The Model Isn't the Deployment

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/domain/ontology.py`](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/ontology.py)  
> **Key Principle**: *Enterprise AI fails not at prompt generation, but at the boundary with physical reality and state machines.*

---

Most conversations about applied AI revolve around model weights: 
*Which foundation model scores higher on MMLU? How do we prompt it to format JSON?*

When you deploy into industrial supply chains, logistics corridors, or regulated trade, you quickly realize: **the model is the easiest 10% of the system.**

Consider two hypothetical failure modes I'd expect in this corridor:
* A Bill of Lading says 1,500 metric tons of soybean meal were loaded, but the hydrometric gauge on the river dropped 40 cm overnight. If you dispatch that push-convoy at full draft, it runs aground at Paso Queso.
* An export declaration in the customs portal says "Cleared", but the physical báscula scale ticket at the terminal has a 450 kg discrepancy with the invoice. The truck will sit in the red channel at the border for 36 hours incurring demurrage fines.

A language model knows nothing about water depth, axle weight, or customs DNA unless you build an **operational ontology grounded in physical truth**.

In the FDE Workbench, before calling a single model, we model the physical reality through 24 strongly typed domain entities:
* Infrastructure limits (silo throughput, weighbridge capacity)
* Logistics constraints (barge convoy drafts, truck bitren axle limits)
* Regulatory regimes (SEPRELAD GRC compliance, SENAVE phytosanitary certs)

The first deliverable of a Forward Deployed Engineer is not a prompt. It is a typed representation of reality.

---

**Code implementation**:
See the 24-entity domain taxonomy and critical path engine:  
👉 [https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/ontology.py](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/ontology.py)
