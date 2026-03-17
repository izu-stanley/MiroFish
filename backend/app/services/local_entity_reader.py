"""
本地实体读取器
从本地 JSON 图谱存储读取实体，接口与 ZepEntityReader 兼容
USE_LOCAL_MODE 时使用
"""

from typing import Dict, Any, List, Optional, Set

from ..config import Config
from ..utils.logger import get_logger
from .local_graph_storage import get_graph_data
from .entity_models import EntityNode, FilteredEntities

logger = get_logger('mirofish.local_entity_reader')


class LocalEntityReader:
    """
    本地实体读取器
    从本地 JSON 存储读取，接口与 ZepEntityReader 一致
    """
    
    def get_all_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        """获取图谱所有节点"""
        try:
            data = get_graph_data(graph_id)
        except FileNotFoundError:
            logger.warning(f"图谱不存在: {graph_id}")
            return []
        
        return data.get("nodes", [])
    
    def get_all_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        """获取图谱所有边"""
        try:
            data = get_graph_data(graph_id)
        except FileNotFoundError:
            return []
        
        return data.get("edges", [])
    
    def filter_defined_entities(
        self,
        graph_id: str,
        defined_entity_types: Optional[List[str]] = None,
        enrich_with_edges: bool = True,
    ) -> FilteredEntities:
        """筛选符合预定义类型的实体（与 ZepEntityReader 接口一致）"""
        all_nodes = self.get_all_nodes(graph_id)
        total_count = len(all_nodes)
        
        all_edges = self.get_all_edges(graph_id) if enrich_with_edges else []
        node_map = {n["uuid"]: n for n in all_nodes}
        
        filtered_entities = []
        entity_types_found: Set[str] = set()
        
        for node in all_nodes:
            labels = node.get("labels", [])
            custom_labels = [l for l in labels if l not in ["Entity", "Node"]]
            
            if not custom_labels:
                continue
            
            if defined_entity_types:
                matching = [l for l in custom_labels if l in defined_entity_types]
                if not matching:
                    continue
                entity_type = matching[0]
            else:
                entity_type = custom_labels[0]
            
            entity_types_found.add(entity_type)
            
            entity = EntityNode(
                uuid=node.get("uuid", ""),
                name=node.get("name", ""),
                labels=labels,
                summary=node.get("summary", ""),
                attributes=node.get("attributes", {}),
            )
            
            if enrich_with_edges:
                related_edges = []
                related_node_uuids: Set[str] = set()
                
                for edge in all_edges:
                    if edge.get("source_node_uuid") == node["uuid"]:
                        related_edges.append({
                            "direction": "outgoing",
                            "edge_name": edge.get("name", ""),
                            "fact": edge.get("fact", ""),
                            "target_node_uuid": edge.get("target_node_uuid", ""),
                        })
                        related_node_uuids.add(edge.get("target_node_uuid", ""))
                    elif edge.get("target_node_uuid") == node["uuid"]:
                        related_edges.append({
                            "direction": "incoming",
                            "edge_name": edge.get("name", ""),
                            "fact": edge.get("fact", ""),
                            "source_node_uuid": edge.get("source_node_uuid", ""),
                        })
                        related_node_uuids.add(edge.get("source_node_uuid", ""))
                
                entity.related_edges = related_edges
                entity.related_nodes = [
                    {
                        "uuid": node_map[n]["uuid"],
                        "name": node_map[n]["name"],
                        "labels": node_map[n].get("labels", []),
                        "summary": node_map[n].get("summary", ""),
                    }
                    for n in related_node_uuids if n in node_map
                ]
            
            filtered_entities.append(entity)
        
        # Hard limit: cap entities to MAX_ENTITY_LIMIT
        capped = filtered_entities[:Config.MAX_ENTITY_LIMIT]
        if len(filtered_entities) > Config.MAX_ENTITY_LIMIT:
            logger.info(f"Local graph: entity count exceeded limit, truncated to {Config.MAX_ENTITY_LIMIT}")
        
        logger.info(f"Local graph filter: total {total_count}, matched {len(capped)} (limit {Config.MAX_ENTITY_LIMIT}), types {entity_types_found}")
        
        return FilteredEntities(
            entities=capped,
            entity_types=entity_types_found,
            total_count=total_count,
            filtered_count=len(capped),
        )
    
    def get_entity_with_context(
        self,
        graph_id: str,
        entity_uuid: str,
    ) -> Optional[EntityNode]:
        """获取单个实体及上下文"""
        all_nodes = self.get_all_nodes(graph_id)
        node_map = {n["uuid"]: n for n in all_nodes}
        
        if entity_uuid not in node_map:
            return None
        
        node = node_map[entity_uuid]
        all_edges = self.get_all_edges(graph_id)
        
        related_edges = []
        related_node_uuids: Set[str] = set()
        
        for edge in all_edges:
            if edge.get("source_node_uuid") == entity_uuid:
                related_edges.append({
                    "direction": "outgoing",
                    "edge_name": edge.get("name", ""),
                    "fact": edge.get("fact", ""),
                    "target_node_uuid": edge.get("target_node_uuid", ""),
                })
                related_node_uuids.add(edge.get("target_node_uuid", ""))
            elif edge.get("target_node_uuid") == entity_uuid:
                related_edges.append({
                    "direction": "incoming",
                    "edge_name": edge.get("name", ""),
                    "fact": edge.get("fact", ""),
                    "source_node_uuid": edge.get("source_node_uuid", ""),
                })
                related_node_uuids.add(edge.get("source_node_uuid", ""))
        
        related_nodes = [
            {
                "uuid": node_map[n]["uuid"],
                "name": node_map[n]["name"],
                "labels": node_map[n].get("labels", []),
                "summary": node_map[n].get("summary", ""),
            }
            for n in related_node_uuids if n in node_map
        ]
        
        return EntityNode(
            uuid=node.get("uuid", ""),
            name=node.get("name", ""),
            labels=node.get("labels", []),
            summary=node.get("summary", ""),
            attributes=node.get("attributes", {}),
            related_edges=related_edges,
            related_nodes=related_nodes,
        )
    
    def get_entities_by_type(
        self,
        graph_id: str,
        entity_type: str,
        enrich_with_edges: bool = True,
    ) -> List[EntityNode]:
        """获取指定类型的所有实体"""
        result = self.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=[entity_type],
            enrich_with_edges=enrich_with_edges,
        )
        return result.entities
