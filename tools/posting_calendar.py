#!/usr/bin/env python3
"""
tools/posting_calendar.py
-------------------------
Posting Calendar & Operator Visibility Engine for FDE Tradecraft Distribution.

Commands:
    python tools/posting_calendar.py list           # View full posting schedule & status
    python tools/posting_calendar.py vanguard       # View the 7 Core Vanguard Posts
    python tools/posting_calendar.py view <id>      # Print full post copy ready for clipboard
    python tools/posting_calendar.py status <id> <status>  # Update status (READY_TO_POST, PUBLISHED, etc.)
    python tools/posting_calendar.py set-url <id> <url>    # Set live publication link
    python tools/posting_calendar.py log-operator --name <str> --company <str> --stage <stage> --notes <str>
    python tools/posting_calendar.py scoreboard     # View overall FDE Evidence Scoreboard
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

STATE_PATH = Path(__file__).parent / "calendar_state.json"
REPO_ROOT = Path(__file__).parent.parent

def load_state():
    if not STATE_PATH.exists():
        print(f"[ERROR] State file not found at {STATE_PATH}")
        sys.exit(1)
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def format_status(status: str) -> str:
    badges = {
        "READY_TO_POST": "\033[92m● READY_TO_POST\033[0m",
        "PUBLISHED": "\033[94m✓ PUBLISHED\033[0m",
        "PLANNED": "\033[93m○ PLANNED\033[0m",
        "RESERVED": "\033[90m▫ RESERVED\033[0m",
        "LOCKED_AWAITING_FIELD_EVIDENCE": "\033[95m🔒 AWAITING_FIELD\033[0m"
    }
    return badges.get(status, status)

def cmd_list(args):
    state = load_state()
    posts = state.get("posts", [])
    
    track_filter = args.track.upper() if args.track else None
    if track_filter:
        posts = [p for p in posts if p.get("track") == track_filter]
        
    print("\n" + "=" * 80)
    print("  FDE POSTING CALENDAR & DISTRIBUTION ENGINE")
    print("=" * 80)
    print(f"{'ID':<7} | {'Date':<10} | {'Track':<9} | {'Status':<15} | {'Title'}")
    print("-" * 80)
    for p in posts:
        st = p['status']
        print(f"{p['id']:<7} | {p['scheduled_date']:<10} | {p['track']:<9} | {st:<15} | {p['title'][:34]}")
    print("=" * 80 + "\n")

def cmd_view(args):
    state = load_state()
    post_id = args.post_id.upper()
    post = next((p for p in state["posts"] if p["id"] == post_id), None)
    if not post:
        print(f"[ERROR] Post with ID '{post_id}' not found.")
        sys.exit(1)
        
    md_file = REPO_ROOT / post["file_path"]
    print("\n" + "=" * 80)
    print(f"  FIELD NOTE [{post['id']}]: {post['title']}")
    print(f"  Track: {post['track']} | Target Date: {post['scheduled_date']} ({post['target_days']})")
    print(f"  Anchor: {post['code_anchor']}")
    print("=" * 80)
    
    if md_file.exists():
        with open(md_file, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(f"[WARNING] Markdown file not found at {md_file}")
    print("=" * 80 + "\n")

def cmd_status(args):
    state = load_state()
    post_id = args.post_id.upper()
    new_status = args.status.upper()
    post = next((p for p in state["posts"] if p["id"] == post_id), None)
    if not post:
        print(f"[ERROR] Post '{post_id}' not found.")
        sys.exit(1)
    old = post["status"]
    post["status"] = new_status
    save_state(state)
    print(f"[UPDATED] {post_id}: {old} -> {new_status}")

def cmd_set_url(args):
    state = load_state()
    post_id = args.post_id.upper()
    post = next((p for p in state["posts"] if p["id"] == post_id), None)
    if not post:
        print(f"[ERROR] Post '{post_id}' not found.")
        sys.exit(1)
    post["published_url"] = args.url
    post["status"] = "PUBLISHED"
    save_state(state)
    print(f"[UPDATED] {post_id} published URL set to: {args.url}")

def cmd_scoreboard(args):
    state = load_state()
    sb = state.get("scoreboard", {})
    posts = state.get("posts", [])
    
    published = sum(1 for p in posts if p["status"] == "PUBLISHED")
    total_vanguard = sum(1 for p in posts if p["track"] == "VANGUARD")
    
    print("\n" + "=" * 70)
    print("  FDE OPERATIONAL EVIDENCE & DISTRIBUTION SCOREBOARD")
    print("=" * 70)
    print(f"  Current Provenance Tier:     {sb.get('provenance_tier', 'SYNTHETIC')}")
    print(f"  Vanguard Posts Published:    {published} / {total_vanguard}")
    print(f"  Conversations Initiated:     {sb.get('conversations_initiated', 0)}")
    print(f"  Operator Responses:          {sb.get('operator_replies', 0)}")
    print(f"  Anonymized Datasets Ingested:{sb.get('anonymized_batches_received', 0)}")
    print("-" * 70)
    print("  Next Milestone: 1 Real Operator -> 1 Real Workflow -> Pre-Registered Delta")
    print("=" * 70 + "\n")

def cmd_log_operator(args):
    state = load_state()
    sb = state.setdefault("scoreboard", {})
    logs = state.setdefault("operator_log", [])
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "name": args.name,
        "company": args.company,
        "stage": args.stage,
        "notes": args.notes
    }
    logs.append(entry)
    sb["conversations_initiated"] = sb.get("conversations_initiated", 0) + 1
    if args.stage.upper() in ["CONVERSATION", "ACCESS", "BASELINE", "EVIDENCE"]:
        sb["operator_replies"] = sb.get("operator_replies", 0) + 1
    if args.stage.upper() in ["ACCESS", "BASELINE", "EVIDENCE"]:
        sb["anonymized_batches_received"] = sb.get("anonymized_batches_received", 0) + 1
        sb["provenance_tier"] = "CUSTOMER_PROVIDED"
        
    save_state(state)
    print(f"[LOGGED] Operator contact '{args.name}' ({args.company}) recorded at stage: {args.stage}")
    print(f"         Total conversations: {sb['conversations_initiated']} | Replies: {sb['operator_replies']}")

def main():
    parser = argparse.ArgumentParser(description="FDE Posting Calendar & Visibility Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    p_list = subparsers.add_parser("list", help="List all scheduled posts")
    p_list.add_argument("--track", choices=["vanguard", "reservoir", "crown_jewel"], help="Filter by track")
    p_list.set_defaults(func=cmd_list)
    
    p_vanguard = subparsers.add_parser("vanguard", help="List Vanguard Seven posts")
    p_vanguard.set_defaults(func=lambda a: cmd_list(argparse.Namespace(track="vanguard")))
    
    p_view = subparsers.add_parser("view", help="View full text of a post")
    p_view.add_argument("post_id", help="Post ID (e.g. FN-01)")
    p_view.set_defaults(func=cmd_view)
    
    p_stat = subparsers.add_parser("status", help="Update post status")
    p_stat.add_argument("post_id", help="Post ID (e.g. FN-01)")
    p_stat.add_argument("status", help="New status")
    p_stat.set_defaults(func=cmd_status)
    
    p_url = subparsers.add_parser("set-url", help="Set live published URL")
    p_url.add_argument("post_id", help="Post ID (e.g. FN-01)")
    p_url.add_argument("url", help="Live post URL")
    p_url.set_defaults(func=cmd_set_url)
    
    p_sb = subparsers.add_parser("scoreboard", help="View FDE evidence scoreboard")
    p_sb.set_defaults(func=cmd_scoreboard)
    
    p_log = subparsers.add_parser("log-operator", help="Log operator conversation / stage")
    p_log.add_argument("--name", required=True, help="Operator contact name")
    p_log.add_argument("--company", required=True, help="Company/Organization")
    p_log.add_argument("--stage", required=True, choices=["DISTRIBUTION", "CONVERSATION", "ACCESS", "BASELINE", "EVIDENCE"], help="Scoreboard stage")
    p_log.add_argument("--notes", default="", help="Operational notes / key takeaways")
    p_log.set_defaults(func=cmd_log_operator)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
