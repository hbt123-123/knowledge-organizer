#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_index - 检索索引构建模块
为知识库构建向量/关键词索引
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common import get_embedding, get_api_config, get_workflow_config


def load_knowledge_base(path: str) -> Optional[Dict]:
    """加载知识库"""
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def extract_keywords(text: str) -> List[str]:
    """提取关键词 - 只保留专业术语，过滤碎片短语"""
    words = re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", text)
    
    stop_words = {
        "的", "是", "在", "和", "了", "与", "或", "及", "等", "为", "有", "被",
        "将", "可", "能", "会", "要", "应", "当", "对", "由", "从", "到", "向",
        "把", "让", "给", "比", "按", "经", "以", "于", "而", "且", "但", "如",
        "则", "即", "又", "也", "都", "就", "才", "只", "还", "已", "最", "更",
        "很", "太", "非", "不", "没", "无", "这", "那", "它", "其", "此", "某",
        "各", "每", "所", "之", "着", "过", "起", "来", "去", "出", "入", "中",
        "上", "下", "前", "后", "左", "右", "内", "外", "大", "小", "多", "少",
        "高", "低", "长", "短", "新", "旧", "好", "坏", "正", "反", "主", "次",
        "the", "is", "and", "or", "a", "an", "to", "of", "in", "on", "at", "by",
        "for", "with", "as", "from", "into", "onto", "upon", "over", "under"
    }
    
    fragment_patterns = [
        "是指", "称为", "定义为", "包括", "如", "例如", "其中", "如下",
        "如下所示", "如下表", "如图", "见图", "见表", "如下式", "根据",
        "按照", "通过", "进行", "采用", "使用", "利用", "应用于", "用于",
        "属于", "归类", "划分", "分为", "分成", "组成", "构成", "形成",
        "产生", "发生", "出现", "存在", "具有", "含有", "包含", "包括",
        "能够", "可以", "需要", "必须", "应该", "应当", "要求", "条件"
    ]
    
    keywords = []
    for w in words:
        if w in stop_words:
            continue
        if len(w) < 2 or len(w) > 10:
            continue
        is_fragment = False
        for pattern in fragment_patterns:
            if pattern in w or w.startswith(pattern) or w.endswith(pattern):
                is_fragment = True
                break
        if is_fragment:
            continue
        if re.match(r'^[是是有为为在在和或及等把被将可可能会要应当对由从到向让给比按经以于而且但如则即又也都不没无这那它其此某各每所之着过起来去出入中上下前后左右内外大小多少高低长短新旧好坏正反主次]+$', w):
            continue
        keywords.append(w)
    
    return list(set(keywords))


def build_keyword_index(kb: Dict) -> Dict:
    """构建关键词索引"""
    index = {
        "type": "keyword",
        "created_at": datetime.now().isoformat() + "Z",
        "entries": []
    }

    inverted_index = defaultdict(list)
    keyword_weights = defaultdict(float)

    technical_term_patterns = [
        r"系数", r"强度", r"密度", r"应力", r"应变", r"模量", r"荷载", r"等级",
        r"抗渗", r"抗冻", r"耐水", r"耐久", r"抗压", r"抗拉", r"抗弯", r"抗剪",
        r"混凝土", r"钢材", r"水泥", r"钢筋", r"砂浆", r"砖石", r"木材", r"玻璃",
        r"弹性", r"塑性", r"脆性", r"韧性", r"硬度", r"耐磨", r"孔隙", r"渗透",
        r"冻融", r"软化", r"饱和", r"干燥", r"湿润", r"吸水", r"含水", r"密实",
        r"配筋", r"截面", r"弯矩", r"剪力", r"轴力", r"扭矩", r"挠度", r"裂缝",
        r"公式", r"定理", r"定律", r"原理", r"方法", r"计算", r"设计", r"验算"
    ]

    for chapter, data in kb.get("chapters", {}).items():
        for kp in data.get("knowledge_points", []):
            kp_id = kp.get("id", kp.get("title", ""))
            text = f"{kp.get('title', '')} {kp.get('description', '')}"
            keywords = extract_keywords(text)

            for kw in keywords:
                if kp_id not in inverted_index[kw]:
                    inverted_index[kw].append(kp_id)
                
                base_weight = 1.0
                for pattern in technical_term_patterns:
                    if re.search(pattern, kw):
                        base_weight = 2.0
                        break
                
                keyword_weights[kw] += base_weight

    for keyword, kp_ids in inverted_index.items():
        avg_weight = keyword_weights[keyword] / len(kp_ids) if kp_ids else 0
        weight = min(1.0, len(kp_ids) / 10.0) * avg_weight
        
        index["entries"].append({
            "keyword": keyword,
            "knowledge_points": kp_ids,
            "weight": round(weight, 2),
            "occurrence_count": len(kp_ids)
        })

    index["entries"].sort(key=lambda x: x["weight"], reverse=True)

    return index


