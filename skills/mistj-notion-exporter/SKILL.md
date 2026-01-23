---
name: mistj-notion-exporter
description: "Notion 页面 Markdown 导出与生成工具，解决原生 MCP 的分页与嵌套丢失问题。"
---

# mistj-notion-exporter

## 🚀 极简工作流

1. **数据抓取 (Shell)**:
   - **环境要求**：仅需 `curl` 与 `jq`。
   - **配置方式**：项目根目录需存在 `notion_credentials.sh` 配置文件。
     - **AI 自动化**：若检测到配置缺失，AI 应主动询问用户：“请输入您的 Notion Integration Token”，并自动在根目录创建 `notion_credentials.sh` 文件。
     - **文件内容格式**：`export NOTION_TOKEN="secret_xxx"`
   - **执行抓取 (Fetch)**：
     运行脚本获取物理数据。它会递归抓取所有子 Block 并存为 `raw.json`。
     ```bash
     ./scripts/fetch_notion.sh <PAGE_ID_OR_URL> <SLUG>
     ```

     - **参数说明**：`SLUG` 是必填项，用于定义输出文件夹名。若不填写，脚本将报错退出。
     - **示例 1 (成功)**：`./scripts/fetch_notion.sh 12345abc my-article`
       - **结果**：在 `./notion_exports/my-article/` 生成 `raw.json`。
     - **示例 2 (报错)**：`./scripts/fetch_notion.sh 12345abc`
       - **结果**：报错并退出，提示 `用法: ./scripts/fetch_notion.sh <PAGE_ID> <SLUG>`。

2. **脚本解析 (Parser)**:
   - 运行解析脚本生成 MD：
     ```bash
     python3 scripts/notion_json_to_md.py notion_exports/{slug}/raw.json -o notion_exports/{slug}/article.md
     ```

3. **定位与同步 (Locating)**:
   - 若需回填图片或内容，利用 `find_block.py` 在本地 `raw.json` 中获取精确 ID：

     ```bash
     python3 scripts/find_block.py notion_exports/{slug}/raw.json "关键词或摘要" [可选Block类型]
     ```

   - **兜底建议**：若脚本未命中或结果不准，AI 应使用 `grep_search` 搜索 `raw.json` 或直接读取该文件进行人工确认，确保 ID 绝对准确。

   - 拿着得到的 ID 调用 Notion MCP 的 `patch-block-children` 进行插入。

## 🛠 工具集

- `scripts/notion_json_to_md.py`: 生成 Markdown 文稿。支持表格、公式、高亮及嵌套列表还原。
- `scripts/find_block.py`: 坐标导航。在本地 `raw.json` 中递归搜索关键词，返回精确的 Block ID。

## 📂 文件规范

每次导出应创建独立的工作区文件夹：

```text
notion_exports/{topic-slug}/
├── raw.json       # 原始抓取的碎片数据 (建议 GitIgnore)
└── article.md     # 最终生成的 Markdown 稿件
```

## ⚠️ 硬性约束

- 严禁在长文档或带表格场景下由 AI 直接通过口头描述还原 MD。
- 必须通过“JSON 落地 -> 脚本编译”的链路产出文件。
