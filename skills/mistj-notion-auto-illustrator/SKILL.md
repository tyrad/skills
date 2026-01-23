---
name: mistj-notion-auto-illustrator
description: "Notion 文章全自动配图端到端工作流。它协调整个过程：(1) 使用内置脚本导出内容，(2) 通过 baoyu-article-illustrator 生成风格一致的视觉方案，(3) 通过 mistj-upyun-uploader 上传至又拍云，(4) 将位置映射到 Notion block ID 并自动完成插入。当用户要求“给我的 Notion 页面配图”、“为这个 Notion URL 添加插图”或“自动化 Notion 文章装饰”时使用。"
---

# Mistj Notion 自动配图助手 (Notion Auto Illustrator)

此 Skill 实现了为 Notion 文章自动添加高质量、风格统一的插图。它协调多个专业 Skill，并在独立的目录中运行以保持工作区整洁。

## 文件隔离原则 (重要)

- **执行路径**：在开始任何操作前，必须创建一个隔离目录 `notion-auto-illustrator/{article-slug}/`。这个 `{article-slug}` 作为整个项目的唯一标识，后续所有工具调用应尽量保持此 Slug 一致。
- **所有产出物**：导出的 JSON、Markdown 文章、生成的图片以及配置文件必须全部存放在该目录中。
  所有操作必须在项目专用的 `notion-auto-illustrator/{article-slug}/` 目录下进行，严禁污染根目录。

### 外科手术式集成原则 (重要)

为了防止破坏 Notion 页面的 Rich Text（加粗、超链接、公式等）以及避免块过度碎片化，严禁预先对整个文档进行行级别拆分。必须采用“外科手术式”集成：

1. 仅在 `baoyu-article-illustrator` 规划的插图点进行切割。
2. 切割时必须解析 `rich_text` 数组，确保分割后的两个块完整保留原有的所有格式。
3. 如果插图点位于两个块之间，则直接插入。

## 核心工作流

### 0. 初始化隔离环境 (环境准备)

- **动作**：根据文章标题生成 Slug，在当前工作区创建并进入 `notion-auto-illustrator/{article-slug}/` 目录。
- **原则**：后续所有步骤生成的文件（JSON, Markdown, Images）必须全部存放在此目录下。

### 1. 导出与处理内容 (Export & Parse)

- **动作**：在隔离目录中运行本 Skill 自带的垂直整合脚本：
  ```bash
  /path/to/skill/scripts/fetch_and_parse.sh <page_url_or_id>
  ```
- **结果**：脚本会自动在当前目录下生成 `./raw.json` 和 `./source-article.md`。

### 2. 生成插图计划 (Planning)

- **动作**：调用 **`baoyu-article-illustrator`** 分析 `./source-article.md`。
- **交互**：该 Skill 会生成 3 种风格方案并请求确认。
- **输出路径**：生成后，方案文件 `outline.md` 位于当前隔离环境的 `illustrations/` 目录下（通常会带有一个由插件生成的子目录，如 `./illustrations/{topic-slug}/`）。
- **确认路径**：在执行下一步前，必须确认 `outline.md` 的实际物理路径，并以该路径为准。

### 3. 图片生成与上传 (Generation & Upload)

- **本地存储**：生图 Skill 会在上述 `./illustrations/{article-slug}/` 目录下生成图片。
- **云端同步**：调用 **`mistj-upyun-uploader`** 上传这些本地图片，并记录获取的又拍云 URL。

### 4. 外科手术式集成 (Surgical Integration)

1. **获取规划**：从 `outline.md` 提取插入点的文本锚点。
2. **定位物理块 (Block Positioning)**：
   - 运行 `python3 scripts/integrate_notion_blocks.py ./raw.json ./illustrations/{article-slug}/outline.md`。
   - 该操作会通过文本匹配，找到目标文本在 `raw.json` 中对应的 `block_id` 及其完整的 JSON 对象（包含 Rich Text）。
3. **执行精准切割 (Integration Exec)**：
   - 使用 `surgical_helper.py` 逻辑分析目标块：
     - **情况 A (锚点位于块末尾)**：直接调用 `patch-block-children` 在原 Block ID 后插入“图片 Block”。
     - **情况 B (锚点位于块中间)**：
       1. 调用 `update-a-block`：将原 Block 更新为切割后的前半部分（保留格式）。
       2. 调用 `patch-block-children`：在原 Block 后**依次**插入“图片 Block”和“包含后半部分内容的新 Paragraph Block”（保留所有格式）。
4. **验证结果**：刷新页面确认格式无损，插画位置精准且无多余空行。

## 映射启发式规则

当 `baoyu-article-illustrator` 识别出类似“在‘为什么要切换’章节后”的位置时，使用以下策略：

1. 提取文本“为什么要切换”。
2. 使用 `integrate_notion_blocks.py` 在 `raw.json` 中搜索此文本。
3. 如果存在多个匹配项，优先选择匹配指定类型（如 `heading_1`, `heading_2`）的项。
4. 确认 `block_id` 后，执行物理插入。

## 多步交互模式

1. **第一阶段 (规划)**：导出 -> 生成大纲 -> 风格确认。
2. **第二阶段 (生成)**：生成图片 -> 上传云端。
3. **第三阶段 (合成)**：外科手术式集成。

## 文件组织

- `SKILL.md`：本指南。
- `scripts/`：
  - `integrate_notion_blocks.py`：自动将插图位置映射到 Notion ID 的工具。
- `references/`：
  - `notion_block_formats.md`：Notion 图片 Block JSON 结构的参考示例。
