#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_directory - 扫描学科目录，识别章节子目录和教学材料
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# 支持的文件类型映射
FILE_TYPE_MAP = {
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".bmp": "image",
    ".webp": "image",
    ".pdf": "document",
    ".pptx": "presentation",
    ".ppt": "presentation",
    ".docx": "document",
    ".doc": "document",
    ".txt": "document",
    ".md": "document",
}

# 章节识别正则表达式
CHAPTER_PATTERNS = [
    r"^第([一二三四五六七八九十百千\d]+)章[\u4e00-\u9fa5]*",  # 第1章 / 第一章
    r"^Chapter\s*([\d]+)[\u4e00-\u9fa5]*",  # Chapter 1
]

# 跳过扫描的目录
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".DS_Store", "output", "indexes"}

# 跳过扫描的文件
SKIP_FILES = {
    "workflow_state.json",
    "knowledge_base.json",
    ".gitignore",
    ".DS_Store",
}


def detect_chapter(dir_name: str) -> Optional[str]:
    """检测目录名是否为章节名"""
    for pattern in CHAPTER_PATTERNS:
        match = re.match(pattern, dir_name, re.IGNORECASE)
        if match:
            return dir_name
    return None


def normalize_chapter_name(dir_name: str) -> str:
    """规范化章节名称"""
    # 尝试提取章节编号和名称
    for pattern in CHAPTER_PATTERNS:
        match = re.match(pattern, dir_name, re.IGNORECASE)
        if match:
            return dir_name
    return "未分类"


def get_file_info(file_path: str, chapter: str) -> Dict:
    """获取文件信息"""
    stat = os.stat(file_path)
    ext = Path(file_path).suffix.lower()

    return {
        "chapter": chapter,
        "file_path": file_path,
        "file_type": FILE_TYPE_MAP.get(ext, "unknown"),
        "file_extension": ext,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        "size": stat.st_size,
    }


def scan_directory(directory_path: str) -> Dict:
    """
    扫描目录，返回文件列表

    Args:
        directory_path: 要扫描的目录路径

    Returns:
        包含状态和文件列表的字典
    """
    # 验证目录存在
    if not os.path.exists(directory_path):
        return {"status": "error", "error": "Directory not found"}

    if not os.path.isdir(directory_path):
        return {"status": "error", "error": "Path is not a directory"}

    # 验证访问权限
    if not os.access(directory_path, os.R_OK):
        return {"status": "error", "error": "Permission denied"}

    files = []
    chapters = set()

    try:
        for root, dirs, filenames in os.walk(directory_path):
            # 过滤掉不需要扫描的目录
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            # 获取当前目录的章节名
            relative_path = os.path.relpath(root, directory_path)
            current_chapter = "未分类"

            if relative_path != ".":
                # 尝试从当前目录名检测章节
                dir_name = os.path.basename(root)
                detected = detect_chapter(dir_name)
                if detected:
                    current_chapter = normalize_chapter_name(detected)
                    chapters.add(current_chapter)

            # 处理当前目录中的文件
            for filename in filenames:
                if filename in SKIP_DIRS:
                    continue
                
                if filename in SKIP_FILES:
                    continue
                
                if filename.endswith("_state.json"):
                    continue

                file_path = os.path.join(root, filename)

                # 跳过目录（只处理文件）
                if os.path.isdir(file_path):
                    continue

                file_info = get_file_info(file_path, current_chapter)
                files.append(file_info)

        # 按章节和文件名排序
        files.sort(key=lambda x: (x["chapter"], x["file_path"]))

        return {"status": "success", "chapter_count": len(chapters), "files": files}

    except PermissionError:
        return {"status": "error", "error": "Permission denied during scan"}
    except Exception as e:
        return {"status": "error", "error": f"Scan failed: {str(e)}"}


def main():
    """主函数，支持命令行调用"""
    if len(sys.argv) < 2:
        # 尝试从stdin读取
        try:
            input_data = sys.stdin.read().strip()
            if input_data:
                data = json.loads(input_data)
                directory_path = data.get("directory_path")
            else:
                print(
                    json.dumps(
                        {"status": "error", "error": "Missing directory_path parameter"}
                    )
                )
                return
        except Exception:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "error": "Usage: python scan.py <directory_path>",
                    }
                )
            )
            return
    else:
        directory_path = sys.argv[1]

    result = scan_directory(directory_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
