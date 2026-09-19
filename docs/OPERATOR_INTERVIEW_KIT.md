# Operator Interview & Calibration Kit
### FDE Workbench — Paraguay Export Economy Pilots

**Purpose:** This kit exists to test the workbench's synthetic assumptions against a real operator's lived experience *before* any engineering effort goes into connectors or a polished demo. Every number in the current briefs is a placeholder dressed up as a fact. The interview's job is to find out which placeholders are close, which are wrong, and — most valuable — what the ontology missed entirely.

**Ground rule for the interviewer:** Don't lead with the workbench's numbers. Ask the operational question first, let them answer from their own experience, *then* compare to the model. If you show the number before asking the question, you'll get confirmation bias instead of calibration.

---

## How to run this

1. Use the **assumption-stripped brief** (see note at the end) as the leave-behind — it shows the workflow, the decision point, and the structure of the economic model, but not the dollar figures. This keeps the operator anchored to their own reality, not yours.
   * Generate via CLI:
     ```powershell
     python run_workbench.py pilot calibration-brief pilot-2026-customs-recon --export calibration-customs.md
     python run_workbench.py pilot calibration-brief pilot-2026-fluvial-draft --export calibration-fluvial.md
     ```
2. Work through the discovery script for whichever pilot is relevant to that operator's role.
3. Capture everything in the **Findings Log** at the end — especially anything that doesn't fit an existing question. Those are the highest-value findings.
4. Do not defend the model's numbers in the room. If an operator's answer contradicts an assumption, write it down as data, not as an error to correct on the spot.

---

## Discovery Script 1 — Customs Reconciler
**Target operator:** Jefe de Comercio Exterior / customs broker / logistics coordinator handling outbound trucks through Ciudad del Este–Foz do Iguaçu.

### A. Volume & workflow shape
1. Roughly how many outbound export shipments does your operation process through Ciudad del Este in a typical month? A typical year?
2. Walk me through what happens, start to finish, from "the truck is loaded" to "the truck has cleared customs on the Brazilian side." Where do delays actually happen?
3. Is the workflow the same for every shipment, or does it vary a lot by product, buyer, or season?

### B. Time & labor (tests: 14 min baseline / 3 min target per shipment, $25/hr loaded rate)
4. When your team compiles the documentation for a customs clearance (VUE, MIC/DTA, packing list, etc.), how much hands-on time does that actually take per shipment — not counting waiting time, just active work?
5. What's the fully-loaded hourly cost of the person doing that work (or their approximate monthly salary + benefits, if hourly rate isn't how you think about it)?
6. If that documentation work were largely correct and pre-compiled for you, how much of that time do you think would remain? (This tests whether a 3-minute target is realistic or fantasy.)

### C. Exceptions & errors (tests: 6.5% baseline / 1.5% target exception rate, $850/exception cost)
7. Out of, say, 100 shipments, how many run into a problem serious enough that it delays clearance or requires rework — a missing document, a tariff code mismatch, a data entry error?
8. When that happens, what does it actually cost you — in truck detention fees, storage, spoilage risk, penalty fees, or just staff time to fix it? Roughly, per incident.
9. What's the single most common cause of those exceptions?

### D. Non-labor costs (tests: $22,000 "working capital drag")
10. Is there a cost to your operation from cash or goods being tied up while clearance is pending — for example, payment terms that don't start until documents clear, or storage fees while a shipment waits? Roughly how much does that cost you annually?

### E. What the model might be missing entirely
11. Is there a step in this process that regularly causes problems that I haven't asked about?
12. Who has to sign off or get involved when something goes wrong — and does that person or role show up in what I've described so far?
13. Has anything about SOFIA (the customs system), a regulation, or a documentation requirement changed in the last year that would make an old assumption about this process outdated?

---

## Discovery Script 2 — Fluvial Draft Optimizer
**Target operator:** Fluvial Fleet Captain / Terminal Operations Director involved in barge convoy loading and river-pass planning on the Hidrovía.

### A. Volume & workflow shape
1. During low-water season, roughly how many outbound push-convoys does your operation run in a typical month?
2. Walk me through how a daily loading plan and draft calculation actually gets made today — who does it, with what tools, and in what order?

### B. Time & labor (tests: 45 min baseline / 10 min target per convoy planning cycle, $40/hr rate)
3. How much time does the person responsible for the loading plan / draft calculation spend on it, per convoy, on a normal day?
4. What's the fully-loaded hourly cost of that role?
5. If the initial draft numbers and loading distribution were already calculated and just needed review, how much of that time would you expect to still need?

### C. Exceptions & errors (tests: 8% baseline / 1% target exception rate, $18,500/exception cost)
6. How often does a convoy run into a real problem tied to draft or loading — grounding risk, having to offload, a delay at a critical pass — out of, say, 100 convoys?
7. When that happens, what does it cost — demurrage, rerouting, offload-and-reload labor, damaged cargo, missed delivery windows? Roughly, per incident.
8. Is low-water season meaningfully different from the rest of the year for this, or is the risk fairly constant?

### D. Non-labor costs (tests: $15,000 "working capital drag")
9. Does a grounding or delay tie up capital or cargo in a way that has a cost beyond the direct incident cost — insurance, contractual penalties with the buyer, fuel burned idling?

### E. What the model might be missing entirely
10. Is there a factor in river-pass planning — gauge readings, weather, another vessel's schedule, a regulatory restriction — that regularly changes the plan and that I haven't asked about?
11. Who else needs to be looped in when a convoy plan has to change last-minute?

---

## Findings Log Template
*(Use one row per pilot per operator interviewed.)*

| Assumption | Model's current figure | Operator's answer | Gap / Direction | Confidence (their tone: certain / rough guess / unsure) |
|---|---|---|---|---|
| Manual minutes (baseline) | | | | |
| Manual minutes (target, if automated) | | | | |
| Loaded hourly rate | | | | |
| Exception rate (baseline) | | | | |
| Exception rate (target) | | | | |
| Cost per exception | | | | |
| Working capital drag | | | | |
| Volume (annual) | | | | |

**New findings not in the model** *(this section matters more than the table above)*:
- Missing step in the workflow:
- Missing decision point / approval gate:
- Missing entity or role:
- Assumption that's directionally wrong, not just off by a percentage:
- Anything time-sensitive (recent regulatory or system change):

---

## Tooling Integration Note

To generate an assumption-stripped calibration brief ready for field use:
```powershell
# Generate calibration brief for Customs Reconciler:
python run_workbench.py pilot calibration-brief pilot-2026-customs-recon --export calibration_customs_recon.md

# Generate calibration brief for Fluvial Draft Optimizer:
python run_workbench.py pilot calibration-brief pilot-2026-fluvial-draft --export calibration_fluvial_draft.md
```

In this output, Section 4 (Economic Impact & ROI) is replaced with an unlabeled version of the assumptions ledger with blank fill-in lines (`baseline: _____`) and the note: *"Values pending field validation — see operator interview."* All other 11 sections (workflow description, decision loop, human authority gates, acceptance criteria, multi-platform options) remain fully populated to test operational structure without anchoring the operator to synthetic financial projections.
