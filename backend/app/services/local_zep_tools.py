"""
本地图谱工具服务
USE_LOCAL_MODE 时使用，提供与 ZepToolsService 兼容的接口
使用本地 JSON 存储 + 简单关键词搜索
"""

import json
import os
import sqlite3
from typing import Dict, Any, List, Optional

from ..config import Config
from ..utils.logger import get_logger
from .local_graph_storage import get_graph_data
from .graph_tools_types import (
    SearchResult,
    NodeInfo,
    EdgeInfo,
    InsightForgeResult,
    PanoramaResult,
    InterviewResult,
    AgentInterview,
    SimulationPostsResult,
)

logger = get_logger('mirofish.local_zep_tools')


def _keyword_search(
    graph_id: str,
    query: str,
    limit: int = 30,
) -> SearchResult:
    """本地关键词搜索"""
    try:
        data = get_graph_data(graph_id)
    except FileNotFoundError:
        return SearchResult(facts=[], edges=[], nodes=[], query=query, total_count=0)
    
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    
    query_lower = query.lower()
    keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
    
    def match_score(text: str) -> int:
        if not text:
            return 0
        text_lower = str(text).lower()
        if query_lower in text_lower:
            return 100
        score = 0
        for kw in keywords:
            if kw in text_lower:
                score += 10
        return score
    
    facts = []
    edges_result = []
    nodes_result = []
    
    for edge in edges:
        score = match_score(edge.get("fact", "")) + match_score(edge.get("name", ""))
        if score > 0:
            facts.append(edge.get("fact", ""))
            edges_result.append({
                "uuid": edge.get("uuid", ""),
                "name": edge.get("name", ""),
                "fact": edge.get("fact", ""),
                "source_node_uuid": edge.get("source_node_uuid", ""),
                "target_node_uuid": edge.get("target_node_uuid", ""),
            })
    
    for node in nodes:
        score = match_score(node.get("name", "")) + match_score(node.get("summary", ""))
        if score > 0:
            if node.get("summary"):
                facts.append(f"[{node.get('name', '')}]: {node.get('summary', '')}")
            nodes_result.append({
                "uuid": node.get("uuid", ""),
                "name": node.get("name", ""),
                "labels": node.get("labels", []),
                "summary": node.get("summary", ""),
            })
    
    return SearchResult(
        facts=facts[:limit],
        edges=edges_result[:limit],
        nodes=nodes_result[:limit],
        query=query,
        total_count=len(facts),
    )


