# The Last Mile of AI: FDE Field Notes

> **Applied engineering notes on what breaks between AI demos and production enterprise reality.**

---

## The Rule of Engagement

When writing and publishing these notes:
1. **Never do interview cosplay**: Never write *"This is what Google/Palantir FDEs do"* or position yourself as a guru.
2. **Follow the Field Formula**:
   - *Here is the ambiguous operational problem.*
   - *Here is the connective tissue I built to interface with it.*
   - *Here is what broke in the real world.*
   - *Here is the architectural trade-off.*
   - *Here is what I measured (accuracy, latency, safety, cost).*
   - *Here is what I still don't know.*
3. **Always anchor in executable code**: Every post links directly to an open-source commit or file in the `fde-workbench` repository (`commit 4d75289`).

---

## 1. The Vanguard Sequence (The Core 7)

> **Primary distribution track**: These 7 notes establish immediate technical differentiation, demonstrating systems architecture, deterministic safety, legacy integration, and senior engineering judgment.

| # | Title | Core Thesis | Primary Code Anchor |
|---|---|---|---|
| [**#01**](01-the-model-isnt-the-deployment.md) | **The Model Isn't the Deployment** | Enterprise AI fails not at prompt generation, but at the boundary with physical reality and state machines. | `fde_workbench/domain/ontology.py` |
| [**#02**](02-the-ugly-integration.md) | **I Deliberately Built the Integration I Didn't Want to Build** | Connective tissue: normalizing legacy Latin TMS exports (Spanish dates, comma decimals, dirty plates). | `fde_workbench/integrations/legacy_connector.py` |
| [**#05**](05-agent-reported-completion.md) | **“Agent-Reported Completion Is Non-Authoritative”** | Why an LLM saying "done" cannot mutate production state. Gating action behind deterministic authority. | `fde_workbench/domain/decisions.py` |
| [**#06**](06-a-successful-ai-demo-proves-almost-nothing.md) | **A Successful AI Demo Proves Almost Nothing** | Building a 50-scenario benchmark: task success, schema validity, p95 latency, and zero unauthorized actions. | `fde_workbench/evals/harness.py` |
| [**#07**](07-auditability-and-observability-are-different.md) | **Auditability and Observability Are Different Systems** | Forensic cryptographic audit trails vs. live runtime telemetry (p50/p95 latency, tokens/sec, cost). | `fde_workbench/telemetry/tracer.py` |
| [**#08**](08-we-saved-40-hours-isnt-an-roi-calculation.md) | **“We Saved 40 Hours” Isn't an ROI Calculation** | The 10-step mathematical bridge from cycle time reduction to annual EBITDA and payback months. | `case-studies/customs-reconciliation/economics.md` |
| [**#12**](12-what-i-would-change-before-a-live-customer.md) | **What I Would Change Before Putting This in Front of a Live Customer** | Senior engineering judgment: what's missing (distributed tracing, network firewalls, live ERP OAuth tokens). | Architecture Retrospective |

---

## 2. The Deep-Dive Technical Reservoir (The 5)

> **Secondary technical track**: Extended deep-dives into data provenance, operator discovery protocol, multi-cloud decoupling, and end-to-end corridor deployment briefs.

| # | Title | Core Thesis | Primary Code Anchor |
|---|---|---|---|
| [**#03**](03-provenance-as-a-primitive.md) | **Why Provenance is an Engineering Primitive** | Why the system refuses to treat `CUSTOMER_PROVIDED` claims the same as `CUSTOMER_OBSERVED` telemetry. | `fde_workbench/domain/provenance.py` |
| [**#04**](04-discovery-before-software.md) | **The First Thing an FDE Builds Isn't Software** | Customer interviews should produce schemas. The assumption-stripped leave-behind pattern. | `docs/tradecraft/02-operator-discovery.md` |
| [**#09**](09-same-operational-model-different-deployment-substrate.md) | **Same Operational Model. Different Deployment Substrate** | Decoupling the domain control plane from enterprise clouds (Gemini, Azure, OpenAI, Databricks). | `fde_workbench/domain/adapters/` |
| [**#10**](10-how-id-approach-customs-reconciliation.md) | **How I'd Approach Customs Reconciliation as an FDE** | Synthetic case study: 100 outbound trucks on the BR-277 border corridor (Modeled 223.5% ROI). | `case-studies/customs-reconciliation/` |
| [**#11**](11-how-id-approach-fluvial-convoy-allocation.md) | **How I'd Approach Fluvial Convoy Allocation** | Synthetic case study: 16-barge push convoys under low-water river restrictions (Modeled 620.4% ROI). | `case-studies/fluvial-convoy/` |


