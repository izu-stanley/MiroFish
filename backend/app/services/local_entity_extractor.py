"""
本地实体提取器
使用 Cursor Agent 从文档中提取实体和关系，用于本地图谱构建
替代 Zep 的自动实体抽取，适合本地/离线模式
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Callable

from ..config import Config
from ..utils.cursor_agent_client import CursorAgentClient
from ..utils.logger import get_logger
from .text_processor import TextProcessor

logger = get_logger('mirofish.local_extractor')

# 单次提取的文本长度限制（本地模式为减少 LLM 调用）
MAX_TEXT_FOR_EXTRACTION = 30000


EXTRACTION_PROMPT = """你是一个知识图谱实体抽取专家。根据给定的文档和本体定义，提取所有相关实体及其关系。

## 本体定义（实体类型和关系类型）

{ontology_json}

## 文档内容

{document_preview}

## 任务

请从文档中提取：
1. **实体**：每个实体必须有 name（名称）、entity_type（对应本体中的实体类型名）、summary（简短描述，1-2句话）、attributes（属性字典，根据该类型的 attributes 定义填写）
2. **关系**：每条关系必须有 source_name（源实体名称）、target_name（目标实体名称）、edge_type（关系类型名）、fact（关系描述）

## 输出格式（严格 JSON）

```json
{{
  "entities": [
    {{
      "name": "实体名称",
      "entity_type": "Student",
      "summary": "武汉大学计算机系学生，关注校园事件",
      "attributes": {{"full_name": "张三", "role": "学生"}}
    }}
  ],
  "relationships": [
    {{
      "source_name": "张三",
      "target_name": "武汉大学",
      "edge_type": "STUDIES_AT",
      "fact": "张三就读于武汉大学计算机系"
    }}
  ]
}}
```

**规则**：
- 只提取文档中明确提到的实体，不要编造
- 实体类型必须在本体 entity_types 的 name 中存在
- 关系类型必须在本体 edge_types 的 name 中存在
- 若实体无法归类到具体类型，使用 Person 或 Organization
- 最多提取 {max_entities} 个实体（优先重要角色），{max_relationships} 条关系
"""


class LocalEntityExtractor:
    """使用 Cursor Agent 从文档提取实体和关系"""
    
    def __init__(self, llm_client: Optional[CursorAgentClient] = None):
        self.llm_client = llm_client or CursorAgentClient()
    
    def extract_from_text(
        self,
        text: str,
        ontology: Dict[str, Any],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        从文本中提取实体和关系
        
        Args:
            text: 文档文本
            ontology: 本体定义（entity_types, edge_types）
            chunk_size: 分块大小（大文档时使用）
            chunk_overlap: 块重叠
            progress_callback: 进度回调 (message, progress_ratio)
            
        Returns:
            (nodes, edges) 节点和边列表
        """
        # 截断过长的文本以节省 LLM 调用
        if len(text) > MAX_TEXT_FOR_EXTRACTION:
            text = text[:MAX_TEXT_FOR_EXTRACTION] + "\n\n...(文档已截断，仅分析前文)..."
            logger.info(f"文档截断至 {MAX_TEXT_FOR_EXTRACTION} 字符用于实体提取")
        
        if progress_callback:
            progress_callback("调用 LLM 提取实体...", 0.1)
        
        ontology_json = json.dumps(ontology, ensure_ascii=False, indent=2)
        
        entity_type_names = [e["name"] for e in ontology.get("entity_types", [])]
        edge_type_names = [e["name"] for e in ontology.get("edge_types", [])]
        
        max_entities = Config.MAX_ENTITY_LIMIT
        max_relationships = max_entities * 2  # allow 2 relationships per entity
        prompt = EXTRACTION_PROMPT.format(
            ontology_json=ontology_json,
            document_preview=text,
            max_entities=max_entities,
            max_relationships=max_relationships,
        )
        
        messages = [
            {"role": "system", "content": "你输出严格的 JSON，不要包含任何其他文字。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.llm_client.chat_json_messages(
                messages=messages,
                temperature=0.2,
                max_tokens=8192,
            )
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            raise
        
        if progress_callback:
            progress_callback("解析提取结果...", 0.8)
        
        entities = response.get("entities", [])[:Config.MAX_ENTITY_LIMIT]
        relationships = response.get("relationships", [])
        
        # 构建节点
        name_to_uuid = {}
        nodes = []
        
        for ent in entities:
            entity_type = ent.get("entity_type", "Person")
            if entity_type not in entity_type_names:
                entity_type = "Person" if "Person" in entity_type_names else entity_type_names[0]
            
            node_uuid = str(uuid.uuid4())
            name = ent.get("name", "Unknown")
            name_to_uuid[name] = node_uuid
            
            nodes.append({
                "uuid": node_uuid,
                "name": name,
                "labels": ["Entity", entity_type],
                "summary": ent.get("summary", ""),
                "attributes": ent.get("attributes", {}),
                "created_at": None,
            })
        
        # 构建边
        edges = []
        for rel in relationships:
            src_name = rel.get("source_name", "")
            tgt_name = rel.get("target_name", "")
            edge_type = rel.get("edge_type", "RELATED_TO")
            
            if edge_type not in edge_type_names:
                edge_type = edge_type_names[0] if edge_type_names else "RELATED_TO"
            
            src_uuid = name_to_uuid.get(src_name)
            tgt_uuid = name_to_uuid.get(tgt_name)
            
            if src_uuid and tgt_uuid:
                edges.append({
                    "uuid": str(uuid.uuid4()),
                    "name": edge_type,
                    "fact": rel.get("fact", ""),
                    "source_node_uuid": src_uuid,
                    "target_node_uuid": tgt_uuid,
                    "attributes": {},
                    "created_at": None,
                })
        
        if progress_callback:
            progress_callback(f"Extraction complete: {len(nodes)} entities, {len(edges)} relations", 1.0)
        
        logger.info(f"Entity extraction complete: {len(nodes)} nodes, {len(edges)} edges")
        
        return nodes, edges
