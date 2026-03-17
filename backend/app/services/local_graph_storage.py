"""
本地图谱存储
USE_LOCAL_MODE 时使用，将图谱数据存储在本地 JSON 文件中
替代 Zep Cloud，实现零外部依赖
"""

import json
import os
import uuid
from typing import Dict, Any, List, Optional

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.local_graph')


def _get_graph_dir(graph_id: str) -> str:
    """获取图谱存储目录"""
    storage_dir = Config.LOCAL_GRAPH_STORAGE_DIR
    os.makedirs(storage_dir, exist_ok=True)
    return os.path.join(storage_dir, graph_id)


def _get_graph_path(graph_id: str) -> str:
    """获取图谱数据文件路径"""
    return os.path.join(_get_graph_dir(graph_id), "graph.json")


def create_graph(graph_id: str, name: str, description: str = "MiroFish Local Graph") -> str:
    """创建本地图谱（初始化目录和空数据文件）"""
    graph_dir = _get_graph_dir(graph_id)
    os.makedirs(graph_dir, exist_ok=True)
    
    meta_path = os.path.join(graph_dir, "meta.json")
    meta = {
        "graph_id": graph_id,
        "name": name,
        "description": description,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    # 初始化空图谱
    graph_data = {"nodes": [], "edges": [], "ontology": None}
    with open(_get_graph_path(graph_id), "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Created local graph: {graph_id}")
    return graph_id


def set_ontology(graph_id: str, ontology: Dict[str, Any]) -> None:
    """保存本体定义"""
    path = _get_graph_path(graph_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"图谱不存在: {graph_id}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["ontology"] = ontology
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.debug(f"已保存本体到图谱 {graph_id}")


def add_nodes_and_edges(
    graph_id: str,
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
) -> None:
    """批量添加节点和边到本地图谱"""
    path = _get_graph_path(graph_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"图谱不存在: {graph_id}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing_uuids = {n["uuid"] for n in data["nodes"]}
    
    for node in nodes:
        if node.get("uuid") not in existing_uuids and len(data["nodes"]) < Config.MAX_ENTITY_LIMIT:
            data["nodes"].append(node)
            existing_uuids.add(node.get("uuid"))
    
    existing_edge_keys = {
        (e.get("source_node_uuid"), e.get("target_node_uuid"), e.get("name", ""))
        for e in data["edges"]
    }
    
    for edge in edges:
        key = (edge.get("source_node_uuid"), edge.get("target_node_uuid"), edge.get("name", ""))
        if key not in existing_edge_keys:
            data["edges"].append(edge)
            existing_edge_keys.add(key)
    
    # Enforce hard limit: truncate to MAX_ENTITY_LIMIT if exceeded
    if len(data["nodes"]) > Config.MAX_ENTITY_LIMIT:
        kept_uuids = {n["uuid"] for n in data["nodes"][:Config.MAX_ENTITY_LIMIT]}
        data["nodes"] = data["nodes"][:Config.MAX_ENTITY_LIMIT]
        data["edges"] = [
            e for e in data["edges"]
            if e.get("source_node_uuid") in kept_uuids and e.get("target_node_uuid") in kept_uuids
        ]
        logger.info(f"图谱 {graph_id}: 实体数超过限制，已截断至 {Config.MAX_ENTITY_LIMIT} 个")
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.debug(f"图谱 {graph_id}: 添加 {len(nodes)} 节点, {len(edges)} 边")


def get_graph_data(graph_id: str) -> Dict[str, Any]:
    """获取完整图谱数据"""
    path = _get_graph_path(graph_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"图谱不存在: {graph_id}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    nodes = data.get("nodes", [])[:Config.MAX_ENTITY_LIMIT]
    edges = data.get("edges", [])
    kept_uuids = {n["uuid"] for n in nodes}
    edges = [e for e in edges if e.get("source_node_uuid") in kept_uuids and e.get("target_node_uuid") in kept_uuids]
    node_map = {n["uuid"]: n.get("name", "") for n in nodes}
    
    # 构建与 Zep 格式兼容的返回结构
    nodes_data = []
    for node in nodes:
        nodes_data.append({
            "uuid": node.get("uuid", ""),
            "name": node.get("name", ""),
            "labels": node.get("labels", ["Entity"]),
            "summary": node.get("summary", ""),
            "attributes": node.get("attributes", {}),
            "created_at": node.get("created_at"),
        })
    
    edges_data = []
    for edge in edges:
        edges_data.append({
            "uuid": edge.get("uuid", ""),
            "name": edge.get("name", ""),
            "fact": edge.get("fact", ""),
            "fact_type": edge.get("name", ""),
            "source_node_uuid": edge.get("source_node_uuid", ""),
            "target_node_uuid": edge.get("target_node_uuid", ""),
            "source_node_name": node_map.get(edge.get("source_node_uuid", ""), ""),
            "target_node_name": node_map.get(edge.get("target_node_uuid", ""), ""),
            "attributes": edge.get("attributes", {}),
            "created_at": edge.get("created_at"),
            "episodes": [],
        })
    
    return {
        "graph_id": graph_id,
        "nodes": nodes_data,
        "edges": edges_data,
        "node_count": len(nodes_data),
        "edge_count": len(edges_data),
    }


def count_agent_post_edges(graph_id: str) -> int:
    """
    Count edges that represent agent posts (written by ZepGraphMemoryUpdater).
    Agent post facts match: "[Agent_name] on twitter: ..." or "[Agent_name] on reddit: ..."
    """
    try:
        data = get_graph_data(graph_id)
        edges = data.get("edges", [])
        count = 0
        for e in edges:
            fact = e.get("fact", "")
            if " on twitter:" in fact or " on reddit:" in fact:
                count += 1
        return count
    except FileNotFoundError:
        return 0


def delete_graph(graph_id: str) -> None:
    """删除本地图谱"""
    import shutil
    graph_dir = _get_graph_dir(graph_id)
    if os.path.exists(graph_dir):
        shutil.rmtree(graph_dir)
        logger.info(f"已删除本地图谱: {graph_id}")
