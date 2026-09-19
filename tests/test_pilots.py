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
        # Total investment: 15,000 + 18,000 = 33,000
        self.assertEqual(econ.total_investment_usd(), 33000.0)
        # Reconciled ROI %: (73,750 / 33,000) * 100 = 223.4848...% -> 223.5%
        expected_reconciled_roi = (73750.0 / 33000.0) * 100.0
        self.assertAlmostEqual(econ.expected_roi_percentage(), expected_reconciled_roi, places=1)
        # Payback period: 15,000 / (106,750 / 12) = ~1.686 months
        self.assertAlmostEqual(econ.payback_period_months(), 15000.0 / (106750.0 / 12.0), places=1)

        summary = econ.summary()
        self.assertEqual(summary["baseline_annual_total_usd"], 131950.0)
        self.assertEqual(summary["target_annual_total_usd"], 25200.0)
        self.assertEqual(summary["addressable_annual_savings_usd"], 106750.0)
        self.assertEqual(summary["first_year_net_roi_usd"], 73750.0)
        self.assertEqual(summary["total_first_year_investment_usd"], 33000.0)
        self.assertEqual(summary["expected_roi_percentage"], 223.5)
        self.assertEqual(summary["payback_period_months"], 1.7)
        self.assertIn("sensitivity_analysis", summary)

    def test_reconciled_roi_percentage_formula_integrity(self):
        """Independent mathematical unit test proving no formula drift in ROI percentage."""
        econ = PilotEconomicModel(
            annual_decision_volume=2000,
            manual_effort_minutes_per_decision=20.0,
            hourly_labor_cost_usd=30.0,
            current_error_or_exception_rate=0.05,
            cost_per_exception_usd=1000.0,
            target_manual_effort_minutes=5.0,
            target_exception_rate=0.01,
            pilot_decision_volume=50,
            pilot_implementation_cost_usd=20000.0,
            annual_software_subscription_usd=10000.0,
            annual_working_capital_financial_value_usd=10000.0,
        )
        # Savings:
        # Baseline = 2000*(20/60)*30 + 2000*0.05*1000 + 10000 = 20000 + 100000 + 10000 = 130,000
        # Target = 2000*(5/60)*30 + 2000*0.01*1000 = 5000 + 20000 = 25,000
        # Savings = 105,000
        # Total Investment = 20,000 + 10,000 = 30,000
        # Net ROI ($) = 105,000 - 30,000 = 75,000
        # Formula: Net 1st-Year ROI / (Implementation Cost + Annual Software License) * 100
        # ROI % = (75,000 / 30,000) * 100 = 250.0%
        net_roi_usd = econ.first_year_net_roi_usd()
        total_outlay = econ.pilot_implementation_cost_usd + econ.annual_software_subscription_usd
        expected_roi_pct = (net_roi_usd / total_outlay) * 100.0

        self.assertEqual(econ.expected_roi_percentage(), expected_roi_pct)
        self.assertEqual(econ.expected_roi_percentage(), 250.0)

    def test_assumptions_ledger(self):
        """Verify that every economic model parameter is tracked with operational rationale."""
        pilot = store.get_pilot("pilot-2026-customs-recon")
        econ = pilot.economic_model
        table = econ.get_assumptions_table()

        self.assertGreaterEqual(len(table), 12)
        params = [item["parameter"] for item in table]
        self.assertIn("annual_decision_volume", params)
        self.assertIn("cost_per_exception_usd", params)
        self.assertIn("pilot_implementation_cost_usd", params)
        self.assertIn("annual_software_subscription_usd", params)
        self.assertIn("working_capital_acceleration_days", params)

        for item in table:
            self.assertTrue(len(item["source_or_rationale"]) > 10, f"Rationale too short for {item['parameter']}")

    def test_sensitivity_analysis_scenarios(self):
        """Verify Low (-20%), Mid (Base), and High (+20%) sensitivity scenarios."""
        pilot = store.get_pilot("pilot-2026-customs-recon")
        econ = pilot.economic_model
        sens = econ.compute_sensitivity(variance=0.20)

        self.assertEqual(sens["variance_pct"], 20.0)
        scenarios = sens["scenarios"]
        self.assertIn("low_conservative", scenarios)
        self.assertIn("mid_base_case", scenarios)
        self.assertIn("high_optimistic", scenarios)

        low = scenarios["low_conservative"]
        mid = scenarios["mid_base_case"]
        high = scenarios["high_optimistic"]

        # Volume must follow variance
        self.assertEqual(mid["annual_volume"], 1800)
        self.assertEqual(low["annual_volume"], 1440)  # -20%
        self.assertEqual(high["annual_volume"], 2160)  # +20%

        # Monotonicity check: Savings & Net ROI must strictly increase Low < Mid < High
        self.assertLess(low["addressable_annual_savings_usd"], mid["addressable_annual_savings_usd"])
        self.assertLess(mid["addressable_annual_savings_usd"], high["addressable_annual_savings_usd"])
        self.assertLess(low["net_first_year_roi_usd"], mid["net_first_year_roi_usd"])
        self.assertLess(mid["net_first_year_roi_usd"], high["net_first_year_roi_usd"])
        self.assertLess(low["roi_percentage"], mid["roi_percentage"])
        self.assertLess(mid["roi_percentage"], high["roi_percentage"])

        # Payback period must decrease Low > Mid > High
        self.assertGreater(low["payback_period_months"], mid["payback_period_months"])
        self.assertGreater(mid["payback_period_months"], high["payback_period_months"])

    def test_synthetic_data_watermark(self):
        """Verify that synthetic watermark notice is present across brief and API."""
        pilot = store.get_pilot("pilot-2026-customs-recon")
        md = FDEBriefGenerator.generate_markdown(pilot)
        self.assertIn("Illustrative — based on synthetic AIDESA data, pending client-specific baseline validation", md)

        data = FDEBriefGenerator.generate_brief_data(pilot)
        self.assertIn("watermark", data)
        self.assertIn("synthetic AIDESA data", data["watermark"])

        res = self.client.get("/api/pilots/pilot-2026-customs-recon/economic-bridge")
        self.assertEqual(res.status_code, 200)
        bridge_data = res.json()
        self.assertIn("watermark", bridge_data)
        self.assertIn("Illustrative — based on synthetic AIDESA data", bridge_data["watermark"])

    def test_adapter_deployment_plan_schema_validation(self):
        """Verify that validate_deployment_plan_schema validates plans across all 4 platforms."""
        pilot = store.get_pilot("pilot-2026-customs-recon")
        self.assertIsNotNone(pilot)

        for p_name in ["gemini", "microsoft", "openai", "databricks"]:
            adapter = ADAPTERS[p_name]
            plan = adapter.generate_pilot_deployment_plan(pilot)
            validation = adapter.validate_deployment_plan_schema(plan)
            self.assertTrue(validation["valid"], f"Validation failed for {p_name}: {validation.get('errors')}")
            self.assertEqual(len(validation["errors"]), 0)

        # Negative test: missing fields or invalid platform
        gemini_adapter = ADAPTERS["gemini"]
        invalid_plan = {"platform": "wrong_platform", "integration_steps": ["step1"]}
        bad_val = gemini_adapter.validate_deployment_plan_schema(invalid_plan)
        self.assertFalse(bad_val["valid"])
        self.assertGreater(len(bad_val["errors"]), 0)

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
        self.assertIn("33,000.00", md)
        self.assertIn("223.5%", md)
        self.assertIn("Gemini Enterprise", md)
        self.assertIn("Azure AI Foundry", md)
        self.assertIn("Databricks Mosaic AI", md)

        # Assumptions Ledger & Sensitivity table headers in Markdown
        self.assertIn("### Assumptions Ledger", md)
        self.assertIn("### Sensitivity Analysis", md)

        # Structured data verification
        data = FDEBriefGenerator.generate_brief_data(pilot)
        self.assertEqual(data["pilot_id"], pilot.pilot_id)
        self.assertEqual(data["customer"], pilot.customer)
        self.assertIn("sections", data)
        self.assertIn("4_economic_impact", data["sections"])
        self.assertIn("assumptions_ledger", data["sections"]["4_economic_impact"])
        self.assertIn("sensitivity_analysis", data["sections"]["4_economic_impact"])
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
            self.assertGreaterEqual(len(plan["integration_steps"]), 3)
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
        self.assertEqual(data["economics_summary"]["expected_roi_percentage"], 223.5)

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
        self.assertEqual(data["calculation_steps"][9]["roi_percentage"], 223.5)
        self.assertIn("assumptions_ledger", data)
        self.assertIn("sensitivity_analysis", data)
        self.assertIn("watermark", data)

    def test_api_get_deployment_plan(self):
        res = self.client.get("/api/pilots/pilot-2026-customs-recon/deployment-plan?platform=databricks_mosaic_ai")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["platform"], "databricks_mosaic_ai")
        self.assertIn("Mosaic AI", data["deployment_plan"]["runtime_framework"])
        self.assertIn("validation", data)
        self.assertTrue(data["validation"]["valid"])

    def test_api_validate_deployment_plan(self):
        res = self.client.get("/api/pilots/pilot-2026-customs-recon/deployment-plan/validate?platform=gemini_enterprise")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["platform"], "gemini_enterprise")
        self.assertTrue(data["validation"]["valid"])

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