class LocalZepTools:
    """本地图谱工具，兼容 ZepToolsService 接口"""
    
    def __init__(self, llm_client=None):
        self._llm_client = llm_client
    
    def search_graph(
        self,
        graph_id: str,
        query: str,
        limit: int = 30,
        scope: str = "edges",
    ) -> SearchResult:
        return _keyword_search(graph_id, query, limit)
    
    def quick_search(
        self,
        graph_id: str,
        query: str,
        limit: int = 30,
    ) -> SearchResult:
        return _keyword_search(graph_id, query, limit)
    
    def panorama_search(
        self,
        graph_id: str,
        query: str,
        include_expired: bool = True,
        limit: int = 100,
    ) -> PanoramaResult:
        try:
            data = get_graph_data(graph_id)
        except FileNotFoundError:
            return PanoramaResult(query=query)
        
        nodes = [NodeInfo(
            uuid=n.get("uuid", ""),
            name=n.get("name", ""),
            labels=n.get("labels", []),
            summary=n.get("summary", ""),
            attributes=n.get("attributes", {}),
        ) for n in data.get("nodes", [])]
        
        edges = [EdgeInfo(
            uuid=e.get("uuid", ""),
            name=e.get("name", ""),
            fact=e.get("fact", ""),
            source_node_uuid=e.get("source_node_uuid", ""),
            target_node_uuid=e.get("target_node_uuid", ""),
        ) for e in data.get("edges", [])]
        
        facts = [e.fact for e in edges if e.fact]
        
        result = PanoramaResult(query=query)
        result.all_nodes = nodes
        result.all_edges = edges
        result.active_facts = facts
        result.total_nodes = len(nodes)
        result.total_edges = len(edges)
        result.active_count = len(facts)
        result.historical_count = 0
        return result
    
    def insight_forge(
        self,
        graph_id: str,
        query: str,
        simulation_requirement: str = "",
        report_context: str = "",
    ) -> InsightForgeResult:
        sr = _keyword_search(graph_id, query, limit=15)
        entity_insights = [
            {"name": n.get("name"), "summary": n.get("summary")} for n in sr.nodes
        ]
        relationship_chains = [e.get("fact", "") for e in sr.edges]
        return InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement,
            sub_queries=[query],
            semantic_facts=sr.facts,
            entity_insights=entity_insights,
            relationship_chains=relationship_chains,
            total_facts=len(sr.facts),
            total_entities=len(entity_insights),
            total_relationships=len(relationship_chains),
        )
    
    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        try:
            data = get_graph_data(graph_id)
        except FileNotFoundError:
            return {"node_count": 0, "edge_count": 0, "entity_types": []}
        
        entity_types = set()
        for n in data.get("nodes", []):
            for label in n.get("labels", []):
                if label not in ("Entity", "Node"):
                    entity_types.add(label)
        
        return {
            "node_count": data.get("node_count", 0),
            "edge_count": data.get("edge_count", 0),
            "entity_types": list(entity_types),
        }
    
    def get_simulation_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        获取模拟相关的上下文信息（本地模式）
        与 ZepToolsService.get_simulation_context 接口兼容
        """
        logger.info(f"获取模拟上下文: {simulation_requirement[:50]}...")
        
        search_result = self.search_graph(
            graph_id=graph_id,
            query=simulation_requirement,
            limit=limit,
        )
        
        stats = self.get_graph_statistics(graph_id)
        graph_stats = {
            "total_nodes": stats.get("node_count", 0),
            "total_edges": stats.get("edge_count", 0),
            "entity_types": {t: 1 for t in stats.get("entity_types", [])},
        }
        
        try:
            data = get_graph_data(graph_id)
            entities = []
            for node in data.get("nodes", []):
                custom_labels = [l for l in node.get("labels", []) if l not in ("Entity", "Node")]
                if custom_labels:
                    entities.append({
                        "name": node.get("name", ""),
                        "type": custom_labels[0],
                        "summary": node.get("summary", ""),
                    })
        except FileNotFoundError:
            entities = []
        
        return {
            "simulation_requirement": simulation_requirement,
            "related_facts": search_result.facts,
            "graph_statistics": graph_stats,
            "entities": entities[:limit],
            "total_entities": len(entities),
        }
    
    def get_simulation_posts(
        self,
        simulation_id: str,
        platform: Optional[str] = None,
        limit: int = 100,
        query: Optional[str] = None,
    ) -> SimulationPostsResult:
        """
        获取模拟中Agent发布的帖子（从SQLite数据库读取）
        
        Args:
            simulation_id: 模拟ID
            platform: 平台过滤 (twitter/reddit)，None表示两个平台都查
            limit: 每平台返回数量限制
            query: 可选关键词过滤帖子内容
            
        Returns:
            SimulationPostsResult
        """
        sim_dir = os.path.join(Config.OASIS_SIMULATION_DATA_DIR, simulation_id)
        if not os.path.isdir(sim_dir):
            return SimulationPostsResult(posts=[], total=0, platform=platform)
        
        all_posts: List[Dict[str, Any]] = []
        platforms_to_query = ["twitter", "reddit"] if platform is None else [platform]
        
        for plat in platforms_to_query:
            db_path = os.path.join(sim_dir, f"{plat}_simulation.db")
            if not os.path.exists(db_path):
                continue
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                try:
                    sql = """
                        SELECT p.post_id, p.content, p.created_at, p.user_id,
                               u.name, u.user_name
                        FROM post p
                        LEFT JOIN user u ON p.user_id = u.user_id
                        ORDER BY p.created_at DESC
                        LIMIT ?
                    """
                    cursor.execute(sql, (limit,))
                    rows = cursor.fetchall()
                    for row in rows:
                        r = dict(row)
                        content = r.get("content") or ""
                        if query and query.lower() not in (content or "").lower():
                            continue
                        author = r.get("name") or r.get("user_name") or f"Agent_{r.get('user_id', 0)}"
                        all_posts.append({
                            "content": content,
                            "author_name": author,
                            "platform": plat,
                            "created_at": r.get("created_at") or "",
                        })
                except sqlite3.OperationalError:
                    pass
                finally:
                    conn.close()
            except Exception as e:
                logger.warning(f"读取 {plat} 帖子失败: {e}")
        
        all_posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return SimulationPostsResult(
            posts=all_posts[:limit],
            total=len(all_posts),
            platform=platform,
        )
    
    def get_entity_summary(
        self,
        graph_id: str,
        entity_name: str,
    ) -> Dict[str, Any]:
        try:
            data = get_graph_data(graph_id)
        except FileNotFoundError:
            return {"entity_name": entity_name, "summary": "", "related_facts": []}
        
        node_map = {n["uuid"]: n for n in data.get("nodes", [])}
        related = []
        
        for n in data.get("nodes", []):
            if entity_name in (n.get("name", ""), n.get("summary", "")):
                for e in data.get("edges", []):
                    if e.get("source_node_uuid") == n["uuid"] or e.get("target_node_uuid") == n["uuid"]:
                        related.append(e.get("fact", ""))
                return {
                    "entity_name": n.get("name", ""),
                    "summary": n.get("summary", ""),
                    "related_facts": related[:10],
                }
        
        return {"entity_name": entity_name, "summary": "", "related_facts": []}
    
    def get_entities_by_type(
        self,
        graph_id: str,
        entity_type: str,
    ) -> List[NodeInfo]:
        try:
            data = get_graph_data(graph_id)
        except FileNotFoundError:
            return []
        
        result = []
        for n in data.get("nodes", []):
            if entity_type in n.get("labels", []):
                result.append(NodeInfo(
                    uuid=n.get("uuid", ""),
                    name=n.get("name", ""),
                    labels=n.get("labels", []),
                    summary=n.get("summary", ""),
                    attributes=n.get("attributes", {}),
                ))
        return result
    
    def interview_agents(
        self,
        simulation_id: str,
        interview_requirement: str,
        simulation_requirement: str = "",
        max_agents: int = 15,
        custom_questions: List[str] = None,
    ) -> InterviewResult:
        """采访 Agent（调用 SimulationRunner，与 Zep 版相同）"""
        from .simulation_manager import SimulationManager
        from .simulation_runner import SimulationRunner
        
        result = InterviewResult(
            interview_topic=interview_requirement,
            interview_questions=custom_questions or [interview_requirement],
        )
        
        manager = SimulationManager()
        profiles = manager.get_profiles(simulation_id, platform="reddit")
        
        if not profiles:
            result.summary = "No agent profiles found for interview"
            return result
        
        result.total_agents = len(profiles)
        selected = list(range(min(max_agents, len(profiles))))
        result.selected_agents = [profiles[i] for i in selected]
        
        prompt = (
            "You are being interviewed. Based on your persona and memories, answer in plain text. "
            f"Do not call any tools.\n\nQuestion: {interview_requirement}"
        )
        interviews_req = [{"agent_id": i, "prompt": prompt} for i in selected]
        
        try:
            api_result = SimulationRunner.interview_agents_batch(
                simulation_id=simulation_id,
                interviews=interviews_req,
                platform=None,
                timeout=120.0,
            )
            if api_result.get("success"):
                results = api_result.get("result", {}).get("results", {})
                for i, agent_idx in enumerate(selected):
                    agent = profiles[agent_idx]
                    agent_name = agent.get("name", agent.get("username", f"Agent_{agent_idx}"))
                    agent_role = agent.get("profession", "未知")
                    agent_bio = agent.get("bio", "")[:500]
                    
                    resp = results.get(f"reddit_{agent_idx}", {}) or results.get(f"twitter_{agent_idx}", {})
                    response_text = resp.get("response", "")
                    
                    result.interviews.append(AgentInterview(
                        agent_name=agent_name,
                        agent_role=agent_role,
                        agent_bio=agent_bio,
                        question=interview_requirement,
                        response=response_text,
                        key_quotes=[],
                    ))
                result.interviewed_count = len(result.interviews)
                result.summary = f"成功采访 {len(result.interviews)} 个 Agent"
            else:
                result.summary = "采访失败：模拟环境可能未运行"
        except Exception as e:
            result.summary = f"采访失败: {str(e)}"
        
        return result
