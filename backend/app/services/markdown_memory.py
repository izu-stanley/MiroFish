"""
Markdown memory layer
Stores persistent context, conversation, and insights in markdown files.
Used by ReportAgent and services needing memory - no cloud.
"""

import os
from typing import Optional

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.markdown_memory')


def _get_memory_dir(project_id: Optional[str] = None, simulation_id: Optional[str] = None) -> str:
    """Get memory directory for project or simulation."""
    base = os.path.join(Config.UPLOAD_FOLDER, 'memory')
    if project_id:
        return os.path.join(base, f'project_{project_id}')
    if simulation_id:
        return os.path.join(base, f'simulation_{simulation_id}')
    return base


def _ensure_dir(path: str) -> None:
    """Ensure parent directory exists."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def read(project_id: Optional[str] = None, simulation_id: Optional[str] = None, filename: str = 'context.md') -> str:
    """
    Read content from a memory file.

    Args:
        project_id: Project ID (optional)
        simulation_id: Simulation ID (optional)
        filename: File name (e.g. context.md, conversation.md, insights.md)

    Returns:
        File content or empty string if not found
    """
    base = _get_memory_dir(project_id, simulation_id)
    path = os.path.join(base, filename)
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write(
    content: str,
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    filename: str = 'context.md',
) -> str:
    """
    Write content to a memory file (overwrites).

    Returns:
        Absolute path of the written file
    """
    base = _get_memory_dir(project_id, simulation_id)
    path = os.path.join(base, filename)
    _ensure_dir(path)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.debug(f"Wrote memory: {path}")
    return os.path.abspath(path)


def append(
    content: str,
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    filename: str = 'conversation.md',
) -> str:
    """
    Append content to a memory file.

    Returns:
        Absolute path of the file
    """
    base = _get_memory_dir(project_id, simulation_id)
    path = os.path.join(base, filename)
    _ensure_dir(path)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)
        if not content.endswith('\n'):
            f.write('\n')
    logger.debug(f"Appended to memory: {path}")
    return os.path.abspath(path)


def get_memory_path(
    project_id: Optional[str] = None,
    simulation_id: Optional[str] = None,
    filename: str = 'context.md',
) -> str:
    """Get the absolute path for a memory file (creates dir if needed)."""
    base = _get_memory_dir(project_id, simulation_id)
    path = os.path.join(base, filename)
    _ensure_dir(path)
    return os.path.abspath(path)
