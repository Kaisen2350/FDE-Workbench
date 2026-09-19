"""Base interface for enterprise AI platform adapters."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from fde_workbench.domain.agent_specs import AgentSpecification


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific compilation of agent specifications."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """The enterprise platform identifier (e.g. 'gemini_enterprise', 'openai', etc.)."""
        pass

    @abstractmethod
    def export_manifest(self, spec: AgentSpecification) -> Dict[str, Any]:
        """Compile a platform-agnostic specification into a platform-compliant configuration manifest."""
        pass

    @abstractmethod
    def validate_manifest_schema(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an exported manifest against the platform's public schema specifications."""
        pass

    @abstractmethod
    def generate_pilot_deployment_plan(self, pilot: Any) -> Dict[str, Any]:
        """Generate platform-specific deployment architecture and installation steps for a pilot."""
        pass

    def validate_deployment_plan_schema(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a generated deployment plan against required enterprise deployment schema.
        Combines:
        1. FDE Operational Blueprint requirements (steps, credentials, human gates).
        2. Real public vendor schema validation of the embedded platform-native manifest.
        """
        errors: List[str] = []
        required_fields = [
            "platform",
            "platform_display_name",
            "runtime_framework",
            "model_deployment",
            "architecture_pattern",
            "integration_steps",
            "credentials_and_env",
            "human_in_loop_mechanism",
            "verification_command",
            "platform_manifest",
        ]
        for field in required_fields:
            val = plan.get(field)
            if val is None or (isinstance(val, (str, list, dict)) and len(val) == 0):
                errors.append(f"Missing or empty required deployment plan field: '{field}'")

        if plan.get("platform") != self.platform_name:
            errors.append(f"Deployment plan platform '{plan.get('platform')}' does not match adapter platform '{self.platform_name}'")

        steps = plan.get("integration_steps", [])
        if isinstance(steps, list):
            if len(steps) < 3:
                errors.append(f"Deployment plan must specify at least 3 integration steps (found {len(steps)})")
        else:
            errors.append("integration_steps must be a list of strings")

        creds = plan.get("credentials_and_env", [])
        if isinstance(creds, list):
            if len(creds) < 1:
                errors.append("credentials_and_env must specify at least 1 credential or environment variable")
        else:
            errors.append("credentials_and_env must be a list of strings")

        hil = str(plan.get("human_in_loop_mechanism", "")).lower()
        if not any(k in hil for k in ["human", "review", "approval", "consent", "gate", "sign"]):
            errors.append("human_in_loop_mechanism must explicitly define human oversight/approval gates")

        # Validate embedded platform-native manifest against real vendor schema
        manifest = plan.get("platform_manifest")
        manifest_val = None
        if manifest and isinstance(manifest, dict):
            manifest_val = self.validate_manifest_schema(manifest)
            if not manifest_val.get("valid"):
                for m_err in manifest_val.get("errors", []):
                    errors.append(f"Vendor Manifest Schema Error: {m_err}")

        return {
            "valid": len(errors) == 0,
            "platform": self.platform_name,
            "errors": errors,
            "schema_doc": "Enterprise FDE Deployment Plan Specification v1.1",
            "vendor_schema_status": manifest_val.get("schema_doc") if manifest_val else "Not Validated",
            "infrastructure_schema_status": (
                "Reference Architecture — Cloud providers (Google Cloud, Azure, Databricks, OpenAI) "
                "publish formal JSON schemas for tool calling and API payloads, but deployment infrastructure "
                "topologies (Cloud Run, Container Apps, Clusters) adhere to vendor Well-Architected frameworks "
                "and IaC templates rather than universal runtime JSON schemas."
            ),
        }

    def validate_compatibility(self, spec: AgentSpecification) -> Dict[str, Any]:
        """Check whether the agent specification satisfies platform-specific requirements."""
        missing_fields: List[str] = []
        if not spec.objective:
            missing_fields.append("objective")
        if not spec.tools:
            missing_fields.append("tools")
        return {
            "platform": self.platform_name,
            "compatible": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "tool_count": len(spec.tools),
            "human_in_loop_enforced": bool(spec.human_approval_requirements),
        }
