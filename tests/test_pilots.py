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
        # Reconciled ROI %: Hardcoded hand-calculated expected value:
        # (73,750 / 33,000) * 100 = 223.484848...% -> 223.5%
        # Strictly assert against independently hand-calculated values (both unrounded and rounded)
        self.assertAlmostEqual(econ.expected_roi_percentage(), 223.484848, places=4)
        self.assertEqual(round(econ.expected_roi_percentage(), 1), 223.5)
        # Payback period: 15,000 / (106,750 / 12) = ~1.68618... months -> 1.7 months
        self.assertAlmostEqual(econ.payback_period_months(), 1.68618, places=4)
        self.assertEqual(round(econ.payback_period_months(), 1), 1.7)

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
        # Independent Hand-Calculation (computed completely external to the codebase):
        # Baseline labor: 2000 * (20/60) * 30 = 20,000.00
        # Baseline exceptions: 2000 * 0.05 * 1000 = 100,000.00
        # Working capital carrying drag: 10,000.00
        # Baseline total cost: 20000 + 100000 + 10000 = 130,000.00
        # Target labor: 2000 * (5/60) * 30 = 5,000.00
        # Target exceptions: 2000 * 0.01 * 1000 = 20,000.00
        # Target total cost: 5000 + 20000 = 25,000.00
        # Addressable annual savings: 130,000 - 25,000 = 105,000.00
        # Total 1st-year outlay: 20,000 (implementation) + 10,000 (license) = 30,000.00
        # Net 1st-year ROI ($): 105,000 - 30,000 = 75,000.00
        # Expected ROI %: (75,000 / 30,000) * 100 = 250.0% exactly
        # Expected Payback: 20,000 / (105,000 / 12) = 2.285714... -> 2.3 months
        self.assertEqual(econ.addressable_annual_savings(), 105000.0)
        self.assertEqual(econ.total_investment_usd(), 30000.0)
        self.assertEqual(econ.first_year_net_roi_usd(), 75000.0)
        self.assertEqual(econ.expected_roi_percentage(), 250.0)
        self.assertAlmostEqual(econ.payback_period_months(), 2.285714, places=4)
        self.assertEqual(round(econ.payback_period_months(), 1), 2.3)
        self.assertEqual(econ.summary()["expected_roi_percentage"], 250.0)
        self.assertEqual(econ.summary()["payback_period_months"], 2.3)

    # =========================================================================================
    # INDEPENDENT ARITHMETIC PROOF & DERIVATION TRAIL (AUDITABLE BY MANUAL INSPECTION)
    # Computed independently external to code logic to eliminate circular / tautological testing.
    #
    # PILOT 1: CUSTOMS RECONCILER (pilot-2026-customs-recon)
    # -----------------------------------------------------------------------------------------
    # 1. Inputs:
    #    - Annual volume (V) = 1,800 trucks
    #    - Baseline touch time (T_base) = 14.0 min = 14.0 / 60 = 0.2333333333 hours
    #    - Target touch time (T_targ) = 3.0 min = 3.0 / 60 = 0.05 hours
    #    - Fully-burdened hourly rate (W) = $25.00 / hour
    #    - Baseline exception rate (E_base) = 6.5% = 0.065
    #    - Target exception rate (E_targ) = 1.5% = 0.015
    #    - Cost per exception (C_exc) = $850.00
    #    - Working capital acceleration annual value (WC) = $22,000.00
    #    - One-off Implementation fee (I) = $15,000.00
    #    - Annual Software license (S) = $18,000.00
    #
    # 2. Arithmetic Derivation:
    #    - Baseline Labor Cost:
    #      1,800 * (14.0 / 60) * $25.00 = 1,800 * 0.2333333333 * 25.00 = 420.0 hrs * $25.00 = $10,500.00
    #    - Baseline Exception Cost:
    #      1,800 * 0.065 * $850.00 = 117.0 exceptions * $850.00 = $99,450.00
    #    - Baseline Total Cost:
    #      $10,500.00 + $99,450.00 + $22,000.00 = $131,950.00
    #
    #    - Target Labor Cost:
    #      1,800 * (3.0 / 60) * $25.00 = 1,800 * 0.05 * $25.00 = 90.0 hrs * $25.00 = $2,250.00
    #    - Target Exception Cost:
    #      1,800 * 0.015 * $850.00 = 27.0 exceptions * $850.00 = $22,950.00
    #    - Target Total Cost:
    #      $2,250.00 + $22,950.00 = $25,200.00
    #
    #    - Addressable Annual Savings:
    #      $131,950.00 - $25,200.00 = $106,750.00
    #
    #    - Total 1st-Year Investment:
    #      $15,000.00 (Implementation) + $18,000.00 (License) = $33,000.00
    #
    #    - Net 1st-Year Dollar ROI:
    #      $106,750.00 - $33,000.00 = $73,750.00
    #
    #    - Net 1st-Year ROI Percentage:
    #      $73,750.00 / $33,000.00 = 2.2348484848...
    #      2.2348484848... * 100 = 223.484848...%  --> Rounds to exactly 223.5%
    #
    #    - Payback Period:
    #      Monthly Gross Run-rate = $106,750.00 / 12 = $8,895.833333... / month
    #      $15,000.00 / $8,895.833333... = 1.686182... months  --> Rounds to exactly 1.7 months
    #
    # PILOT 2: FLUVIAL DRAFT OPTIMIZER (pilot-2026-fluvial-draft)
    # -----------------------------------------------------------------------------------------
    # 1. Inputs:
    #    - Annual volume (V) = 240 push-convoys
    #    - Baseline touch time (T_base) = 45.0 min = 45.0 / 60 = 0.75 hours
    #    - Target touch time (T_targ) = 10.0 min = 10.0 / 60 = 0.1666666667 hours
    #    - Fully-burdened hourly rate (W) = $40.00 / hour
    #    - Baseline exception rate (E_base) = 8.0% = 0.08
    #    - Target exception rate (E_targ) = 1.0% = 0.01
    #    - Cost per exception (C_exc) = $18,500.00 (alijo lightening barge + demurrage)
    #    - Working capital acceleration annual value (WC) = $15,000.00
    #    - One-off Implementation fee (I) = $22,000.00
    #    - Annual Software license (S) = $24,000.00
    #
    # 2. Arithmetic Derivation:
    #    - Baseline Labor Cost:
    #      240 * (45.0 / 60) * $40.00 = 240 * 0.75 * 40.00 = 180.0 hrs * $40.00 = $7,200.00
    #    - Baseline Exception Cost:
    #      240 * 0.08 * $18,500.00 = 19.2 exceptions * $18,500.00 = $355,200.00
    #    - Baseline Total Cost:
    #      $7,200.00 + $355,200.00 + $15,000.00 = $377,400.00
    #
    #    - Target Labor Cost:
    #      240 * (10.0 / 60) * $40.00 = 240 * 0.1666666667 * 40.00 = 40.0 hrs * $40.00 = $1,600.00
    #    - Target Exception Cost:
    #      240 * 0.01 * $18,500.00 = 2.4 exceptions * $18,500.00 = $44,400.00
    #    - Target Total Cost:
    #      $1,600.00 + $44,400.00 = $46,000.00
    #
    #    - Addressable Annual Savings:
    #      $377,400.00 - $46,000.00 = $331,400.00
    #
    #    - Total 1st-Year Investment:
    #      $22,000.00 (Implementation) + $24,000.00 (License) = $46,000.00
    #
    #    - Net 1st-Year Dollar ROI:
    #      $331,400.00 - $46,000.00 = $285,400.00
    #
    #    - Net 1st-Year ROI Percentage:
    #      $331,400.00 - $46,000.00 = $285,400.00
    #      $285,400.00 / $46,000.00 = 6.204347826...
    #      6.204347826... * 100 = 620.43478...%  --> Rounds to exactly 620.4%
    #
    #    - Payback Period:
    #      Monthly Gross Run-rate = $331,400.00 / 12 = $27,616.666667... / month
    #      $22,000.00 / $27,616.666667... = 0.796619... months  --> Rounds to exactly 0.8 months
    # =========================================================================================

    def test_canonical_pilots_hand_calculated_roi_verifications(self):
        """
        Verify both canonical enterprise pilots against external hand-calculated benchmarks.
        Ensures zero formula drift or tautological circular assertions.
        """
        # --- 1. Customs Reconciler Pilot ---
        pilot_customs = store.get_pilot("pilot-2026-customs-recon")
        self.assertIsNotNone(pilot_customs)
        econ_c = pilot_customs.economic_model

        # Verification against independent constants derived in arithmetic trail above:
        self.assertEqual(econ_c.baseline_annual_total_cost(), 131950.0)
        self.assertEqual(econ_c.target_annual_total_cost(), 25200.0)
        self.assertEqual(econ_c.addressable_annual_savings(), 106750.0)
        self.assertEqual(econ_c.total_investment_usd(), 33000.0)
        self.assertEqual(econ_c.first_year_net_roi_usd(), 73750.0)
        self.assertAlmostEqual(econ_c.expected_roi_percentage(), 223.484848, places=4)
        self.assertEqual(round(econ_c.expected_roi_percentage(), 1), 223.5)
        self.assertEqual(round(econ_c.payback_period_months(), 1), 1.7)
        self.assertEqual(econ_c.summary()["expected_roi_percentage"], 223.5)
        self.assertEqual(econ_c.summary()["payback_period_months"], 1.7)

        # --- 2. Fluvial Draft Optimizer Pilot ---
        pilot_fluvial = store.get_pilot("pilot-2026-fluvial-draft")
        self.assertIsNotNone(pilot_fluvial)
        econ_f = pilot_fluvial.economic_model

        # Verification against independent constants derived in arithmetic trail above:
        self.assertEqual(econ_f.baseline_annual_total_cost(), 377400.0)
        self.assertEqual(econ_f.target_annual_total_cost(), 46000.0)
        self.assertEqual(econ_f.addressable_annual_savings(), 331400.0)
        self.assertEqual(econ_f.total_investment_usd(), 46000.0)
        self.assertEqual(econ_f.first_year_net_roi_usd(), 285400.0)
        self.assertAlmostEqual(econ_f.expected_roi_percentage(), 620.43478, places=4)
        self.assertEqual(round(econ_f.expected_roi_percentage(), 1), 620.4)
        self.assertEqual(round(econ_f.payback_period_months(), 1), 0.8)
        self.assertEqual(econ_f.summary()["expected_roi_percentage"], 620.4)
        self.assertEqual(econ_f.summary()["payback_period_months"], 0.8)

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

    def test_calibration_brief_sections_and_numeric_absence(self):
        """Confirm Section 4's numeric fields are absent from calibration output and structural sections match."""
        from fde_workbench.domain.brief_generator import generate_calibration_brief
        for pilot_id in ["pilot-2026-customs-recon", "pilot-2026-fluvial-draft"]:
            pilot = store.get_pilot(pilot_id)
            self.assertIsNotNone(pilot)

            std_md = FDEBriefGenerator.generate_markdown(pilot, store=store, calibration_mode=False)
            calib_md = generate_calibration_brief(pilot_id, store=store)

            # Split both briefs into sections using markdown header 2 (## )
            import re
            std_sections = re.split(r"\n(?=## \d+\. )", std_md)
            calib_sections = re.split(r"\n(?=## \d+\. )", calib_md)

            # Must have preamble + 12 sections = 13 parts
            self.assertEqual(len(std_sections), 13)
            self.assertEqual(len(calib_sections), 13)

            # Preamble (index 0) must match
            self.assertEqual(std_sections[0], calib_sections[0])

            # Qualitative non-numeric sections must match exactly
            for idx in [2, 3, 5, 7, 8, 12]:
                self.assertEqual(
                    std_sections[idx],
                    calib_sections[idx],
                    f"Section {idx} differs between standard and calibration brief for {pilot_id}!"
                )

            # Section 1 verification (qualitative baseline focus areas without numbers):
            s1_calib = calib_sections[1]
            self.assertIn("Operational Baseline Focus Areas (Pending Field Calibration)", s1_calib)
            self.assertIn("[ Pending field validation — see Section 4 ]", s1_calib)

            # Section 4 verification:
            s4_calib = calib_sections[4]
            self.assertTrue(s4_calib.startswith("## 4. Economic Impact & ROI Equation"))
            self.assertIn("Values pending field validation — see operator interview.", s4_calib)
            self.assertIn("baseline: `_____`", s4_calib)

            # Assert numeric calculations, dollar amounts, ROI percentages, and sensitivity analysis are ABSENT
            self.assertNotIn("Net 1st-Year ROI ($):", s4_calib)
            self.assertNotIn("ROI %:", s4_calib)
            self.assertNotIn("Capital Payback Period:", s4_calib)
            self.assertNotIn("Sensitivity Analysis", s4_calib)
            self.assertNotIn("Addressable Annual Savings:", s4_calib)
            self.assertNotIn("Baseline Annual Cost:", s4_calib)
            self.assertNotIn("Total 1st-Year Investment:", s4_calib)

            # Section 10 verification (qualitative acceptance criteria without hardcoded assumption thresholds):
            s10_calib = calib_sections[10]
            self.assertIn("Thresholds Pending Field Calibration", s10_calib)
            self.assertIn("[ Target threshold pending field validation — see Section 4 ]", s10_calib)

    def test_zero_occurrences_of_pilot_assumption_values_in_calibration_brief(self):
        """Assert zero occurrences of the pilot's specific assumption values anywhere in calibration brief outside the ledger's own blank-field labels."""
        from fde_workbench.domain.brief_generator import generate_calibration_brief
        for pilot_id in ["pilot-2026-customs-recon", "pilot-2026-fluvial-draft"]:
            pilot = store.get_pilot(pilot_id)
            econ = pilot.economic_model
            calib_md = generate_calibration_brief(pilot_id, store=store)

            # Specific numeric assumption values from the economic model that must NEVER appear as anchoring leaks:
            checks = [
                ("annual_decision_volume", str(econ.annual_decision_volume)),
                ("annual_decision_volume_comma", f"{econ.annual_decision_volume:,}"),
                ("manual_effort_minutes", f"{econ.manual_effort_minutes_per_decision}"),
                ("manual_effort_minutes_int", f"{int(econ.manual_effort_minutes_per_decision)} min"),
                ("hourly_labor_cost", f"${econ.hourly_labor_cost_usd:.2f}"),
                ("hourly_labor_cost_raw", f"${int(econ.hourly_labor_cost_usd)}"),
                ("error_rate_pct", f"{econ.current_error_or_exception_rate * 100:.1f}%"),
                ("cost_per_exception", f"${econ.cost_per_exception_usd:,.2f}"),
                ("cost_per_exception_raw", f"${int(econ.cost_per_exception_usd)}"),
                ("target_mins", f"{econ.target_manual_effort_minutes:.1f} min"),
                ("target_mins_raw", f"{int(econ.target_manual_effort_minutes)} min"),
                ("target_err_pct", f"{econ.target_exception_rate * 100:.1f}%"),
                ("pilot_vol_shipments", f"{econ.pilot_decision_volume} decisions"),
                ("pilot_vol_consecutive", f"{econ.pilot_decision_volume} consecutive"),
                ("impl_cost", f"${int(econ.pilot_implementation_cost_usd):,}"),
                ("license_cost", f"${int(econ.annual_software_subscription_usd):,}"),
            ]

            lines = calib_md.split("\n")
            for name, val in checks:
                for idx, line in enumerate(lines):
                    self.assertNotIn(
                        val,
                        line,
                        f"Found anchoring leak of {name}='{val}' at L{idx+1} in calibration brief for {pilot_id}!\nLine content: {line}"
                    )

    def test_api_get_calibration_brief(self):
        """Verify GET /api/pilots/{pilot_id}/calibration-brief endpoint returns valid calibration markdown."""
        res = self.client.get("/api/pilots/pilot-2026-customs-recon/calibration-brief")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["pilot_id"], "pilot-2026-customs-recon")
        calib_md = data["calibration_markdown"]
        self.assertIn("Values pending field validation — see operator interview.", calib_md)
        self.assertIn("baseline: `_____`", calib_md)
        self.assertNotIn("Net 1st-Year ROI ($):", calib_md)


if __name__ == "__main__":
    unittest.main()
