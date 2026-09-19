"""Canonical Pilot Specification and Economic Bridge domain models."""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from fde_workbench.domain.provenance import ProvenanceType


class PilotStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    EVALUATING = "EVALUATING"
    CONVERTED = "CONVERTED"
    ABORTED = "ABORTED"


class PilotEconomicModel(BaseModel):
    """
    Formal economic calculation engine linking physical operational friction
    to hard enterprise financial value.
    
    Formula:
    Baseline Annual Cost = Labor Cost + Exception Cost + Working Capital Drag
    Target Annual Cost   = Reduced Labor + Reduced Exceptions
    Addressable Value    = Baseline Total - Target Total
    Pilot Value          = Volume in Pilot * Net Savings per Unit
    Net First-Year ROI   = Addressable Savings - Implementation Cost - Annual Software
    """
    annual_decision_volume: int = Field(..., description="Annual count of operational decisions / shipments")
    manual_effort_minutes_per_decision: float = Field(..., description="Minutes of human effort per decision today")
    hourly_labor_cost_usd: float = Field(default=25.0, description="Blended hourly cost of human decision makers")
    current_error_or_exception_rate: float = Field(..., description="Current rate of exceptions, rework, or delays (e.g. 0.065 for 6.5%)")
    cost_per_exception_usd: float = Field(..., description="Financial consequence per exception (demurrage, fines, delay)")
    
    # Intervention targets
    target_manual_effort_minutes: float = Field(..., description="Target minutes post-intervention (e.g. 3.0 min)")
    target_exception_rate: float = Field(..., description="Target exception rate post-intervention (e.g. 0.02 for 2.0%)")
    
    # Pilot-specific financial parameters
    pilot_decision_volume: int = Field(default=100, description="Volume to be processed inside pilot boundary")
    pilot_implementation_cost_usd: float = Field(default=15000.0, description="FDE configuration & integration cost")
    annual_software_subscription_usd: float = Field(default=18000.0, description="Annual platform / license estimate")
    working_capital_acceleration_days: float = Field(default=0.0, description="Days of CCC reduction")
    annual_working_capital_financial_value_usd: float = Field(default=0.0, description="Financial carrying value of accelerated cash")

    def baseline_annual_labor_cost(self) -> float:
        return self.annual_decision_volume * (self.manual_effort_minutes_per_decision / 60.0) * self.hourly_labor_cost_usd

    def baseline_annual_exception_cost(self) -> float:
        return self.annual_decision_volume * self.current_error_or_exception_rate * self.cost_per_exception_usd

    def baseline_annual_total_cost(self) -> float:
        return self.baseline_annual_labor_cost() + self.baseline_annual_exception_cost() + self.annual_working_capital_financial_value_usd

    def target_annual_labor_cost(self) -> float:
        return self.annual_decision_volume * (self.target_manual_effort_minutes / 60.0) * self.hourly_labor_cost_usd

    def target_annual_exception_cost(self) -> float:
        return self.annual_decision_volume * self.target_exception_rate * self.cost_per_exception_usd

    def target_annual_total_cost(self) -> float:
        return self.target_annual_labor_cost() + self.target_annual_exception_cost()

    def addressable_annual_savings(self) -> float:
        return max(0.0, self.baseline_annual_total_cost() - self.target_annual_total_cost())

    def savings_per_decision_unit(self) -> float:
        if self.annual_decision_volume <= 0:
            return 0.0
        return self.addressable_annual_savings() / self.annual_decision_volume

    def pilot_measured_value(self) -> float:
        """Estimated financial benefit realized strictly within the pilot batch."""
        return self.pilot_decision_volume * self.savings_per_decision_unit()

    def first_year_net_roi_usd(self) -> float:
        return self.addressable_annual_savings() - self.pilot_implementation_cost_usd - self.annual_software_subscription_usd

    def expected_roi_percentage(self) -> float:
        if self.pilot_implementation_cost_usd <= 0:
            return 0.0
        return (self.first_year_net_roi_usd() / self.pilot_implementation_cost_usd) * 100.0

    def payback_period_months(self) -> float:
        monthly_savings = self.addressable_annual_savings() / 12.0
        if monthly_savings <= 0:
            return 999.0
        return self.pilot_implementation_cost_usd / monthly_savings

    def summary(self) -> Dict[str, Any]:
        return {
            "baseline_annual_total_usd": round(self.baseline_annual_total_cost(), 2),
            "baseline_annual_labor_usd": round(self.baseline_annual_labor_cost(), 2),
            "baseline_annual_exception_usd": round(self.baseline_annual_exception_cost(), 2),
            "target_annual_total_usd": round(self.target_annual_total_cost(), 2),
            "addressable_annual_savings_usd": round(self.addressable_annual_savings(), 2),
            "savings_per_shipment_usd": round(self.savings_per_decision_unit(), 2),
            "pilot_batch_value_usd": round(self.pilot_measured_value(), 2),
            "pilot_implementation_cost_usd": round(self.pilot_implementation_cost_usd, 2),
            "annual_subscription_usd": round(self.annual_software_subscription_usd, 2),
            "first_year_net_roi_usd": round(self.first_year_net_roi_usd(), 2),
            "expected_roi_percentage": round(self.expected_roi_percentage(), 1),
            "payback_period_months": round(self.payback_period_months(), 1),
        }


