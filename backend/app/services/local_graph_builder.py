"""
本地图谱构建服务
USE_LOCAL_MODE 时使用，替代 GraphBuilderService (Zep)
"""

import uuid
from typing import Dict, Any, List, Optional, Callable

from ..config import Config
from ..utils.logger import get_logger
from .text_processor import TextProcessor
from .local_graph_storage import (
    create_graph,
    set_ontology,
    add_nodes_and_edges,
    get_graph_data,
)
from .local_entity_extractor import LocalEntityExtractor

logger = get_logger('mirofish.local_graph_builder')


class LocalGraphBuilderService:
    """本地图谱构建，无需 Zep Cloud"""
    
    def create_graph(self, name: str) -> str:
        """创建本地图谱"""
        graph_id = f"mirofish_local_{uuid.uuid4().hex[:12]}"
        create_graph(graph_id, name)
        return graph_id
    
    def set_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        """设置本体"""
        set_ontology(graph_id, ontology)
    
    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> List[str]:
        """
        从文本块提取实体并添加到图谱
        本地模式：合并所有块，一次 LLM 调用提取
        """
        # 合并文本
        full_text = "\n\n".join(chunks)
        
        extractor = LocalEntityExtractor()
        
        def cb(msg: str, ratio: float):
            if progress_callback:
                progress_callback(msg, ratio)
        
        nodes, edges = extractor.extract_from_text(
            text=full_text,
            ontology=self._get_ontology(graph_id),
            progress_callback=cb,
        )
        
        if nodes or edges:
            add_nodes_and_edges(graph_id, nodes, edges)
        
        # 返回空列表（本地模式无 episode 等待）
        return []
    
    def _get_ontology(self, graph_id: str) -> Dict[str, Any]:
        """从存储读取本体"""
        import json
        import os
        from .local_graph_storage import _get_graph_path
        
        path = _get_graph_path(graph_id)
        if not os.path.exists(path):
            return {"entity_types": [], "edge_types": []}
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return data.get("ontology") or {"entity_types": [], "edge_types": []}
    
    def _wait_for_episodes(
        self,
        episode_uuids: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None,
        timeout: int = 600,
    ) -> None:
        """本地模式无需等待（实体已同步提取）"""
        if progress_callback:
            progress_callback("Local mode: no wait needed", 1.0)
    
    def get_graph_data(self, graph_id: str) -> Dict[str, Any]:
        """获取图谱数据"""
        return get_graph_data(graph_id)
    
    def delete_graph(self, graph_id: str) -> None:
        """删除图谱"""
        from .local_graph_storage import delete_graph
        delete_graph(graph_id)
