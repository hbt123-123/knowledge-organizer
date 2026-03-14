#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_knowledge - 知识融合模块
将新知识点合并到知识库，处理重复和冲突
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


def load_knowledge_base(path: str) -> Dict:
    """加载知识库"""
    if not os.path.exists(path):
        # 创建新知识库
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat() + "Z",
            "last_updated": datetime.now().isoformat() + "Z",
            "chapters": {},
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat() + "Z",
            "last_updated": datetime.now().isoformat() + "Z",
            "chapters": {},
        }


def save_knowledge_base(path: str, base: Dict) -> bool:
    """保存知识库"""
    try:
        # 确保目录存在
        os.makedirs(
            os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True
        )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def find_duplicate(kp: Dict, chapter_kps: List[Dict]) -> Optional[Dict]:
    """查找重复的知识点"""
    for existing in chapter_kps:
        # 标题相同视为重复
        if existing.get("title") == kp.get("title"):
            return existing
    return None


def merge_knowledge_base(
    new_knowledge: List[Dict], knowledge_base: Dict, strategy: str = "merge", 
    default_chapter: str = "未分类"
) -> Dict:
    """
    合并知识点到知识库

    Args:
        new_knowledge: 新知识点列表
        knowledge_base: 现有知识库
        strategy: 合并策略 (overwrite/add/merge)
        default_chapter: 默认章节名（当知识点无章节时使用）

    Returns:
        合并结果统计
    """
    stats = {"added": 0, "modified": 0, "skipped": 0, "conflicts_resolved": 0}

    chapter_groups = {}
    for kp in new_knowledge:
        chapter = kp.get("chapter") or default_chapter
        if chapter not in chapter_groups:
            chapter_groups[chapter] = []
        chapter_groups[chapter].append(kp)

    # 处理每个章节
    for chapter, kps in chapter_groups.items():
        if chapter not in knowledge_base["chapters"]:
            knowledge_base["chapters"][chapter] = {"knowledge_points": []}

        chapter_kps = knowledge_base["chapters"][chapter]["knowledge_points"]

        for kp in kps:
            duplicate = find_duplicate(kp, chapter_kps)

            if duplicate:
                if strategy == "overwrite":
                    # 完全覆盖
                    chapter_kps.remove(duplicate)
                    chapter_kps.append(kp)
                    stats["modified"] += 1
                elif strategy == "add":
                    # 跳过
                    stats["skipped"] += 1
                else:  # merge
                    # 智能合并：更新内容但保留关联
                    merged_kp = {**duplicate, **kp}
                    merged_kp["updated_at"] = datetime.now().isoformat() + "Z"
                    chapter_kps.remove(duplicate)
                    chapter_kps.append(merged_kp)
                    stats["modified"] += 1
                    if duplicate.get("description") != kp.get("description"):
                        stats["conflicts_resolved"] += 1
            else:
                # 新增
                kp["created_at"] = datetime.now().isoformat() + "Z"
                kp["updated_at"] = datetime.now().isoformat() + "Z"
                chapter_kps.append(kp)
                stats["added"] += 1

    # 更新时间戳
    knowledge_base["last_updated"] = datetime.now().isoformat() + "Z"

    # 更新版本号
    if stats["added"] > 0 or stats["modified"] > 0:
        version_parts = knowledge_base["version"].split(".")
        if len(version_parts) == 3:
            patch = int(version_parts[2]) + 1
            knowledge_base["version"] = f"{version_parts[0]}.{version_parts[1]}.{patch}"

    return stats


def merge(
    new_knowledge: List[Dict], knowledge_base_path: str, strategy: str = "merge",
    extraction_result: Dict = None
) -> Dict:
    """
    主合并函数

    Args:
        new_knowledge: 新知识点列表
        knowledge_base_path: 知识库路径
        strategy: 合并策略
        extraction_result: 完整的提取结果（包含 chapter 字段），用于获取章节名

    Returns:
        合并结果
    """
    if not new_knowledge:
        return {"status": "error", "error": "Empty knowledge list"}

    if not knowledge_base_path:
        return {"status": "error", "error": "Missing knowledge base path"}

    default_chapter = "未分类"
    if extraction_result and "chapter" in extraction_result:
        default_chapter = extraction_result["chapter"]

    for kp in new_knowledge:
        if "chapter" not in kp or not kp["chapter"]:
            kp["chapter"] = default_chapter

    kb = load_knowledge_base(knowledge_base_path)

    stats = merge_knowledge_base(new_knowledge, kb, strategy, default_chapter)

    if save_knowledge_base(knowledge_base_path, kb):
        return {
            "status": "success",
            "stats": stats,
            "merged_base_path": knowledge_base_path,
            "version": kb["version"],
            "chapter": default_chapter,
        }
    else:
        return {"status": "error", "error": "Failed to save knowledge base"}


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="知识融合")
    parser.add_argument("--knowledge", required=True, help="新知识点JSON字符串或完整提取结果JSON")
    parser.add_argument("--path", required=True, help="知识库路径")
    parser.add_argument(
        "--strategy",
        default="merge",
        choices=["overwrite", "add", "merge"],
        help="合并策略",
    )

    args = parser.parse_args()

    try:
        data = json.loads(args.knowledge)
    except json.JSONDecodeError:
        print(json.dumps({"status": "error", "error": "Invalid JSON"}))
        return

    if "knowledge_points" in data:
        knowledge_list = data["knowledge_points"]
        extraction_result = data
    else:
        knowledge_list = data if isinstance(data, list) else [data]
        extraction_result = None

    result = merge(knowledge_list, args.path, args.strategy, extraction_result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
