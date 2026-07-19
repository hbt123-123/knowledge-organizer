---
name: knowledge-organizer
description: 学科知识增量积累多Skill系统。用于构建学科知识增量积累工作流，包含目录扫描、多模态解析、知识提取、知识融合、多格式导出、索引构建六大核心能力。触发条件：用户提到知识管理、教学材料处理、知识库构建、学科知识积累。
---

# knowledge-organizer Skill

## 什么时候使用这个 Skill

当用户需要以下操作时使用此 Skill：

- 构建学科知识库系统
- 处理教学材料（PDF、PPT、图片）
- 提取和整理知识点
- 增量积累知识内容
- 导出知识为多种格式
- 构建知识检索索引

## 工作方式

### AI 驱动的知识提取

本 Skill 采用 **AI 直接执行** 的模式：

```
┌─────────────────────────────────────────────────────────┐
│                    工作流程                               │
├─────────────────────────────────────────────────────────┤
│  1. scan_directory    │  扫描目录（脚本执行）              │
│  2. parse_multimodal  │  解析文件（脚本执行）              │
│     - 文本文件        │  直接提取文本                      │
│     - 图片文件        │  调用多模态 API 解析               │
│  3. extract_knowledge │  提取知识点（AI 直接执行）         │
│  4. merge_knowledge   │  合并知识（脚本执行）              │
│  5. export_formats    │  导出格式（脚本执行）              │
│  6. build_index       │  构建索引（脚本执行）              │
└─────────────────────────────────────────────────────────┘
```

### API 使用说明

| 功能 | 是否需要 API | 说明 |
|------|-------------|------|
| PDF/PPT/DOCX 解析 | ❌ 不需要 | 使用本地库解析 |
| 文本知识点提取 | ❌ 不需要 | 由当前对话 AI 直接执行 |
| 图片内容解析 | ✅ 需要 | 调用多模态 API |
| 向量索引 | ✅ 可选 | 需要 embedding API（关键词索引不需要） |

## 子 Skills 列表

| Skill | 路径 | 执行方式 | 功能 |
|-------|------|---------|------|
| scan_directory | `scan_directory/` | 脚本 | 扫描学科目录，识别章节和教学材料 |
| parse_multimodal | `parse_multimodal/` | 脚本 | 解析PDF/PPT/图片，提取内容 |
| extract_knowledge | `extract_knowledge/` | **AI执行** | 从内容中提取知识点 |
| merge_knowledge | `merge_knowledge/` | 脚本 | 增量合并到知识库 |
| export_formats | `export_formats/` | 脚本 | 导出为MD/HTML（按章节分割） |
| build_index | `build_index/` | 脚本 | 构建向量/关键词索引 |

## AI 执行知识点提取

当执行 `extract_knowledge` 时，AI 应：

1. **阅读解析后的内容** - 从 `parse_multimodal` 的输出获取文本
2. **识别知识点** - 找出概念、定义、公式、例题、定理
3. **生成结构化输出** - 按照 SKILL.md 指定的 JSON 格式输出

详细指导请参考：[extract_knowledge/SKILL.md](extract_knowledge/SKILL.md)

## 配置说明

### 图片解析 API 配置

在项目根目录创建 `config.json`：

```json
{
  "api": {
    "base_url": "https://coding.dashscope.aliyuncs.com/v1",
    "api_key": "your-api-key",
    "vision_model": "qwen3.5-plus"
  }
}
```

或通过环境变量：

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

## 快速开始

### 运行完整工作流

```bash
python workflow_example.py "/path/to/subject"
```

输出文件将保存在学科目录下：
- `knowledge_base.json` - 知识库
- `output/学科名_章节名.md` - 每个章节的 Markdown 笔记
- `output/学科名_章节名.html` - 每个章节的 HTML 文档
- `indexes/knowledge_base_keyword.json` - 关键词索引

### 输出文件命名规则

**导出格式时，每个章节生成两个独立文件：**

| 文件类型 | 命名格式 | 示例 |
|---------|---------|------|
| Markdown | `学科名_章节名.md` | `数学_第1章-集合.md` |
| HTML | `学科名_章节名.html` | `数学_第1章-集合.html` |

**优势：**
- 每个章节独立成文件，便于单独复习
- 文件大小适中，加载快速
- 方便分享特定章节内容

### 使用单个 Skill

```bash
# 扫描目录
python scan_directory/scripts/scan.py "/path/to/course"

# 解析文件
python parse_multimodal/scripts/parse.py "/path/to/file.pdf"

# 解析图片（使用多模态 API）
python parse_multimodal/scripts/parse.py "/path/to/image.png"

# 解析图片（不使用 API）
python parse_multimodal/scripts/parse.py "/path/to/image.png" --no-vision

# 合并知识
python merge_knowledge/scripts/merge.py --knowledge '[]' --path "kb.json"

# 导出格式（按章节分割，生成 md 和 html）
python export_formats/scripts/export.py --base "kb.json" --formats "md,html" --output "." --subject "数学"

# 构建索引
python build_index/scripts/index.py --base "kb.json" --type "keyword" --output "."
```

## 依赖技术栈

- **PDF解析**: pymupdf
- **PPT解析**: python-pptx
- **DOCX解析**: python-docx
- **图片解析**: Pillow + 多模态 API
- **PDF生成**: reportlab

## 项目结构

```
knowledge-organizer/
├── SKILL.md                  # 项目总览（本文件）
├── config.json               # API配置文件
├── pyproject.toml            # 项目依赖管理
├── workflow_example.py       # 工作流示例
├── common/                   # 共享模块
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   └── api_client.py         # API客户端（图片解析）
├── scan_directory/
│   ├── SKILL.md
│   └── scripts/scan.py
├── parse_multimodal/
│   ├── SKILL.md
│   └── scripts/parse.py
├── extract_knowledge/
│   ├── SKILL.md              # AI执行指导
│   └── scripts/extract.py    # 工具函数
├── merge_knowledge/
│   ├── SKILL.md
│   └── scripts/merge.py
├── export_formats/
│   ├── SKILL.md
│   └── scripts/export.py
└── build_index/
    ├── SKILL.md
    └── scripts/index.py
```
