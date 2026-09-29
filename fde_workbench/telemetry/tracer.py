"""Granular tracing and observability for Forward Deployed Engineering pipelines.

Tracks:
- Request -> Model -> Retrieval -> Tool -> Decision -> Action lifecycle
- p50, p90, p95 latency
- Token throughput (tokens in / tokens out)
- Live financial inference cost accounting
- State transition traces
"""

import time
import uuid
import math
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# Standard reference pricing per 1M tokens (USD)
MODEL_PRICING = {
    "gemini-2.5-flash": {"input_per_million": 0.15, "output_per_million": 0.60},
    "gemini-2.5-pro": {"input_per_million": 1.25, "output_per_million": 5.00},
    "gpt-4o": {"input_per_million": 2.50, "output_per_million": 10.00},
    "gpt-4o-mini": {"input_per_million": 0.15, "output_per_million": 0.60},
}


class TraceSpan(BaseModel):
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: Optional[str] = None
    name: str  # e.g., "retrieval", "model_inference", "tool_call:báscula_lookup"
    start_time: float
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    model_name: Optional[str] = None
    tool_name: Optional[str] = None
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    error: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)

    def close(self, status: str = "COMPLETED", error: Optional[str] = None):
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 2)
        self.status = status
        self.error = error
        if self.model_name and self.model_name in MODEL_PRICING:
            pricing = MODEL_PRICING[self.model_name]
            in_cost = (self.tokens_in / 1_000_000.0) * pricing["input_per_million"]
            out_cost = (self.tokens_out / 1_000_000.0) * pricing["output_per_million"]
            self.cost_usd = round(in_cost + out_cost, 6)


class TraceRecord(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"trc-{uuid.uuid4().hex[:10]}")
    workflow_name: str
    pilot_id: Optional[str] = None
    start_time: float = Field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    spans: List[TraceSpan] = Field(default_factory=list)
    total_tokens_in: int = 0
    total_tokens_out: int = 0
    total_cost_usd: float = 0.0
    status: str = "RUNNING"
    error: Optional[str] = None

    def start_span(self, name: str, parent_id: Optional[str] = None, **kwargs) -> TraceSpan:
        span = TraceSpan(
            name=name,
            parent_id=parent_id,
            start_time=time.perf_counter(),
            **kwargs,
        )
        self.spans.append(span)
        return span

    def close(self, status: str = "COMPLETED", error: Optional[str] = None):
        self.end_time = time.perf_counter()
        self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 2)
        self.status = status
        self.error = error
        self.total_tokens_in = sum(s.tokens_in for s in self.spans)
        self.total_tokens_out = sum(s.tokens_out for s in self.spans)
        self.total_cost_usd = round(sum(s.cost_usd for s in self.spans), 6)


class TelemetryCollector:
    """In-memory operational telemetry aggregator for FDE runtimes."""

    def __init__(self):
        self.traces: List[TraceRecord] = []

    def record_trace(self, trace: TraceRecord):
        if trace.end_time is None:
            trace.close()
        self.traces.append(trace)

    def get_metrics_summary(self) -> Dict[str, Any]:
        if not self.traces:
            return {
                "total_traces": 0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "error_rate_pct": 0.0,
            }

        latencies = sorted(t.duration_ms for t in self.traces)
        n = len(latencies)

        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return latencies[int(k)]
            d0 = latencies[int(f)] * (c - k)
            d1 = latencies[int(c)] * (k - f)
            return round(d0 + d1, 2)

        errors = sum(1 for t in self.traces if t.status == "FAILED" or t.error is not None)

        return {
            "total_traces": n,
            "avg_latency_ms": round(sum(latencies) / n, 2),
            "p50_latency_ms": percentile(0.50),
            "p90_latency_ms": percentile(0.90),
            "p95_latency_ms": percentile(0.95),
            "p99_latency_ms": percentile(0.99),
            "total_tokens_in": sum(t.total_tokens_in for t in self.traces),
            "total_tokens_out": sum(t.total_tokens_out for t in self.traces),
            "total_tokens": sum(t.total_tokens_in + t.total_tokens_out for t in self.traces),
            "total_cost_usd": round(sum(t.total_cost_usd for t in self.traces), 4),
            "error_rate_pct": round((errors / n) * 100.0, 2),
        }

    def reset(self):
        self.traces.clear()


# Global telemetry singleton
tracer = TelemetryCollector()
