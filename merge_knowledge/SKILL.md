---
name: merge_knowledge
description: 将新知识点增量合并到现有知识库。处理重复项、冲突解决、版本控制，支持增量累积。触发条件：用户提到合并知识、更新知识库、添加到知识存储、同步知识。
---

# merge_knowledge Skill

## 什么时候使用这个 Skill

当用户需要以下操作时使用此 Skill：

- 将新提取的知识点添加到现有知识库
- 更新已存在的知识点
- 从多个来源同步知识
- 处理知识库中的重复项和冲突
- 建立增量积累的知识体系

## 你的任务

你是一个知识库管理员，负责将新知识点智能合并到现有知识库中。

### 步骤 1：检查现有知识库

1. **读取现有知识库**
   - 如果知识库文件存在，读取其内容
   - 了解现有的章节结构和知识点

2. **分析现有结构**
   - 识别已有的章节分组
   - 记录现有知识点的标题和 ID
   - 了解知识库的版本号

### 步骤 2：处理新知识点

对于每个新知识点，执行以下检查：

1. **重复检测**
   - 检查是否有相同标题的知识点已存在
   - 比较内容是否完全相同

2. **冲突处理**
   - 如果标题相同但内容不同，判断是否为更新版本
   - 根据选择的策略决定保留哪个版本

### 步骤 3：选择合并策略

根据具体情况选择合适的策略：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| overwrite | 完全覆盖，删除重复项 | 需要完全替换旧版本 |
| add | 仅添加新项，保留现有项 | 避免任何修改 |
| merge | 智能合并，保留最新版本 | 常规增量更新（默认） |

### 步骤 4：执行合并

1. **识别章节归属**
   - 从提取结果的顶层 `chapter` 字段获取章节名
   - 如果知识点自身有 `chapter` 字段，优先使用
   - 否则使用提取结果的章节名作为默认章节

2. **添加新知识点**
   - 为新知识点生成唯一 ID
   - 添加到对应章节下

3. **处理重复项**
   - 根据策略决定是更新还是跳过
   - 记录修改历史（可选）

4. **更新版本号**
   - 遵循语义化版本号（主版本.次版本.修订号）
   - 次版本递增：添加新内容
   - 修订号递增：修复错误或微小调整

### 步骤 5：输出结果

```json
{
  "status": "success",
  "stats": {
    "added": 5,
    "modified": 2,
    "skipped": 3,
    "conflicts_resolved": 1
  },
  "merged_base_path": "/path/to/knowledge_base.json",
  "version": "1.2.0",
  "changes": [
    {
      "type": "added",
      "title": "新知识点标题",
      "chapter": "第1章-集合"
    },
    {
      "type": "modified",
      "old_title": "旧标题",
      "new_title": "新标题"
    }
  ]
}
```

## 知识库结构规范

合并后的知识库应遵循以下结构：

```json
{
  "version": "1.2.0",
  "last_updated": "2024-01-15T10:30:00Z",
  "total_points": 150,
  "chapters": {
    "第1章-集合": {
      "knowledge_points": [
        {
          "id": "uuid-string",
          "title": "集合的定义",
          "description": "集合是把具有共同特征的事物或对象汇总在一起的结果。",
          "category": "概念",
          "related_concepts": ["元素", "子集", "空集"],
          "source_file": "/path/to/source.pdf",
          "extracted_at": "2024-01-15T10:30:00Z"
        }
      ],
      "point_count": 10
    },
    "第2章-函数": {
      "knowledge_points": [...],
      "point_count": 15
    }
  }
}
```

## 输出要求

1. **增量更新**：只添加新内容，不过度修改已有内容
2. **冲突解决**：提供清晰的冲突解决策略
3. **版本追踪**：维护版本号便于追溯
4. **完整性**：确保知识库结构完整

## 错误处理

如果合并失败，根据具体情况返回错误：

- **知识库路径无效**：`{"status": "error", "error": "Invalid knowledge base path"}`
- **无效的 JSON 格式**：`{"status": "error", "error": "Invalid JSON format"}`
- **合并失败**：`{"status": "error", "error": "Merge failed: <具体原因>"}`
- **权限不足**：`{"status": "error", "error": "Permission denied"}`

## 可选的辅助工具

如果需要自动化合并，可以使用 `scripts/merge.py` 脚本：

```bash
# 合并知识点到知识库
python scripts/merge.py --knowledge '[{"title": "集合的定义", ...}]' --path "/db/knowledge.json" --strategy merge

# 使用覆盖策略
python scripts/merge.py --knowledge '[...]' --path "/db/knowledge.json" --strategy overwrite
```

**注意**：脚本是可选的辅助工具，你也可以直接修改 JSON 文件进行合并。

## 后续步骤

合并完成后，可以选择：

- 将结果传递给 **export_formats** Skill 导出为不同格式
- 将结果传递给 **build_index** Skill 构建检索索引