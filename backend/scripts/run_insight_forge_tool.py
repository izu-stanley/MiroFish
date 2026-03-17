#!/usr/bin/env python3
"""
Run report agent's insight_forge tool for a given graph/simulation.
Uses graph_id and simulation_id from env, or discovers from latest report meta.

Usage:
  cd backend && python scripts/run_insight_forge_tool.py
  # Uses defaults from a recent report (mirofish_local_04f59b373607, sim_502f105ce2e9)

  GRAPH_ID=mirofish_local_01b628b36df4 SIMULATION_ID=sim_d8397b5c4adb python scripts/run_insight_forge_tool.py
"""

import json
import os
import sys

# backend root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.services.report_agent import ReportAgent, ReportManager


def _discover_from_reports():
    """Get graph_id and simulation_id from most recent report meta."""
    reports_dir = ReportManager.REPORTS_DIR
    if not os.path.isdir(reports_dir):
        return None, None, None
    best = None
    best_created = ""
    for item in os.listdir(reports_dir):
        path = os.path.join(reports_dir, item, "meta.json")
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            created = meta.get("created_at", "")
            if created and (not best_created or created > best_created):
                best_created = created
                best = meta
        except Exception:
            continue
    if not best:
        return None, None, None
    return (
        best.get("graph_id"),
        best.get("simulation_id"),
        best.get("simulation_requirement", ""),
    )


def main():
    graph_id = os.environ.get("GRAPH_ID")
    simulation_id = os.environ.get("SIMULATION_ID")
    simulation_requirement = os.environ.get("SIMULATION_REQUIREMENT", "")

    if not graph_id or not simulation_id:
        g, s, req = _discover_from_reports()
        if g:
            graph_id = graph_id or g
        if s:
            simulation_id = simulation_id or s
        if req and not simulation_requirement:
            simulation_requirement = req

    # Fallback defaults from known report (MacBook 15% + 16GB)
    if not graph_id:
        graph_id = "mirofish_local_04f59b373607"
    if not simulation_id:
        simulation_id = "sim_502f105ce2e9"
    if not simulation_requirement:
        simulation_requirement = (
            "Simulate how consumers, tech media, developers, and investors would "
            "react on Twitter and Reddit if Apple announces a 15% price increase "
            "across all MacBook models while simultaneously upgrading base RAM to 16GB on every SKU."
        )

    print(f"Using graph_id={graph_id}, simulation_id={simulation_id}\n")

    query = (
        "MacBook price increase future trends risks consumer reaction "
        "competitor repairability"
    )
    report_context = "章节: 值得关注的未来趋势与风险 (Notable Future Trends and Risks)"

    agent = ReportAgent(
        graph_id=graph_id,
        simulation_id=simulation_id,
        simulation_requirement=simulation_requirement,
    )
    raw_result = agent._execute_tool(
        "insight_forge",
        {"query": query, "report_context": report_context},
        report_context=report_context,
    )
    print("=== insight_forge raw tool result ===\n")
    print(raw_result)


if __name__ == "__main__":
    main()
