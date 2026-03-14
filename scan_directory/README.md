# scan_directory Skill

## 概述
scan_directory 是一个用于扫描学科目录的Skill，能够识别指定目录下的所有章节子目录和教学材料文件（图片、PPT、PDF等），并返回结构化的文件清单。

## 功能
- 递归扫描指定学科目录
- 自动识别章节子目录结构
- 检测并分类教学材料文件（图片、PPT、PDF等）
- 返回标准化的JSON格式输出

## 输入参数
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| directory_path | string | 是 | 学科主目录的绝对路径 |

## 输出格式
```json
{
  "status": "success",
  "chapter_count": 3,
  "files": [
    {
      "chapter": "第1章-绪论",
      "file_path": "/path/to/chapter1/image.png",
      "file_type": "image",
      "file_extension": ".png",
      "last_modified": "2024-01-15T10:30:00Z",
      "size": 1024000
    }
  ]
}
```

## 使用示例

### 作为独立Skill调用
```
输入: {"directory_path": "/user/courses/math"}
输出: {
  "status": "success",
  "chapter_count": 5,
  "files": [
    {"chapter": "第1章-集合", "file_path": "...", "file_type": "pptx", ...},
    {"chapter": "第2章-函数", "file_path": "...", "file_type": "pdf", ...}
  ]
}
```

### 在Agent工作流中调用
```typescript
// Agent检测到新教学资料
const scanResult = await callSkill('scan_directory', {
  directory_path: '/user/courses/physics'
});

// 根据返回的文件列表决定后续处理
for (const file of scanResult.files) {
  // 调用parse_multimodal处理每个文件
}
```

## 支持的文件类型
- **图片**: .png, .jpg, .jpeg, .gif, .bmp, .webp
- **文档**: .pdf
- **演示文稿**: .pptx, .ppt
- **文字文档**: .docx, .doc, .txt, .md

## 章节识别规则
1. 优先识别带有"第X章"或"Chapter X"格式的目录名
2. 支持中文数字章节名（如"第一章"、"第二章"）
3. 对于不符合格式的目录，统一归类为"未分类"

## 错误处理
- 目录不存在: 返回 `{"status": "error", "error": "Directory not found"}`
- 无权限访问: 返回 `{"status": "error", "error": "Permission denied"}`
- 空目录: 返回 `{"status": "success", "files": [], "chapter_count": 0}`

## 实现注意事项
- 使用异步I/O提高扫描性能
- 缓存目录结构以支持增量扫描
- 支持大规模目录（1000+文件）的快速扫描
