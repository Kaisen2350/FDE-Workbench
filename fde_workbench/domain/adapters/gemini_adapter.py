"""Google Cloud / Gemini Enterprise platform adapter stub."""

from typing import Dict, Any
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
