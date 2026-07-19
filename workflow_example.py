#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workflow_example.py - 完整工作流示例
演示如何串联6个Skills完成知识积累
包含错误处理、恢复机制和状态追踪
"""

import json
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

sys.path.insert(0, os.path.join(scripts_dir, "scan_directory", "scripts"))
sys.path.insert(0, os.path.join(scripts_dir, "parse_multimodal", "scripts"))
sys.path.insert(0, os.path.join(scripts_dir, "extract_knowledge", "scripts"))
sys.path.insert(0, os.path.join(scripts_dir, "merge_knowledge", "scripts"))
sys.path.insert(0, os.path.join(scripts_dir, "export_formats", "scripts"))
sys.path.insert(0, os.path.join(scripts_dir, "build_index", "scripts"))

from scan import scan_directory
from parse import parse_file
from merge import merge
from export import export_formats
from index import build_index


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    name: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict] = None


class WorkflowState:
    """工作流状态管理"""

    def __init__(self, state_file: str = "./workflow_state.json", persist: bool = False):
        self.state_file = state_file
        self.persist = persist
        self.steps: Dict[str, StepResult] = {}
        self.load()

    def load(self):
        """加载状态（仅当启用持久化时）"""
        if not self.persist:
            return
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for name, step_data in data.get("steps", {}).items():
                        self.steps[name] = StepResult(**step_data)
            except Exception:
                pass

    def save(self):
        """保存状态（仅当启用持久化时）"""
        if not self.persist:
            return
        data = {
            "last_updated": datetime.now().isoformat(),
            "steps": {name: asdict(step) for name, step in self.steps.items()}
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def start_step(self, name: str):
        """开始步骤"""
        self.steps[name] = StepResult(
            name=name,
            status=StepStatus.RUNNING.value,
            start_time=datetime.now().isoformat()
        )
        self.save()
    
    def complete_step(self, name: str, data: Optional[Dict] = None):
        """完成步骤"""
        if name in self.steps:
            self.steps[name].status = StepStatus.SUCCESS.value
            self.steps[name].end_time = datetime.now().isoformat()
            self.steps[name].data = data
            self.save()
    
    def fail_step(self, name: str, error: str):
        """失败步骤"""
        if name in self.steps:
            self.steps[name].status = StepStatus.FAILED.value
            self.steps[name].end_time = datetime.now().isoformat()
            self.steps[name].error = error
            self.save()
    
    def skip_step(self, name: str, reason: str):
        """跳过步骤"""
        self.steps[name] = StepResult(
            name=name,
            status=StepStatus.SKIPPED.value,
            error=reason
        )
        self.save()
    
    def can_resume_from(self, name: str) -> bool:
        """检查是否可以从某步骤恢复"""
        if name not in self.steps:
            return False
        return self.steps[name].status in [StepStatus.SUCCESS.value, StepStatus.SKIPPED.value]
    
    def get_step_data(self, name: str) -> Optional[Dict]:
        """获取步骤数据"""
        if name in self.steps:
            return self.steps[name].data
        return None
    
    def clear(self):
        """清除状态"""
        self.steps = {}
        if os.path.exists(self.state_file):
            os.remove(self.state_file)


class KnowledgeWorkflow:
    """知识管理工作流"""
    
    def __init__(
        self,
        subject_dir: str,
        knowledge_base_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        index_dir: Optional[str] = None,
        resume: bool = True,
        save_state: bool = False
    ):
        self.subject_dir = os.path.abspath(subject_dir)
        subject_name = os.path.basename(self.subject_dir.rstrip(os.sep))

        self.knowledge_base_path = knowledge_base_path or os.path.join(self.subject_dir, "knowledge_base.json")
        self.output_dir = output_dir or os.path.join(self.subject_dir, "output")
        self.index_dir = index_dir or os.path.join(self.subject_dir, "indexes")
        self.state = WorkflowState(
            os.path.join(self.subject_dir, "workflow_state.json"),
            persist=save_state,
        )
        self.resume = resume

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
    
    def run(self) -> Dict[str, Any]:
        """运行完整工作流"""
        print("=" * 60)
        print("学科知识增量积累工作流")
        print("=" * 60)
        
        results = {
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "success": True,
            "errors": []
        }
        
        scan_result = self._step_scan()
        results["steps"]["scan"] = scan_result
        
        if scan_result.get("status") != "success":
            results["success"] = False
            results["errors"].append(f"扫描失败: {scan_result.get('error')}")
            return self._finalize(results)
        
        files = scan_result.get("files", [])
        if not files:
            print("\n没有发现文件，工作流结束")
            return self._finalize(results)
        
        processed_count = 0
        for i, file_info in enumerate(files[:5]):
            file_path = file_info["file_path"]
            chapter = file_info.get("chapter", "未分类")
            
            print(f"\n{'='*40}")
            print(f"处理文件 [{i+1}/{min(len(files), 5)}]: {os.path.basename(file_path)}")
            print(f"章节: {chapter}")
            print("=" * 40)
            
            parse_result = self._step_parse(file_path)
            if parse_result.get("status") != "success":
                print(f"  解析失败: {parse_result.get('error')}")
                continue
            
            extract_result = self._step_extract(
                parse_result.get("content", {}),
                chapter
            )
            
            if extract_result.get("status") == "pending":
                print(f"\n  {'='*50}")
                print(f"  知识点提取需要 AI 执行")
                print(f"  请参考 extract_knowledge/SKILL.md 中的指导")
                print(f"  {'='*50}")
                
                content = parse_result.get("content", {})
                text = content.get("text", "")
                print(f"\n  内容预览 (前1000字符):")
                print(f"  {text[:1000]}")
                print(f"\n  请 AI 提取知识点后，使用以下命令继续:")
                print(f"  python merge_knowledge/scripts/merge.py --knowledge '[知识点JSON]' --path '{self.knowledge_base_path}'")
                continue
            
            if extract_result.get("status") != "success":
                print(f"  提取失败: {extract_result.get('error')}")
                continue
            
            merge_result = self._step_merge(
                extract_result.get("knowledge_points", [])
            )
            if merge_result.get("status") != "success":
                print(f"  合并失败: {merge_result.get('error')}")
                continue
            
            processed_count += 1
        
        if processed_count > 0:
            self._step_export()
            self._step_index()
        
        results["processed_files"] = processed_count
        return self._finalize(results)
    
    def _step_scan(self) -> Dict:
        """步骤1: 扫描目录"""
        step_name = "scan"
        print("\n[Step 1] 扫描目录...")
        
        if self.resume and self.state.can_resume_from(step_name):
            print("  从缓存恢复...")
            cached = self.state.get_step_data(step_name)
            if cached:
                return cached
        
        self.state.start_step(step_name)
        
        try:
            result = scan_directory(self.subject_dir)
            
            if result.get("status") == "success":
                print(f"  状态: 成功")
                print(f"  发现章节数: {result.get('chapter_count')}")
                print(f"  发现文件数: {len(result.get('files', []))}")
                self.state.complete_step(step_name, result)
            else:
                print(f"  状态: 失败 - {result.get('error')}")
                self.state.fail_step(step_name, result.get("error", "Unknown error"))
            
            return result
        except Exception as e:
            error = str(e)
            print(f"  状态: 异常 - {error}")
            self.state.fail_step(step_name, error)
            return {"status": "error", "error": error}
    
    def _step_parse(self, file_path: str) -> Dict:
        """步骤2: 解析文件"""
        print(f"\n[Step 2] 解析文件...")
        
        try:
            result = parse_file(file_path)
            
            if result.get("status") == "success":
                content = result.get("content", {})
                text_len = len(content.get("text", ""))
                img_count = len(content.get("images", []))
                print(f"  状态: 成功")
                print(f"  文本长度: {text_len} 字符")
                print(f"  图片数量: {img_count}")
            else:
                print(f"  状态: 失败 - {result.get('error')}")
            
            return result
        except Exception as e:
            error = str(e)
            print(f"  状态: 异常 - {error}")
            return {"status": "error", "error": error}
    
    def _step_extract(self, content: Dict, chapter: str) -> Dict:
        """步骤3: 提取知识（由 AI 直接执行）"""
        print(f"\n[Step 3] 提取知识点...")
        print(f"  注意: 知识点提取应由 AI 根据 extract_knowledge/SKILL.md 指导直接执行")
        
        text = content.get("text", "") if content else ""
        if not text:
            return {"status": "error", "error": "Empty content"}
        
        print(f"  内容预览: {text[:200]}...")
        print(f"  章节: {chapter}")
        print(f"\n  请 AI 根据 extract_knowledge/SKILL.md 中的指导提取知识点")
        
        return {
            "status": "pending",
            "message": "等待 AI 执行知识点提取",
            "chapter": chapter,
            "content": content,
            "content_length": len(text)
        }
    
    def _step_merge(self, knowledge_points: List[Dict]) -> Dict:
        """步骤4: 合并知识"""
        print(f"\n[Step 4] 合并到知识库...")
        
        try:
            result = merge(
                new_knowledge=knowledge_points,
                knowledge_base_path=self.knowledge_base_path,
                strategy="merge"
            )
            
            if result.get("status") == "success":
                stats = result.get("stats", {})
                print(f"  状态: 成功")
                print(f"  新增: {stats.get('added', 0)}")
                print(f"  更新: {stats.get('modified', 0)}")
                print(f"  跳过: {stats.get('skipped', 0)}")
                print(f"  版本: {result.get('version')}")
            else:
                print(f"  状态: 失败 - {result.get('error')}")
            
            return result
        except Exception as e:
            error = str(e)
            print(f"  状态: 异常 - {error}")
            return {"status": "error", "error": error}
    
    def _step_export(self) -> Dict:
        """步骤5: 导出格式"""
        step_name = "export"
        print(f"\n[Step 5] 导出多格式...")
        
        if not os.path.exists(self.knowledge_base_path):
            print("  状态: 跳过 - 知识库不存在")
            self.state.skip_step(step_name, "Knowledge base not found")
            return {"status": "skipped", "error": "Knowledge base not found"}
        
        self.state.start_step(step_name)
        
        try:
            result = export_formats(
                knowledge_base_path=self.knowledge_base_path,
                formats=["md"],
                output_dir=self.output_dir
            )
            
            if result.get("status") == "success":
                files = result.get("files", [])
                print(f"  状态: 成功")
                print(f"  导出文件数: {len(files)}")
                for f in files:
                    print(f"    - {f.get('format')}: {os.path.basename(f.get('path', ''))}")
                self.state.complete_step(step_name, result)
            else:
                print(f"  状态: 失败 - {result.get('error')}")
                self.state.fail_step(step_name, result.get("error", "Unknown error"))
            
            return result
        except Exception as e:
            error = str(e)
            print(f"  状态: 异常 - {error}")
            self.state.fail_step(step_name, error)
            return {"status": "error", "error": error}
    
    def _step_index(self) -> Dict:
        """步骤6: 构建索引"""
        step_name = "index"
        print(f"\n[Step 6] 构建检索索引...")
        
        if not os.path.exists(self.knowledge_base_path):
            print("  状态: 跳过 - 知识库不存在")
            self.state.skip_step(step_name, "Knowledge base not found")
            return {"status": "skipped", "error": "Knowledge base not found"}
        
        self.state.start_step(step_name)
        
        try:
            result = build_index(
                knowledge_base_path=self.knowledge_base_path,
                index_type="keyword",
                index_output_path=self.index_dir
            )
            
            if result.get("status") == "success":
                print(f"  状态: 成功")
                print(f"  索引条目数: {result.get('entry_count')}")
                print(f"  构建耗时: {result.get('build_time_ms')}ms")
                self.state.complete_step(step_name, result)
            else:
                print(f"  状态: 失败 - {result.get('error')}")
                self.state.fail_step(step_name, result.get("error", "Unknown error"))
            
            return result
        except Exception as e:
            error = str(e)
            print(f"  状态: 异常 - {error}")
            self.state.fail_step(step_name, error)
            return {"status": "error", "error": error}
    
    def _finalize(self, results: Dict) -> Dict:
        """完成工作流"""
        results["end_time"] = datetime.now().isoformat()
        
        print("\n" + "=" * 60)
        print("工作流完成!")
        print("=" * 60)
        
        if results["success"]:
            print("状态: 成功 ✓")
        else:
            print("状态: 部分失败 ✗")
            for error in results.get("errors", []):
                print(f"  - {error}")
        
        print(f"\n知识库: {self.knowledge_base_path}")
        print(f"输出目录: {self.output_dir}")
        print(f"索引目录: {self.index_dir}")
        
        return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="学科知识增量积累工作流")
    parser.add_argument("subject_dir", help="学科目录路径（输出文件将保存在此目录下）")
    parser.add_argument("--no-resume", action="store_true", help="不恢复之前的状态")
    parser.add_argument("--clear", action="store_true", help="清除状态并重新开始")
    parser.add_argument(
        "--save-state",
        action="store_true",
        help="启用 workflow_state.json 状态持久化（默认关闭，不写入状态文件）",
    )

    args = parser.parse_args()

    workflow = KnowledgeWorkflow(
        subject_dir=args.subject_dir,
        resume=not args.no_resume,
        save_state=args.save_state,
    )

    if args.clear:
        workflow.state.clear()
        print("已清除工作流状态")

    result = workflow.run()
    if args.save_state:
        print(f"\n状态已保存到 {workflow.state.state_file}")


if __name__ == "__main__":
    main()
