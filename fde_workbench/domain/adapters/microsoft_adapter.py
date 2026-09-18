"""Microsoft Azure AI Foundry / Semantic Kernel platform adapter stub."""

from typing import Dict, Any
from fde_workbench.domain.adapters.base import PlatformAdapter
from fde_workbench.domain.agent_specs import AgentSpecification


class MicrosoftAdapter(PlatformAdapter):
    """Compiles platform-agnostic AgentSpecification into Azure AI Foundry / Semantic Kernel manifest."""

    @property
    def platform_name(self) -> str:
        return "microsoft_azure"

    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        plugins = []
        for tool in spec.tools:
            plugins.append({
                "plugin_name": tool.name,
                "description": tool.description,
                "schema": tool.input_schema,
                "execution_policy": "ReadOnly" if tool.read_only else "RequiresConsent",
            })

        return {
            "platform": "Microsoft Azure AI Foundry / Semantic Kernel",
            "agent_definition": {
                "id": spec.spec_id,
                "displayName": spec.title,
                "description": spec.objective,
                "promptTemplate": (
                    f"<system>\n"
                    f"Objective: {spec.objective}\n"
                    f"Domain Context: {spec.context}\n"
                    f"Rules: {spec.reasoning_requirements}\n"
                    f"Human In The Loop: {spec.human_approval_requirements}\n"
                    f"</system>"
                ),
                "plugins": plugins,
                "governance": {
                    "responsibleAiPolicy": "StrictParaguayExportGRC",
                    "humanInTheLoopGates": [spec.human_approval_requirements],
                    "targetKpiList": spec.kpis,
                },
            },
        }
