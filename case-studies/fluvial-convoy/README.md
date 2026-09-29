# Synthetic Deployment Case: Hidrovía Dynamic Convoy Draft Allocation

> **Corridor**: Paraguay River Fluvial Spine (Villeta ➔ Corumbá / Nueva Palmira / San Lorenzo)  
> **Enterprise**: Agro-Industrial del Este S.A. (AIDESA)  
> **Pilot ID**: `pilot-2026-fluvial-draft`  
> **Provenance**: Explicitly marked `ProvenanceType.SYNTHETIC`  
> **Core Outcome**: **620.4% Net 1st-Year ROI** ($285,400 net value, **0.8-month payback period**)

---

## Executive Summary

Outbound grain and soy meal push-convoys (typically 16-barge units pushing ~24,000 MT) navigating the Paraguay-Paraná Hidrovía waterway face critical seasonal draft restrictions. 

During low-water season (July–November), water levels at critical passes (*Paso Queso*, *Paso Bermejo*, *Paso Curupayty*) drop unpredictably. Miscalculating permissible convoy draft leads to catastrophic groundings (average $18,500 per incident in emergency lightering, tug assistance, and port demurrage) or chronic underloading (leaving valuable freight capacity unused).

This synthetic deployment case models an FDE intervention deploying a **Dynamic Convoy Draft Allocation Engine** that combines real-time hydrometric river gauge bulletins (Prefectura Naval), barge stowage plans, and predictive bathymetry to safely maximize cargo tonnage per convoy.

---

## Case Study Artifacts

| Document | Purpose & Contents |
|---|---|
| [**1. Operator Discovery**](discovery.md) | Structured intake findings, calibration notes with *Capitán de Flota* and *Director de Terminal*, and assumption validation. |
| [**2. Architecture & Control**](architecture.md) | Systems topology, Prefectura Naval hydrometric feeds, deterministic draft gating, and fleet master authority. |
| [**3. Auditable Economic Model**](economics.md) | 10-step mathematical bridge from lightering avoidance and cycle time reduction to EBITDA savings. |
| [**4. 12-Section Deployment Brief**](deployment-brief.md) | Complete client-facing deployment brief delivered to enterprise executive leadership. |

---

## Technical & Operational Verification

Run the automated verification suite for this pilot:
```bash
# Calculate auditable economic model
python run_workbench.py pilot economics pilot-2026-fluvial-draft

# Generate client deployment brief
python run_workbench.py pilot brief pilot-2026-fluvial-draft

# Verify multi-platform deployment plan across Gemini, Azure, OpenAI, Databricks
python run_workbench.py pilot deploy-plan pilot-2026-fluvial-draft --platform google_cloud_gemini_enterprise
```
