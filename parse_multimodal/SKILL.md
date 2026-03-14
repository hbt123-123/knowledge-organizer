---
name: parse_multimodal
description: 多模态文件解析。解析PDF/PPT/图片文件，提取文本、图像描述、表格内容。用于解析教学材料、提取文档内容、转换视觉内容为文本描述。触发条件：用户提到解析文件、从PDF/图片提取文本、处理文档、转换视觉内容为文本。
---

# parse_multimodal Skill

## 什么时候使用这个 Skill

当用户需要以下操作时使用此 Skill：

- 解析 PDF 文件，提取文本、图像、表格
- 解析 PPT/PPTX 文件，提取幻灯片内容和图像
- 分析图片文件，用视觉模型提取图像描述
- 将扫描的文档或图片转换为可编辑的文本
- 处理教学材料，提取章节内容和图表信息

## 你的任务

你是一个多模态文件解析器，负责从各种文件格式中提取结构化内容。

### 步骤 1：识别文件类型

根据文件扩展名判断文件类型：

| 扩展名 | 文件类型 |
|--------|----------|
| .pdf | PDF 文档 |
| .pptx, .ppt | PowerPoint 演示文稿 |
| .png, .jpg, .jpeg, .gif, .bmp | 图片文件 |

### 步骤 2：解析文件内容

#### 如果是图片文件 (.png, .jpg, .jpeg 等)

1. **调用视觉模型分析图像**
   - 使用你的视觉理解能力分析图片内容
   - 提取图像中的文字（OCR）
   - 描述图像中的图表、图示、流程图
   - 识别图像中包含的公式、表格结构

2. **返回结构化描述**
   - 图像中的文字内容
   - 图像的视觉描述（图表含义、流程说明等）
   - 识别到的数据类型（表格、公式、示意图等）

#### 如果是 PDF 文件

1. **提取文本内容**
   - 逐页读取 PDF 文本
   - 保留章节标题和段落结构
   - 识别页眉页脚并排除

2. **提取图像**
   - 提取嵌入的图像
   - 记录图像所在页面
   - 对每张图像调用视觉模型进行描述

3. **提取表格**（如果存在）
   - 识别表格结构
   - 转换为行列数据格式

4. **提取元数据**
   - 页数
   - 文档标题（如果可用）
   - 作者（如果可用）

#### 如果是 PPT/PPTX 文件

1. **提取幻灯片内容**
   - 读取每张幻灯片的标题和正文
   - 提取项目符号列表
   - 识别文本框和形状中的文字

2. **提取图像**
   - 提取每张幻灯片中的图片
   - 记录图片所在幻灯片编号
   - 对图片进行视觉描述

3. **提取表格**（如果存在）

### 步骤 3：组织输出结构

将解析结果组织为统一的 JSON 格式：

```json
{
  "status": "success",
  "file_path": "/path/to/file.pdf",
  "file_type": "pdf",
  "content": {
    "text": "提取的文本内容，按页面或章节组织...",
    "images": [
      {
        "page": 1,
        "description": "图像的详细描述",
        "extracted_text": "图像中识别出的文字（可选）"
      }
    ],
    "tables": [
      {
        "page": 1,
        "caption": "表格标题（可选）",
        "data": [
          ["header1", "header2"],
          ["row1col1", "row1col2"]
        ]
      }
    ],
    "metadata": {
      "page_count": 10,
      "title": "文档标题",
      "slides_count": 20
    }
  }
}
```

## 输出要求

1. **完整性**：尽可能提取所有可用的文本和视觉信息
2. **结构化**：保持内容的层次结构（章节、段落）
3. **可读性**：图像描述应该清晰、准确，便于后续知识提取
4. **元数据**：记录关键元信息（页数、标题等）

## 错误处理

如果解析失败，根据具体情况返回错误：

- **文件不存在**：`{"status": "error", "error": "File not found", "file_path": "..."}`
- **不支持的文件类型**：`{"status": "error", "error": "Unsupported file type"}`
- **解析失败**：`{"status": "error", "error": "Parse failed: <具体原因>"}`
- **文件损坏**：`{"status": "error", "error": "File corrupted or cannot be read"}`

## 可选的辅助工具

如果需要自动化处理，可以使用 `scripts/parse.py` 脚本：

```bash
# 解析图片
python scripts/parse.py "/path/to/image.png"

# 解析 PDF
python scripts/parse.py "/path/to/file.pdf"

# 指定 OCR 语言
python scripts/parse.py "/path/to/image.png" --ocr-lang chi_sim
```

**注意**：脚本是可选的辅助工具，主要依靠你的内置能力进行解析。

## 后续步骤

解析完成后，将结果传递给 **extract_knowledge** Skill 进行知识点提取。