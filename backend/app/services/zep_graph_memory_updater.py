"""
Graph memory updater - stub for Zep Cloud; local mode writes to local graph.
"""

import threading
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentActivity:
    """Agent活动记录 (stub)"""
    platform: str = ""
    agent_id: int = 0
    agent_name: str = ""
    action_type: str = ""
    action_args: Dict[str, Any] = None
    round_num: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if self.action_args is None:
            self.action_args = {}


class ZepGraphMemoryUpdater:
    """
    Graph memory updater.
    - Zep Cloud mode: no-op (stub)
    - Local mode: writes agent posts to local graph as searchable edges
    """

    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        self._hub_uuid: Optional[str] = None

    def start(self):
        pass

    def stop(self):
        pass

    def add_activity(self, *args, **kwargs):
        pass

    def add_activity_from_dict(self, action_data: dict, platform: str):
        """
        将Agent活动写入图谱（仅本地模式且 action_type=CREATE_POST 时）
        """
        from ..config import Config
        if not Config.USE_LOCAL_MODE:
            return
        action_type = action_data.get("action_type", "")
        if action_type != "CREATE_POST":
            return
        action_args = action_data.get("action_args") or {}
        content = action_args.get("content", "").strip()
        if not content:
            return
        agent_name = action_data.get("agent_name", f"Agent_{action_data.get('agent_id', 0)}")

        from .local_graph_storage import get_graph_data, add_nodes_and_edges

        try:
            data = get_graph_data(self.graph_id)
            nodes = data.get("nodes", [])
            if not nodes:
                return
            hub_uuid = nodes[0]["uuid"]

            edge_uuid = str(uuid.uuid4())
            fact = f"[{agent_name}] on {platform}: {content}"
            edge = {
                "uuid": edge_uuid,
                "name": f"agent_post_{uuid.uuid4().hex[:8]}",
                "fact": fact,
                "source_node_uuid": hub_uuid,
                "target_node_uuid": hub_uuid,
            }
            add_nodes_and_edges(self.graph_id, [], [edge])
        except Exception as e:
            from ..utils.logger import get_logger
            get_logger("mirofish.zep_graph_memory").warning(f"写入图谱失败: {e}")


class ZepGraphMemoryManager:
    """Stub: no-op manager (Zep Cloud removed)."""

    _updaters: Dict[str, ZepGraphMemoryUpdater] = {}
    _lock = threading.Lock()
    _stop_all_done = False

    @classmethod
    def create_updater(cls, simulation_id: str, graph_id: str) -> ZepGraphMemoryUpdater:
        updater = ZepGraphMemoryUpdater(graph_id)
        updater.start()
        with cls._lock:
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
            cls._updaters[simulation_id] = updater
        return updater

    @classmethod
    def get_updater(cls, simulation_id: str) -> Optional[ZepGraphMemoryUpdater]:
        return cls._updaters.get(simulation_id)

    @classmethod
    def stop_updater(cls, simulation_id: str):
        with cls._lock:
            if simulation_id in cls._updaters:
                cls._updaters[simulation_id].stop()
                del cls._updaters[simulation_id]

    @classmethod
    def stop_all(cls):
        if cls._stop_all_done:
            return
        cls._stop_all_done = True
        with cls._lock:
            for updater in cls._updaters.values():
                try:
                    updater.stop()
                except Exception:
                    pass
            cls._updaters.clear()

    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        return {}
