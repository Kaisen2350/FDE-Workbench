# Synthetic Deployment Case: Export Customs Reconciliation

> **Corridor**: Ciudad del Este (PY) ➔ Foz do Iguaçu (BR) via Friendship Bridge (PY-02 / BR-277)  
> **Enterprise**: Agro-Industrial del Este S.A. (AIDESA)  
> **Pilot ID**: `pilot-2026-customs-recon`  
> **Provenance**: Explicitly marked `ProvenanceType.SYNTHETIC`  
> **Core Outcome**: **223.5% Net 1st-Year ROI** ($73,750 net value, **1.7-month payback period**)

---

## Executive Summary

Outbound export trucks transporting high-protein soybean meal pellets and crude degummed oil across the Brazilian border face severe documentation delays and customs clearance friction in the SOFIA/VUE system.

A manual 14-minute document preparation cycle coupled with a 6.5% documentation mismatch rate triggers costly border dwell penalties ($850/incident in detention, storage, and re-inspection fees) and accumulates 16.8 hours of border dwell time per truck.

This synthetic deployment case demonstrates an FDE intervention deploying a **Deterministic Customs Reconciliation Assistant** integrated with SAP Business One, Trans-Chaco TMS, and official DNIT customs tariff tables.

---

## Case Study Artifacts

| Document | Purpose & Contents |
|---|---|
| [**1. Operator Discovery**](discovery.md) | Structured intake dossier, interview calibration notes with *Jefe de Comercio Exterior*, and assumption testing. |
| [**2. Architecture & Control**](architecture.md) | Systems topology, deterministic state gating, human authority sign-off, and rollback triggers. |
| [**3. Auditable Economic Model**](economics.md) | 10-step mathematical bridge from cycle time reduction to annual EBITDA savings and payback. |
| [**4. 12-Section Deployment Brief**](deployment-brief.md) | Complete client-facing briefing document delivered to the enterprise executive sponsor. |

---

## Technical & Operational Verification

Run the automated verification suite for this pilot:
```bash
# Calculate auditable economic model
python run_workbench.py pilot economics pilot-2026-customs-recon

# Generate client deployment brief
python run_workbench.py pilot brief pilot-2026-customs-recon

# Verify multi-platform deployment plan across Azure, Gemini, OpenAI, Databricks
python run_workbench.py pilot deploy-plan pilot-2026-customs-recon --platform microsoft_azure_ai_foundry
```
