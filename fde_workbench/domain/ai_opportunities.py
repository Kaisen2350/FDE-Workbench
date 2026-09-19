"""AI Opportunity abstraction and multi-dimensional FDE Prioritization framework."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fde_workbench.domain.ontology import EntityTypeEnum
from fde_workbench.domain.provenance import ProvenanceType


class DeploymentComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EconomicLeverage(BaseModel):
    """Economic impact dimensions (1-10 scale)."""
    revenue_impact: int = Field(default=5, ge=1, le=10, description="1=negligible, 10=direct export top-line unlock")
    cost_impact: int = Field(default=5, ge=1, le=10, description="1=minor opex, 10=major recurring operational cost drain")
    working_capital_impact: int = Field(default=5, ge=1, le=10, description="1=no cash tie-up, 10=unfreezes trapped inventory/receivables")
    risk_exposure: int = Field(default=5, ge=1, le=10, description="1=harmless, 10=catastrophic vessel grounding or border seizure")

    def score(self) -> float:
        return (self.revenue_impact + self.cost_impact + self.working_capital_impact + self.risk_exposure) / 4.0


class OperationalCharacteristics(BaseModel):
    """Operational friction and operational reality dimensions (1-10 scale)."""
    frequency: int = Field(default=5, ge=1, le=10, description="1=annual/rare, 10=daily or continuous per convoy")
    decision_complexity: int = Field(default=5, ge=1, le=10, description="1=rule lookup, 10=multi-variable trade-off with uncertainty")
    current_manual_effort: int = Field(default=5, ge=1, le=10, description="1=automated, 10=exhausting manual spreadsheet reconciliations")
    latency_sensitivity: int = Field(default=5, ge=1, le=10, description="1=relaxed SLA, 10=sub-hour delay triggers penalties")
    cross_system_fragmentation: int = Field(default=5, ge=1, le=10, description="1=single screen, 10=fragmented across SAP, TMS, Sheets, WhatsApp")

    def score(self) -> float:
        return (self.frequency + self.decision_complexity + self.current_manual_effort + self.latency_sensitivity + self.cross_system_fragmentation) / 5.0


class DeploymentFeasibility(BaseModel):
    """Technical and organizational execution feasibility (1-10 scale, 10 = easiest)."""
    data_availability: int = Field(default=5, ge=1, le=10, description="1=untracked/paper-only, 10=structured and accessible in ERP/Sheets")
    integration_complexity: int = Field(default=5, ge=1, le=10, description="1=legacy mainframe lock-in, 10=standard REST/Google Workspace API")
    security_sensitivity: int = Field(default=5, ge=1, le=10, description="1=extreme bank secrecy/PII, 10=internal supply chain operational data")
    human_approval_clarity: int = Field(default=5, ge=1, le=10, description="1=ambiguous accountability, 10=clear single human sign-off role")
    change_management_readiness: int = Field(default=5, ge=1, le=10, description="1=hostile/resistant, 10=eager operational champions on site")

    def score(self) -> float:
        return (self.data_availability + self.integration_complexity + self.security_sensitivity + self.human_approval_clarity + self.change_management_readiness) / 5.0


class StrategicValue(BaseModel):
    """Strategic leverage for FDE deployment replication across Paraguay (1-10 scale)."""
    repeatability: int = Field(default=5, ge=1, le=10, description="1=one-off snowflake problem, 10=shared by all regional exporters")
    adjacent_workflows_count: int = Field(default=5, ge=1, le=10, description="1=isolated silo, 10=bridges 4+ upstream/downstream lifecycles")
    cross_customer_applicability: int = Field(default=5, ge=1, le=10, description="1=client-specific bespoke, 10=applicable to 50+ Mercosur exporters")
    reusable_ip_potential: int = Field(default=5, ge=1, le=10, description="1=throwaway code, 10=core vertical FDE domain asset")

    def score(self) -> float:
        return (self.repeatability + self.adjacent_workflows_count + self.cross_customer_applicability + self.reusable_ip_potential) / 4.0


class FDEPrioritization(BaseModel):
    """
    Multi-dimensional FDE Prioritization evaluation.
    Internal decision matrix replacing generic scores with rigorous operational trade-offs.
    """
    economic_leverage: EconomicLeverage
    operational_characteristics: OperationalCharacteristics
    deployment_feasibility: DeploymentFeasibility
    strategic_value: StrategicValue
    pilot_recommendation: str = Field(default="HIGH_PRIORITY_PILOT", description="HIGH_PRIORITY_PILOT, PHASE_2_EXPANSION, DEFER")
    prioritization_rationale: str = Field(..., description="Executive justification explaining why this opportunity is or is not an FDE pilot candidate")

    def summary(self) -> Dict[str, Any]:
        return {
            "economic_leverage": round(self.economic_leverage.score(), 1),
            "operational_characteristics": round(self.operational_characteristics.score(), 1),
            "deployment_feasibility": round(self.deployment_feasibility.score(), 1),
            "strategic_value": round(self.strategic_value.score(), 1),
            "pilot_recommendation": self.pilot_recommendation,
            "is_pilot_candidate": self.pilot_recommendation == "HIGH_PRIORITY_PILOT",
        }


class AIOpportunity(BaseModel):
    """
    Structured model for identifying, prioritizing, and scoping potential AI interventions
    grounded directly in operational bottlenecks and decisions.
    """
    id: str = Field(..., description="Unique opportunity ID, e.g. 'opp-01-customs-recon'")
    title: str = Field(..., description="Opportunity name")
    workflow: str = Field(..., description="Operational workflow being targeted, e.g. 'Cross-Border Customs Clearance'")
    bottleneck: str = Field(..., description="Precise operational friction, latency cause, or human bottleneck")
    business_impact: str = Field(..., description="Quantified cost, demurrage penalty, or delay incurred today")
    entities_involved: List[EntityTypeEnum] = Field(..., description="Domain entities connected to this workflow")
    data_required: List[str] = Field(..., description="Inputs required from ERP, Google Drive, VUE, TMS, or sensors")
    decision_involved: str = Field(..., description="Specific managerial decision that this opportunity supports or automates")
    proposed_ai_intervention: str = Field(..., description="Deterministic extraction, cross-document reconciliation, prediction, etc.")
    human_in_the_loop_requirement: str = Field(..., description="Mandatory human sign-off boundary (e.g. broker approval before DNA filing)")
    permissions_required: List[str] = Field(..., description="Read/write security boundaries needed")
    failure_modes: List[str] = Field(..., description="Risks when AI generates false positives, hallucinated NCM codes, or misses alerts")
    kpi: str = Field(..., description="Primary KPI moved by this intervention, e.g. 'Customs Border Dwell Time'")
    deployment_complexity: DeploymentComplexity = Field(default=DeploymentComplexity.MEDIUM)
    estimated_payoff_annual_usd: float = Field(default=0.0, description="Estimated annual operational savings")
    provenance: ProvenanceType = Field(default=ProvenanceType.SYNTHETIC)
    prioritization: Optional[FDEPrioritization] = Field(default=None, description="Multi-dimensional FDE evaluation matrix")
