#!/usr/bin/env python3
"""Run report tools for chapter Stakeholder and Community Reaction."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_agent import ReportAgent

GRAPH_ID = os.environ.get("GRAPH_ID", "mirofish_local_01b628b36df4")
SIMULATION_ID = os.environ.get("SIMULATION_ID", "sim_d8397b5c4adb")
SIMULATION_REQUIREMENT = "Simulate Apple MacBook price increase reaction"
REPORT_CTX = "Chapter: Stakeholder and Community Reaction"

def main():
    agent = ReportAgent(
        graph_id=GRAPH_ID,
        simulation_id=SIMULATION_ID,
        simulation_requirement=SIMULATION_REQUIREMENT,
    )
    # 1) get_simulation_posts - preferred first
    print("\n" + "=" * 60 + "\n[TOOL 1] get_simulation_posts\n" + "=" * 60)
    r1 = agent._execute_tool(
        "get_simulation_posts",
        {"platform": None, "limit": 35, "query": "MacBook price increase consumer community reaction"},
        report_context=REPORT_CTX,
    )
    print(r1 or "(empty)")
    # 2) insight_forge - stakeholder and community reaction
    print("\n" + "=" * 60 + "\n[TOOL 2] insight_forge\n" + "=" * 60)
    r2 = agent._execute_tool(
        "insight_forge",
        {
            "query": "MacBook price increase stakeholder and community reaction: consumers, developers, investors, r/apple, competitors Dell Microsoft Framework, sentiment and debate",
            "report_context": REPORT_CTX,
        },
        report_context=REPORT_CTX,
    )
    print(r2 or "(empty)")
    # 3) panorama_search - full picture
    print("\n" + "=" * 60 + "\n[TOOL 3] panorama_search\n" + "=" * 60)
    r3 = agent._execute_tool(
        "panorama_search",
        {"query": "MacBook price increase stakeholder community consumer competitor reaction 16GB", "include_expired": True},
        report_context=REPORT_CTX,
    )
    print(r3 or "(empty)")
    # 4) quick_search - stakeholder community
    print("\n" + "=" * 60 + "\n[TOOL 4] quick_search\n" + "=" * 60)
    r4 = agent._execute_tool(
        "quick_search",
        {"query": "MacBook price increase consumer community reaction 16GB RAM", "limit": 12},
        report_context=REPORT_CTX,
    )
    print(r4 or "(empty)")

if __name__ == "__main__":
    main()
