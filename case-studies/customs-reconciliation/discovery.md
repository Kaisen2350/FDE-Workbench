# Operator Discovery: Customs Reconciliation & Tariff Pilot

> **Target Role**: Jefe de Comercio Exterior / Customs Broker  
> **Enterprise Footprint**: 2,400 annual export dispatches through Ciudad del Este (PY-02 / BR-277)

---

## 1. Structured Intake Findings (`DiscoveryIntake`)

During initial discovery intake with AIDESA operations, the Foreign Trade department reported severe friction at the border crossing:

* **Stated Pain**: *"Our trucks wait up to two days at the Foz border terminal because of paperwork mismatches."*
* **Root Operational Cause**: Inbound weighbridge scales, SAP export sales orders, and phytosanitary certificates (SENAVE) have slight variances in gross vs net weight, product classification descriptions, or NCM Mercosur tariff codes.
* **Systems of Record**:
  - SAP Business One (Sales orders, export invoices in USD)
  - Trans-Chaco TMS (Carrier dispatches, bitren truck plates)
  - VUE / SOFIA (Paraguayan single-window export portal)
  - Receita Federal SISCOMEX (Brazilian import customs system)

---

## 2. Operator Calibration Protocol

Using the **Assumption-Stripped Calibration Kit** (`docs/briefs/calibration-customs.md`), the FDE interviewed the customs broker without revealing internal economic estimates:

| Assumption | Initial Hypothesis | Operator Response | Calibration Result |
|---|---|---|---|
| Manual prep time per truck | 20 minutes | *"It takes about 12–15 minutes if documents are clean; up to 45 minutes if there's a discrepancy."* | Calibrated baseline: **14.0 minutes** |
| Exception rate | 10.0% | *"About 6 to 7 trucks out of 100 hit red channel due to paperwork mismatches."* | Calibrated baseline: **6.5%** |
| Cost per exception | $1,200 | *"Detention fees are $450/day plus broker refiling and terminal storage: roughly $800–$900."* | Calibrated baseline: **$850.00** |
| Working capital drag | Unquantified | *"Payment terms start upon clean B/L and customs receipt. 16-hour delays tie up ~$20k/year in carrying costs."* | Calibrated baseline: **$22,000.00/yr** |

---

## 3. Discovered Human Decision Gates

The FDE mapped the exact manual sign-off requirement:
* **Current State**: The *Jefe de Comercio Exterior* manually reviews each paper pack before authorizing the driver to proceed to the customs gate.
* **Design Requirement**: The AI system must **not** directly submit to the SOFIA portal. It must compile the reconciliation diff, highlight discrepancies, pre-fill the export declaration draft, and demand an explicit digital human authorization (`status: AUTHORIZED`).
