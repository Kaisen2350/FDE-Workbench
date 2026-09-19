"""OpenAI Assistants / Function Calling platform adapter stub."""

import re
from typing import Dict, Any, List
from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.agent_specs import AgentSpecification


class OpenAIAdapter(PlatformAdapter):
    """Compiles platform-agnostic AgentSpecification into OpenAI Assistant API manifest."""

    @property
    def platform_name(self) -> str:
        return "openai"

    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        tools = []
        for tool in spec.tools:
            params = dict(tool.input_schema) if tool.input_schema else {"type": "object", "properties": {}}
            if "type" not in params:
                params["type"] = "object"
            if "properties" not in params:
                params["properties"] = {}
            if "required" not in params:
                params["required"] = list(params.get("properties", {}).keys())
            if "additionalProperties" not in params:
                params["additionalProperties"] = False

            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": params,
                    "strict": True,
                },
            })

        return {
            "platform": "OpenAI Assistants API",
            "name": spec.title,
            "description": spec.objective,
            "instructions": (
                f"OBJECTIVE: {spec.objective}\n\n"
                f"OPERATIONAL CONTEXT:\n{spec.context}\n\n"
                f"REASONING PROTOCOL:\n{spec.reasoning_requirements}\n\n"
                f"HUMAN APPROVAL REQUIREMENTS:\n{spec.human_approval_requirements}"
            ),
            "tools": tools,
            "metadata": {
                "spec_id": spec.spec_id,
                "version": spec.version,
                "entities": [e.value for e in spec.entities],
                "allowed_actions": spec.actions,
                "kpis": spec.kpis,
            },
        }

    def validate_manifest_schema(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates against official OpenAI Assistants API v2 Function Calling JSON Schema.
        Spec: https://platform.openai.com/docs/api-reference/assistants/createAssistant#assistants-createassistant-tools
        """
        errors: List[str] = []
        if manifest.get("platform") != "OpenAI Assistants API":
            errors.append("Invalid platform header")

        if not manifest.get("name"):
            errors.append("Assistant 'name' is required")
        if not manifest.get("instructions"):
            errors.append("Assistant 'instructions' is required")

        tools = manifest.get("tools", [])
        if not isinstance(tools, list) or len(tools) == 0:
            errors.append("tools must be a non-empty list")
        else:
            for i, tool in enumerate(tools):
                if tool.get("type") != "function":
                    errors.append(f"tools[{i}].type must be 'function'")
                fn = tool.get("function", {})
                name = fn.get("name", "")
                if not name or not re.match(r"^[a-zA-Z0-9_-]{1,64}$", name):
                    errors.append(f"Tool {i} function name '{name}' violates regex '^[a-zA-Z0-9_-]{{1,64}}$'")
                if not fn.get("description"):
                    errors.append(f"Tool {i} function missing description")
                params = fn.get("parameters")
                if not isinstance(params, dict) or params.get("type") != "object":
                    errors.append(f"Tool {i} function parameters must be an object schema with type='object'")
                else:
                    if fn.get("strict") is True:
                        if params.get("additionalProperties") is not False:
                            errors.append(f"Tool {i} strict function schema requires 'additionalProperties: false'")
                        props = params.get("properties", {})
                        reqs = params.get("required", [])
                        for prop_key in props:
                            if prop_key not in reqs:
                                errors.append(f"Tool {i} strict function schema requires property '{prop_key}' to be in 'required'")
                if fn.get("strict") is not True:
                    errors.append(f"Tool {i} function strict mode should be True for deterministic execution")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_doc": "OpenAI Assistants API v2 Function Calling Specification (strict: true)",
            "vendor_schema_url": "https://platform.openai.com/docs/guides/function-calling",
        }

    def generate_pilot_deployment_plan(self, pilot: Any) -> Dict[str, Any]:
        """Generate OpenAI Enterprise deployment architecture and execution steps."""
        fn_name = "reconcile_customs_clearance_pack" if "customs" in pilot.pilot_id else "optimize_fluvial_convoy_draft"
        return {
            "platform": self.platform_name,
            "platform_display_name": "OpenAI Enterprise",
            "runtime_framework": "OpenAI Assistants API v2 with Strict Structured Outputs",
            "model_deployment": "gpt-4o-2024-08-06 (Structured Outputs) with strict: true",
            "architecture_pattern": "FastAPI Webhook gateway orchestrating OpenAI Assistants runs with PostgreSQL session persistence",
            "integration_steps": [
                f"1. Create dedicated OpenAI Project '{pilot.customer}-FDE-Pilot' with enterprise data privacy (zero training)",
                f"2. Upload customs tariff code vectors and SOP manuals to OpenAI Vector Store 'vs_customs_py'",
                f"3. Register Assistant with strict tool definitions matching {pilot.title} schemas",
                f"4. Implement run poller handling 'requires_action' tool calls with human verification gate",
                f"5. Deliver reconciled payloads to {pilot.decision_owner} operational queue via internal webhook",
            ],
            "credentials_and_env": [
                "OPENAI_API_KEY=sk-proj-secrets://vault/openai-aidesa",
                "OPENAI_PROJECT_ID=proj_aidesa_fde_001",
                "OPENAI_VECTOR_STORE_ID=vs_customs_mercosur_001",
            ],
            "human_in_loop_mechanism": f"Assistant Run pauses in 'requires_action' state. Application waits for {pilot.decision_owner} approval in operator portal before submitting tool outputs back to the Run.",
            "verification_command": "curl https://api.openai.com/v1/models -H \"Authorization: Bearer $OPENAI_API_KEY\"",
            "platform_manifest": {
                "platform": "OpenAI Assistants API",
                "name": pilot.title[:64],
                "description": f"FDE agent for {pilot.customer} - {pilot.workflow}",
                "instructions": (
                    f"OBJECTIVE: {pilot.decision}\n\n"
                    f"OPERATIONAL WORKFLOW: {pilot.workflow}\n\n"
                    f"HUMAN APPROVAL GATE: {pilot.human_approval_required}"
                ),
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "description": f"Operational execution tool for {pilot.decision}",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "reference_id": {
                                        "type": "string",
                                        "description": "Operational shipment or declaration reference ID",
                                    },
                                    "batch_count": {
                                        "type": "integer",
                                        "description": "Number of dispatch units in batch",
                                    },
                                },
                                "required": ["reference_id", "batch_count"],
                                "additionalProperties": False,
                            },
                            "strict": True,
                        },
                    }
                ],
            },
        }

    def validate_deployment_plan_schema(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment plan against OpenAI Assistants API requirements."""
        result = super().validate_deployment_plan_schema(plan)
        errors = list(result.get("errors", []))

        creds = " ".join(plan.get("credentials_and_env", []))
        if "OPENAI" not in creds:
            errors.append("OpenAI deployment plan must specify OPENAI_API_KEY")

        runtime = str(plan.get("runtime_framework", "")).lower()
        if "assistants" not in runtime:
            errors.append("OpenAI deployment plan runtime_framework must reference OpenAI Assistants API")

        result["valid"] = len(errors) == 0
        result["errors"] = errors
        result["schema_doc"] = "OpenAI Enterprise Assistants Deployment Plan Specification (Tools v2 strict: true)"
        result["vendor_schema_url"] = "https://platform.openai.com/docs/guides/function-calling"
        return result