def is_embedding_enabled() -> bool:
    """检查 embedding 是否启用"""
    config = get_api_config()
    return config.get("enable_embedding", False) and bool(config.get("embedding_model"))


def build_vector_index(kb: Dict) -> Dict:
    """构建向量索引"""
    config = get_api_config()
    
    index = {
        "type": "vector",
        "embedding_model": config.get("embedding_model", "not_configured"),
        "created_at": datetime.now().isoformat() + "Z",
        "entries": [],
        "embedding_enabled": False
    }

    if not is_embedding_enabled():
        index["note"] = "Embedding API 未启用。如需向量索引，请在 config.json 中设置 enable_embedding: true 并配置 embedding_model"
        return index

    for chapter, data in kb.get("chapters", {}).items():
        for kp in data.get("knowledge_points", []):
            kp_id = kp.get("id", kp.get("title", ""))
            title = kp.get("title", "")
            description = kp.get("description", "")
            
            text_to_embed = f"{title}\n{description}"
            
            embedding_result = get_embedding(text_to_embed)
            
            if embedding_result.get("status") == "success":
                entry = {
                    "id": kp_id,
                    "vector": embedding_result.get("embedding", []),
                    "metadata": {
                        "title": title,
                        "chapter": chapter,
                        "category": kp.get("category", ""),
                        "description": description[:200] if description else ""
                    }
                }
                index["entries"].append(entry)
            else:
                index["entries"].append({
                    "id": kp_id,
                    "vector": [],
                    "error": embedding_result.get("error", "Embedding failed"),
                    "metadata": {
                        "title": title,
                        "chapter": chapter,
                        "category": kp.get("category", "")
                    }
                })

    index["embedding_enabled"] = True
    return index


def build_hybrid_index(kb: Dict) -> Dict:
    """构建混合索引"""
    keyword_idx = build_keyword_index(kb)
    vector_idx = build_vector_index(kb)

    return {
        "type": "hybrid",
        "keyword_index": keyword_idx,
        "vector_index": vector_idx,
        "created_at": datetime.now().isoformat() + "Z",
        "fusion_strategy": "reciprocal_rank",
        "embedding_enabled": vector_idx.get("embedding_enabled", False)
    }


def build_index(
    knowledge_base_path: str,
    index_type: str,
    index_output_path: str
) -> Dict:
    """
    构建索引

    Args:
        knowledge_base_path: 知识库路径
        index_type: 索引类型 (vector/keyword/hybrid)
        index_output_path: 输出路径

    Returns:
        索引构建结果
    """
    start_time = time.time()

    valid_types = {"vector", "keyword", "hybrid"}
    if index_type not in valid_types:
        return {"status": "error", "error": f"Invalid index type: {index_type}"}

    kb = load_knowledge_base(knowledge_base_path)
    if kb is None:
        return {"status": "error", "error": "Knowledge base not found"}

    os.makedirs(index_output_path, exist_ok=True)

    base_name = Path(knowledge_base_path).stem

    if index_type == "keyword":
        index_data = build_keyword_index(kb)
        output_file = os.path.join(index_output_path, f"{base_name}_keyword.json")
    elif index_type == "vector":
        if not is_embedding_enabled():
            return {
                "status": "error",
                "error": "Embedding API 未启用。请在 config.json 中设置 enable_embedding: true 并配置 embedding_model，或使用 --type keyword 构建关键词索引"
            }
        index_data = build_vector_index(kb)
        output_file = os.path.join(index_output_path, f"{base_name}_vector.json")
    else:
        index_data = build_hybrid_index(kb)
        output_file = os.path.join(index_output_path, f"{base_name}_hybrid.json")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {"status": "error", "error": f"Failed to save index: {str(e)}"}

    build_time_ms = int((time.time() - start_time) * 1000)

    if index_type == "hybrid":
        entry_count = len(index_data.get("keyword_index", {}).get("entries", []))
    else:
        entry_count = len(index_data.get("entries", []))

    result = {
        "status": "success",
        "index_file_path": output_file,
        "entry_count": entry_count,
        "build_time_ms": build_time_ms,
        "index_type": index_type,
    }
    
    if index_type in ["vector", "hybrid"]:
        result["embedding_enabled"] = index_data.get("embedding_enabled", False)

    return result


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="构建检索索引")
    parser.add_argument("--base", required=True, help="知识库路径")
    parser.add_argument(
        "--type",
        required=True,
        choices=["vector", "keyword", "hybrid"],
        help="索引类型 (推荐使用 keyword，无需 embedding API)"
    )
    parser.add_argument("--output", required=True, help="输出路径")

    args = parser.parse_args()

    result = build_index(args.base, args.type, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
