#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_formats - 多格式导出模块
从知识库导出PDF、思维导图、Markdown、HTML格式
支持视觉重构协议：结构模块化、样式增强
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

# 添加design skill的路径
design_dir = Path(__file__).parent.parent.parent / "design"
sys.path.insert(0, str(design_dir / "scripts"))

# 尝试导入design skill的搜索功能
try:
    from core import search
except Exception:
    # 如果导入失败，使用默认设计
    search = None


SUPPORTED_FORMATS = {"pdf", "mindmap", "md", "html"}


def get_design_config(subject_name: str) -> Dict:
    """
    从design skill获取设计配置
    
    Args:
        subject_name: 学科名称，用于搜索合适的设计风格
    
    Returns:
        设计配置字典
    """
    default_config = {
        "colors": {
            "primary": "#2563eb",
            "primary-light": "#3b82f6",
            "bg": "#f8fafc",
            "card": "#ffffff",
            "text": "#1e293b",
            "text-light": "#64748b",
            "border": "#e2e8f0",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444"
        },
        "fonts": {
            "heading": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "body": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
        },
        "style": "modern"
    }
    
    if search is None:
        return default_config
    
    try:
        # 搜索适合教育/学习的设计风格
        query = f"教育 {subject_name} 学习 现代 简洁"
        style_results = search(query, domain="style", max_results=1)
        
        # 搜索适合的配色方案
        color_results = search(f"教育 学习 专业", domain="color", max_results=1)
        
        # 搜索适合的字体
        typography_results = search("教育 学习 清晰 易读", domain="typography", max_results=1)
        
        # 构建配置
        config = default_config.copy()
        
        # 处理风格结果
        if style_results.get("results"):
            style = style_results["results"][0]
            if style.get("Primary Colors"):
                colors = style["Primary Colors"].split(",")
                if colors:
                    config["colors"]["primary"] = colors[0].strip()
        
        # 处理配色结果
        if color_results.get("results"):
            color = color_results["results"][0]
            for key, color_key in {
                "primary": "Primary",
                "bg": "Background",
                "text": "Foreground",
                "card": "Card",
                "text-light": "Muted Foreground"
            }.items():
                if color.get(color_key):
                    config["colors"][key] = color[color_key]
        
        # 处理字体结果
        if typography_results.get("results"):
            typography = typography_results["results"][0]
            if typography.get("Heading Font"):
                config["fonts"]["heading"] = typography["Heading Font"]
            if typography.get("Body Font"):
                config["fonts"]["body"] = typography["Body Font"]
        
        return config
    except Exception as e:
        print(f"Design config error: {e}")
        return default_config


def load_knowledge_base(path: str) -> Optional[Dict]:
    """加载知识库"""
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def filter_chapters(kb: Dict, chapter_filter: str) -> Dict:
    """过滤章节"""
    if not chapter_filter:
        return kb

    filtered = {**kb, "chapters": {}}

    for chapter, data in kb.get("chapters", {}).items():
        if chapter_filter in chapter:
            filtered["chapters"][chapter] = data

    return filtered


def bold_keywords(text: str) -> str:
    """将核心名词和动词加粗"""
    keywords = [
        "定义", "概念", "公式", "定理", "性质", "特征", "方法", "原理",
        "强度", "密度", "应力", "应变", "荷载", "弹性", "塑性", "脆性", "韧性",
        "混凝土", "钢材", "水泥", "钢筋", "材料", "结构", "构件", "截面",
        "计算", "分析", "设计", "验算", "确定", "求解", "推导", "证明",
        "抗压", "抗拉", "抗弯", "抗剪", "抗渗", "抗冻", "耐水", "耐久",
        "孔隙率", "含水率", "饱和度", "软化系数", "抗渗等级", "强度等级"
    ]
    
    result = text
    for kw in sorted(keywords, key=len, reverse=True):
        if kw in result and f"**{kw}**" not in result:
            result = result.replace(kw, f"**{kw}**")
    return result


