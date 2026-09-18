"""Unit tests for operational events and the 5-stage decision pipeline."""

import unittest
from datetime import datetime
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.events import OperationalEventRecord, EventSeverity, EventStatus
from fde_workbench.domain.decisions import DecisionRecord, DecisionOption, AuthorizedAction, DecisionOutcome


class TestEventsAndDecisions(unittest.TestCase):

    def test_operational_event_creation_and_transition(self):
        ev = OperationalEventRecord(
            id="evt-test-01",
            entity_id="shp-001",
            entity_type=EntityTypeEnum.SHIPMENT,
            event_type="shipment_delayed",
            source="TMS",
            severity=EventSeverity.HIGH,
            expected_state={"arrival_time": "14:00", "convoy_draft_ft": 9.5},
            observed_state={"arrival_time": "22:00", "convoy_draft_ft": 10.2},
            operational_impact="Barge convoy draft exceeds channel depth",
            financial_impact=15000.0,
            required_decision="Lighten barge load or wait for dam surge",
            status=EventStatus.DETECTED,
        )
        self.assertEqual(ev.status, EventStatus.DETECTED)
        self.assertEqual(ev.financial_impact, 15000.0)

        # Status transition
        ev.transition_to(EventStatus.TRIAGED, note="Assigned to Fluvial Captain", actor="Logistics Director")
        self.assertEqual(ev.status, EventStatus.TRIAGED)
        self.assertEqual(len(ev.history), 1)
        self.assertEqual(ev.history[0]["from_status"], "DETECTED")
        self.assertEqual(ev.history[0]["to_status"], "TRIAGED")

    def test_decision_pipeline_workflow_stages(self):
        dec = DecisionRecord(
            decision_id="dec-test-01",
            triggering_event_id="evt-test-01",
            decision_owner="role-logistics-director",
            context={"river_gauge": "8.5ft", "anchor_zone": "km 1530"},
            options=[
                DecisionOption(
                    option_id="OPT-1",
                    title="Alijo operation",
                    description="Transfer cargo to hopper",
                    cost_estimate_usd=5000.0,
                )
            ],
            recommendation="Proceed with option 1",
            authorization_required=True,
            authorized_action=AuthorizedAction(
                action_type="CHARTER_ALIJO",
                target_entity_id="shp-001",
                parameters={"tons": 400.0},
                authorized_by="role-executive",
            ),
            outcome=DecisionOutcome(
                observed_result="Barge cleared channel",
                actual_latency_hours=18.0,
                financial_delta_usd=-5200.0,
                kpi_impact="No demurrage incurred",
                verified=True,
            ),
        )

        stages = dec.get_pipeline_stages()
        self.assertEqual(len(stages), 5)
        self.assertEqual(stages[0]["stage"], "1. OBSERVATION")
        self.assertEqual(stages[1]["stage"], "2. CONTEXT")
        self.assertEqual(stages[2]["stage"], "3. DECISION")
        self.assertEqual(stages[3]["stage"], "4. AUTHORIZED ACTION")
        self.assertEqual(stages[4]["stage"], "5. OUTCOME")
        self.assertTrue(stages[4]["data"]["verified"])


if __name__ == "__main__":
    unittest.main()
