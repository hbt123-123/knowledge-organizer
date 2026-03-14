# 学科知识增量积累多Skill系统

> 用于构建学科知识增量积累工作流的多Skill系统

## 系统架构

本项目包含6个核心Skills，形成完整的知识管理解决方案：

```
┌─────────────────────────────────────────────────────────┐
│                    学科知识管理系统                        │
├─────────────────────────────────────────────────────────┤
│  1. scan_directory    │  扫描学科目录，识别文件            │
│  2. parse_multimodal  │  多模态文件解析                    │
│  3. extract_knowledge │  知识点提取                       │
│  4. merge_knowledge   │  知识融合                         │
│  5. export_formats    │  多格式导出                       │
│  6. build_index       │  检索索引构建                      │
└─────────────────────────────────────────────────────────┘
```

## Skills列表

| Skill | 路径 | 功能 |
|-------|------|------|
| scan_directory | `scan_directory/` | 扫描学科目录，识别章节和教学材料 |
| parse_multimodal | `parse_multimodal/` | 解析PDF/PPT/图片，提取内容 |
| extract_knowledge | `extract_knowledge/` | 从内容中提取知识点 |
| merge_knowledge | `merge_knowledge/` | 增量合并到知识库 |
| export_formats | `export_formats/` | 导出为PDF/MD/思维导图 |
| build_index | `build_index/` | 构建向量/关键词索引 |

## 快速开始

### 1. 安装依赖

```bash
# 核心依赖
pip install openai httpx Pillow

# PDF解析（可选）
pip install pymupdf

# PPT解析（可选）
pip install python-pptx

# PDF导出（可选）
pip install reportlab

# 或安装全部可选依赖
pip install -e ".[all]"
```

### 2. 配置 API

在项目根目录创建 `config.json`：

```json
{
  "api": {
    "base_url": "https://coding.dashscope.aliyuncs.com/v1",
    "api_key": "your-api-key",
    "model": "qwen3.5-plus",
    "vision_model": "qwen3.5-plus",
    "embedding_model": "text-embedding-v3"
  },
  "workflow": {
    "max_retries": 3,
    "retry_delay": 1.0,
    "timeout": 120
  }
}
```

或通过环境变量配置：

```bash
export DASHSCOPE_API_KEY="your-api-key"
export DASHSCOPE_BASE_URL="https://coding.dashscope.aliyuncs.com/v1"
```

### 3. 运行完整工作流

```bash
python workflow_example.py "./sample_course"
```

### 4. 使用单个Skill

```bash
# 扫描目录
python scan_directory/scripts/scan.py "/path/to/course"

# 解析文件
python parse_multimodal/scripts/parse.py "/path/to/file.pdf"

# 提取知识
python extract_knowledge/scripts/extract.py --content "文本..." --chapter "第1章"

# 合并知识
python merge_knowledge/scripts/merge.py --knowledge '[]' --path "kb.json"

# 导出格式
python export_formats/scripts/export.py --base "kb.json" --formats "md" --output "."

# 构建索引
python build_index/scripts/index.py --base "kb.json" --type "keyword" --output "."
```

## 工作流

```
Agent检测到新教学资料
        │
        ▼
   scan_directory  ──► 发现新文件列表
        │
        ▼
   parse_multimodal ──► 解析文件内容
        │
        ▼
   extract_knowledge ──► 提取知识点
        │
        ▼
   merge_knowledge ──► 增量合并到知识库
        │
        ▼
   export_formats ──► 导出可用格式
        │
        ▼
   build_index ──► 构建AI检索索引
        │
        ▼
   知识系统已更新
```

## 工作流特性

- **错误处理**：每个步骤都有完整的错误捕获和报告
- **状态恢复**：支持从断点恢复，避免重复处理
- **进度追踪**：实时显示处理进度和统计信息

### 工作流命令行选项

```bash
# 运行工作流
python workflow_example.py "./sample_course"

# 不恢复之前的状态
python workflow_example.py "./sample_course" --no-resume

# 清除状态并重新开始
python workflow_example.py "./sample_course" --clear

# 指定输出路径
python workflow_example.py "./sample_course" --kb "./my_kb.json" --output "./my_output"
```

## 依赖技术栈

- **LLM**: qwen3.5-plus / kimi-k2.5 (通义千问 API)
- **视觉模型**: qwen3.5-plus (支持多模态)
- **Embedding**: text-embedding-v3
- **PDF解析**: PyMuPDF
- **PPT解析**: python-pptx
- **PDF生成**: reportlab

## 项目结构

```
knowledge-organizer/
├── SKILL.md                  # 项目总览
├── config.json               # API配置文件
├── pyproject.toml            # 项目依赖管理
├── workflow_example.py       # 工作流示例
├── common/                   # 共享模块
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   └── api_client.py         # API客户端
├── scan_directory/
│   ├── SKILL.md
│   └── scripts/scan.py
├── parse_multimodal/
│   ├── SKILL.md
│   └── scripts/parse.py
├── extract_knowledge/
│   ├── SKILL.md
│   └── scripts/extract.py
├── merge_knowledge/
│   ├── SKILL.md
│   └── scripts/merge.py
├── export_formats/
│   ├── SKILL.md
│   └── scripts/export.py
├── build_index/
│   ├── SKILL.md
│   └── scripts/index.py
└── sample_course/            # 示例测试数据
    ├── 第1章-集合/
    └── 第2章-函数/
```

## 注意事项

- API 密钥请妥善保管，不要提交到版本控制
- 知识点提取和向量索引需要消耗 API 调用额度
- 处理大量文件时建议分批进行
