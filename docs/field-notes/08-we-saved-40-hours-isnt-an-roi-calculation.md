# FDE Field Note #08: “We Saved 40 Hours” Isn't an ROI Calculation

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`case-studies/customs-reconciliation/economics.md`](https://github.com/kaisen2350/fde-workbench/blob/main/case-studies/customs-reconciliation/economics.md)  
> **Key Principle**: *Telling an enterprise CFO that an AI deployment "saved 40 hours of manual review" gets a blank stare. If saved hours don't reduce overtime, prevent penalties, or accelerate cash collection, the net financial impact on the P&L is exactly \$0.*

---

One of the quickest ways for an engineering team to lose executive credibility is presenting an AI ROI slide that looks like this:

$$\text{15 clerks} \times \text{2 hours/day saved} \times \text{\$35/hour} \times \text{250 days} = \text{\$262,500 Saved}$$

When the CFO looks at the quarterly financial statements, what actually happened?
* Headcount did not decrease by a single employee.
* Payroll expense did not drop.
* Overtime was unaffected.
* The company just spent \$75,000 on cloud compute and model tokens.

To the CFO, that wasn't an operational optimization—it was a pure margin reduction.

### The 10-Step Mathematical Bridge to EBITDA

A Forward Deployed Engineer must translate software latency improvements into line items that directly impact EBITDA and working capital. 

In our Customs Reconciliation Case Study ([`case-studies/customs-reconciliation/economics.md`](https://github.com/kaisen2350/fde-workbench/blob/main/case-studies/customs-reconciliation/economics.md)), we model economics through a rigorous 10-step bridge:

```text
[Operational Reality]
  1. Baseline Volume: 100 outbound grain trucks/day (~26,000 shipments/year)
  2. Document Exception Rate: 6.5% baseline (1,690 trucks flagged at border per year)
  3. Escalation Dwell Time: 36 hours avg border delay per red-channel inspection
  
[Direct Financial Bleed]
  4. Demurrage & Detention Penalties: $850 per detained truck (carrier waiting charges)
  5. Broker Rework & Customs Penalties: $220 in administrative legal fees per incident
  6. Working Capital Drag: $42,000 invoice value locked during border dispute @ 12% WACC
  
[The Deployment Delta]
  7. Automated 4-Way Cross-Check: Drops exception rate from 6.5% to 1.8%
  8. Direct Annual Avoided Cost: 
     - Demurrage avoided: 1,222 incidents × $850 = $1,038,700 (gross carrier bleed)
     - Enterprise share (contractual pass-through): $258,800 net cash savings
  
[The Financial Gate]
  9. Net 1st-Year ROI: 
     (Annual Net Savings $258,800 - Initial Deployment CapEx $80,000) / $80,000 = 223.5%
 10. Modeled Capital Payback: 
     ($80,000 CapEx / $47,600 monthly net operational delta) = 1.7 Months
```

### Why We Use "Modeled" Instead of "Guaranteed"

Notice the terminology: **Modeled Net 1st-Year ROI**, not *Realized Savings*.

In enterprise deployments, physical variables drift:
* Customs authorities may launch an unannounced manual strike, increasing baseline dwell regardless of paperwork accuracy.
* Commodity spot prices fluctuate, shifting working capital carrying costs.
* Carrier contracts may cap demurrage chargebacks.

If an FDE claims "guaranteed savings" before a 90-day production bake period, experienced operators will immediately distrust the numbers. If you present an assumption-calibrated model where every operational parameter can be toggled by the finance team, they become partners in the deployment.

---

**Economic specification**:
See the full 10-step mathematical model and sensitivity tables:  
👉 [https://github.com/kaisen2350/fde-workbench/blob/main/case-studies/customs-reconciliation/economics.md](https://github.com/kaisen2350/fde-workbench/blob/main/case-studies/customs-reconciliation/economics.md)
