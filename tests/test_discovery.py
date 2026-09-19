"""Unit tests for FDE Discovery Intake and Transformation Engine."""

import unittest
from datetime import datetime
from fde_workbench.domain.discovery import (
    DiscoveryIntake,
    CompanyDiscoveryProfile,
    CriticalWorkflowIntake,
    BottleneckIntake,
    DecisionIntake,
    KPIIntake,
    DataSourceIntake,
    StakeholderIntake,
    ConstraintsIntake,
    DiscoveryTransformationEngine,
)
from fde_workbench.storage.store import WorkbenchStore


class TestDiscovery(unittest.TestCase):

    def setUp(self):
        self.store = WorkbenchStore(db_path=":memory:")

    def test_discovery_intake_validation_and_model_generation(self):
        intake = DiscoveryIntake(
            intake_id="intake-test-001",
            date_conducted=datetime.utcnow(),
            lead_fde="FDE Principal",
            company_profile=CompanyDiscoveryProfile(
                name="Agro-Industrial del Este S.A.",
                ruc="80099412-4",
                industry="Agro-Industrial / Soybean & Grain Export",
                headcount=250,
                annual_revenue_usd="85M USD",
                export_markets=["Brazil (Terrestrial)", "Argentina (Fluvial)", "Chile"],
                facilities=[
                    {"id": "fac-villeta", "name": "Planta Fluvial Villeta", "type": "RIVER_PORT", "city": "Villeta", "has_barge_dock": True},
                    {"id": "fac-hernandarias", "name": "Planta Maquila Hernandarias", "type": "MAQUILA_ASSEMBLY", "city": "Hernandarias"},
                ],
                erp="SAP Business One",
                crm="Spreadsheets",
                tms_wms="Trans-Chaco TMS",
                cloud_ecosystem="Google Workspace",
            ),
            critical_workflows=[
                CriticalWorkflowIntake(
                    id="wf-fluvial-export",
                    name="Hidrovía Fluvial Grain Barge Export",
                    description="Crushed soybean meal barging down Paraguay-Paraná river to Rosario.",
                    volume_per_month="45,000 MT",
                    lead_time_days=18.0,
                    primary_systems=["Trans-Chaco TMS", "SAP B1"],
                ),
                CriticalWorkflowIntake(
                    id="wf-border-customs",
                    name="Cross-Border Terrestrial Trucking via Ciudad del Este",
                    description="Bitren dispatch to Brazil through Puente de la Amistad.",
                    volume_per_month="120 trucks",
                    lead_time_days=3.0,
                    primary_systems=["VUE Portal", "TMS"],
                ),
            ],
            known_bottlenecks=[
                BottleneckIntake(
                    id="bnk-river-draft",
                    workflow_id="wf-fluvial-export",
                    title="Paraguay River Draft Restrictions at Paso Queso",
                    description="Severe low water level restricts barge convoy draft, forcing cargo offloading or grounding.",
                    estimated_cost_exposure_annual_usd=180000.0,
                    delay_hours=72.0,
                    primary_cause="Seasonal drought and irregular navigation channel maintenance",
                ),
                BottleneckIntake(
                    id="bnk-customs-hold",
                    workflow_id="wf-border-customs",
                    title="Missing Transit Document (MIC/DTA) at Border",
                    description="Customs broker delays in attaching international transport permits.",
                    estimated_cost_exposure_annual_usd=65000.0,
                    delay_hours=14.0,
                    primary_cause="Manual data re-entry between SAP B1 and DNIT VUE portal",
                ),
            ],
            key_decisions=[
                DecisionIntake(
                    id="dec-alijo-charter",
                    title="Charter Emergency Alijo Barge vs Hold Convoy",
                    decision_maker_role="Logistics Director",
                    frequency="During Low-Water Alert Periods",
                    information_sources=["Prefectura Naval Bulletin", "Barge Pilot GPS"],
                    consequence_of_delay="Demurrage penalties of $6,400/day plus vessel grounding risk",
                )
            ],
            current_kpis=[
                KPIIntake(id="kpi-ccc", name="Cash Conversion Cycle", current_value="62", target_value="45", unit="days"),
                KPIIntake(id="kpi-border", name="Customs Border Dwell Time", current_value="18.4", target_value="6.0", unit="hours"),
            ],
            data_sources=[
                DataSourceIntake(id="ds-sap", name="SAP B1 SQL DB", system="SAP B1", format="SQL", accessibility="Direct Read Access"),
                DataSourceIntake(id="ds-vue", name="DNIT VUE Portal", system="VUE", format="REST API", accessibility="Direct Read Access"),
                DataSourceIntake(id="ds-prefectura", name="Prefectura Naval Hydrometric Bulletins", system="Prefectura", format="PDFs", accessibility="Manual Export"),
            ],
            stakeholders=[
                StakeholderIntake(role_title="Logistics Director", department="Supply Chain & Shipping", key_priorities=["River passage safety", "Demurrage minimization"]),
                StakeholderIntake(role_title="Customs Compliance Chief", department="Foreign Trade", key_priorities=["Zero border dwell fines", "MIC/DTA automation"]),
            ],
            constraints=ConstraintsIntake(
                security="Client export pricing and supplier RUC lists must remain in local SQLite / client Google Cloud tenant.",
                compliance="SENAVE and DNIT customs documentation strictly requires human customs broker sign-off.",
                budget_tier="Phase 2 FDE Pilot ($25,000-$50,000 deployment scope)",
                integration="Read-only access to SAP B1 replica; Google Drive API access permitted.",
                change_management="Dispatch clerks comfortable with Google Sheets and WhatsApp alerts.",
            ),
        )

        self.assertEqual(intake.company_profile.name, "Agro-Industrial del Este S.A.")
        self.assertEqual(len(intake.known_bottlenecks), 2)

        # Run Discovery Transformation Engine
        summary = DiscoveryTransformationEngine.generate_operational_model(intake, self.store)
        self.assertEqual(summary["entities"], 5)  # 1 org + 2 facilities + 2 roles
        self.assertEqual(summary["opportunities"], 2)
        self.assertEqual(summary["pilot_candidates"], 2)

        # Verify entities populated in store
        org = self.store.get_entity("org-agro-industr")
        self.assertIsNotNone(org)
        self.assertEqual(org.name, "Agro-Industrial del Este S.A.")

        # Verify opportunities populated with FDE Prioritization
        opps = self.store.list_opportunities()
        self.assertEqual(len(opps), 2)
        for opp in opps:
            self.assertIsNotNone(opp.prioritization)
            self.assertEqual(opp.prioritization.pilot_recommendation, "HIGH_PRIORITY_PILOT")


if __name__ == "__main__":
    unittest.main()
