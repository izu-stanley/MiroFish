# Running the report flow and insight_forge tool

## How the report flow gets graph_id and simulation_id

- **API** (`POST /api/report/generate`): The client sends `simulation_id`. The server loads the simulation with `SimulationManager.get_simulation(simulation_id)`, then gets `graph_id` from `state.graph_id` or `project.graph_id`, and `simulation_requirement` from the project.
- **Config / env**: There are no `GRAPH_ID` or `SIMULATION_ID` in `app/config.py` or `.env`. They always come from the simulation/report context.
- **Discovery**: The script `run_insight_forge_tool.py` can discover `graph_id` and `simulation_id` from the latest report under `uploads/reports/<report_id>/meta.json` if you don’t set `GRAPH_ID` / `SIMULATION_ID`.

## Existing data (from your uploads)

- **Graph IDs**: `uploads/local_graphs/` — e.g. `mirofish_local_04f59b373607`, `mirofish_local_01b628b36df4`.
- **Simulation IDs**: `uploads/simulations/` — e.g. `sim_502f105ce2e9`, `sim_d8397b5c4adb`.
- **Report** for chapter “值得关注的未来趋势与风险”: e.g. report `report_677c1e69a4c1` (outline has that section) or `report_ab9495dafd8d` (completed MacBook 15%+16GB report) use:
  - `graph_id`: `mirofish_local_04f59b373607` or `mirofish_local_01b628b36df4`
  - `simulation_id`: `sim_502f105ce2e9` or `sim_d8397b5c4adb`

## Run insight_forge and get raw tool result

From the **backend** directory:

```bash
# Use IDs from latest report (or defaults)
python scripts/run_insight_forge_tool.py
```

With explicit IDs:

```bash
GRAPH_ID=mirofish_local_04f59b373607 SIMULATION_ID=sim_502f105ce2e9 python scripts/run_insight_forge_tool.py
```

The script instantiates `ReportAgent` with that `graph_id` and `simulation_id`, calls `_execute_tool("insight_forge", {"query": "MacBook price increase future trends risks consumer reaction competitor repairability", "report_context": "章节: 值得关注的未来趋势与风险"})`, and prints the **raw tool result** (the string returned by `InsightForgeResult.to_text()`).

- **insight_forge** only needs a valid **graph_id** (it reads from `uploads/local_graphs/<graph_id>/graph.json`). No running simulation or DB is required.
- **get_simulation_posts** needs a valid **simulation_id** and expects SQLite DBs under `uploads/simulations/<simulation_id>/twitter_simulation.db` and `reddit_simulation.db`.

## Run the full report flow

1. Start the backend (e.g. `uv run run.py` or your usual command).
2. Ensure you have a simulation (create via graph + simulation APIs or scripts like `run_twitter_simulation.py` / `run_reddit_simulation.py`).
3. Trigger report generation: `POST /api/report/generate` with `{"simulation_id": "sim_xxxx"}`.
4. Poll `GET /api/report/generate/status?task_id=...` or stream logs; the report agent will call insight_forge, panorama_search, quick_search, get_simulation_posts (and optionally interview_agents) with the simulation’s `graph_id` and `simulation_id`.
