---
name: design
description: "综合设计 skill：UI/UX 智能（67 种风格、161 种配色、57 种字体配对、161 种产品类型）、品牌识别、Design Token、Logo/CIP/横幅生成、shadcn/ui + Tailwind、演示文稿。操作：设计、构建、创建、实施、审查、修复、优化。元素：按钮、模态框、导航栏、卡片、图表。风格：玻璃拟态、黏土拟态、极简主义、粗野主义、新拟态、Bento Grid、深色模式。平台：React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui、HTML/CSS。"
argument-hint: "[ui-ux|brand|logo|cip|banner|slides|icon] [context]"
---

# Design - 统一设计智能

综合设计 skill，整合了 UI/UX 智能、品牌识别、Logo/CIP 生成、横幅、演示文稿和 UI 样式。这是一个统一的 skill，处理所有设计相关任务。

## 何时使用

当任务涉及 **UI 结构、视觉设计、品牌识别或用户体验** 时使用此 Skill。

### 必须使用

- 设计新页面（落地页、仪表盘、管理后台、SaaS、移动端 App）
- 创建或重构 UI 组件
- 选择配色方案、字体、间距系统
- 品牌识别和视觉资产
- Logo、横幅、图标或演示文稿设计
- 审查 UI 代码的 UX、无障碍性或视觉一致性

### 跳过

- 纯后端逻辑开发
- 仅涉及 API 或数据库设计
- 基础设施或 DevOps 工作

---

## 子技能路由

| 任务 | 子技能 / 参考 | 位置 |
|------|---------------|------|
| UI/UX 决策、风格、配色 | **UI/UX 智能** | 本 SKILL.md |
| 品牌识别、声音、资产 | Brand | `references/brand-guideline-template.md` / `references/messaging-framework.md` |
| Design Token、规格、CSS 变量 | Design System | `references/token-architecture.md` |
| shadcn/ui、Tailwind、代码 | UI Styling | `references/shadcn-components.md` / `references/tailwind-customization.md` |
| Logo 设计、AI 生成 | Logo | `references/logo-design.md` |
| CIP mockups、交付物 | CIP | `references/cip-design.md` |
| 演示文稿、PPT | Slides | `references/slides.md` |
| 横幅设计 | Banner | `references/banner-sizes-and-styles.md` |
| SVG 图标 | Icon | `references/icon-design.md` |

---

## UI/UX 智能

### 67 种 UI 风格

| # | 风格 | 适用于 |
|---|------|--------|
| 1 | 极简主义 & 瑞士风格 | 企业应用、仪表盘 |
| 2 | 新拟态 | 健康/养生、冥想 |
| 3 | 玻璃拟态 | 现代 SaaS、金融仪表盘 |
| 4 | 粗野主义 | 设计作品集、艺术项目 |
| 5 | 黏土拟态 | 教育类 App、儿童应用 |
| 6 | 深色模式 (OLED) | 夜间模式、编程平台 |
| 7 | Bento Grid | 仪表盘、产品页 |
| 8 | AI 原生 UI | AI 产品、聊天机器人 |
| 9 | 赛博朋克 UI | 游戏、科技产品 |
| 10 | 有机生物风格 | 养生、可持续品牌 |
| ... | ... | ... |

### 161 种配色方案

行业特定配色，存于 `data/colors.csv`。适用于：
- 科技 & SaaS、金融、医疗健康、电商
- 创意、生活方式、新兴科技

### 57 种字体配对

精选排版，存于 `data/typography.csv`。可直接使用 Google Fonts。

### 10 种技术栈

指南适用于：React、Next.js、Vue、Svelte、SwiftUI、React Native、Flutter、Tailwind、shadcn/ui、HTML/CSS

### UX 指南（优先级顺序）

| 优先级 | 类别 | 关键检查 |
|--------|------|----------|
| 1 | 无障碍性 | 对比度 4.5:1、Alt 文本、键盘导航 |
| 2 | 触控与交互 | 最小 44×44px、间距 8px+ |
| 3 | 性能 | WebP/AVIF、懒加载 |
| 4 | 风格选择 | 一致性、SVG 图标 |
| 5 | 布局与响应式 | 移动优先断点 |
| 6 | 字体与颜色 | 基础 16px、语义化 Token |
| 7 | 动画 | 时长 150-300ms |
| 8 | 表单与反馈 | 可见标签、错误靠近字段 |
| 9 | 导航 | 可预测的返回、底部导航 ≤5 |
| 10 | 图表 | 图例、提示框 |

---

## 快速命令

### UI/UX 搜索

```bash
# 搜索风格
python3 scripts/search.py "玻璃拟态 现代" --domain style

# 搜索配色
python3 scripts/search.py "金融" --domain color

# 搜索字体
python3 scripts/search.py "优雅 serif" --domain typography

# 生成设计系统
python3 scripts/search.py "美容 spa" --design-system -p "品牌名称"
```

### 设计系统生成器

```bash
# 生成并输出
python3 scripts/search.py "saas 仪表盘" --design-system -p "我的应用"

# 生成 Markdown 格式
python3 scripts/search.py "金融" --design-system -f markdown

# 持久化到文件
python3 scripts/search.py "saas" --design-system --persist -p "我的应用"
```

---

## 数据文件

| 文件 | 描述 |
|------|------|
| `data/colors.csv` | 配色方案 |
| `data/typography.csv` | 字体配对 |
| `data/styles.csv` | UI 风格 |
| `data/products.csv` | 产品类型 |
| `data/design.csv` | 设计推理规则 |
| `data/ux-guidelines.csv` | UX 指南 |
| `data/charts.csv` | 图表类型 |
| `data/landing.csv` | 落地页模式 |
| `data/icons.csv` | 图标推荐 |
| `data/app-interface.csv` | App 界面模式 |
| `data/react-performance.csv` | React 性能 |
| `data/google-fonts.csv` | Google Fonts |
| `data/slide-*.csv` | 幻灯片数据 |
| `data/logo/colors.csv` | Logo 配色 |
| `data/logo/styles.csv` | Logo 风格 |
| `data/logo/industries.csv` | Logo 行业指南 |
| `data/cip/deliverables.csv` | CIP 交付物 |
| `data/icon/styles.csv` | 图标风格 |

---

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/search.py` | 主搜索引擎，搜索所有设计数据 |
| `scripts/design_system.py` | 设计系统生成器 |
| `scripts/core.py` | 核心工具函数 |

---

## 参考文档

| 文件 | 描述 |
|------|------|
| `references/brand-guideline-template.md` | 品牌指南模板 |
| `references/messaging-framework.md` | 消息框架 |
| `references/visual-identity.md` | 视觉识别 |
| `references/token-architecture.md` | Token 架构 |
| `references/shadcn-components.md` | shadcn/ui 组件 |
| `references/shadcn-theming.md` | shadcn/ui 主题 |
| `references/tailwind-customization.md` | Tailwind 定制 |
| `references/logo-design.md` | Logo 设计指南 |
| `references/logo-style-guide.md` | Logo 风格指南 |
| `references/cip-design.md` | CIP 设计 |
| `references/cip-deliverable-guide.md` | CIP 交付物指南 |
| `references/slides.md` | 演示文稿指南 |
| `references/slides-create.md` | 幻灯片创建 |
| `references/banner-sizes-and-styles.md` | 横幅尺寸与风格 |
| `references/icon-design.md` | 图标设计 |