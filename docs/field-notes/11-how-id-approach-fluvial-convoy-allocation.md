# FDE Field Note #11: How I'd Approach Fluvial Convoy Allocation

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`case-studies/fluvial-convoy/`](https://github.com/kaisen2350/fde-workbench/blob/main/case-studies/fluvial-convoy/)  
> **Key Principle**: *In river logistics, software does not optimize abstract queues. It optimizes inches of water draft under an iron hull. Every inch left unloaded is lost revenue; every inch overloaded is a shipwreck.*

---

Over 80% of Paraguay's foreign trade moves by water along the 3,400-kilometer Hidrovía Paraguay-Paraná corridor, connecting river terminals in Asunción and Villeta to ocean ports in Argentina and Uruguay.

The entire economic engine depends on one physical variable: **river water depth**.

### The Friction: The Cost of an Inch

A standard push-convoy consists of 16 Mississippi-style dry bulk barges propelled by a single 6,000-horsepower line-haul pushboat, carrying up to 25,000 metric tons of grain.

On a commercial barge:
$$\mathbf{1\text{ inch of water draft}} \approx \mathbf{18\text{ metric tons of cargo capacity per barge}}$$

During the dry winter season, hydrometric levels drop rapidly at shallow passes like Paso Queso and Pedernal. This creates a high-stakes operational dilemma:
* **The Overload Risk**: If a convoy is loaded to 9'6" (nine feet, six inches) and the river gauge drops to 9'2" before the convoy arrives 4 days later, the lead barges run aground. The channel is blocked, salvage tugs charge \$15,000/day, and customer delivery contracts trigger liquidated damages.
* **The Conservative Underload Penalty**: To avoid grounding, port captains frequently apply blunt, ultra-conservative safety buffers, loading barges to only 8'6".
  $$\text{16 barges} \times \text{12 inches underloaded} \times \text{18 tons/inch} = \mathbf{3,456\text{ metric tons of empty capacity per trip}}$$
  Across a 40-voyage annual schedule, that leaves tens of thousands of tons of contracted freight on the riverbank.

### The FDE Approach: Hydro-Dynamic Draft Optimization

An FDE approaches this not as an isolated ML prediction problem, but as an integrated operational control loop:

$$\begin{matrix}
\text{Prefectura Naval Gauges} & \text{River Depth Soundings} & \text{Silo Grain Stock} & \text{Fleet Availability} \\
\searrow & \downarrow & \downarrow & \swarrow \\
& \mathbf{\text{Hydrometric Telemetry Ingestion \& Validation}} & \\
& \downarrow & \\
& \mathbf{\text{Dynamic 72-Hour River Transit Forecasting}} & \\
& \downarrow & \\
& \mathbf{\text{Optimal Barge Loading \& Hull Stress Allocation}} & \\
& \downarrow & \\
& \mathbf{\text{Terminal Port Captain Cryptographic Authorization}} & \\
& \downarrow & \\
& \text{Precision Chute Loading Execution} &
\end{matrix}$$

1. **Transit-Aware Water Prediction**: You don't load for today's water level at the terminal. You load for the predicted water level at critical shallow passes 72 to 96 hours in the future when the convoy actually navigates them.
2. **Hull Stress & Draft Balancing**: Loading cannot simply maximize gross tonnage; it must balance barge draft (trim, hogging, and sagging) to prevent structural fractures and steering loss.
3. **The Human Invariant**: The AI draft optimizer produces a mathematically bound loading recommendation. The licensed Port Captain retains sole authority to sign off on the dispatch docket.

### Modeled Operational & Economic Delta

In our synthetic fluvial convoy case study:
* **Capacity Recovery**: Safely recovering an average of 4.2 inches of allowable draft through dynamic predictive modeling.
* **Tonnage Delta**: +1,209 metric tons of additional export volume per convoy voyage.
* **Net Freight Savings**: \$496,000 in annualized net operational value.
* **Financial Gate**: Modeled Net 1st-Year ROI of **620.4%** with an initial capital payback of **0.8 months** on an \$80,000 initial pilot implementation.

---

**Full case study & architecture brief**:
Explore the hydrometric models, risk analysis, and convoy economics:  
👉 [https://github.com/kaisen2350/fde-workbench/tree/main/case-studies/fluvial-convoy](https://github.com/kaisen2350/fde-workbench/tree/main/case-studies/fluvial-convoy)
