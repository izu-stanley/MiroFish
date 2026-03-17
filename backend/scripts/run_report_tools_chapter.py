#!/usr/bin/env python3
"""Run insight_forge, panorama_search, quick_search for report chapter 值得关注的未来趋势与风险."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_agent import ReportAgent

GRAPH_ID = os.environ.get("GRAPH_ID", "mirofish_local_01b628b36df4")
SIMULATION_ID = os.environ.get("SIMULATION_ID", "sim_d8397b5c4adb")
SIMULATION_REQUIREMENT = (
    "Simulate Apple MacBook price increase reaction"
)

REPORT_CTX = "章节: 值得关注的未来趋势与风险"

def main():
    agent = ReportAgent(
        graph_id=GRAPH_ID,
        simulation_id=SIMULATION_ID,
        simulation_requirement=SIMULATION_REQUIREMENT,
    )
    # 1) insight_forge
    print("\n" + "="*60 + "\n[TOOL 1] insight_forge\n" + "="*60)
    r1 = agent._execute_tool(
        "insight_forge",
        {"query": "MacBook price increase future trends risks consumer reaction competitor repairability sustainability", "report_context": REPORT_CTX},
        report_context=REPORT_CTX,
    )
    print(r1 or "(empty)")
    # 2) panorama_search
    print("\n" + "="*60 + "\n[TOOL 2] panorama_search\n" + "="*60)
    r2 = agent._execute_tool(
        "panorama_search",
        {"query": "Apple MacBook price increase executive media Dell Microsoft Framework reaction posts", "include_expired": True},
        report_context=REPORT_CTX,
    )
    print(r2 or "(empty)")
    # 3) quick_search
    print("\n" + "="*60 + "\n[TOOL 3] quick_search\n" + "="*60)
    r3 = agent._execute_tool(
        "quick_search",
        {"query": "MacBook 涨价 趋势 风险 竞品 可维修 生态 忠诚度", "limit": 15},
        report_context=REPORT_CTX,
    )
    print(r3 or "(empty)")
    # 4) get_simulation_posts (optional)
    print("\n" + "="*60 + "\n[TOOL 4] get_simulation_posts\n" + "="*60)
    r4 = agent._execute_tool(
        "get_simulation_posts",
        {"limit": 25, "query": "price increase MacBook trend risk"},
        report_context=REPORT_CTX,
    )
    print(r4 or "(empty)")

if __name__ == "__main__":
    main()
