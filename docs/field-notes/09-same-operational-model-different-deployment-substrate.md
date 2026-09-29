# FDE Field Note #09: Same Operational Model. Different Deployment Substrate

> **Target Channel**: LinkedIn / Substack / X  
> **Repository Anchor**: [`fde_workbench/domain/adapters/`](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/adapters/)  
> **Key Principle**: *Enterprise clients rarely adopt vendor-locked AI architectures. A production control plane must keep domain ontology and deterministic state engines completely decoupled from the cloud execution substrate.*

---

When entering enterprise engagements, you will encounter diverse infrastructure environments:
* Client A has their data lake in Google BigQuery and requires all model endpoints to reside in **Google Cloud Vertex AI**.
* Client B has an enterprise agreement with Microsoft and mandates **Azure OpenAI** behind private VNet endpoints and Microsoft Entra ID.
* Client C runs their feature store in **Databricks Unity Catalog** and uses **Mosaic AI Model Serving**.

If your application logic is tightly coupled to a single vendor's SDK—or entangled in leaky abstractions like LangChain chains—moving from Client A to Client B means a painful, multi-month rewrite.

### The Decoupled Architecture

In the FDE Workbench, domain truth is strictly isolated from cloud runtimes:

$$\begin{matrix}
\text{Physical Reality (Hydrometric Gauges, Báscula Scales)} \\
\Downarrow \\
\mathbf{\text{Canonical Domain Ontology (24 Typed Entities)}} \\
\Downarrow \\
\mathbf{\text{Deterministic State Machine (Evidence } \rightarrow \text{ Decision } \rightarrow \text{ Action)}} \\
\Downarrow \\
\begin{bmatrix}
\text{Vertex AI Adapter} & \text{Azure AI Adapter} & \text{Databricks Adapter} & \text{OpenAI Adapter}
\end{bmatrix} \\
\Downarrow \\
\text{Customer Enterprise VPC}
\end{matrix}$$

### The Adapter Contract

All platform adapters implement an identical interface contract:

1. **`format_system_instructions()`**: Injects domain ontology rules, physical invariants, and strict Pydantic JSON schemas.
2. **`format_tools()`**: Serializes domain tools into provider-native function calling declarations (Google OpenAPI schema vs. OpenAI JSON schema).
3. **`execute_inference()`**: Handles connection pooling, backoff retries, and token streaming.
4. **`parse_response()`**: Enforces that the model's raw string response validates against the domain's strongly typed `DecisionRecommendation` schema.

```python
# The identical decision pipeline runs identically across substrates:
decision_pipeline = DecisionPipeline(
    adapter=VertexAIAdapter(project_id="corp-logistics", model="gemini-1.5-flash")
    # OR: adapter=AzureAIAdapter(endpoint="https://corp.openai.azure.com", deployment="gpt-4o")
    # OR: adapter=DatabricksAdapter(endpoint_name="mosaic-meta-llama-3-70b")
)
```

### The Strategic Value to Customers

Decoupling the operational engine from the cloud layer delivers two enormous advantages:
1. **Zero Vendor Lock-in**: If model pricing, token rates, or regional availability shifts, the client can redirect inference without touching business rules.
2. **Local-First Verification**: 100% of the state engine, legacy connectors, evaluation scenarios, and cryptographic audit checks run locally in unit tests without requiring a live cloud connection or API credentials.

---

**Code implementation**:
See the 4 enterprise platform adapters and interface definitions:  
👉 [https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/adapters/](https://github.com/kaisen2350/fde-workbench/blob/main/fde_workbench/domain/adapters/)
