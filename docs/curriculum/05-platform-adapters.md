# FDE Curriculum Module 5: Multi-Platform Enterprise Substrates

> *"Enterprise clients rarely adopt a new cloud just to run an AI pilot. If they are an Azure shop, they deploy on Azure. If they run on Databricks, they deploy on Mosaic AI. An FDE decouples the operational model from the execution substrate: 'Same operational model, different deployment adapter'."*

---

## 1. The FDE Architectural Doctrine

A common mistake in AI engineering is tightly coupling domain logic to a specific vendor SDK (e.g. building exclusively for LangChain or AWS Bedrock). In enterprise deployments, **cloud procurement friction kills pilots faster than bad code**.

An elite FDE enforces an architectural decoupling:

$$\text{FDE Operational Control Plane} \longrightarrow \text{Platform Adapter} \longrightarrow \text{Customer Environment}$$

```
┌────────────────────────────────────────────────────────┐
│             FDE OPERATIONAL CONTROL PLANE              │
│  • Domain Ontology (24 Entities & Relationships)       │
│  • Evidence Provenance & Cryptographic Audit Ledger    │
│  • 5-Stage Decision Pipeline & Human Authority Gates   │
│  • Canonical Pilot Specifications                      │
└──────────────────────────┬─────────────────────────────┘
                           │ Dispatches via Platform Adapters
         ┌─────────────────┼──────────────────┬─────────────────┐
         ▼                 ▼                  ▼                 ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐
│  Google Cloud   ││ Microsoft Azure ││ OpenAI           ││ Databricks      │
│  Vertex AI /    ││ AI Foundry /    ││ Enterprise /     ││ Mosaic AI /     │
│  Gemini SDK     ││ Semantic Kernel ││ Assistants v2    ││ Unity Catalog   │
└─────────────────┘└─────────────────┘└─────────────────┘└─────────────────┘
```

The core moat is **operational tradecraft $\times$ domain ontology $\times$ economic translation**. The cloud is merely the execution substrate.

---

## 2. The 4 Enterprise Platform Adapters

The `fde-workbench` implements 4 production adapters in `fde_workbench/adapters/`:

### 1. Google Cloud / Gemini Enterprise (`GeminiPlatformAdapter`)
* **Substrate**: Vertex AI Agent Engine with `gemini-2.5-flash` (or `pro`).
* **Tool Pattern**: OpenAPI 3.0 tool definitions targeting FastAPI endpoints.
* **Code Scaffolding**: Runnable Python client code utilizing the modern `google-genai` SDK (`from google import genai`).
* **Best Fit**: Organizations running Google Workspace, BigQuery, or GCP infrastructure.

### 2. Microsoft Azure AI Foundry (`AzurePlatformAdapter`)
* **Substrate**: Azure OpenAI Service (GPT-4o) managed through Azure AI Studio.
* **Tool Pattern**: Semantic Kernel plugins with declarative function decorators.
* **Governance**: Microsoft Entra ID (Azure AD) RBAC with mandatory `RequiresConsent` filters for human approval.
* **Best Fit**: Microsoft 365, Dynamics, and Power Platform enterprise shops.

### 3. OpenAI Enterprise (`OpenAIPlatformAdapter`)
* **Substrate**: OpenAI Assistants API v2 with Vector Store file search.
* **Tool Pattern**: Strict JSON Schema function calling (`strict: true`).
* **Governance**: Enterprise workspace isolation with zero data retention (ZDR).
* **Best Fit**: Fast-moving tech enterprises without cloud-specific commitments.

### 4. Databricks Mosaic AI (`DatabricksPlatformAdapter`)
* **Substrate**: Mosaic AI Agent Framework + MLflow `pyfunc` serving.
* **Tool Pattern**: Unity Catalog SQL functions (`catalog.schema.function`) governed by Unity Catalog governance.
* **Storage**: Delta Lake tables with change data feed (CDF).
* **Best Fit**: Enterprises with massive data lakes and existing lakehouse governance.

---

## 3. Canonical Deployment Plan Generation

Every platform adapter consumes a canonical `PilotSpecification` and outputs a platform-specific deployment blueprint:
- **Runtime Environment**: Compute cluster, container, or serverless configuration.
- **Model Configuration**: Temperature, system instructions, and token parameters.
- **Tool Registrations**: Automatically generated schema definitions for each operational tool.
- **Security & RBAC**: Identity mapping (IAM roles, service principals, or OAuth tokens).
- **Telemetry & Observability**: Logging targets (Cloud Logging, Azure Monitor, MLflow).

```bash
# Generate Azure deployment plan
python run_workbench.py pilot deploy-plan pilot-2026-customs-recon --platform microsoft_azure_ai_foundry

# Generate Databricks deployment plan
python run_workbench.py pilot deploy-plan pilot-2026-customs-recon --platform databricks_mosaic_ai
```

---

## 4. Hands-on Lab: Switching Substrates

### 1. Inspect the Platform Switcher in the UI
* Launch `python run_workbench.py`
* Navigate to **Tab 11: FDE Pilot Engine**
* Select `pilot-2026-customs-recon`
* Use the **Platform Substrate Switcher** to flip between Google Gemini, Azure, OpenAI, and Databricks. Notice how tool schemas, architecture notes, and security guardrails update instantly while the underlying economic model and ontology remain identical.

### 2. Generate Runnable Python Code for Gemini Enterprise
```python
from fde_workbench.storage.store import store
from fde_workbench.adapters.gemini import GeminiPlatformAdapter

pilot = store.get_pilot("pilot-2026-customs-recon")
adapter = GeminiPlatformAdapter()
plan = adapter.generate_deployment_plan(pilot)

print("Generated Gemini System Instruction:")
print(plan["system_instruction"])
print("\nRegistered OpenAPI Tools:")
print(list(plan["tools"].keys()))
```

### 3. Verify Adapter Validation Suite
Run the automated test suite confirming all 4 platform adapters output compliant schemas:
```bash
python -m unittest tests/test_adapters.py -v
```

---

## Key Takeaways for the FDE
1. **Never fight the client's IT department**: Deploy into the environment they have already accredited.
2. **Abstract the reasoning plane**: Keep the ontology, state machine, and decision rules in a clean, vendor-neutral core.
3. **Automate multi-platform code generation**: Provide turn-key scaffolding for Gemini, Azure, OpenAI, and Databricks.
