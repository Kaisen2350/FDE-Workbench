"""Operational Telemetry & Observability Layer for FDE Workflows.

Distinguishes live operational telemetry (latency, tokens, cost, tool traces)
from tamper-evident cryptographic audit chains (compliance, governance, fraud prevention).
"""

from .tracer import TelemetryCollector, TraceRecord, TraceSpan, tracer

__all__ = ["TelemetryCollector", "TraceRecord", "TraceSpan", "tracer"]
