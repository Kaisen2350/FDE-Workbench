"""Unit test suite for FDE Pilot Engine, Economic Bridge, Brief Generator, and Multi-Platform Proof."""

import unittest
from fastapi.testclient import TestClient

from fde_workbench.domain.pilots import PilotSpecification, PilotEconomicModel, PilotStatus
from fde_workbench.domain.brief_generator import FDEBriefGenerator
from fde_workbench.domain.adapters import ADAPTERS
from fde_workbench.domain.provenance import ProvenanceType
from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.synthetic.generator import seed_synthetic_company
from fde_workbench.api.app import app, store


class TestPilotEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_synthetic_company(store)
        cls.client = TestClient(app)

    def test_pilot_economic_model_math(self):
        """Verify mathematical integrity of the FDE economic bridge calculation."""
        econ = PilotEconomicModel(
            annual_decision_volume=1800,
            manual_effort_minutes_per_decision=14.0,
            hourly_labor_cost_usd=25.0,
            current_error_or_exception_rate=0.065,
            cost_per_exception_usd=850.0,
            target_manual_effort_minutes=3.0,
            target_exception_rate=0.015,
            pilot_decision_volume=100,
            pilot_implementation_cost_usd=15000.0,
            annual_software_subscription_usd=18000.0,
            working_capital_acceleration_days=3.5,
            annual_working_capital_financial_value_usd=22000.0,
        )

        # Baseline:
        # Labor: 1800 * (14/60) * 25 = 10,500
        self.assertAlmostEqual(econ.baseline_annual_labor_cost(), 10500.0, places=2)
        # Exception: 1800 * 0.065 * 850 = 99,450
        self.assertAlmostEqual(econ.baseline_annual_exception_cost(), 99450.0, places=2)
        # Total baseline: 10,500 + 99,450 + 22,000 = 131,950
        self.assertAlmostEqual(econ.baseline_annual_total_cost(), 131950.0, places=2)

        # Target:
        # Labor: 1800 * (3/60) * 25 = 2,250
        self.assertAlmostEqual(econ.target_annual_labor_cost(), 2250.0, places=2)
        # Exception: 1800 * 0.015 * 850 = 22,950
        self.assertAlmostEqual(econ.target_annual_exception_cost(), 22950.0, places=2)
        # Total target: 2,250 + 22,950 = 25,200
        self.assertAlmostEqual(econ.target_annual_total_cost(), 25200.0, places=2)

        # Addressable savings: 131,950 - 25,200 = 106,750
        self.assertAlmostEqual(econ.addressable_annual_savings(), 106750.0, places=2)
        # Per unit savings: 106,750 / 1800 = 59.3055...
        self.assertAlmostEqual(econ.savings_per_decision_unit(), 106750.0 / 1800.0, places=2)
        # Pilot batch value: 100 * (106,750 / 1800) = ~5,930.56
        self.assertAlmostEqual(econ.pilot_measured_value(), 100 * (106750.0 / 1800.0), places=2)

        # Net first-year ROI: 106,750 - 15,000 - 18,000 = 73,750
        self.assertAlmostEqual(econ.first_year_net_roi_usd(), 73750.0, places=2)
        # ROI %: (73,750 / 15,000) * 100 = 491.666...%
        self.assertAlmostEqual(econ.expected_roi_percentage(), (73750.0 / 15000.0) * 100.0, places=1)
        # Payback period: 15,000 / (106,750 / 12) = ~1.686 months
        self.assertAlmostEqual(econ.payback_period_months(), 15000.0 / (106750.0 / 12.0), places=1)

        summary = econ.summary()
        self.assertEqual(summary["baseline_annual_total_usd"], 131950.0)
        self.assertEqual(summary["target_annual_total_usd"], 25200.0)
        self.assertEqual(summary["addressable_annual_savings_usd"], 106750.0)
        self.assertEqual(summary["first_year_net_roi_usd"], 73750.0)
        self.assertEqual(summary["expected_roi_percentage"], 491.7)
        self.assertEqual(summary["payback_period_months"], 1.7)

    def test_brief_generator_12_sections(self):
        """Ensure client deployment brief adheres strictly to the 12-section standard."""
        pilot = store.get_pilot("pilot-2026-customs-recon")
        self.assertIsNotNone(pilot)

        md = FDEBriefGenerator.generate_markdown(pilot)
        required_sections = [
            "## 1. Operational Problem",
            "## 2. Empirical Evidence",
            "## 3. Decision Loop",
            "## 4. Economic Impact & ROI Equation",
            "## 5. Proposed AI Intervention",
            "## 6. Human Authority & Governance",
            "## 7. Required Data & Telemetry",
            "## 8. Architecture & Integration Pattern",
            "## 9. Pilot Scope & Duration",
            "## 10. Success & Acceptance Criteria",
            "## 11. Enterprise Platform Options",
            "## 12. Expansion Path & Flywheel Leverage",
        ]
        for sec in required_sections:
            self.assertIn(sec, md, f"Missing required section: {sec}")

        # Check critical content elements
        self.assertIn(pilot.title, md)
        self.assertIn(pilot.customer, md)
        self.assertIn(pilot.decision_owner, md)
        self.assertIn("106,750.00", md)
        self.assertIn("Gemini Enterprise", md)
        self.assertIn("Azure AI Foundry", md)
        self.assertIn("Databricks Mosaic AI", md)

        # Structured data verification
        data = FDEBriefGenerator.generate_brief_data(pilot)
        self.assertEqual(data["pilot_id"], pilot.pilot_id)
        self.assertEqual(data["customer"], pilot.customer)
        self.assertIn("sections", data)
        self.assertIn("4_economic_impact", data["sections"])
        self.assertIn("6_human_authority", data["sections"])
        self.assertIn("11_platform_options", data["sections"])
        self.assertEqual(len(data["sections"]["11_platform_options"]["platform_breakdown"]), 4)

    def test_multi_platform_deployment_proof(self):
        """Verify that all 4 platform adapters generate valid enterprise deployment plans."""
        pilot = store.get_pilot("pilot-2026-customs-recon")
        self.assertIsNotNone(pilot)

        platforms = ["gemini", "microsoft", "openai", "databricks"]
        for p in platforms:
            adapter = ADAPTERS.get(p)
            self.assertIsNotNone(adapter, f"Adapter not found for platform: {p}")
            plan = adapter.generate_pilot_deployment_plan(pilot)
            self.assertIn("platform", plan)
            self.assertIn("runtime_framework", plan)
            self.assertIn("integration_steps", plan)
            self.assertGreater(len(plan["integration_steps"]), 0)
            self.assertIn("credentials_and_env", plan)
            self.assertIn("human_in_loop_mechanism", plan)
            self.assertIn("verification_command", plan)
            # Ensure customer name and decision owner are propagated
            self.assertIn(pilot.customer, str(plan))

    def test_api_list_pilots(self):
        res = self.client.get("/api/pilots")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["count"], 2)
        pilot_ids = [p["pilot_id"] for p in data["pilots"]]
        self.assertIn("pilot-2026-customs-recon", pilot_ids)
        self.assertIn("pilot-2026-fluvial-draft", pilot_ids)

    def test_api_get_pilot_detail(self):
        res = self.client.get("/api/pilots/pilot-2026-customs-recon")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["pilot"]["pilot_id"], "pilot-2026-customs-recon")
        self.assertIn("economics_summary", data)
        self.assertEqual(data["economics_summary"]["expected_roi_percentage"], 491.7)

    def test_api_get_pilot_brief(self):
        res = self.client.get("/api/pilots/pilot-2026-customs-recon/brief")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("brief_markdown", data)
        self.assertIn("## 1. Operational Problem", data["brief_markdown"])
        self.assertIn("brief_data", data)
        self.assertEqual(data["brief_data"]["pilot_id"], "pilot-2026-customs-recon")

    def test_api_get_economic_bridge(self):
        res = self.client.get("/api/pilots/pilot-2026-customs-recon/economic-bridge")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["pilot_id"], "pilot-2026-customs-recon")
        self.assertEqual(len(data["calculation_steps"]), 10)
        self.assertEqual(data["calculation_steps"][5]["name"], "Addressable Annual Savings")

    def test_api_get_deployment_plan(self):
        res = self.client.get("/api/pilots/pilot-2026-customs-recon/deployment-plan?platform=databricks_mosaic_ai")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["platform"], "databricks_mosaic_ai")
        self.assertIn("Mosaic AI", data["deployment_plan"]["runtime_framework"])

    def test_api_set_platform(self):
        res = self.client.post("/api/pilots/pilot-2026-customs-recon/platform", json={"platform": "microsoft_azure_ai_foundry"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["selected_platform"], "microsoft_azure_ai_foundry")

        # Verify persisted in store
        pilot = store.get_pilot("pilot-2026-customs-recon")
        self.assertEqual(pilot.selected_platform, "microsoft_azure_ai_foundry")

        # Reset back to gemini_enterprise
        self.client.post("/api/pilots/pilot-2026-customs-recon/platform", json={"platform": "gemini_enterprise"})

    def test_api_set_status(self):
        res = self.client.post("/api/pilots/pilot-2026-customs-recon/status", json={"status": "APPROVED"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["new_status"], "APPROVED")

        # Verify persisted
        pilot = store.get_pilot("pilot-2026-customs-recon")
        self.assertEqual(pilot.status, PilotStatus.APPROVED)

        # Reset back
        self.client.post("/api/pilots/pilot-2026-customs-recon/status", json={"status": "PROPOSED"})


if __name__ == "__main__":
    unittest.main()
