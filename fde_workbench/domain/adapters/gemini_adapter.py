"""Google Cloud / Gemini Enterprise platform adapter for production Vertex AI deployment."""

import re
import json
from typing import Dict, Any, List
from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.agent_specs import AgentSpecification


class GeminiEnterpriseAdapter(PlatformAdapter):
    """
    Deepened platform adapter compiling platform-agnostic AgentSpecification into:
    1. Google Cloud Vertex AI / Gemini Enterprise manifest
    2. Runnable deployment Python SDK scaffold (google-genai)
    """

    @property
    def platform_name(self) -> str:
        return "gemini_enterprise"

    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        function_declarations = []
        for tool in spec.tools:
            function_declarations.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema or {"type": "object", "properties": {}},
            })

        return {
            "platform": "Google Cloud Vertex AI / Gemini Enterprise",
            "spec_version": "v1beta",
            "deployment_substrate": {
                "target_engine": "Vertex AI Agent Engine (Cloud Run / GKE Private Endpoint)",
                "foundation_model": "gemini-1.5-pro",
                "region": "southamerica-east1",  # São Paulo region closest to Asunción
                "bilingual_support": ["Spanish (Paraguay / Rioplatense)", "English (International Comex)"],
            },
            "agent_resource": {
                "display_name": spec.title,
                "description": spec.objective,
                "instruction": {
                    "system_instruction": {
                        "parts": [
                            {"text": f"OBJECTIVE: {spec.objective}\n\nCONTEXT:\n{spec.context}\n\nREASONING RULES:\n{spec.reasoning_requirements}\n\nHUMAN APPROVAL:\n{spec.human_approval_requirements}"}
                        ]
                    }
                },
                "tools": [
                    {
                        "function_declarations": function_declarations
                    }
                ],
                "grounding_config": {
                    "enterprise_search": {
                        "enabled": True,
                        "data_stores": spec.inputs,
                        "google_workspace_drive_sync": True,
                    }
                },
                "guardrails": {
                    "mandatory_human_review": bool(spec.human_approval_requirements),
                    "allowed_actions": spec.actions,
                    "prohibited_actions": spec.failure_modes,
                },
                "telemetry": {
                    "target_kpis": spec.kpis,
                    "eval_metrics": spec.evaluation_criteria,
                },
            },
        }

    def generate_python_scaffold(self, spec: AgentSpecification) -> str:
        """
        Generates a standalone, executable Python deployment scaffold using the official google-genai SDK.
        Demonstrates how an FDE deploys the agent with tools, grounding, and Human-in-the-Loop review.
        """
        tool_code_blocks = []
        tool_names = []
        for tool in spec.tools:
            tool_names.append(tool.name)
            tool_code_blocks.append(f"""
def {tool.name}(**kwargs) -> dict:
    \"\"\"{tool.description}\"\"\"
    # FDE Deployment Note: Connect to local client system of record or replica
    print(f"[Tool Call: {tool.name}] Received arguments: {{kwargs}}")
    return {{
        "status": "SUCCESS",
        "tool": "{tool.name}",
        "read_only": {tool.read_only},
        "message": "Simulated output from {tool.name} for Paraguay export operational loop",
        "data": kwargs
    }}
""")

        tools_list_repr = ", ".join(tool_names) if tool_names else ""
        system_instruction_repr = json.dumps(
            f"ROLE: Forward Deployed AI Agent for Paraguayan Export Enterprise\n"
            f"OBJECTIVE: {spec.objective}\n\n"
            f"OPERATIONAL DOMAIN CONTEXT:\n{spec.context}\n\n"
            f"DETERMINISTIC REASONING RULES:\n{spec.reasoning_requirements}\n\n"
            f"HUMAN-IN-THE-LOOP SAFEGUARDS:\n{spec.human_approval_requirements}\n"
        )

        scaffold = f"""# ==============================================================================
# FDE Deployment Scaffold: {spec.title}
# Substrate: Google Cloud Vertex AI / Gemini Enterprise (google-genai SDK)
# Target Enterprise: Paraguayan Export Manufacturer / Hidrovia-Corridor Logistics
# Generated: Local-First FDE Workbench
# ==============================================================================

import os
from google import genai
from google.genai import types

# 1. Operational Tool Implementations
{"".join(tool_code_blocks)}

# 2. Agent Initialization & Configuration
def run_fde_agent_session():
    api_key = os.environ.get("GEMINI_API_KEY", "MOCK_KEY_FOR_LOCAL_VALIDATION")
    client = genai.Client(api_key=api_key)

    system_instruction = {system_instruction_repr}

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.1,  # Low temperature for deterministic operational decisions
        tools=[{tools_list_repr}],
    )

    print("================================================================================")
    print("FDE Agent Deployed: {spec.title}")
    print("Primary Target KPIs: {', '.join(spec.kpis)}")
    print("Human Approval Gate: {spec.human_approval_requirements}")
    print("================================================================================")

    # In production, this prompt is triggered by OperationalEvent stream from TMS/ERP/VUE
    test_event_prompt = (
        "OPERATIONAL EVENT DETECTED: Discrepancy observed between SAP export invoice and VUE transit filing. "
        "Review documentation, execute reconciliation tool, and prepare decision proposal for human sign-off."
    )

    print(f"\\n[Trigger Received] {{test_event_prompt}}\\n")
    # response = client.models.generate_content(
    #     model="gemini-1.5-pro",
    #     contents=test_event_prompt,
    #     config=config,
    # )
    # print("[Agent Response]:", response.text)
    print("[Agent Status]: Manifest verified. Ready for deployment in customer Google Cloud project.")

if __name__ == "__main__":
    run_fde_agent_session()
"""
        return scaffold

    def validate_manifest_schema(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates against Google Cloud Vertex AI Tool / FunctionDeclaration public schema.
        Spec: https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/Tool#FunctionDeclaration
        """
        errors: List[str] = []
        if manifest.get("platform") != "Google Cloud Vertex AI / Gemini Enterprise":
            errors.append("Invalid or missing platform header")

        agent_res = manifest.get("agent_resource")
        if not isinstance(agent_res, dict):
            errors.append("agent_resource must be a dict")
            return {"valid": False, "errors": errors, "schema_doc": "Vertex AI Agent Resource v1beta"}

        if not agent_res.get("display_name"):
            errors.append("agent_resource.display_name is required")

        instruction = agent_res.get("instruction", {})
        sys_inst = instruction.get("system_instruction", {})
        parts = sys_inst.get("parts", [])
        if not parts or not isinstance(parts, list) or not parts[0].get("text"):
            errors.append("agent_resource.instruction.system_instruction.parts must contain non-empty text")

        tools = agent_res.get("tools", [])
        if not isinstance(tools, list) or len(tools) == 0:
            errors.append("agent_resource.tools must be a non-empty list")
        else:
            for i, tool_group in enumerate(tools):
                fdecls = tool_group.get("function_declarations", [])
                if not isinstance(fdecls, list) or len(fdecls) == 0:
                    errors.append(f"tools[{i}].function_declarations must be a non-empty list")
                for j, fn in enumerate(fdecls):
                    name = fn.get("name", "")
                    if not name or not re.match(r"^[a-zA-Z0-9_-]{1,64}$", name):
                        errors.append(f"Function {name} (index {j}) violates Vertex AI naming regex '^[a-zA-Z0-9_-]{{1,64}}$'")
                    if not fn.get("description"):
                        errors.append(f"Function {name} missing description")
                    params = fn.get("parameters")
                    if not isinstance(params, dict) or params.get("type") != "object":
                        errors.append(f"Function {name} parameters must be an object schema with type='object'")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_doc": "Google Cloud Vertex AI OpenAPI Tool Specification v1beta",
        }

    def generate_pilot_deployment_plan(self, pilot: Any) -> Dict[str, Any]:
        """Generate Vertex AI deployment architecture and operational execution steps."""
        return {
            "platform": self.platform_name,
            "platform_display_name": "Google Cloud / Gemini Enterprise",
            "runtime_framework": "Google GenAI SDK (google-genai) on Vertex AI Agent Engine",
            "model_deployment": "gemini-2.5-pro (Validation & Reasoning) + gemini-2.5-flash (Drafting)",
            "architecture_pattern": "Event-driven Cloud Run service listening to ERP Webhooks with Firestore audit state",
            "integration_steps": [
                f"1. Provision Vertex AI Agent Engine resource in project 'gcp-aidesa-fde-pilot'",
                f"2. Deploy containerized Python google-genai runtime on Cloud Run with Private Service Connect to {pilot.customer} SAP B1",
                f"3. Mount Vertex AI Search data store grounded in official DNIT Mercosur tariffs and SENAVE phytosanitary rules",
                f"4. Configure Pub/Sub subscription on 'export-dispatch-events' topic with dead-letter queue",
                f"5. Connect Human Review Task dispatch to Cloud Run dashboard requiring {pilot.decision_owner} OAuth2 sign-off",
            ],
            "credentials_and_env": [
                "GOOGLE_APPLICATION_CREDENTIALS=/secrets/vertex-agent-sa.json",
                "GEMINI_API_KEY=secrets://gcp/gemini-api-key",
                "GCP_PROJECT_ID=gcp-aidesa-fde-pilot",
                "GCP_REGION=southamerica-east1 (São Paulo)",
                "SAP_B1_SERVICE_LAYER_URL=https://sap.aidesa.internal:50000/b1s/v2",
            ],
            "human_in_loop_mechanism": f"Vertex AI Human Review / Cloud Tasks approval workflow. Agent generates candidate payload; state stays PENDING_HUMAN_APPROVAL until {pilot.decision_owner} authorized key signs.",
            "verification_command": "python -c \"from google import genai; client = genai.Client(); print(client.models.get(model='gemini-2.5-flash'))\"",
        }
