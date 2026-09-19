"""Unit tests for the multi-dimensional FDE Prioritization model."""

import unittest
from fde_workbench.domain.ai_opportunities import (
    EconomicLeverage,
    OperationalCharacteristics,
    DeploymentFeasibility,
    StrategicValue,
    FDEPrioritization,
    AIOpportunity,
    DeploymentComplexity,
)
from fde_workbench.domain.ontology import EntityTypeEnum


class TestPrioritization(unittest.TestCase):

    def test_dimension_scoring_calculations(self):
        econ = EconomicLeverage(
            revenue_impact=8,
            cost_impact=9,
            working_capital_impact=7,
            risk_exposure=10,
        )
        self.assertAlmostEqual(econ.score(), 8.5)

        ops = OperationalCharacteristics(
            frequency=10,
            decision_complexity=6,
            current_manual_effort=9,
            latency_sensitivity=9,
            cross_system_fragmentation=8,
        )
        self.assertAlmostEqual(ops.score(), 8.4)

        feas = DeploymentFeasibility(
            data_availability=8,
            integration_complexity=7,
            security_sensitivity=9,
            human_approval_clarity=10,
            change_management_readiness=8,
        )
        self.assertAlmostEqual(feas.score(), 8.4)

        strat = StrategicValue(
            repeatability=10,
            adjacent_workflows_count=8,
            cross_customer_applicability=9,
            reusable_ip_potential=9,
        )
        self.assertAlmostEqual(strat.score(), 9.0)

        prio = FDEPrioritization(
            economic_leverage=econ,
            operational_characteristics=ops,
            deployment_feasibility=feas,
            strategic_value=strat,
            pilot_recommendation="HIGH_PRIORITY_PILOT",
            prioritization_rationale="Ideal FDE pilot: High pain point with structured input data and direct executive buy-in.",
        )

        summary = prio.summary()
        self.assertEqual(summary["economic_leverage"], 8.5)
        self.assertEqual(summary["operational_characteristics"], 8.4)
        self.assertEqual(summary["deployment_feasibility"], 8.4)
        self.assertEqual(summary["strategic_value"], 9.0)
        self.assertTrue(summary["is_pilot_candidate"])

    def test_opportunity_with_prioritization(self):
        opp = AIOpportunity(
            id="opp-test-01",
            title="Customs Exception Resolution",
            workflow="Cross-Border Customs Clearance",
            bottleneck="Missing transit documents stall trucks at Ciudad del Este border",
            business_impact="$85,000/year detention costs",
            entities_involved=[EntityTypeEnum.CUSTOMS_DECLARATION],
            data_required=["VUE Portal", "SAP B1"],
            decision_involved="Expedite customs filing",
            proposed_ai_intervention="Automated document completeness validation",
            human_in_the_loop_requirement="Broker authorization",
            permissions_required=["READ: VUE"],
            failure_modes=["False warning"],
            kpi="Customs Border Dwell Time",
            deployment_complexity=DeploymentComplexity.LOW,
            estimated_payoff_annual_usd=34000.0,
            prioritization=FDEPrioritization(
                economic_leverage=EconomicLeverage(revenue_impact=6, cost_impact=9, working_capital_impact=7, risk_exposure=8),
                operational_characteristics=OperationalCharacteristics(frequency=9, decision_complexity=5, current_manual_effort=8, latency_sensitivity=9, cross_system_fragmentation=7),
                deployment_feasibility=DeploymentFeasibility(data_availability=9, integration_complexity=8, security_sensitivity=8, human_approval_clarity=9, change_management_readiness=8),
                strategic_value=StrategicValue(repeatability=10, adjacent_workflows_count=7, cross_customer_applicability=10, reusable_ip_potential=9),
                pilot_recommendation="HIGH_PRIORITY_PILOT",
                prioritization_rationale="Immediate ROI with clear single-department boundary.",
            ),
        )

        self.assertIsNotNone(opp.prioritization)
        self.assertEqual(opp.prioritization.pilot_recommendation, "HIGH_PRIORITY_PILOT")


if __name__ == "__main__":
    unittest.main()