def generate_key_takeaways(kps: List[Dict]) -> str:
    """生成核心结论模块"""
    lines = []
    lines.append("\n> [!SUMMARY] 📌 核心结论\n")
    
    key_points = []
    for kp in kps[:5]:
        title = kp.get("title", "")
        desc = kp.get("description", "")[:100]
        if title:
            key_points.append(f"> - **{title}**：{bold_keywords(desc)}\n")
    
    if not key_points:
        key_points.append("> - 本章知识点已提取，请查看详细解析\n")
    
    lines.extend(key_points)
    return "".join(lines)


def generate_knowledge_map(kps: List[Dict]) -> str:
    """生成知识图谱模块"""
    lines = []
    lines.append("\n## 🧠 知识图谱\n")
    
    concepts = [kp for kp in kps if kp.get("category") in ["概念", "定义"]]
    formulas = [kp for kp in kps if kp.get("category") == "公式"]
    
    if len(concepts) > 1:
        lines.append("\n### 📊 概念关系图\n")
        lines.append("\n```mermaid\n")
        lines.append("graph LR\n")
        for i, kp in enumerate(concepts[:8]):
            title = kp.get("title", "").replace('"', "'")
            node_id = f"n{i}"
            lines.append(f'    {node_id}["{title}"]\n')
            if i > 0:
                lines.append(f"    n{i-1} --> {node_id}\n")
        lines.append("```\n")
    
    comparisons = []
    for kp in kps:
        desc = kp.get("description", "")
        if "与" in kp.get("title", "") or "对比" in desc or "区别" in desc:
            comparisons.append(kp)
    
    if comparisons:
        lines.append("\n### 📋 对比分析\n")
        lines.append("\n| 特性 | 内容 |\n|------|------|\n")
        for kp in comparisons[:3]:
            title = kp.get("title", "")
            desc = kp.get("description", "")[:80]
            lines.append(f"| {title} | {bold_keywords(desc)} |\n")
    
    if not concepts and not comparisons:
        lines.append("\n*本章暂无复杂概念关系*\n")
    
    return "".join(lines)


def generate_deep_dive(kps: List[Dict]) -> str:
    """生成详细解析模块"""
    lines = []
    lines.append("\n## 📖 详细解析\n")
    
    categories = {}
    for kp in kps:
        cat = kp.get("category", "概念")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(kp)
    
    category_config = {
        "定义": {"icon": "📝", "order": 1},
        "概念": {"icon": "💡", "order": 2},
        "公式": {"icon": "📐", "order": 3},
        "定理": {"icon": "📜", "order": 4},
        "例题": {"icon": "✏️", "order": 5},
        "表格": {"icon": "📊", "order": 6}
    }
    
    sorted_cats = sorted(categories.keys(), key=lambda x: category_config.get(x, {}).get("order", 99))
    
    for category in sorted_cats:
        config = category_config.get(category, {"icon": "📌"})
        icon = config["icon"]
        lines.append(f"\n### {icon} {category}\n")
        
        for kp in categories[category]:
            title = kp.get("title", "Untitled")
            lines.append(f"\n#### {title}\n")
            
            if kp.get("formula"):
                formula = kp["formula"]
                latex = formula.get("latex", "")
                if latex:
                    lines.append(f"\n**📐 公式**: {latex}\n")
                variables = formula.get("variables", [])
                if variables:
                    lines.append("\n| 符号 | 含义 | 单位 |\n|:----:|------|------|\n")
                    for var in variables:
                        lines.append(f"| {var.get('symbol', '')} | {var.get('meaning', '')} | {var.get('unit', '')} |\n")
            
            if kp.get("table_data"):
                table = kp["table_data"]
                headers = table.get("headers", [])
                rows = table.get("rows", [])
                if headers:
                    lines.append("\n| " + " | ".join(headers) + " |\n")
                    lines.append("| " + " | ".join([":---:"] * len(headers)) + " |\n")
                    for row in rows:
                        lines.append("| " + " | ".join(str(cell) for cell in row) + " |\n")
            
            if kp.get("example_data"):
                example = kp["example_data"]
                lines.append(f"\n**📋 已知**: {example.get('known', '')}\n")
                lines.append(f"\n**🎯 求**: {example.get('required', '')}\n")
                solution = example.get("solution", [])
                if solution:
                    lines.append("\n**📝 解题步骤**:\n")
                    for i, step in enumerate(solution, 1):
                        lines.append(f"   {i}. {step}\n")
            
            description = kp.get("description", "")
            if description:
                lines.append(f"\n{bold_keywords(description)}\n")
            
            related = kp.get("related_concepts", [])
            if related:
                lines.append(f"\n🔗 **相关概念**: {', '.join(related)}\n")
            
            lines.append("\n---\n")
    
    return "".join(lines)


