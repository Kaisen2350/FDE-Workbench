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
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema or {"type": "object", "properties": {}},
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
        Validates against OpenAI Assistants API Tool definition schema.
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
                if fn.get("strict") is not True:
                    errors.append(f"Tool {i} function strict mode should be True for deterministic execution")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_doc": "OpenAI Assistants API Function Tool Specification",
        }

    def generate_pilot_deployment_plan(self, pilot: Any) -> Dict[str, Any]:
        """Generate OpenAI Enterprise deployment architecture and execution steps."""
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
        }
