#!/usr/bin/env python3
"""Run report tools for chapter: Advocate and Critical Voices.
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
REPORT_CTX = "Chapter: Advocate and Critical Voices"

def main():
    agent = ReportAgent(
        graph_id=GRAPH_ID,
        simulation_id=SIMULATION_ID,
        simulation_requirement=SIMULATION_REQUIREMENT,
    )
    # 1) get_simulation_posts - preferred first, filter for advocate/critical
    print("\n" + "=" * 60 + "\n[TOOL 1] get_simulation_posts\n" + "=" * 60)
    r1 = agent._execute_tool(
        "get_simulation_posts",
        {
            "platform": None,
            "limit": 100,
            "query": "repair planned obsolescence repairability longevity",
        },
        report_context=REPORT_CTX,
    )
    print(r1 or "(empty)")
    # 2) insight_forge - advocate and critical voices
    print("\n" + "=" * 60 + "\n[TOOL 2] insight_forge\n" + "=" * 60)
    r2 = agent._execute_tool(
        "insight_forge",
        {
            "query": "Advocate and critical voices reaction to Apple skipping iPhone 18 in 2026: Louis Rossmann iFixit right-to-repair planned obsolescence repairability longevity criticism of Apple extend lineup",
            "report_context": REPORT_CTX,
        },
        report_context=REPORT_CTX,
    )
    print(r2 or "(empty)")
    # 3) panorama_search - full picture of advocate/critical
    print("\n" + "=" * 60 + "\n[TOOL 3] panorama_search\n" + "=" * 60)
    r3 = agent._execute_tool(
        "panorama_search",
        {
            "query": "iPhone 18 skip advocate critical repair longevity Louis Rossmann iFixit planned obsolescence",
            "include_expired": True,
        },
        report_context=REPORT_CTX,
    )
    print(r3 or "(empty)")
    # 4) quick_search - advocate critical
    print("\n" + "=" * 60 + "\n[TOOL 4] quick_search\n" + "=" * 60)
    r4 = agent._execute_tool(
        "quick_search",
        {"query": "Apple iPhone 18 skip 2026 repair advocate critical repairability", "limit": 25},
        report_context=REPORT_CTX,
    )
    print(r4 or "(empty)")

if __name__ == "__main__":
    main()
