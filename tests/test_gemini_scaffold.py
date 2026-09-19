"""Unit tests for Gemini Enterprise adapter deepening and Python SDK scaffolding."""

import unittest
from fde_workbench.domain.adapters.gemini_adapter import GeminiEnterpriseAdapter
from fde_workbench.domain.agent_specs import AgentSpecification, ToolDefinition
from fde_workbench.domain.ontology import EntityTypeEnum


class TestGeminiScaffold(unittest.TestCase):

    def setUp(self):
        self.adapter = GeminiEnterpriseAdapter()
        self.spec = AgentSpecification(
            spec_id="spec-customs-recon",
            title="Cross-Border Customs Transit Document Reconciler",
            version="1.0.0",
            objective="Reconcile SAP B1 invoices against DNIT VUE transit permits before truck dispatch",
            trigger="On shipment ready for dispatch",
            inputs=["SAP_B1_EXPORT_DOCUMENTS", "DNIT_VUE_PORTAL"],
            entities=[EntityTypeEnum.SHIPMENT, EntityTypeEnum.CUSTOMS_DECLARATION],
            context="Paraguay-Brazil border corridor through Ciudad del Este (Puente de la Amistad).",
            tools=[
                ToolDefinition(
                    name="read_vue_transit_permit",
                    description="Fetch XML declaration from DNIT VUE portal",
                    input_schema={"type": "object", "properties": {"permit_number": {"type": "string"}}, "required": ["permit_number"]},
                    read_only=True,
                ),
                ToolDefinition(
                    name="verify_weight_invoice_reconciliation",
                    description="Compare invoice net weight against weighbridge ticket",
                    input_schema={"type": "object", "properties": {"invoice_id": {"type": "string"}}, "required": ["invoice_id"]},
                    read_only=True,
                ),
            ],
            reasoning_requirements="Deterministic cross-check of NCM code, net weight, carrier RUC, and truck license plate",
            human_approval_requirements="Customs compliance broker must confirm any re-filing or correction",
            actions=["FLAG_DISCREPANCY", "NOTIFY_DISPATCHER"],
            failure_modes=["False mismatch due to rounding", "Stale customs status"],
            evaluation_criteria=["Zero undetected border documentation mismatches", "Reconciliation completed in < 60 seconds"],
            kpis=["Customs Border Dwell Time", "OTIF Delivery"],
        )

    def test_gemini_manifest_export_and_validation(self):
        manifest = self.adapter.export_manifest(self.spec)
        self.assertEqual(manifest["platform"], "Google Cloud Vertex AI / Gemini Enterprise")
        self.assertIn("deployment_substrate", manifest)
        self.assertEqual(manifest["deployment_substrate"]["foundation_model"], "gemini-1.5-pro")

        validation = self.adapter.validate_manifest_schema(manifest)
        self.assertTrue(validation["valid"], f"Validation failed: {validation.get('errors')}")

    def test_gemini_python_scaffold_generation(self):
        scaffold = self.adapter.generate_python_scaffold(self.spec)
        self.assertIn("from google import genai", scaffold)
        self.assertIn("def read_vue_transit_permit", scaffold)
        self.assertIn("def verify_weight_invoice_reconciliation", scaffold)
        self.assertIn("Cross-Border Customs Transit Document Reconciler", scaffold)
        self.assertIn("Customs compliance broker must confirm", scaffold)

        # Check Python syntax validity
        compiled = compile(scaffold, "<string>", "exec")
        self.assertIsNotNone(compiled)


if __name__ == "__main__":
    unittest.main()
