"""Unit tests for platform-agnostic agent specifications and enterprise adapters."""

import unittest
from fde_workbench.domain.agent_specs import AgentSpecification, ToolDefinition
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.adapters import ADAPTERS


class TestAdapters(unittest.TestCase):

    def setUp(self):
        self.spec = AgentSpecification(
            spec_id="test-agent-spec",
            title="Customs Auto-Reconciliation Agent",
            objective="Reconcile VUE with ERP export invoices",
            trigger="On shipment ready",
            inputs=["SAP B1 Invoice", "VUE JSON"],
            entities=[EntityTypeEnum.SHIPMENT, EntityTypeEnum.CUSTOMS_DECLARATION],
            context="Mercosur cross-border trade",
            tools=[
                ToolDefinition(
                    name="query_vue",
                    description="Query customs VUE portal",
                    input_schema={"type": "object", "properties": {"decl_id": {"type": "string"}}},
                    read_only=True,
                )
            ],
            reasoning_requirements="Deterministic matching",
            human_approval_requirements="Customs broker sign-off",
            actions=["Issue Green Gate Pass", "Flag Discrepancy"],
            failure_modes=["API timeout"],
            evaluation_criteria=["100% NCM precision"],
            kpis=["Customs Dwell Hours"],
        )

    def test_all_enterprise_adapters_compile(self):
        platforms = ["gemini", "openai", "microsoft", "databricks"]
        for p in platforms:
            self.assertIn(p, ADAPTERS)
            adapter = ADAPTERS[p]
            manifest = adapter.export_manifest(self.spec)
            self.assertIsInstance(manifest, dict)
            self.assertIn("platform", manifest)

            compat = adapter.validate_compatibility(self.spec)
            self.assertTrue(compat["compatible"])
            self.assertTrue(compat["human_in_loop_enforced"])


if __name__ == "__main__":
    unittest.main()
