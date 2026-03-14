---
name: build_index
description: 构建检索索引。为知识库构建可搜索的索引（向量索引、关键词索引、混合索引），实现快速AI语义搜索。触发条件：用户提到构建索引、创建搜索索引、向量化知识、优化知识检索。
---

# build_index Skill

## 什么时候使用这个 Skill

当用户需要以下操作时使用此 Skill：

- 为知识库构建可搜索的索引
- 创建向量数据库实现语义搜索
- 构建关键词索引实现精确匹配
- 优化知识的检索速度和准确性
- 准备知识库的 AI 问答能力

## 你的任务

你是一个索引构建专家，负责为知识库构建高效的检索索引。

### 步骤 1：读取知识库

1. **加载知识库文件**
   - 读取 JSON 格式的知识库
   - 提取所有知识点

2. **分析内容**
   - 统计知识点数量
   - 识别章节结构
   - 了解内容类型分布

### 步骤 2：选择索引类型

根据需求选择合适的索引类型：

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| vector | 向量索引，支持语义搜索 | AI 问答、相似知识推荐 |
| keyword | 关键词索引，支持精确匹配 | 关键词搜索、快速定位 |
| hybrid | 混合索引，结合两者优点 | 需要同时支持语义和精确搜索 |

### 步骤 3：构建索引

#### 类型 1：向量索引

1. **为每个知识点生成向量**
   - 提取知识点的标题和描述
   - 调用 embedding 模型生成向量表示
   - 使用语义理解能力生成向量（如果没有 API）

2. **组织索引结构**
   ```json
   {
     "type": "vector",
     "embedding_model": "text-embedding-3-small",
     "dimension": 1536,
     "entries": [
       {
         "id": "kp-uuid-1",
         "vector": [0.123, -0.456, 0.789, ...],
         "metadata": {
           "title": "集合的定义",
           "description": "集合是把具有共同特征的事物或对象汇总在一起的结果。",
           "category": "概念",
           "chapter": "第1章-集合",
           "related_concepts": ["元素", "子集", "空集"]
         }
       }
     ]
   }
   ```

#### 类型 2：关键词索引

1. **提取关键词**
   - 从标题和描述中提取关键词
   - 去除停用词（的、了、在等）
   - 识别专业术语

2. **构建倒排索引**
   ```json
   {
     "type": "keyword",
     "entries": [
       {
         "keyword": "集合",
         "knowledge_points": ["kp-uuid-1", "kp-uuid-2"],
         "weight": 0.8
       },
       {
         "keyword": "元素",
         "knowledge_points": ["kp-uuid-1", "kp-uuid-3"],
         "weight": 0.6
       }
     ]
   }
   ```

#### 类型 3：混合索引

同时生成向量索引和关键词索引：

```json
{
  "type": "hybrid",
  "vector_index": { ... },
  "keyword_index": { ... },
  "fusion_strategy": "reciprocal_rank"
}
```

### 步骤 4：保存索引

1. **创建输出目录**（如果不存在）
2. **保存索引文件**
   - 向量索引：`knowledge_vector.json`
   - 关键词索引：`knowledge_keyword.json`
   - 混合索引：`knowledge_hybrid.json`
3. **记录元信息**

### 步骤 5：输出结果

```json
{
  "status": "success",
  "index_file_path": "/index/knowledge_vector.json",
  "entry_count": 150,
  "build_time_ms": 2500,
  "index_type": "vector",
  "metadata": {
    "knowledge_base_version": "1.2.0",
    "created_at": "2024-01-15T10:30:00Z",
    "dimension": 1536
  }
}
```

## 输出要求

1. **索引完整性**：每个知识点都要有对应的索引条目
2. **向量质量**：向量要准确反映内容的语义
3. **关键词覆盖**：关键词要覆盖主要概念
4. **检索效率**：索引结构要便于快速查询

## 错误处理

如果索引构建失败，根据具体情况返回错误：

- **知识库不存在**：`{"status": "error", "error": "Knowledge base not found"}`
- **无效索引类型**：`{"status": "error", "error": "Invalid index type"}`
- **构建失败**：`{"status": "error", "error": "Index build failed: <具体原因>"}`
- **向量生成失败**：`{"status": "error", "error": "Vector generation failed: <具体原因>"}`

## 可选的辅助工具

如果需要自动化索引构建，可以使用 `scripts/index.py` 脚本：

```bash
# 构建向量索引
python scripts/index.py --base "/db/knowledge.json" --type "vector" --output "/index"

# 构建关键词索引
python scripts/index.py --base "/db/knowledge.json" --type "keyword" --output "/index"

# 构建混合索引
python scripts/index.py --base "/db/knowledge.json" --type "hybrid" --output "/index"
```

**注意**：脚本是可选的辅助工具，你也可以直接生成索引文件。

## 后续步骤

索引构建完成后，知识库就可以支持：

- 语义搜索（使用向量索引）
- 关键词搜索（使用关键词索引）
- AI 问答（结合索引和 LLM）