def generate_self_test(kps: List[Dict]) -> str:
    """生成考前自测模块"""
    lines = []
    lines.append("\n## ⚡ 考前自测\n")
    lines.append("\n> [!TIP] 💡 点击下方箭头查看参考答案\n")
    
    questions = []
    for i, kp in enumerate(kps[:3], 1):
        title = kp.get("title", "")
        desc = kp.get("description", "")
        category = kp.get("category", "")
        
        if category == "定义":
            q = f"请简述 **{title}** 的定义。"
            a = desc
        elif category == "公式":
            q = f"请写出 **{title}** 并解释各参数含义。"
            a = desc
            if kp.get("formula"):
                latex = kp["formula"].get("latex", "")
                if latex:
                    a = f"{latex}\n\n{desc}"
        elif category == "概念":
            q = f"什么是 **{title}**？它有哪些重要特性？"
            a = desc
        else:
            q = f"请解释 **{title}** 的核心内容。"
            a = desc
        
        questions.append((q, a))
    
    for i, (q, a) in enumerate(questions, 1):
        lines.append(f"\n### 问题 {i}\n")
        lines.append(f"\n{q}\n")
        lines.append("\n<details>\n")
        lines.append("<summary>👉 点击查看参考答案</summary>\n")
        lines.append(f"\n{bold_keywords(a)}\n")
        lines.append("\n</details>\n")
    
    if len(questions) < 3:
        for i in range(len(questions) + 1, 4):
            lines.append(f"\n### 问题 {i}\n")
            lines.append(f"\n本章还有哪些重要知识点需要掌握？\n")
            lines.append("\n<details>\n")
            lines.append("<summary>👉 点击查看参考答案</summary>\n")
            lines.append("\n请结合详细解析模块进行复习。\n")
            lines.append("\n</details>\n")
    
    return "".join(lines)


