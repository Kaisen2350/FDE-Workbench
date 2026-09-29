# FDE Field Note #04: The First Thing an FDE Builds Isn't Software

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`docs/tradecraft/02-operator-discovery.md`](https://github.com/[your-username]/fde-workbench/blob/main/docs/tradecraft/02-operator-discovery.md)  
> **Key Principle**: *Customer interviews should produce typed schemas, not meeting minutes. And never show the operator your numbers first.*

---

When entering an enterprise, technical teams often make one of two mistakes:
1. They ask the client what they want built (producing a laundry list of feature requests).
2. They walk in with a slide deck showing an estimated ROI model with assumed numbers.

Both fail. The first produces software that solves symptoms instead of root friction. The second produces confirmation bias: if you ask an operator, *"We estimated customs exceptions happen 6.5% of the time and cost \$850, is that right?"*, they will just nod.

An FDE runs **Operator Calibration** with two specific techniques:

### 1. The Assumption-Stripped Leave-Behind Pattern
When leaving materials with terminal captains or customs brokers:
* Show the workflow sequence.
* Show the decision points and approval gates.
* Show the *structure* of the economic equations:
  $$\text{Cost} = \text{Labor} + \text{Exceptions} + \text{Working Capital Drag}$$
* **Strip every dollar figure and minute estimate.**

This anchors the operator to their actual lived experience rather than your model's hypothesis.

### 2. Turning Interviews into Typed Schemas (`DiscoveryIntake`)
Instead of leaving discovery notes in Google Docs, we structure the intake as a strongly validated Pydantic JSON schema:
* Critical workflows & friction points
* Systems of record (SAP, TMS, SOFIA)
* Headcount by role
* Bounded physical constraints

The `DiscoveryTransformationEngine` then compiles that intake into domain entities, relationships, and prioritized AI candidate opportunities.

The deliverable of discovery is an engineering backlog grounded in calibrated numbers.

---

**Code implementation**:
See the discovery intake engine and operator interview calibration scripts:  
👉 [https://github.com/[your-username]/fde-workbench/blob/main/docs/tradecraft/02-operator-discovery.md](https://github.com/[your-username]/fde-workbench/blob/main/docs/tradecraft/02-operator-discovery.md)
