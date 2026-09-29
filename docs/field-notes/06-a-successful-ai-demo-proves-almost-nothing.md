# FDE Field Note #06: A Successful AI Demo Proves Almost Nothing

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/evals/harness.py`](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/evals/harness.py)  
> **Key Principle**: *An AI demo proves a model can generate tokens on a happy path. An FDE evaluation harness proves a system can survive 50 dirty operational scenarios without a single unauthorized mutation.*

---

In enterprise AI sales, a demonstration usually looks like this:
The team loads a clean PDF invoice into a UI, asks the model to extract line items, and the model outputs flawless JSON. Everyone in the conference room nods.

In production logistics, that demo proves almost nothing.

Here is what happens on Monday morning:
* 3 out of 100 invoices have illegible handwritten customs stamps that produce hallucinated HS codes.
* A legacy TMS exports a dispatch with a 42.35 metric ton axle weight, violating Brazilian bitren highway limits.
* A river draft sensor reports 8.2 feet at Paso Queso, but the convoy draft recommendation script attempts to auto-dispatch 16 barges loaded for 9.5 feet.
* If the autonomous agent executes that dispatch, a \$4M barge convoy runs aground in the Hidrovía.

### The Non-Negotiable Safety Invariant: `unauthorized_actions == 0`

When evaluating enterprise AI systems, traditional ML metrics (BLEU, ROUGE, or benchmark accuracy percentages) are insufficient. 

If an agent has a **98% task success rate** across 50 operations, but the remaining 2% represents **two unauthorized ERP mutations or customs filings**, that system is un-deployable. In regulated environments, safety is binary:

$$\text{System Safety Score} = \begin{cases} \text{Task Success Rate}, & \text{if } \text{unauthorized\_actions} = 0 \\ 0.0, & \text{if } \text{unauthorized\_actions} > 0 \end{cases}$$

### The 50-Scenario Benchmark Suite

In the FDE Workbench, we built an automated evaluation harness ([`fde_workbench/evals/harness.py`](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/evals/harness.py)) that executes across 50 distinct edge-case scenarios:
1. **Physical boundary failures**: Low river drafts, silo throughput bottlenecks, weighbridge tare discrepancies.
2. **Regulatory & compliance failures**: Sanction list matches, phytosanitary cert expiration, tariff code mismatches.
3. **Adversarial & operational injections**: Out-of-bounds weight overrides, prompt injection in driver remarks, corrupted dates.

The harness evaluates four deterministic metrics:
* **Task Success Rate** ($\ge 90\%$)
* **Schema Validity Rate** ($100\%$ required)
* **p95 Latency & Cost per Task**
* **Unauthorized Actions** ($0$ tolerated)

### Honest Calibration: Synthetic Benchmarks vs. Cloud LLMs

One critical lesson when reporting benchmark numbers: **be precise about what you are measuring**.
In our open-source reference harness, deterministic evaluations run locally in ~8.9 ms per task at \$0.000000 per token. We explicitly flag this in benchmark logs:

```text
[Synthetic Reference Workload — Local Deterministic Harness; Not Representative of Remote Cloud LLM Latency/Cost]
```

When connecting to remote frontier models (Vertex AI Gemini, Azure OpenAI), network RTT and token billing will dominate latency and cost. Conflating local harness execution with remote cloud API calls destroys engineering credibility in technical reviews.

---

**Code implementation**:
See the 50-scenario benchmark engine and safety assertions:  
👉 [https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/evals/harness.py](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/evals/harness.py)
