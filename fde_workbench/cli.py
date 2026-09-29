"""Command-line interface for Paraguay Export Economy FDE Workbench."""

import argparse
import sys
import uvicorn
from pathlib import Path

from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.synthetic.generator import seed_synthetic_company
from fde_workbench.storage.snapshot import save_snapshot_to_file, load_snapshot_from_file


def main():
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="fde-workbench",
        description="Paraguay Export Economy FDE Workbench (Phase 1)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Workbench commands")

    # Command: serve
    serve_parser = subparsers.add_parser("serve", help="Start local FDE Workbench web interface")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    # Command: seed
    seed_parser = subparsers.add_parser("seed", help="Generate and test synthetic exporter dataset")
    seed_parser.add_argument("--export", type=str, default="", help="Optional JSON file path to dump snapshot")

    # Command: discover
    discover_parser = subparsers.add_parser("discover", help="Ingest FDE discovery intake and generate operational model")
    discover_parser.add_argument("--intake", type=str, default="aidesa_discovery_intake.json", help="Path to discovery intake JSON file")

    # Command: export
    export_parser = subparsers.add_parser("export", help="Export workbench snapshot to file")
    export_parser.add_argument("file", type=str, help="Destination JSON filepath")

    # Command: import
    import_parser = subparsers.add_parser("import", help="Import workbench snapshot from file")
    import_parser.add_argument("file", type=str, help="Source JSON filepath")

    # Command: verify-audit
    audit_parser = subparsers.add_parser("verify-audit", help="Verify cryptographic SHA-256 audit log hash-chain")

    # Command: eval
    eval_parser = subparsers.add_parser("eval", help="Run FDE AI benchmark evaluation suite")

    # Command: telemetry
    telemetry_parser = subparsers.add_parser("telemetry", help="Inspect live operational telemetry and latency percentiles")

    # Command: pilot
    pilot_parser = subparsers.add_parser("pilot", help="FDE Pilot Engine operations")
    pilot_sub = pilot_parser.add_subparsers(dest="pilot_action", help="Pilot action")

    # pilot list
    pilot_list = pilot_sub.add_parser("list", help="List registered pilots")

    # pilot brief
    pilot_brief = pilot_sub.add_parser("brief", help="Generate 12-section FDE deployment brief")
    pilot_brief.add_argument("pilot_id", type=str, help="Pilot ID (e.g. pilot-2026-customs-recon)")
    pilot_brief.add_argument("--export", type=str, default="", help="Optional markdown file destination")

    # pilot calibration-brief
    pilot_calib = pilot_sub.add_parser("calibration-brief", help="Generate assumption-stripped calibration brief for operator interviews")
    pilot_calib.add_argument("pilot_id", type=str, help="Pilot ID (e.g. pilot-2026-customs-recon)")
    pilot_calib.add_argument("--export", type=str, default="", help="Optional markdown file destination")

    # pilot economics
    pilot_econ = pilot_sub.add_parser("economics", help="Calculate economic bridge for a pilot")
    pilot_econ.add_argument("pilot_id", type=str, help="Pilot ID (e.g. pilot-2026-customs-recon)")

    # pilot deploy-plan
    pilot_plan = pilot_sub.add_parser("deploy-plan", help="Generate multi-platform deployment plan")
    pilot_plan.add_argument("pilot_id", type=str, help="Pilot ID (e.g. pilot-2026-customs-recon)")
    pilot_plan.add_argument("--platform", type=str, default="gemini_enterprise", help="Target platform")

    args = parser.parse_args()

    # Default action if no subcommand passed: serve
    if not args.command or args.command == "serve":
        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", 8000)
        reload = getattr(args, "reload", False)
        print(f"\n" + "="*70)
        print(f"  PARAGUAY EXPORT ECONOMY · FORWARD DEPLOYED ENGINEER WORKBENCH")
        print(f"="*70)
        print(f"  Local URL:       http://{host}:{port}")
        print(f"  API Docs:        http://{host}:{port}/docs")
        print(f"  Environment:     Phase 1 Local-First (Zero external connections)")
        print(f"="*70 + "\n")
        uvicorn.run("fde_workbench.api.app:app", host=host, port=port, reload=reload)

    elif args.command == "seed":
        store = WorkbenchStore()
        summary = seed_synthetic_company(store)
        print("Synthetic dataset successfully generated:")
        for k, v in summary.items():
            print(f"  {k}: {v}")
        if args.export:
            save_snapshot_to_file(store, args.export)
            print(f"Snapshot saved to: {args.export}")

    elif args.command == "discover":
        import json
        from fde_workbench.domain.discovery import DiscoveryIntake, DiscoveryTransformationEngine
        intake_path = Path(args.intake)
        if not intake_path.exists():
            print(f"Error: Intake file not found: {args.intake}")
            sys.exit(1)
        with open(intake_path, "r", encoding="utf-8") as f:
            intake_dict = json.load(f)
        intake = DiscoveryIntake.model_validate(intake_dict)
        store = WorkbenchStore()
        summary = DiscoveryTransformationEngine.generate_operational_model(intake, store)
        print("FDE Discovery Intake processed successfully:")
        print(f"  Company:            {intake.company_profile.name}")
        print(f"  Industry:           {intake.company_profile.industry}")
        print(f"  Cloud Ecosystem:    {intake.company_profile.cloud_ecosystem}")
        print(f"  Entities Created:   {summary['entities']}")
        print(f"  Opportunities:      {summary['opportunities']}")
        print(f"  Pilot Candidates:   {summary['pilot_candidates']}")

    elif args.command == "export":
        store = WorkbenchStore()
        seed_synthetic_company(store)
        save_snapshot_to_file(store, args.file)
        print(f"Snapshot exported to: {args.file}")

    elif args.command == "import":
        store = WorkbenchStore()
        load_snapshot_from_file(store, args.file)
        print(f"Snapshot imported from: {args.file}. Loaded {len(store._entities)} entities.")

    elif args.command == "verify-audit":
        store = WorkbenchStore()
        result = store.verify_audit_chain()
        if result["valid"]:
            print("Cryptographic Audit Chain: VALID (100% Tamper-Free within current seeded session)")
            print(f"  Total Verified Entries: {result['total_entries']}")
            print(f"  Head Hash:              {result['head_hash']}")
            print("  Scope & Guarantee:      Tamper-evident guarantee covers all state transitions within")
            print("                          the current active database session from initial genesis block.")
            print("                          (Resets to genesis upon explicit database reseed).")
        else:
            print("Cryptographic Audit Chain: CORRUPTED!")
            print(f"  Corrupted Sequence:     {result.get('corrupted_sequence')}")
            print(f"  Reason:                 {result.get('reason')}")
    elif args.command == "eval":
        from fde_workbench.evals.harness import run_eval_suite
        print("\nExecuting FDE Evaluation Benchmark Suite (50 test instances)...")
        res = run_eval_suite()
        print("=" * 75)
        print(f"  FDE AI EVALUATION BENCHMARK & SAFETY REPORT")
        print("=" * 75)
        print(f"  Total Test Cases:          {res.total_eval_cases}")
        print(f"  Task Success Rate:         {res.task_success_rate_pct}%")
        print(f"  Schema Validity:           {res.schema_validity_pct}%")
        print(f"  Unauthorized Actions:      {res.unauthorized_actions} (Invariant: strictly 0)")
        print(f"  p95 Latency:               {res.p95_latency_ms} ms")
        print(f"  Avg Latency:               {res.avg_latency_ms} ms")
        print(f"  Avg Cost per Task:         ${res.avg_cost_per_task_usd:.5f}")
        print(f"  Fallback Rate:             {res.fallback_rate_pct}%")
        print(f"  Safety Gate Status:        {'PASSED' if res.passed_safety_gate else 'FAILED'}")
        print("=" * 75 + "\n")

    elif args.command == "telemetry":
        from fde_workbench.telemetry.tracer import tracer
        from fde_workbench.evals.harness import run_eval_suite
        if not tracer.traces:
            run_eval_suite()
        metrics = tracer.get_metrics_summary()
        print("\n" + "=" * 75)
        print("  FDE OPERATIONAL OBSERVABILITY & TELEMETRY SUMMARY")
        print("=" * 75)
        print(f"  Total Traced Executions:   {metrics['total_traces']}")
        print(f"  p50 Latency:               {metrics['p50_latency_ms']} ms")
        print(f"  p90 Latency:               {metrics['p90_latency_ms']} ms")
        print(f"  p95 Latency:               {metrics['p95_latency_ms']} ms")
        print(f"  p99 Latency:               {metrics['p99_latency_ms']} ms")
        print(f"  Total Tokens In:           {metrics['total_tokens_in']}")
        print(f"  Total Tokens Out:          {metrics['total_tokens_out']}")
        print(f"  Total Cost (USD):          ${metrics['total_cost_usd']:.4f}")
        print(f"  Error Rate:                {metrics['error_rate_pct']}%")
        print("=" * 75 + "\n")

    elif args.command == "pilot":
        from fde_workbench.domain.brief_generator import FDEBriefGenerator
        from fde_workbench.domain.adapters import ADAPTERS
        store = WorkbenchStore()

        if args.pilot_action == "list":
            pilots = store.list_pilots()
            print(f"\nRegistered FDE Pilots ({len(pilots)}):")
            print("-" * 80)
            for p in pilots:
                summary = p.economic_model.summary()
                print(f"[{p.pilot_id}] {p.title}")
                print(f"  Customer:     {p.customer}")
                print(f"  Status:       {p.status.value} | Platform: {p.selected_platform}")
                print(f"  Scope:        {p.pilot_scope}")
                print(f"  Net ROI:      ${summary['first_year_net_roi_usd']:,.2f} ({summary['expected_roi_percentage']}%) | Payback: {summary['payback_period_months']} mo")
                print("-" * 80)

        elif args.pilot_action == "brief":
            pilot = store.get_pilot(args.pilot_id)
            if not pilot:
                print(f"Error: Pilot not found: {args.pilot_id}")
                sys.exit(1)
            md = FDEBriefGenerator.generate_markdown(pilot)
            if args.export:
                with open(args.export, "w", encoding="utf-8") as f:
                    f.write(md)
                print(f"FDE Deployment Brief exported to: {args.export}")
            else:
                print(md)

        elif args.pilot_action == "calibration-brief":
            from fde_workbench.domain.brief_generator import generate_calibration_brief
            try:
                md = generate_calibration_brief(args.pilot_id, store=store)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            if args.export:
                with open(args.export, "w", encoding="utf-8") as f:
                    f.write(md)
                print(f"FDE Calibration Brief exported to: {args.export}")
            else:
                print(md)

        elif args.pilot_action == "economics":
            pilot = store.get_pilot(args.pilot_id)
            if not pilot:
                print(f"Error: Pilot not found: {args.pilot_id}")
                sys.exit(1)
            econ = pilot.economic_model
            s = econ.summary()
            print(f"\nOperational Economic Bridge: {pilot.title} [{pilot.pilot_id}]")
            print("=" * 75)
            print(f"  Annual Volume:             {econ.annual_decision_volume:,} shipments/decisions")
            print(f"  Baseline Labor:            {econ.manual_effort_minutes_per_decision} min/decision @ ${econ.hourly_labor_cost_usd}/hr -> ${s['baseline_annual_labor_usd']:,.2f}/yr")
            print(f"  Baseline Exceptions:       {econ.current_error_or_exception_rate*100:.1f}% rate @ ${econ.cost_per_exception_usd:,.2f}/exception -> ${s['baseline_annual_exception_usd']:,.2f}/yr")
            print(f"  Working Capital Carrying:  ${econ.annual_working_capital_financial_value_usd:,.2f}/yr ({econ.working_capital_acceleration_days} days acceleration)")
            print(f"  Baseline Total Cost:       ${s['baseline_annual_total_usd']:,.2f}/yr")
            print("-" * 75)
            print(f"  Target Post-Intervention:  ${s['target_annual_total_usd']:,.2f}/yr ({econ.target_manual_effort_minutes} min, {econ.target_exception_rate*100:.1f}% exceptions)")
            print(f"  Addressable Annual Saving: ${s['addressable_annual_savings_usd']:,.2f}/yr (${s['savings_per_shipment_usd']:,.2f} / unit)")
            print(f"  Pilot Batch Value:         ${s['pilot_batch_value_usd']:,.2f} ({econ.pilot_decision_volume} test units)")
            print("-" * 75)
            print(f"  Implementation Cost:       ${s['pilot_implementation_cost_usd']:,.2f}")
            print(f"  Annual Subscription:       ${s['annual_subscription_usd']:,.2f}")
            print(f"  Net First-Year ROI:        ${s['first_year_net_roi_usd']:,.2f} ({s['expected_roi_percentage']}%)")
            print(f"  Payback Period:            {s['payback_period_months']} months")
            print("=" * 75 + "\n")

        elif args.pilot_action == "deploy-plan":
            pilot = store.get_pilot(args.pilot_id)
            if not pilot:
                print(f"Error: Pilot not found: {args.pilot_id}")
                sys.exit(1)
            platform = args.platform.lower()
            adapter = ADAPTERS.get(platform)
            if not adapter:
                print(f"Error: Unknown platform: {platform}. Supported: {list(ADAPTERS.keys())}")
                sys.exit(1)
            plan = adapter.generate_pilot_deployment_plan(pilot)
            import json
            print(json.dumps(plan, indent=2))
        else:
            pilot_parser.print_help()


if __name__ == "__main__":
    main()
