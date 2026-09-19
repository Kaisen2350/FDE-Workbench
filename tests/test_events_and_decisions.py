"""Unit tests for operational events and the 5-stage decision pipeline with escalation."""

import unittest
from datetime import datetime, timedelta
from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.events import OperationalEventRecord, EventSeverity, EventStatus
from fde_workbench.domain.decisions import DecisionRecord, DecisionOption, AuthorizedAction, DecisionOutcome, DecisionStatus


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
            status=DecisionStatus.EXECUTED,
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

    def test_decision_timeout_and_escalation(self):
        """Verify automatic transition to ESCALATED when pending past threshold."""
        creation_time = datetime(2026, 9, 18, 10, 0, 0)
        dec = DecisionRecord(
            decision_id="dec-timeout-test",
            timestamp=creation_time,
            triggering_event_id="evt-timeout-test",
            decision_owner="role-customs-compliance",
            status=DecisionStatus.DECISION_PENDING,
            escalation_timeout_hours=4.0,
            escalation_target_role="role-executive",
            recommendation="Urgent broker clearance",
        )

        # Time advanced by only 2 hours (less than 4.0h threshold)
        check_2h = dec.check_and_escalate(current_time=creation_time + timedelta(hours=2))
        self.assertFalse(check_2h)
        self.assertEqual(dec.status, DecisionStatus.DECISION_PENDING)

        # Time advanced by 5.5 hours (exceeds 4.0h threshold)
        check_5h = dec.check_and_escalate(current_time=creation_time + timedelta(hours=5, minutes=30))
        self.assertTrue(check_5h)
        self.assertEqual(dec.status, DecisionStatus.ESCALATED)
        self.assertIsNotNone(dec.escalated_at)
        self.assertEqual(dec.escalation_target_role, "role-executive")
        self.assertIn("threshold: 4.0h", dec.escalation_reason)
        self.assertIn("role-customs-compliance", dec.escalation_reason)

    def test_seeded_pre_aged_decision_escalation_end_to_end(self):
        """
        Verify end-to-end that AIDESA's pre-aged decision in DECISION_PENDING state
        transitions to ESCALATED upon running check_all_escalations(), and generates
        a valid cryptographically hash-chained audit log entry.
        """
        import tempfile
        import os
        from fde_workbench.storage.store import WorkbenchStore
        from fde_workbench.synthetic.generator import seed_synthetic_company

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            test_store = WorkbenchStore(db_path=db_path)
            seed_synthetic_company(test_store)

            # 1. Verify pre-aged decision was seeded in DECISION_PENDING state
            dec = test_store.get_decision("dec-2026-005-escalated")
            self.assertIsNotNone(dec)
            self.assertEqual(dec.status, DecisionStatus.DECISION_PENDING)
            self.assertEqual(dec.escalation_timeout_hours, 4.0)
            self.assertEqual(dec.escalation_target_role, "role-executive")

            # Verify initial audit trail length and validity
            initial_val = test_store.verify_audit_chain()
            self.assertTrue(initial_val["valid"])
            initial_count = initial_val["total_entries"]

            # 2. Trigger on-demand escalation sweep
            now = datetime.utcnow()
            escalated_decisions = test_store.check_all_escalations(current_time=now)
            self.assertEqual(len(escalated_decisions), 1)
            self.assertEqual(escalated_decisions[0].decision_id, "dec-2026-005-escalated")
            self.assertEqual(escalated_decisions[0].status, DecisionStatus.ESCALATED)

            # 3. Reload from SQLite and assert persisted state transition
            reloaded = test_store.get_decision("dec-2026-005-escalated")
            self.assertIsNotNone(reloaded)
            self.assertEqual(reloaded.status, DecisionStatus.ESCALATED)
            self.assertEqual(reloaded.escalation_target_role, "role-executive")
            self.assertIn("(threshold: 4.0h)", reloaded.escalation_reason)

            # 4. Verify new tamper-evident audit log entry was appended
            new_val = test_store.verify_audit_chain()
            self.assertTrue(new_val["valid"])
            self.assertEqual(new_val["total_entries"], initial_count + 1)
            self.assertNotEqual(new_val["head_hash"], initial_val["head_hash"])

            # Verify latest audit log entry details (get_audit_trail returns DESC order)
            latest_audit = test_store.get_audit_trail(limit=5)[0]
            self.assertEqual(latest_audit["action"], "ESCALATE_DECISION")
            self.assertEqual(latest_audit["entity_id"], "dec-2026-005-escalated")
            self.assertTrue(latest_audit["details"].get("auto_timeout"))
            self.assertEqual(latest_audit["details"].get("escalated_to"), "role-executive")
        finally:
            try:
                test_store._conn.close()
            except Exception:
                pass
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
