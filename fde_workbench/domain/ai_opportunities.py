"""AI Opportunity abstraction modeling where AI agents can alleviate operational bottlenecks."""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fde_workbench.domain.ontology import EntityTypeEnum


class DeploymentComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AIOpportunity(BaseModel):
    """
    Structured model for identifying and scoping potential AI interventions
    grounded directly in operational reality.
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
