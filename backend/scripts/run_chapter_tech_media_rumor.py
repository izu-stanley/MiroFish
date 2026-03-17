#!/usr/bin/env python3
"""Run report tools for chapter: Tech Media and Rumor Cycle Reaction.
   iPhone 18 skip / Apple 2026 release pause scenario."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_agent import ReportAgent

GRAPH_ID = os.environ.get("GRAPH_ID", "mirofish_local_01b628b36df4")
SIMULATION_ID = os.environ.get("SIMULATION_ID", "sim_d8397b5c4adb")
SIMULATION_REQUIREMENT = (
    "Simulate how consumers, tech media, developers, and everyday iPhone users "
    "would react on Twitter and Reddit if Apple announces it will skip the iPhone 18 "
    "release in 2026 and extend the current lineup's lifecycle by a full year."
)
REPORT_CTX = "Chapter: Tech Media and Rumor Cycle Reaction"

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
        {
            "platform": None,
            "limit": 80,
            "query": "iPhone 18 skip tech media rumor",
        },
        report_context=REPORT_CTX,
    )
    print(r1 or "(empty)")
    # 2) insight_forge - tech media and rumor cycle
    print("\n" + "=" * 60 + "\n[TOOL 2] insight_forge\n" + "=" * 60)
    r2 = agent._execute_tool(
        "insight_forge",
        {
            "query": "Tech media and rumor cycle reaction to Apple skipping iPhone 18 in 2026: how The Verge Bloomberg Mark Gurman MacRumors Ming-Chi Kuo report and speculate, rumor cycle disruption, upgrade cycle coverage, leak ecosystem, what to expect 2027",
            "report_context": REPORT_CTX,
        },
        report_context=REPORT_CTX,
    )
    print(r2 or "(empty)")
    # 3) panorama_search - full picture
    print("\n" + "=" * 60 + "\n[TOOL 3] panorama_search\n" + "=" * 60)
    r3 = agent._execute_tool(
        "panorama_search",
        {
            "query": "iPhone 18 skip tech media rumor cycle Mark Gurman MacRumors The Verge Bloomberg analyst leak",
            "include_expired": True,
        },
        report_context=REPORT_CTX,
    )
    print(r3 or "(empty)")
    # 4) quick_search
    print("\n" + "=" * 60 + "\n[TOOL 4] quick_search\n" + "=" * 60)
    r4 = agent._execute_tool(
        "quick_search",
        {"query": "Apple iPhone 18 skip 2026 tech media rumor cycle coverage", "limit": 25},
        report_context=REPORT_CTX,
    )
    print(r4 or "(empty)")

if __name__ == "__main__":
    main()
