#!/usr/bin/env python3
"""
MiroFish CLI - Run the full pipeline without the UI.
Uses Cursor Agent as the brain, no Ollama, no cloud.
"""

import argparse
import os
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="MiroFish CLI - Run the full simulation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mirofish run ./my-project --requirement "Predict campus event outcomes"
  mirofish run . --seed-file doc.md --requirement "Simulate social media response"
        """,
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Directory containing seed files (.md, .txt, .pdf) or base dir when using --seed-file",
    )
    parser.add_argument(
        "--seed-file",
        action="append",
        dest="seed_files",
        metavar="PATH",
        help="Explicit seed file path (can be repeated)",
    )
    parser.add_argument(
        "-r",
        "--requirement",
        required=True,
        help="Simulation requirement description",
    )
    parser.add_argument(
        "--name",
        dest="project_name",
        help="Project name (optional)",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        help="Max simulation rounds (default: from config)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        help="Write report to file (default: print to stdout)",
    )

    args = parser.parse_args()

    # Resolve project_dir before changing cwd
    project_dir = os.path.abspath(os.path.expanduser(args.project_dir))
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Add backend to path and set cwd
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(script_dir, "backend")
    sys.path.insert(0, backend_dir)
    os.chdir(backend_dir)

    from app.services.pipeline import run_pipeline

    def progress(stage: str, msg: str):
        print(f"[{stage}] {msg}", flush=True)

    try:
        result = run_pipeline(
            project_dir=project_dir,
            requirement=args.requirement,
            seed_files=args.seed_files,
            project_name=args.project_name,
            max_rounds=args.max_rounds,
            progress_callback=progress,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n--- Pipeline complete ---")
    print(f"Project ID: {result['project_id']}")
    print(f"Simulation ID: {result['simulation_id']}")
    print(f"Report ID: {result['report_id']}")
    print(f"Report path: {result['report_path']}")

    report_content = result.get("report_content", "")
    if report_content:
        # Always save to versioned path: reports/report_YYYYMMDD_HHMMSS.md
        reports_dir = os.path.join(project_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_path = os.path.join(reports_dir, f"report_{timestamp}.md")
        with open(versioned_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report written to: {versioned_path}")

        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"Report also written to: {args.output_file}")


if __name__ == "__main__":
    main()
