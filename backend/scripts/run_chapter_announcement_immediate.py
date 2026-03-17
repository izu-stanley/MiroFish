#!/usr/bin/env python3
"""Run report tools for chapter: The Announcement and Immediate Future State.
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
REPORT_CTX = "Chapter: The Announcement and Immediate Future State"

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
            "query": "iPhone 18 skip announcement Apple 2026 release pause extend lineup",
        },
        report_context=REPORT_CTX,
    )
    print(r1 or "(empty)")
    # 2) insight_forge - announcement and immediate reaction
    print("\n" + "=" * 60 + "\n[TOOL 2] insight_forge\n" + "=" * 60)
    r2 = agent._execute_tool(
        "insight_forge",
        {
            "query": "Apple skip iPhone 18 2026 announcement immediate reaction: consumers, tech media, developers, Twitter Reddit, rumor cycle, upgrade expectations, product longevity",
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
            "query": "iPhone 18 skip Apple 2026 announcement immediate future state stakeholders reaction",
            "include_expired": True,
        },
        report_context=REPORT_CTX,
    )
    print(r3 or "(empty)")
    # 4) quick_search
    print("\n" + "=" * 60 + "\n[TOOL 4] quick_search\n" + "=" * 60)
    r4 = agent._execute_tool(
        "quick_search",
        {"query": "Apple iPhone 18 skip announcement 2026 consumer media reaction", "limit": 30},
        report_context=REPORT_CTX,
    )
    print(r4 or "(empty)")
    # 5) optional: interview_agents (if simulation running)
    print("\n" + "=" * 60 + "\n[TOOL 5] interview_agents (optional)\n" + "=" * 60)
    try:
        r5 = agent._execute_tool(
            "interview_agents",
            {"interview_topic": "Reaction to Apple announcing it will skip iPhone 18 in 2026 and extend current lineup by one year", "max_agents": 10},
            report_context=REPORT_CTX,
        )
        print(r5 or "(empty)")
    except Exception as e:
        print(f"(interview_agents failed: {e})")

if __name__ == "__main__":
    main()
