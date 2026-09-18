"""Platform-agnostic Agent Specification model."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fde_workbench.domain.ontology import EntityTypeEnum


class ToolDefinition(BaseModel):
    """Platform-agnostic tool specification."""
    name: str = Field(..., description="Tool name e.g. 'read_vue_customs_declaration'")
    description: str = Field(..., description="What the tool does and when to call it")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema of parameters")
    read_only: bool = Field(default=True, description="Whether tool mutates state or merely reads")
    required_permissions: List[str] = Field(default_factory=list, description="Permission scopes required")


class AgentSpecification(BaseModel):
    """
    Platform-agnostic specification defining an autonomous or semi-autonomous
    agent blueprint ready to be compiled to any enterprise AI platform.
    """
    spec_id: str = Field(..., description="Unique specification ID, e.g. 'agent-spec-customs-recon'")
    title: str = Field(..., description="Human-readable agent title")
    version: str = Field(default="1.0.0")
    objective: str = Field(..., description="Clear operational objective and business goal")
    trigger: str = Field(..., description="Trigger condition (e.g. 'On new shipment created', 'Cron: Every 15 min')")
    inputs: List[str] = Field(..., description="Data sources and document feeds provided as inputs")
    entities: List[EntityTypeEnum] = Field(..., description="Domain entities the agent observes or manages")
    context: str = Field(..., description="Operational domain context injected into the agent system instructions")
    tools: List[ToolDefinition] = Field(default_factory=list, description="Available tools and functions")
    permissions: List[str] = Field(default_factory=list, description="Enterprise permissions and access boundaries")
    reasoning_requirements: str = Field(..., description="Deterministic validation vs. fuzzy reasoning requirements")
    human_approval_requirements: str = Field(..., description="Mandatory human sign-off checkpoints")
    actions: List[str] = Field(default_factory=list, description="Permitted actions the agent may execute")
    failure_modes: List[str] = Field(default_factory=list, description="Identified failure modes and fallback actions")
    evaluation_criteria: List[str] = Field(default_factory=list, description="Benchmark test cases and acceptance criteria")
    kpis: List[str] = Field(default_factory=list, description="Operational KPIs targeted for improvement")
