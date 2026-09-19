"""Command-line interface for Paraguay Export Economy FDE Workbench."""

import argparse
import sys
import uvicorn
from pathlib import Path

from fde_workbench.storage.store import WorkbenchStore
from fde_workbench.synthetic.generator import seed_synthetic_company
from fde_workbench.storage.snapshot import save_snapshot_to_file, load_snapshot_from_file


def main():
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
            print("Cryptographic Audit Chain: VALID (100% Tamper-Free)")
            print(f"  Total Verified Entries: {result['total_entries']}")
            print(f"  Head Hash:              {result['head_hash']}")
        else:
            print("Cryptographic Audit Chain: CORRUPTED!")
            print(f"  Corrupted Sequence:     {result.get('corrupted_sequence')}")
            print(f"  Reason:                 {result.get('reason')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
