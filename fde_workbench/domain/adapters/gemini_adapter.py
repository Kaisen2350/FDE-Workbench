"""Google Cloud / Gemini Enterprise platform adapter stub."""

import re
from typing import Dict, Any, List
from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.agent_specs import AgentSpecification


class GeminiEnterpriseAdapter(PlatformAdapter):
    """Compiles platform-agnostic AgentSpecification into Vertex AI / Gemini Enterprise manifest."""

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
            "schema_doc": "Google Cloud Vertex AI Tool / FunctionDeclaration Specification (v1beta)",
        }
