"""
Pipeline orchestrator for CLI
Runs the full MiroFish workflow: init -> ontology -> graph -> simulate -> report
Uses Cursor Agent as the brain, no cloud dependencies.
"""

import os
import glob
import time
from typing import List, Optional, Callable

from ..config import Config
from ..models.project import ProjectManager, ProjectStatus
from ..utils.file_parser import FileParser
from ..utils.logger import get_logger
from .text_processor import TextProcessor
from .ontology_generator import OntologyGenerator
from .local_graph_builder import LocalGraphBuilderService
from .local_graph_storage import count_agent_post_edges
from .simulation_manager import SimulationManager, SimulationStatus
from .simulation_runner import SimulationRunner, RunnerStatus
from .report_agent import ReportAgent, ReportManager, ReportStatus

logger = get_logger('mirofish.pipeline')

ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}


def _collect_seed_files(project_dir: str, seed_files: Optional[List[str]] = None) -> List[str]:
    """Collect seed file paths from directory or explicit list."""
    if seed_files:
        resolved = []
        for p in seed_files:
            path = p if os.path.isabs(p) else os.path.join(project_dir, p)
            if os.path.isfile(path):
                resolved.append(path)
        return resolved
    paths = []
    for ext in ALLOWED_EXTENSIONS:
        paths.extend(glob.glob(os.path.join(project_dir, f'*.{ext}')))
    return sorted(paths)


def run_pipeline(
    project_dir: str,
    requirement: str,
    seed_files: Optional[List[str]] = None,
    project_name: Optional[str] = None,
    max_rounds: Optional[int] = None,
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> dict:
    """
    Run the full MiroFish pipeline.

    Args:
        project_dir: Directory containing seed files (or base dir when seed_files provided)
        requirement: Simulation requirement description
        seed_files: Optional explicit list of file paths (overrides project_dir scan)
        project_name: Optional project name
        max_rounds: Optional max simulation rounds
        progress_callback: Optional (stage, message) callback

    Returns:
        Dict with project_id, simulation_id, report_id, report_path, report_content
    """
    def _progress(stage: str, msg: str):
        logger.info(f"[{stage}] {msg}")
        if progress_callback:
            progress_callback(stage, msg)

    # Resolve backend root for workspace (Cursor Agent needs a path)
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(backend_root, 'uploads')

    # 1. Init: create project and ingest files
    _progress("init", "Creating project...")
    project = ProjectManager.create_project(name=project_name or os.path.basename(project_dir) or "CLI Project")
    project.simulation_requirement = requirement
    ProjectManager.save_project(project)

    files = _collect_seed_files(project_dir, seed_files)
    if not files:
        raise ValueError(
            f"No seed files found in {project_dir}. "
            f"Add .md, .txt, .pdf files or use --seed-file to specify paths."
        )

    document_texts = []
    all_text = ""
    for fp in files:
        _progress("init", f"Ingesting {os.path.basename(fp)}...")
        info = ProjectManager.add_file_from_path(project.project_id, fp)
        project.files.append({"filename": info["original_filename"], "size": info["size"]})
        text = FileParser.extract_text(info["path"])
        text = TextProcessor.preprocess_text(text)
        document_texts.append(text)
        all_text += f"\n\n=== {info['original_filename']} ===\n{text}"

    project.total_text_length = len(all_text)
    ProjectManager.save_extracted_text(project.project_id, all_text)
    ProjectManager.save_project(project)
    _progress("init", f"Project {project.project_id} created with {len(files)} files")

    # 2. Ontology
    _progress("ontology", "Generating ontology via Cursor Agent...")
    generator = OntologyGenerator()
    ontology = generator.generate(
        document_texts=document_texts,
        simulation_requirement=requirement,
        additional_context=None,
    )
    project.ontology = {
        "entity_types": ontology.get("entity_types", []),
        "edge_types": ontology.get("edge_types", []),
    }
    project.analysis_summary = ontology.get("analysis_summary", "")
    project.status = ProjectStatus.ONTOLOGY_GENERATED
    ProjectManager.save_project(project)
    _progress("ontology", f"Ontology: {len(project.ontology['entity_types'])} entity types")

    # 3. Graph build
    _progress("graph", "Building local graph...")
    text = ProjectManager.get_extracted_text(project.project_id)
    chunks = TextProcessor.split_text(
        text,
        chunk_size=project.chunk_size or Config.DEFAULT_CHUNK_SIZE,
        overlap=project.chunk_overlap or Config.DEFAULT_CHUNK_OVERLAP,
    )
    builder = LocalGraphBuilderService()
    graph_id = builder.create_graph(name=project.name or "MiroFish Graph")
    project.graph_id = graph_id
    ProjectManager.save_project(project)
    builder.set_ontology(graph_id, project.ontology)
    builder.add_text_batches(graph_id, chunks, batch_size=3)
    project.status = ProjectStatus.GRAPH_COMPLETED
    ProjectManager.save_project(project)
    graph_data = builder.get_graph_data(graph_id)
    _progress("graph", f"Graph built: {graph_data.get('node_count', 0)} nodes, {graph_data.get('edge_count', 0)} edges")

    # 4. Create and prepare simulation
    _progress("simulation", "Creating simulation...")
    manager = SimulationManager()
    state = manager.create_simulation(
        project_id=project.project_id,
        graph_id=graph_id,
        enable_twitter=True,
        enable_reddit=True,
    )

    def _sim_progress(stage, pct, msg, **kwargs):
        _progress("simulation", f"[{stage}] {msg}")

    manager.prepare_simulation(
        simulation_id=state.simulation_id,
        simulation_requirement=requirement,
        document_text=all_text[:50000],
        use_llm_for_profiles=True,
        progress_callback=_sim_progress,
    )
    state = manager.get_simulation(state.simulation_id)
    if state.status == SimulationStatus.FAILED:
        raise RuntimeError(f"Simulation preparation failed: {state.error}")

    # 5. Run simulation
    _progress("simulation", "Starting simulation...")
    SimulationRunner.start_simulation(
        simulation_id=state.simulation_id,
        platform="parallel",
        max_rounds=max_rounds or Config.OASIS_DEFAULT_MAX_ROUNDS,
        enable_graph_memory_update=True,
        graph_id=graph_id,
    )
    # Poll until complete
    while True:
        run_state = SimulationRunner.get_run_state(state.simulation_id)
        if not run_state:
            break
        status = run_state.runner_status
        if status in (RunnerStatus.COMPLETED, RunnerStatus.STOPPED, RunnerStatus.FAILED):
            break
        _progress("simulation", f"Running... round {run_state.current_round}/{run_state.total_rounds}")
        time.sleep(5)
    _progress("simulation", "Simulation complete")

    # Verify graph memory: log agent post count
    agent_post_count = count_agent_post_edges(graph_id)
    _progress("simulation", f"Graph memory: {agent_post_count} agent post edges in graph")

    # 6. Report
    _progress("report", "Generating report via Cursor Agent...")

    def _report_progress(stage, progress, message):
        _progress("report", f"[{stage}] {message}")

    agent = ReportAgent(
        graph_id=graph_id,
        simulation_id=state.simulation_id,
        simulation_requirement=requirement,
    )
    report = agent.generate_report(progress_callback=_report_progress)
    report_path = ReportManager._get_report_markdown_path(report.report_id)
    report_content = ""
    if report_path and os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

    _progress("report", f"Report saved: {report_path or report.report_id}")

    return {
        "project_id": project.project_id,
        "simulation_id": state.simulation_id,
        "report_id": report.report_id,
        "report_path": report_path,
        "report_content": report_content,
    }
