"""Decision abstraction modeling the operational decision-making pipeline."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class DecisionOption(BaseModel):
    """An evaluated operational alternative."""
    option_id: str = Field(..., description="e.g. 'OPT-A', 'OPT-B'")
    title: str = Field(..., description="Short summary of option")
    description: str = Field(..., description="Detailed operational steps")
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    cost_estimate_usd: float = Field(default=0.0)
    delay_hours_estimate: float = Field(default=0.0)
    risk_level: str = Field(default="MEDIUM", description="LOW, MEDIUM, HIGH")


class AuthorizedAction(BaseModel):
    """Execution parameters once a decision option is authorized."""
    action_type: str = Field(..., description="e.g. 'REROUTE_SHIPMENT', 'APPLY_DISCOUNT', 'EXPEDITE_CUSTOMS'")
    target_entity_id: str = Field(..., description="Entity being modified or acted upon")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action arguments")
    authorized_by: str = Field(..., description="Employee role or person authorizing action")
    authorized_at: datetime = Field(default_factory=datetime.utcnow)
    execution_status: str = Field(default="EXECUTED", description="PENDING, EXECUTED, FAILED")


class DecisionOutcome(BaseModel):
    """Observed real-world outcome following execution."""
    observed_result: str = Field(..., description="What actually occurred after the action")
    actual_latency_hours: float = Field(default=0.0, description="Hours taken to resolve")
    financial_delta_usd: float = Field(default=0.0, description="Actual cost incurred or saved")
    kpi_impact: str = Field(default="", description="Impact on primary operational KPI")
    verified: bool = Field(default=True, description="Whether the outcome was audited and confirmed")


class DecisionRecord(BaseModel):
    """
    Formal Decision abstraction enforcing the conceptual workflow:
    OBSERVATION -> CONTEXT -> DECISION -> AUTHORIZED ACTION -> OUTCOME
    """
    decision_id: str = Field(..., description="Unique decision ID, e.g. 'dec-2026-001'")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    triggering_event_id: str = Field(..., description="ID of the OperationalEvent that provoked this decision")
    decision_owner: str = Field(..., description="Role responsible for the decision, e.g. 'Logistics Operations Director'")
    context: Dict[str, Any] = Field(default_factory=dict, description="Operational context: constraints, river level, stock, contract clauses")
    options: List[DecisionOption] = Field(default_factory=list, description="Candidate actions evaluated")
    recommendation: str = Field(..., description="Recommended path and rationale")
    authorization_required: bool = Field(default=True, description="Whether human executive approval is mandatory")
    authorized_action: Optional[AuthorizedAction] = Field(default=None, description="The authorized action executed")
    outcome: Optional[DecisionOutcome] = Field(default=None, description="The measured post-execution reality")

    def get_pipeline_stages(self) -> List[Dict[str, Any]]:
        """Returns the sequential workflow stages for inspection UI."""
        return [
            {
                "stage": "1. OBSERVATION",
                "label": "Operational Event Detection",
                "data": {
                    "triggering_event_id": self.triggering_event_id,
                    "timestamp": self.timestamp.isoformat(),
                },
            },
            {
                "stage": "2. CONTEXT",
                "label": "Constraints & Business State",
                "data": self.context,
            },
            {
                "stage": "3. DECISION",
                "label": "Options Evaluation & Recommendation",
                "data": {
                    "decision_owner": self.decision_owner,
                    "options_count": len(self.options),
                    "options": [opt.model_dump() for opt in self.options],
                    "recommendation": self.recommendation,
                    "authorization_required": self.authorization_required,
                },
            },
            {
                "stage": "4. AUTHORIZED ACTION",
                "label": "Executive Authorization & Execution",
                "data": self.authorized_action.model_dump() if self.authorized_action else None,
            },
            {
                "stage": "5. OUTCOME",
                "label": "Observed Operational Result",
                "data": self.outcome.model_dump() if self.outcome else None,
            },
        ]
