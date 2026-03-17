#!/usr/bin/env python3
"""Run report tools for chapter 媒体与创作者的反应分化."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_agent import ReportAgent

GRAPH_ID = os.environ.get("GRAPH_ID", "mirofish_local_01b628b36df4")
SIMULATION_ID = os.environ.get("SIMULATION_ID", "sim_d8397b5c4adb")
SIMULATION_REQUIREMENT = "Simulate Apple MacBook price increase reaction"
REPORT_CTX = "章节: 媒体与创作者的反应分化"

def main():
    agent = ReportAgent(
        graph_id=GRAPH_ID,
        simulation_id=SIMULATION_ID,
        simulation_requirement=SIMULATION_REQUIREMENT,
    )
    # 1) get_simulation_posts - 优先获取 Agent 发帖
    print("\n" + "=" * 60 + "\n[TOOL 1] get_simulation_posts\n" + "=" * 60)
    r1 = agent._execute_tool(
        "get_simulation_posts",
        {"platform": None, "limit": 35, "query": "MacBook"},
        report_context=REPORT_CTX,
    )
    print(r1 or "(empty)")
    # 2) insight_forge - 媒体与创作者分化
    print("\n" + "=" * 60 + "\n[TOOL 2] insight_forge\n" + "=" * 60)
    r2 = agent._execute_tool(
        "insight_forge",
        {
            "query": "MacBook price increase media and creator reaction differentiation: how tech media vs YouTubers and creators report and comment differently, The Verge Ars Technica MKBHD Linus Tech Tips stance and tone",
            "report_context": REPORT_CTX,
        },
        report_context=REPORT_CTX,
    )
    print(r2 or "(empty)")
    # 3) panorama_search - 全貌
    print("\n" + "=" * 60 + "\n[TOOL 3] panorama_search\n" + "=" * 60)
    r3 = agent._execute_tool(
        "panorama_search",
        {"query": "Apple MacBook price increase media creator The Verge MKBHD Linus Ars Technica coverage reaction", "include_expired": True},
        report_context=REPORT_CTX,
    )
    print(r3 or "(empty)")
    # 4) quick_search - 补充
    print("\n" + "=" * 60 + "\n[TOOL 4] quick_search\n" + "=" * 60)
    r4 = agent._execute_tool(
        "quick_search",
        {"query": "MacBook price increase media creator reaction 16GB", "limit": 12},
        report_context=REPORT_CTX,
    )
    print(r4 or "(empty)")

if __name__ == "__main__":
    main()
