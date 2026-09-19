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
    assumptions_ledger: Dict[str, str] = Field(default_factory=dict, description="Source or operational rationale for each model parameter")

    def total_investment_usd(self) -> float:
        """Total first-year financial outlay: implementation cost + annual software subscription."""
        return self.pilot_implementation_cost_usd + self.annual_software_subscription_usd

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
        return self.addressable_annual_savings() - self.total_investment_usd()

    def expected_roi_percentage(self) -> float:
        """
        Net First-Year ROI Percentage.
        Formula: Net 1st-Year ROI ($) / Total First-Year Outlay (Implementation + Annual License) * 100
        """
        tot = self.total_investment_usd()
        if tot <= 0:
            return 0.0
        return (self.first_year_net_roi_usd() / tot) * 100.0

    def payback_period_months(self) -> float:
        monthly_savings = self.addressable_annual_savings() / 12.0
        if monthly_savings <= 0:
            return 999.0
        return self.pilot_implementation_cost_usd / monthly_savings

    def get_assumptions_table(self) -> List[Dict[str, Any]]:
        """Returns structured ledger listing every parameter, value, and rationale."""
        default_rationales = {
            "annual_decision_volume": "Annualized operational decision/shipment frequency.",
            "manual_effort_minutes_per_decision": "Observed baseline manual touch-time per decision.",
            "hourly_labor_cost_usd": "Blended fully-burdened hourly cost of operations/customs personnel.",
            "current_error_or_exception_rate": "Historical baseline error, delay, or rework incidence.",
            "cost_per_exception_usd": "Consequential direct cost per exception (demurrage, fines, re-work).",
            "target_manual_effort_minutes": "Target assisted operator confirmation time post-intervention.",
            "target_exception_rate": "Residual exception rate threshold after automated pre-validation.",
            "pilot_decision_volume": "Controlled test volume boundary within pilot timeline.",
            "pilot_implementation_cost_usd": "Fixed FDE engineering, configuration, and integration investment.",
            "annual_software_subscription_usd": "Estimated annual platform / software runtime subscription.",
            "working_capital_acceleration_days": "Estimated Cash Conversion Cycle (CCC) acceleration in days.",
            "annual_working_capital_financial_value_usd": "Carrying value of accelerated liquidity at enterprise WACC.",
        }
        params = [
            ("annual_decision_volume", self.annual_decision_volume, "decisions/year"),
            ("manual_effort_minutes_per_decision", self.manual_effort_minutes_per_decision, "minutes/decision"),
            ("hourly_labor_cost_usd", self.hourly_labor_cost_usd, "USD/hour"),
            ("current_error_or_exception_rate", f"{self.current_error_or_exception_rate * 100:.1f}%", "percentage"),
            ("cost_per_exception_usd", self.cost_per_exception_usd, "USD/exception"),
            ("target_manual_effort_minutes", self.target_manual_effort_minutes, "minutes/decision"),
            ("target_exception_rate", f"{self.target_exception_rate * 100:.1f}%", "percentage"),
            ("pilot_decision_volume", self.pilot_decision_volume, "decisions in pilot"),
            ("pilot_implementation_cost_usd", self.pilot_implementation_cost_usd, "USD one-off"),
            ("annual_software_subscription_usd", self.annual_software_subscription_usd, "USD/year"),
            ("working_capital_acceleration_days", self.working_capital_acceleration_days, "days"),
            ("annual_working_capital_financial_value_usd", self.annual_working_capital_financial_value_usd, "USD/year carrying value"),
        ]
        table = []
        for key, val, unit in params:
            rationale = self.assumptions_ledger.get(key, default_rationales.get(key, "Model parameter."))
            table.append({
                "parameter": key,
                "value": val,
                "unit": unit,
                "source_or_rationale": rationale,
            })
        return table

    def compute_sensitivity(self, variance: float = 0.20) -> Dict[str, Any]:
        """
        Computes Low (conservative), Mid (base case), and High (optimistic) scenarios.
        Low: -variance on volume, +variance on residual exceptions and touch time, -variance on working capital.
        Mid: base parameters.
        High: +variance on volume, -variance on residual exceptions and touch time, +variance on working capital.
        """
        # Low case (conservative)
        low_vol = max(1, int(self.annual_decision_volume * (1.0 - variance)))
        low_target_mins = self.target_manual_effort_minutes * (1.0 + variance)
        low_target_err = min(1.0, self.target_exception_rate * (1.0 + variance))
        low_wc = self.annual_working_capital_financial_value_usd * (1.0 - variance)

        low_base_labor = low_vol * (self.manual_effort_minutes_per_decision / 60.0) * self.hourly_labor_cost_usd
        low_base_exc = low_vol * self.current_error_or_exception_rate * self.cost_per_exception_usd
        low_base_total = low_base_labor + low_base_exc + low_wc
        low_target_labor = low_vol * (low_target_mins / 60.0) * self.hourly_labor_cost_usd
        low_target_exc = low_vol * low_target_err * self.cost_per_exception_usd
        low_target_total = low_target_labor + low_target_exc
        low_savings = max(0.0, low_base_total - low_target_total)
        low_net_roi = low_savings - self.total_investment_usd()
        low_roi_pct = (low_net_roi / self.total_investment_usd()) * 100.0 if self.total_investment_usd() > 0 else 0.0
        low_monthly = low_savings / 12.0
        low_payback = self.pilot_implementation_cost_usd / low_monthly if low_monthly > 0 else 999.0

        # Mid case (base)
        mid_savings = self.addressable_annual_savings()
        mid_net_roi = self.first_year_net_roi_usd()
        mid_roi_pct = self.expected_roi_percentage()
        mid_payback = self.payback_period_months()

        # High case (optimistic)
        high_vol = int(self.annual_decision_volume * (1.0 + variance))
        high_target_mins = max(0.5, self.target_manual_effort_minutes * (1.0 - variance))
        high_target_err = max(0.001, self.target_exception_rate * (1.0 - variance))
        high_wc = self.annual_working_capital_financial_value_usd * (1.0 + variance)

        high_base_labor = high_vol * (self.manual_effort_minutes_per_decision / 60.0) * self.hourly_labor_cost_usd
        high_base_exc = high_vol * self.current_error_or_exception_rate * self.cost_per_exception_usd
        high_base_total = high_base_labor + high_base_exc + high_wc
        high_target_labor = high_vol * (high_target_mins / 60.0) * self.hourly_labor_cost_usd
        high_target_exc = high_vol * high_target_err * self.cost_per_exception_usd
        high_target_total = high_target_labor + high_target_exc
        high_savings = max(0.0, high_base_total - high_target_total)
        high_net_roi = high_savings - self.total_investment_usd()
        high_roi_pct = (high_net_roi / self.total_investment_usd()) * 100.0 if self.total_investment_usd() > 0 else 0.0
        high_monthly = high_savings / 12.0
        high_payback = self.pilot_implementation_cost_usd / high_monthly if high_monthly > 0 else 999.0

        return {
            "variance_pct": round(variance * 100.0, 1),
            "scenarios": {
                "low_conservative": {
                    "label": f"Low (Conservative -{int(variance*100)}%)",
                    "annual_volume": low_vol,
                    "target_manual_minutes": round(low_target_mins, 1),
                    "target_exception_rate_pct": round(low_target_err * 100, 2),
                    "addressable_annual_savings_usd": round(low_savings, 2),
                    "net_first_year_roi_usd": round(low_net_roi, 2),
                    "roi_percentage": round(low_roi_pct, 1),
                    "payback_period_months": round(low_payback, 1),
                },
                "mid_base_case": {
                    "label": "Mid (Base Case)",
                    "annual_volume": self.annual_decision_volume,
                    "target_manual_minutes": round(self.target_manual_effort_minutes, 1),
                    "target_exception_rate_pct": round(self.target_exception_rate * 100, 2),
                    "addressable_annual_savings_usd": round(mid_savings, 2),
                    "net_first_year_roi_usd": round(mid_net_roi, 2),
                    "roi_percentage": round(mid_roi_pct, 1),
                    "payback_period_months": round(mid_payback, 1),
                },
                "high_optimistic": {
                    "label": f"High (Optimistic +{int(variance*100)}%)",
                    "annual_volume": high_vol,
                    "target_manual_minutes": round(high_target_mins, 1),
                    "target_exception_rate_pct": round(high_target_err * 100, 2),
                    "addressable_annual_savings_usd": round(high_savings, 2),
                    "net_first_year_roi_usd": round(high_net_roi, 2),
                    "roi_percentage": round(high_roi_pct, 1),
                    "payback_period_months": round(high_payback, 1),
                },
            }
        }

    def summary(self) -> Dict[str, Any]:
        tot_inv = round(self.total_investment_usd(), 2)
        annual_lic = round(self.annual_software_subscription_usd, 2)
        return {
            "baseline_annual_total_usd": round(self.baseline_annual_total_cost(), 2),
            "baseline_annual_labor_usd": round(self.baseline_annual_labor_cost(), 2),
            "baseline_annual_exception_usd": round(self.baseline_annual_exception_cost(), 2),
            "target_annual_total_usd": round(self.target_annual_total_cost(), 2),
            "addressable_annual_savings_usd": round(self.addressable_annual_savings(), 2),
            "savings_per_shipment_usd": round(self.savings_per_decision_unit(), 2),
            "pilot_batch_value_usd": round(self.pilot_measured_value(), 2),
            "pilot_implementation_cost_usd": round(self.pilot_implementation_cost_usd, 2),
            "annual_subscription_usd": annual_lic,
            "annual_software_license_usd": annual_lic,
            "total_investment_usd": tot_inv,
            "total_first_year_investment_usd": tot_inv,
            "first_year_net_roi_usd": round(self.first_year_net_roi_usd(), 2),
            "expected_roi_percentage": round(self.expected_roi_percentage(), 1),
            "payback_period_months": round(self.payback_period_months(), 1),
            "assumptions_count": len(self.assumptions_ledger),
            "sensitivity_analysis": self.compute_sensitivity(),
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