def export_markdown(kb: Dict, output_path: str) -> bool:
    """导出为Markdown - 视觉重构协议版"""
    try:
        lines = []
        
        lines.append("# 📚 知识点总结\n\n")
        lines.append(f"> **版本**: {kb.get('version', 'N/A')} | ")
        lines.append(f"**更新时间**: {kb.get('last_updated', 'N/A')}\n\n")
        
        total_points = sum(
            len(data.get("knowledge_points", []))
            for data in kb.get("chapters", {}).values()
        )
        lines.append(f"> **知识点总数**: {total_points}\n\n")
        
        lines.append("---\n\n")
        
        chapters = kb.get("chapters", {})
        
        if len(chapters) > 1:
            lines.append("## 📖 目录\n\n")
            for i, chapter in enumerate(chapters.keys(), 1):
                point_count = len(chapters[chapter].get("knowledge_points", []))
                anchor = chapter.replace(" ", "-").replace("/", "-").replace("#", "")
                lines.append(f"{i}. [{chapter}](#{anchor}) ({point_count}个知识点)\n")
            lines.append("\n---\n")

        for chapter, data in chapters.items():
            lines.append(f"\n## 📑 {chapter}\n")
            
            kps = data.get("knowledge_points", [])
            
            if not kps:
                lines.append("\n*本章暂无知识点*\n")
                continue
            
            lines.append(generate_key_takeaways(kps))
            lines.append(generate_knowledge_map(kps))
            lines.append(generate_deep_dive(kps))
            lines.append(generate_self_test(kps))
            
            lines.append("\n---\n")

        lines.append("\n## 📝 复习建议\n\n")
        lines.append("> [!NOTE] 🎯 高效复习策略\n")
        lines.append("> \n")
        lines.append("> 1. **概念理解** - 重点理解各概念的定义和内涵\n")
        lines.append("> 2. **公式记忆** - 熟练掌握重要公式的推导和应用\n")
        lines.append("> 3. **例题练习** - 通过例题加深对知识点的理解\n")
        lines.append("> 4. **关联复习** - 注意知识点之间的联系和区别\n")
        lines.append("\n---\n\n")
        lines.append(f"*📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False


def export_html(kb: Dict, output_path: str, design_config: Dict = None) -> bool:
    """导出为HTML - 现代文档风格，带侧边目录"""
    try:
        if design_config is None:
            design_config = get_design_config("知识总结")
        
        colors = design_config.get("colors", {})
        fonts = design_config.get("fonts", {})
        
        chapters = kb.get("chapters", {})
        total_points = sum(len(d.get("knowledge_points", [])) for d in chapters.values())
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 知识点总结</title>
    <style>
        :root {{
            --primary: {colors.get('primary', '#2563eb')};
            --primary-light: {colors.get('primary-light', '#3b82f6')};
            --bg: {colors.get('bg', '#f8fafc')};
            --card: {colors.get('card', '#ffffff')};
            --text: {colors.get('text', '#1e293b')};
            --text-light: {colors.get('text-light', '#64748b')};
            --border: {colors.get('border', '#e2e8f0')};
            --success: {colors.get('success', '#10b981')};
            --warning: {colors.get('warning', '#f59e0b')};
            --danger: {colors.get('danger', '#ef4444')};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }}
        
        .container {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .sidebar {{
            width: 280px;
            background: var(--card);
            height: 100vh;
            position: sticky;
            top: 0;
            border-right: 1px solid var(--border);
            overflow-y: auto;
            padding: 2rem 1.5rem;
        }}
        
        .sidebar h2 {{
            font-size: 1.25rem;
            margin-bottom: 1.5rem;
            color: var(--primary);
        }}
        
        .sidebar nav a {{
            display: block;
            padding: 0.75rem 1rem;
            color: var(--text-light);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            transition: all 0.2s;
        }}
        
        .sidebar nav a:hover {{
            background: var(--bg);
            color: var(--primary);
        }}
        
        .main {{
            flex: 1;
            padding: 2rem 3rem;
            max-width: 900px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: var(--text);
        }}
        
        .header .meta {{
            color: var(--text-light);
            font-size: 0.9rem;
        }}
        
        .chapter {{
            margin-bottom: 3rem;
        }}
        
        .chapter-title {{
            font-size: 1.75rem;
            color: var(--primary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--primary);
        }}
        
        .summary-box {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-left: 4px solid var(--primary);
            padding: 1.5rem;
            border-radius: 0 12px 12px 0;
            margin-bottom: 2rem;
        }}
        
        .summary-box h3 {{
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}
        
        .summary-box ul {{
            list-style: none;
        }}
        
        .summary-box li {{
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
        }}
        
        .summary-box li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--success);
            font-weight: bold;
        }}
        
        .knowledge-point {{
            background: var(--card);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }}
        
        .knowledge-point h4 {{
            color: var(--text);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}
        
        .knowledge-point .category {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-bottom: 0.75rem;
        }}
        
        .formula {{
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 1rem 0;
            text-align: center;
            font-size: 1.1rem;
        }}
        
        .warning-box {{
            background: #fef3c7;
            border-left: 4px solid var(--warning);
            padding: 1rem 1.5rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        
        .self-test {{
            background: var(--card);
            border: 2px dashed var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
        }}
        
        .self-test h3 {{
            color: var(--primary);
            margin-bottom: 1rem;
        }}
        
        .question {{
            margin-bottom: 1.5rem;
        }}
        
        .question summary {{
            cursor: pointer;
            color: var(--primary);
            font-weight: 500;
            padding: 0.5rem;
        }}
        
        .question summary:hover {{
            background: var(--bg);
            border-radius: 8px;
        }}
        
        .answer {{
            background: var(--bg);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 0.5rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--bg);
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f8fafc;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
            font-size: 0.9rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }}
        
        @media print {{
            .sidebar {{ display: none; }}
            .main {{ max-width: 100%; padding: 1rem; }}
            .knowledge-point {{ break-inside: avoid; }}
        }}
        
        @media (max-width: 768px) {{
            .sidebar {{ display: none; }}
            .main {{ padding: 1rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <aside class="sidebar">
            <h2>📖 目录导航</h2>
            <nav>
                <a href="#top">📚 开始</a>
'''
        
        for chapter in chapters.keys():
            anchor = chapter.replace(" ", "-").replace("/", "-")
            html += f'                <a href="#{anchor}">{chapter}</a>\n'
        
        html += '''            </nav>
        </aside>
        
        <main class="main">
            <header class="header" id="top">
                <h1>📚 知识点总结</h1>
                <div class="meta">
'''
        
        html += f'                    版本: {kb.get("version", "N/A")} | '
        html += f'知识点: {total_points} 个 | '
        html += f'更新: {kb.get("last_updated", "N/A")}\n'
        
        html += '''                </div>
            </header>
'''
        
        for chapter, data in chapters.items():
            kps = data.get("knowledge_points", [])
            anchor = chapter.replace(" ", "-").replace("/", "-")
            
            html += f'''
            <section class="chapter" id="{anchor}">
                <h2 class="chapter-title">📑 {chapter}</h2>
                
                <div class="summary-box">
                    <h3>📌 核心结论</h3>
                    <ul>
'''
            
            for kp in kps[:5]:
                title = kp.get("title", "")
                html += f'                        <li><strong>{title}</strong></li>\n'
            
            html += '''                    </ul>
                </div>
'''
            
            for kp in kps:
                title = kp.get("title", "Untitled")
                category = kp.get("category", "概念")
                desc = kp.get("description", "")
                
                html += f'''
                <div class="knowledge-point">
                    <span class="category">{category}</span>
                    <h4>{title}</h4>
'''
                
                if kp.get("formula"):
                    latex = kp["formula"].get("latex", "")
                    if latex:
                        html += f'                    <div class="formula">{latex}</div>\n'
                
                if desc:
                    html += f'                    <p>{desc}</p>\n'
                
                if kp.get("related_concepts"):
                    related = ", ".join(kp["related_concepts"])
                    html += f'                    <p><small>🔗 相关概念: {related}</small></p>\n'
                
                html += '                </div>\n'
            
            html += f'''
                <div class="self-test">
                    <h3>⚡ 考前自测</h3>
'''
            
            for i, kp in enumerate(kps[:3], 1):
                title = kp.get("title", "")
                desc = kp.get("description", "")
                html += f'''                    <details class="question">
                        <summary>问题 {i}: 什么是 {title}？</summary>
                        <div class="answer">{desc}</div>
                    </details>
'''
            
            html += '''                </div>
            </section>
'''
        
        html += f'''
            <footer class="footer">
                📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </footer>
        </main>
    </div>
</body>
</html>
'''
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return True
    except Exception as e:
        print(f"HTML export error: {e}")
        return False


def export_mindmap(kb: Dict, output_path: str) -> bool:
    """导出为思维导图（Freemind格式）"""
    try:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>\n']
        lines.append('<map version="0.9.0">\n')
        lines.append('  <node TEXT="知识库">\n')

        for chapter, data in kb.get("chapters", {}).items():
            lines.append(f'    <node TEXT="{chapter}">\n')

            for kp in data.get("knowledge_points", []):
                title = kp.get("title", "Untitled")
                category = kp.get("category", "")
                lines.append(f'      <node TEXT="{title}" NOTE="{category}"/>\n')

            lines.append("    </node>\n")

        lines.append("  </node>\n")
        lines.append("</map>\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return True
    except Exception:
        return False


def export_pdf(kb: Dict, output_path: str) -> bool:
    """导出为PDF"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("知识点总结", styles["Title"]))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"版本: {kb.get('version', 'N/A')}", styles["Normal"]))
        story.append(
            Paragraph(f"更新时间: {kb.get('last_updated', 'N/A')}", styles["Normal"])
        )
        story.append(Spacer(1, 0.3 * inch))

        for chapter, data in kb.get("chapters", {}).items():
            story.append(Paragraph(chapter, styles["Heading1"]))

            for kp in data.get("knowledge_points", []):
                title = kp.get("title", "Untitled")
                category = kp.get("category", "")
                description = kp.get("description", "")

                story.append(
                    Paragraph(f"<b>{title}</b> ({category})", styles["Heading2"])
                )
                story.append(Paragraph(description, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

        doc.build(story)
        return True

    except ImportError:
        return export_markdown(kb, output_path.replace(".pdf", ".txt"))
    except Exception:
        return False


def sanitize_filename(name: str) -> str:
    """清理文件名，移除非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()


def export_markdown_chapter(chapter: str, kps: List[Dict], output_path: str, kb_meta: Dict) -> bool:
    """导出单个章节为Markdown"""
    try:
        lines = []
        
        lines.append(f"# 📚 {chapter}\n\n")
        lines.append(f"> **版本**: {kb_meta.get('version', 'N/A')} | ")
        lines.append(f"**更新时间**: {kb_meta.get('last_updated', 'N/A')}\n\n")
        lines.append(f"> **知识点总数**: {len(kps)}\n\n")
        
        lines.append("---\n\n")
        
        if not kps:
            lines.append("\n*本章暂无知识点*\n")
        else:
            lines.append(generate_key_takeaways(kps))
            lines.append(generate_knowledge_map(kps))
            lines.append(generate_deep_dive(kps))
            lines.append(generate_self_test(kps))
        
        lines.append("\n---\n\n")
        lines.append(f"*📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False


def export_html_chapter(chapter: str, kps: List[Dict], output_path: str, kb_meta: Dict, design_config: Dict = None) -> bool:
    """导出单个章节为HTML"""
    try:
        if design_config is None:
            design_config = get_design_config(chapter)
        
        colors = design_config.get("colors", {})
        fonts = design_config.get("fonts", {})
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 {chapter}</title>
    <style>
        :root {{
            --primary: {colors.get('primary', '#2563eb')};
            --primary-light: {colors.get('primary-light', '#3b82f6')};
            --bg: {colors.get('bg', '#f8fafc')};
            --card: {colors.get('card', '#ffffff')};
            --text: {colors.get('text', '#1e293b')};
            --text-light: {colors.get('text-light', '#64748b')};
            --border: {colors.get('border', '#e2e8f0')};
            --success: {colors.get('success', '#10b981')};
            --warning: {colors.get('warning', '#f59e0b')};
            --danger: {colors.get('danger', '#ef4444')};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {fonts.get('body', '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif')};
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: var(--text);
        }}
        
        .header .meta {{
            color: var(--text-light);
            font-size: 0.9rem;
        }}
        
        .summary-box {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-left: 4px solid var(--primary);
            padding: 1.5rem;
            border-radius: 0 12px 12px 0;
            margin-bottom: 2rem;
        }}
        
        .summary-box h3 {{
            color: var(--primary);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}
        
        .summary-box ul {{
            list-style: none;
        }}
        
        .summary-box li {{
            padding: 0.5rem 0;
            padding-left: 1.5rem;
            position: relative;
        }}
        
        .summary-box li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--success);
            font-weight: bold;
        }}
        
        .knowledge-point {{
            background: var(--card);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid var(--border);
        }}
        
        .knowledge-point h4 {{
            color: var(--text);
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}
        
        .knowledge-point .category {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-bottom: 0.75rem;
        }}
        
        .formula {{
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 1rem 0;
            text-align: center;
            font-size: 1.1rem;
        }}
        
        .self-test {{
            background: var(--card);
            border: 2px dashed var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
        }}
        
        .self-test h3 {{
            color: var(--primary);
            margin-bottom: 1rem;
        }}
        
        .question {{
            margin-bottom: 1.5rem;
        }}
        
        .question summary {{
            cursor: pointer;
            color: var(--primary);
            font-weight: 500;
            padding: 0.5rem;
        }}
        
        .question summary:hover {{
            background: var(--bg);
            border-radius: 8px;
        }}
        
        .answer {{
            background: var(--bg);
            padding: 1rem;
            border-radius: 8px;
            margin-top: 0.5rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--bg);
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f8fafc;
        }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-light);
            font-size: 0.9rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }}
        
        @media print {{
            .knowledge-point {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📚 {chapter}</h1>
            <div class="meta">
'''
        
        html += f'                版本: {kb_meta.get("version", "N/A")} | '
        html += f'知识点: {len(kps)} 个 | '
        html += f'更新: {kb_meta.get("last_updated", "N/A")}\n'
        
        html += '''            </div>
        </header>
'''
        
        if not kps:
            html += '''
        <p>本章暂无知识点</p>
'''
        else:
            html += '''
        <div class="summary-box">
            <h3>📌 核心结论</h3>
            <ul>
'''
            
            for kp in kps[:5]:
                title = kp.get("title", "")
                html += f'                <li><strong>{title}</strong></li>\n'
            
            html += '''            </ul>
        </div>
'''
            
            for kp in kps:
                title = kp.get("title", "Untitled")
                category = kp.get("category", "概念")
                desc = kp.get("description", "")
                
                html += f'''
        <div class="knowledge-point">
            <span class="category">{category}</span>
            <h4>{title}</h4>
'''
                
                if kp.get("formula"):
                    latex = kp["formula"].get("latex", "")
                    if latex:
                        html += f'            <div class="formula">{latex}</div>\n'
                
                if desc:
                    html += f'            <p>{desc}</p>\n'
                
                if kp.get("related_concepts"):
                    related = ", ".join(kp["related_concepts"])
                    html += f'            <p><small>🔗 相关概念: {related}</small></p>\n'
                
                html += '        </div>\n'
            
            html += '''
        <div class="self-test">
            <h3>⚡ 考前自测</h3>
'''
            
            for i, kp in enumerate(kps[:3], 1):
                title = kp.get("title", "")
                desc = kp.get("description", "")
                html += f'''            <details class="question">
                <summary>问题 {i}: 什么是 {title}？</summary>
                <div class="answer">{desc}</div>
            </details>
'''
            
            html += '''        </div>
'''
        
        html += f'''
        <footer class="footer">
            📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </footer>
    </div>
</body>
</html>
'''
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return True
    except Exception as e:
        print(f"HTML export error: {e}")
        return False


def export_formats(
    knowledge_base_path: str,
    formats: List[str],
    output_dir: str,
    chapter_filter: Optional[str] = None,
    split_by_chapter: bool = True,
    subject_name: Optional[str] = None,
) -> Dict:
    """
    导出知识库为多种格式

    Args:
        knowledge_base_path: 知识库路径
        formats: 格式列表
        output_dir: 输出目录
        chapter_filter: 章节过滤
        split_by_chapter: 是否按章节分割导出（默认True）
        subject_name: 学科名称（用于文件名）

    Returns:
        导出结果
    """
    kb = load_knowledge_base(knowledge_base_path)
    if kb is None:
        return {"status": "error", "error": "Knowledge base not found"}

    invalid_formats = [f for f in formats if f not in SUPPORTED_FORMATS]
    if invalid_formats:
        return {"status": "error", "error": f"Invalid formats: {invalid_formats}"}

    os.makedirs(output_dir, exist_ok=True)

    if chapter_filter:
        kb = filter_chapters(kb, chapter_filter)

    exported_files = []
    base_name = Path(knowledge_base_path).stem
    
    if subject_name is None:
        subject_name = base_name.replace("_knowledge_base", "").replace("knowledge_base", "")
    
    kb_meta = {
        "version": kb.get("version", "N/A"),
        "last_updated": kb.get("last_updated", "N/A")
    }

    chapters = kb.get("chapters", {})

    if split_by_chapter and "md" in formats and "html" in formats:
        # 获取设计配置
        design_config = get_design_config(subject_name)
        
        for chapter, data in chapters.items():
            kps = data.get("knowledge_points", [])
            chapter_clean = sanitize_filename(chapter)
            file_base = f"{subject_name}_{chapter_clean}"
            
            md_path = os.path.join(output_dir, file_base + ".md")
            html_path = os.path.join(output_dir, file_base + ".html")
            
            if export_markdown_chapter(chapter, kps, md_path, kb_meta):
                if os.path.exists(md_path):
                    exported_files.append({
                        "format": "md",
                        "chapter": chapter,
                        "path": md_path,
                        "size": os.path.getsize(md_path),
                    })
            
            if export_html_chapter(chapter, kps, html_path, kb_meta, design_config):
                if os.path.exists(html_path):
                    exported_files.append({
                        "format": "html",
                        "chapter": chapter,
                        "path": html_path,
                        "size": os.path.getsize(html_path),
                    })
        
        other_formats = [f for f in formats if f not in ("md", "html")]
        if other_formats:
            format_functions = {
                "mindmap": export_mindmap,
                "pdf": export_pdf,
            }
            format_extensions = {"mindmap": ".mm", "pdf": ".pdf"}
            
            for fmt in other_formats:
                output_path = os.path.join(output_dir, base_name + format_extensions[fmt])
                success = format_functions[fmt](kb, output_path)
                
                if success and os.path.exists(output_path):
                    exported_files.append({
                        "format": fmt,
                        "path": output_path,
                        "size": os.path.getsize(output_path),
                    })
    else:
        # 获取设计配置
        design_config = get_design_config(subject_name)
        
        format_functions = {
            "md": export_markdown,
            "html": export_html,
            "mindmap": export_mindmap,
            "pdf": export_pdf,
        }
        format_extensions = {"md": ".md", "html": ".html", "mindmap": ".mm", "pdf": ".pdf"}

        for fmt in formats:
            output_path = os.path.join(output_dir, base_name + format_extensions[fmt])
            if fmt == "html":
                success = format_functions[fmt](kb, output_path, design_config)
            else:
                success = format_functions[fmt](kb, output_path)

            if success and os.path.exists(output_path):
                exported_files.append(
                    {
                        "format": fmt,
                        "path": output_path,
                        "size": os.path.getsize(output_path),
                    }
                )

    return {"status": "success", "files": exported_files}


def main():
    """主函数，支持命令行调用"""
    import argparse

    parser = argparse.ArgumentParser(description="多格式导出")
    parser.add_argument("--base", required=True, help="知识库路径")
    parser.add_argument("--formats", required=True, help="格式列表，逗号分隔 (md,html,pdf,mindmap)")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--chapter", default="", help="章节过滤")
    parser.add_argument("--subject", default="", help="学科名称（用于文件名）")
    parser.add_argument("--no-split", action="store_true", help="不按章节分割导出")

    args = parser.parse_args()

    formats = [f.strip() for f in args.formats.split(",")]
    chapter_filter = args.chapter if args.chapter else None
    split_by_chapter = not args.no_split
    subject_name = args.subject if args.subject else None

    result = export_formats(args.base, formats, args.output, chapter_filter, split_by_chapter, subject_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