class PilotSpecification(BaseModel):
    """
    Canonical FDE Pilot Blueprint.
    Defines the exact parameters, data sources, human authorities, platform options,
    and measurable acceptance criteria for an operational deployment on Monday morning.
    """
    pilot_id: str = Field(..., description="Unique pilot identifier, e.g. 'pilot-2026-customs-recon'")
    opportunity_id: str = Field(..., description="Underlying AI opportunity ID, e.g. 'opp-2026-001'")
    agent_spec_id: Optional[str] = Field(default=None, description="Compiled AgentSpecification ID")
    title: str = Field(..., description="Clear human-readable pilot title")
    customer: str = Field(..., description="Target client enterprise name")
    workflow: str = Field(..., description="Target operational workflow")
    decision: str = Field(..., description="Operational decision loop being augmented/automated")
    decision_owner: str = Field(..., description="Human role accountable for authorizing decisions")
    
    # Measurement & KPIs
    baseline_kpi: Dict[str, Any] = Field(..., description="Current measured performance baseline")
    target_kpi: Dict[str, Any] = Field(..., description="Explicit pilot performance targets")
    measurement_method: str = Field(..., description="Auditable measurement methodology")
    
    # Data & Integrations
    data_sources: List[str] = Field(default_factory=list, description="Specific ERP, TMS, and document feeds")
    required_integrations: List[str] = Field(default_factory=list, description="Read/write API connections required")
    trigger: str = Field(..., description="Execution trigger condition")
    inputs: List[str] = Field(default_factory=list, description="Input document types and parameters")
    context: str = Field(..., description="Operational Paraguayan domain context and regulatory rules")
    
    # Authority & Actions
    recommended_action: str = Field(..., description="What the agent proposes or prepares")
    human_approval_required: str = Field(..., description="Mandatory sign-off authority and gate definition")
    authorized_actions: List[str] = Field(default_factory=list, description="Whitelisted actions the agent may take")
    
    # Platform Substrates
    supported_platforms: List[str] = Field(
        default_factory=lambda: ["gemini_enterprise", "microsoft_azure_ai_foundry", "openai_assistants", "databricks_mosaic_ai"],
        description="Platforms compatible with this pilot blueprint"
    )
    selected_platform: str = Field(default="gemini_enterprise", description="Default/Active deployment platform")
    
    # Scope & Governance
    pilot_duration: str = Field(default="30 days", description="Calendar duration of the pilot phase")
    pilot_scope: str = Field(..., description="Boundaries of volume or corridors (e.g. 100 shipments)")
    failure_modes: List[str] = Field(default_factory=list, description="Risk failure modes and automated fallbacks")
    rollback_condition: str = Field(..., description="Hard criteria for aborting or rolling back to manual")
    safety_constraints: List[str] = Field(default_factory=list, description="Inviolable operational and security boundaries")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Specific quantifiable gates for production sign-off")
    
    # Economics & Effort
    economic_model: PilotEconomicModel = Field(..., description="Auditable financial model")
    implementation_effort: str = Field(..., description="Estimated engineering and configuration time")
    deployment_dependencies: List[str] = Field(default_factory=list, description="Prerequisites (API keys, credentials, approvals)")
    
    # Lifecycle & Strategy
    status: PilotStatus = Field(default=PilotStatus.PROPOSED, description="Current lifecycle state")
    expansion_path: str = Field(..., description="Next adjacent operational workflow enabled by pilot success")
    provenance: ProvenanceType = Field(default=ProvenanceType.SYNTHETIC)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
