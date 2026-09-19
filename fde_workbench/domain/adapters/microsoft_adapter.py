"""Microsoft Azure AI Foundry / Semantic Kernel platform adapter stub."""

from typing import Dict, Any, List
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

    def validate_manifest_schema(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates against Microsoft Semantic Kernel Plugin & Azure AI Agent manifest specification.
        Spec: https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/
        """
        errors: List[str] = []
        if manifest.get("platform") != "Microsoft Azure AI Foundry / Semantic Kernel":
            errors.append("Invalid platform header")

        agent_def = manifest.get("agent_definition")
        if not isinstance(agent_def, dict):
            errors.append("agent_definition must be a dict")
            return {"valid": False, "errors": errors, "schema_doc": "Azure AI Foundry / Semantic Kernel Agent"}

        if not agent_def.get("id"):
            errors.append("agent_definition.id is required")
        if not agent_def.get("displayName"):
            errors.append("agent_definition.displayName is required")
        if not agent_def.get("promptTemplate"):
            errors.append("agent_definition.promptTemplate is required")

        plugins = agent_def.get("plugins", [])
        if not isinstance(plugins, list) or len(plugins) == 0:
            errors.append("plugins must be a non-empty list")
        else:
            for i, p in enumerate(plugins):
                if not p.get("plugin_name"):
                    errors.append(f"plugins[{i}].plugin_name is required")
                if not p.get("description"):
                    errors.append(f"plugins[{i}].description is required")
                if p.get("execution_policy") not in ("ReadOnly", "RequiresConsent"):
                    errors.append(f"plugins[{i}].execution_policy must be 'ReadOnly' or 'RequiresConsent'")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_doc": "Microsoft Azure AI Foundry & Semantic Kernel Plugin Specification",
        }

    def generate_pilot_deployment_plan(self, pilot: Any) -> Dict[str, Any]:
        """Generate Azure AI Foundry / Semantic Kernel deployment architecture."""
        plugin_name = "CustomsClearancePlugin" if "customs" in pilot.pilot_id else "FluvialDraftPlugin"
        return {
            "platform": self.platform_name,
            "platform_display_name": "Microsoft Azure AI Foundry",
            "runtime_framework": "Microsoft Semantic Kernel (C# / Python) on Azure Container Apps",
            "model_deployment": "Azure OpenAI Service: gpt-4o (Reasoning) + gpt-4o-mini (Extraction)",
            "architecture_pattern": "Azure Container App microservice with Azure Service Bus and Cosmos DB audit state",
            "integration_steps": [
                f"1. Provision Azure AI Foundry hub and project in 'rg-aidesa-fde-pilot' (Brazil South region)",
                f"2. Deploy Semantic Kernel agent with native plugins for {pilot.customer} SAP B1 Service Layer read operations",
                f"3. Configure Azure AI Search index with hybrid vector/semantic search over Customs and CRT regulations",
                f"4. Implement Semantic Kernel Filter enforcing 'RequiresConsent' policy on all state-mutating actions",
                f"5. Route pending reconciliations to Microsoft Teams Adaptive Card for {pilot.decision_owner} 1-click approval",
            ],
            "credentials_and_env": [
                "AZURE_OPENAI_ENDPOINT=https://aidesa-ai-foundry.openai.azure.com/",
                "AZURE_OPENAI_API_KEY=secrets://azure/keyvault/openai-key",
                "AZURE_SUBSCRIPTION_ID=sub-aidesa-pilot-001",
                "AZURE_RESOURCE_GROUP=rg-aidesa-fde-pilot",
                "AZURE_REGION=brazilsouth (São Paulo)",
            ],
            "human_in_loop_mechanism": f"Semantic Kernel Function Invocation Filter intercepting tool calls; blocks execution and posts Adaptive Card to Teams until {pilot.decision_owner} approval callback is received.",
            "verification_command": "az cognitiveservices account show --name aidesa-ai-foundry --resource-group rg-aidesa-fde-pilot",
            "platform_manifest": {
                "platform": "Microsoft Azure AI Foundry / Semantic Kernel",
                "agent_definition": {
                    "id": pilot.pilot_id,
                    "displayName": pilot.title,
                    "description": f"FDE agent for {pilot.customer} - {pilot.workflow}",
                    "promptTemplate": (
                        f"<system>\n"
                        f"Objective: {pilot.decision}\n"
                        f"Operational Context: {pilot.workflow}\n"
                        f"Human Gate: {pilot.human_approval_required}\n"
                        f"</system>"
                    ),
                    "plugins": [
                        {
                            "plugin_name": plugin_name,
                            "description": f"Operational execution plugin for {pilot.decision}",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "reference_id": {"type": "string", "description": "Tracking identifier"},
                                },
                                "required": ["reference_id"],
                            },
                            "execution_policy": "RequiresConsent",
                        }
                    ],
                    "governance": {
                        "responsibleAiPolicy": "StrictParaguayExportGRC",
                        "humanInTheLoopGates": [pilot.human_approval_required],
                        "targetKpiList": [f"error_rate_target: {pilot.target_kpi.get('error_rate', 1.0)}%"],
                    },
                },
            },
        }

    def validate_deployment_plan_schema(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment plan against Azure AI Foundry / Semantic Kernel requirements."""
        result = super().validate_deployment_plan_schema(plan)
        errors = list(result.get("errors", []))

        creds = " ".join(plan.get("credentials_and_env", []))
        if "AZURE" not in creds:
            errors.append("Azure AI Foundry deployment plan must specify AZURE credentials/endpoint")

        runtime = str(plan.get("runtime_framework", "")).lower()
        if "semantic kernel" not in runtime and "azure" not in runtime:
            errors.append("Azure deployment plan runtime_framework must reference Semantic Kernel or Azure Container Apps")

        result["valid"] = len(errors) == 0
        result["errors"] = errors
        result["schema_doc"] = "Microsoft Azure AI Foundry Agent Deployment Plan Specification (Semantic Kernel Plugin Manifest)"
        result["vendor_schema_url"] = "https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/"
        return result

