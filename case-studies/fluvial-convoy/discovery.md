# Operator Discovery: Fluvial Convoy Draft Optimizer

> **Target Role**: Fleet Operations Director / Capitán de Flota  
> **Enterprise Footprint**: 240 push-convoys annually departing Planta Fluvial Villeta (km 1590)

---

## 1. Structured Intake Findings (`DiscoveryIntake`)

In discovery sessions with AIDESA fluvial fleet management:
* **Stated Pain**: *"When the river drops at Paso Queso, we either guess conservatively and leave 3,000 tons on the dock, or we draft 2 inches too deep and get stuck on a sandbar for 4 days."*
* **Root Operational Cause**: River gauge reports from Prefectura Naval arrive via daily PDF bulletins. Translating river level readings at Asunción, Villeta, and Humaitá into effective permissible draft across a 16-barge footprint requires 45 minutes of manual spreadsheeting per convoy.
* **Systems of Record**:
  - Daily Hydrometric PDF Bulletins (Prefectura Naval General)
  - Barge Loading Sheets & Draft Survey Forms (Terminal Villeta Báscula)
  - Trans-Chaco Fluvial TMS (Barge hull assignments, push-boat power ratings)

---

## 2. Operator Calibration Protocol

Using the **Assumption-Stripped Calibration Kit** (`docs/briefs/calibration-fluvial.md`), the FDE calibrated key model parameters directly with the terminal director:

| Assumption | Initial Hypothesis | Operator Response | Calibration Result |
|---|---|---|---|
| Convoy planning cycle | 60 minutes | *"Takes about 40 to 50 minutes to collect gauge data, calculate draft allowances, and reassign barge positions."* | Calibrated baseline: **45.0 minutes** |
| Grounding / draft exception rate | 12.0% | *"In low water season, about 7 to 9 convoys out of 100 require emergency lightering or encounter grounding delays."* | Calibrated baseline: **8.0%** |
| Cost per exception | $25,000 | *"Demurrage on 16 barges is ~$8,000/day. Lightering barge mobilization is $10,000. Typical incident costs $18k–$20k."* | Calibrated baseline: **$18,500.00** |
| Working capital drag | Unquantified | *"A stuck convoy ties up ~$3.5M of soybean meal for 3–5 days. Annual financing drag is ~$15k."* | Calibrated baseline: **$15,000.00/yr** |

---

## 3. Discovered Human Decision Gates

* **The Fleet Captain is King**: Under maritime law and company policy, the *Capitán de Flota* bears legal and physical responsibility for the convoy.
* **Non-Authoritative Requirement**: The system must provide an advisory draft recommendation with confidence bounds, but the Fleet Captain must sign off on the stowage plan before lines are cast off.
