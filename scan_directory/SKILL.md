---
name: scan_directory
description: 扫描学科目录，识别所有章节子目录和教学材料。触发条件：用户提到扫描目录、列出课程文件、查找教学材料、检查学科目录下的文件、发现新的教学内容。
---

# scan_directory Skill

## 什么时候使用这个 Skill

当用户提到以下场景时，使用这个 skill：
- 扫描学科目录
- 列出课程文件  
- 检查某个学科目录下有哪些材料
- 发现新的教学内容
- 查看有哪些章节

## 你的任务

作为 AI，你需要执行以下步骤来完成目录扫描任务：

### 步骤 1: 获取目录路径

从用户请求中提取 `directory_path`：
- 如果用户指定了路径，直接使用
- 如果没有指定，询问用户

### 步骤 2: 验证目录

执行以下检查：
1. 检查目录是否存在 → 不存在返回错误
2. 检查是否有读取权限 → 无权限返回错误
3. 检查是否为有效目录

### 步骤 3: 扫描目录结构

使用 `os.walk()` 或 Read 工具递归遍历目录：

**需要跳过的目录**：
- `.git`, `__pycache__`, `.venv`, `node_modules`, `.DS_Store`

**识别章节**：
- 匹配模式：`第X章`、`Chapter X`、`第一章`、`第二章` 等
- 不符合格式的目录归类为 "未分类"

**识别文件类型**：
| 扩展名 | 类型 |
|--------|------|
| .png, .jpg, .jpeg, .gif, .bmp, .webp | image |
| .pdf | document |
| .pptx, .ppt | presentation |
| .docx, .doc, .txt, .md | document |

### 步骤 4: 构建输出 JSON

返回以下格式：

```json
{
  "status": "success",
  "chapter_count": <数字>,
  "files": [
    {
      "chapter": "第1章-章节名",
      "file_path": "/absolute/path/to/file.ext",
      "file_type": "image|document|presentation",
      "file_extension": ".ext",
      "last_modified": "2024-01-15T10:30:00Z",
      "size": 1024000
    }
  ]
}
```

**注意**：
- 所有路径使用绝对路径
- `last_modified` 使用 ISO 8601 格式（UTC）
- `size` 单位为字节
- 按章节和文件名排序

### 步骤 5: 错误处理

| 情况 | 返回 |
|------|------|
| 目录不存在 | `{"status": "error", "error": "Directory not found"}` |
| 无权限 | `{"status": "error", "error": "Permission denied"}` |
| 空目录 | `{"status": "success", "files": [], "chapter_count": 0}` |

## 辅助工具

### 使用 scripts/scan.py（可选）

如果你想使用辅助脚本加速执行：

```bash
python scripts/scan.py "/path/to/directory"
```

这个脚本会返回符合上述格式的 JSON 结果。

### 或者直接编写代码

你也可以直接使用 Read/Glob 工具或编写 Python 代码执行扫描。

## 输出要求

1. 返回纯 JSON 格式（不要有额外文本）
2. 确保 `status` 字段正确反映执行结果
3. 如果出错，`error` 字段包含清晰的错误信息

## 示例

**用户请求**："扫描一下数学课程目录，看看有哪些文件"

**你的执行**：
1. 提取路径（用户没有指定，询问或假设常见路径）
2. 执行扫描
3. 返回结构化结果

**返回示例**：
```json
{
  "status": "success",
  "chapter_count": 3,
  "files": [
    {"chapter": "第1章-集合", "file_path": "/courses/math/ch1/intro.pdf", "file_type": "document", "file_extension": ".pdf", "last_modified": "2024-01-15T10:30:00Z", "size": 1024000},
    {"chapter": "第2章-函数", "file_path": "/courses/math/ch2/slides.pptx", "file_type": "presentation", "file_extension": ".pptx", "last_modified": "2024-01-16T14:20:00Z", "size": 2048000}
  ]
}
```