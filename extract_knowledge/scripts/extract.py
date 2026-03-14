#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_knowledge - 知识点提取工具函数
此 Skill 由 AI 直接执行，不需要调用外部 API
提供辅助函数用于生成知识点 JSON 格式
"""

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

CATEGORIES = ["概念", "定义", "公式", "例题", "定理"]


def create_knowledge_point(
    title: str,
    description: str,
    category: str,
    related_concepts: List[str] = None,
    source_file: str = ""
) -> Dict:
    """
    创建单个知识点对象
    
    Args:
        title: 知识点标题
        description: 详细描述
        category: 分类（概念/定义/公式/例题/定理）
        related_concepts: 相关概念列表
        source_file: 来源文件名
        
    Returns:
        知识点字典
    """
    if category not in CATEGORIES:
        category = "概念"
    
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "category": category,
        "related_concepts": related_concepts or [],
        "source_file": source_file,
        "extracted_at": datetime.now().isoformat() + "Z",
    }


def create_extraction_result(
    chapter: str,
    knowledge_points: List[Dict],
    source_file: str = ""
) -> Dict:
    """
    创建提取结果
    
    Args:
        chapter: 章节名称
        knowledge_points: 知识点列表
        source_file: 来源文件名
        
    Returns:
        提取结果字典
    """
    stats = {
        "total": len(knowledge_points),
        "concepts": sum(1 for kp in knowledge_points if kp["category"] == "概念"),
        "definitions": sum(1 for kp in knowledge_points if kp["category"] == "定义"),
        "formulas": sum(1 for kp in knowledge_points if kp["category"] == "公式"),
        "examples": sum(1 for kp in knowledge_points if kp["category"] == "例题"),
        "theorems": sum(1 for kp in knowledge_points if kp["category"] == "定理"),
    }
    
    return {
        "status": "success",
        "chapter": chapter,
        "knowledge_points": knowledge_points,
        "stats": stats,
    }


def get_extraction_prompt_template() -> str:
    """
    获取知识点提取的提示词模板
    AI 可以参考此模板构建提取提示
    """
    return """请从以下内容中提取知识点。

## 内容
{content}

## 提取要求
1. 识别所有重要的知识点
2. 每个知识点分类为：概念、定义、公式、例题、定理
3. 建立知识点之间的关联

## 输出格式
请输出 JSON 格式：
```json
{
  "chapter": "章节名称",
  "knowledge_points": [
    {
      "title": "知识点标题",
      "description": "详细描述（50-200字）",
      "category": "概念|定义|公式|例题|定理",
      "related_concepts": ["相关概念1", "相关概念2"]
    }
  ]
}
```"""


# 以下函数保留用于命令行测试，但不再调用外部 API
def extract_knowledge(
    raw_content: Dict,
    chapter_name: str,
    existing_knowledge_base: Optional[str] = None
) -> Dict:
    """
    知识点提取函数（由 AI 直接执行）
    
    注意：此函数现在只是一个占位符，实际的知识点提取
    应该由 AI 根据 SKILL.md 中的指导直接完成。
    
    Args:
        raw_content: 解析后的内容
        chapter_name: 章节名称
        existing_knowledge_base: 已有知识库路径
        
    Returns:
        提取结果
    """
    return {
        "status": "pending",
        "message": "知识点提取应由 AI 根据 SKILL.md 指导直接完成",
        "chapter": chapter_name,
        "content_preview": str(raw_content)[:500] if raw_content else "",
    }


def main():
    """主函数，用于测试工具函数"""
    import json
    
    # 测试创建知识点
    kp = create_knowledge_point(
        title="测试知识点",
        description="这是一个测试知识点的描述",
        category="概念",
        related_concepts=["相关概念1", "相关概念2"]
    )
    
    result = create_extraction_result(
        chapter="测试章节",
        knowledge_points=[kp]
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
