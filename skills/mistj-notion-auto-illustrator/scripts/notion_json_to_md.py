#!/usr/bin/env python3
import json
import sys
import os

# =================================================================
# Notion MCP 数据解析器 - 混合动力版
# 职责：专注将 MCP 抓取的 JSON 物理还原为 Markdown
# =================================================================

class MCPNotionParser:
    def __init__(self):
        pass

    def rich_text_to_md(self, rich_text_list):
        md = ""
        for rt in rich_text_list:
            r_type = rt.get("type")
            content = rt.get("plain_text", "")
            
            if r_type == "equation":
                content = f"${rt['equation']['expression']}$"
            elif r_type == "mention":
                m_type = rt["mention"]["type"]
                if m_type == "page":
                    page_id = rt["mention"]["page"]["id"].replace("-", "")
                    content = f"[{content}](https://www.notion.so/{page_id})"
                elif m_type == "date":
                    content = f"📅 {rt['mention']['date']['start']}"

            anno = rt.get("annotations", {})
            if anno.get("bold"): content = f"**{content}**"
            if anno.get("italic"): content = f"*{content}*"
            if anno.get("code"): content = f"`{content}`"
            if anno.get("strikethrough"): content = f"~~{content}~~"
            
            # 处理颜色和高亮 (Color & Highlight)
            color = anno.get("color", "default")
            if color != "default":
                if "_background" in color:
                    # 将橙色背景等还原为高亮标签
                    content = f"<mark>{content}</mark>"
                else:
                    # 普通文字颜色
                    clean_color = color.replace("_", "")
                    content = f"<span style='color:{clean_color}'>{content}</span>"
            
            link = rt.get("link")
            if link:
                md += f"[{content}]({link['url']})"
            else:
                md += content
        return md

    def parse_blocks(self, blocks, depth=0):
        """解析 Block 列表，支持嵌套结果"""
        md = ""
        indent = "    " * depth

        for block in blocks:
            b_type = block["type"]
            
            if b_type.startswith("heading_"):
                level = b_type.split("_")[1]
                md += f"{'#' * int(level)} {self.rich_text_to_md(block[b_type]['rich_text'])}\n\n"
            
            elif b_type == "paragraph":
                md += f"{self.rich_text_to_md(block['paragraph']['rich_text'])}\n\n"
            
            elif b_type in ["bulleted_list_item", "numbered_list_item"]:
                prefix = "*" if b_type == "bulleted_list_item" else "1."
                md += f"{indent}{prefix} {self.rich_text_to_md(block[b_type]['rich_text'])}\n"
            
            elif b_type == "to_do":
                checked = "x" if block["to_do"]["checked"] else " "
                md += f"{indent}* [{checked}] {self.rich_text_to_md(block['to_do']['rich_text'])}\n"
            
            elif b_type == "quote":
                md += f"> {self.rich_text_to_md(block['quote']['rich_text'])}\n\n"
            
            elif b_type == "callout":
                icon = ""
                if block["callout"].get("icon") and block["callout"]["icon"]["type"] == "emoji":
                    icon = block["callout"]["icon"]["emoji"] + " "
                md += f"> {icon}{self.rich_text_to_md(block['callout']['rich_text'])}\n\n"
            
            elif b_type == "divider":
                md += "--- \n\n"
            
            elif b_type == "code":
                txt = self.rich_text_to_md(block["code"]["rich_text"])
                md += f"```{block['code']['language']}\n{txt}\n```\n\n"
            
            elif b_type in ["image", "video", "file", "pdf"]:
                info = block[b_type]
                url = info[info["type"]]["url"]
                prefix = "![Image]" if b_type == "image" else f"📎 [{b_type.upper()}]"
                md += f"{prefix}({url})\n\n"
            
            elif b_type == "table":
                # 🛡️ 安全处理：由于单次 MCP 请求不包含表格行，这里预留位置
                md += f"\n[TABLE_PLACEHOLDER: {block['id']}]\n\n"
            
            elif b_type == "table_row":
                # 如果输入的是表格行的 JSON，则处理单元格
                cells = [self.rich_text_to_md(c) for c in block["table_row"]["cells"]]
                md += "| " + " | ".join(cells) + " |\n"

            # 递归处理本地已有的子 Block (如果 AI 手动拼接了数据)
            if block.get("children"):
                md += self.parse_blocks(block["children"], depth + 1)
        
        return md

import argparse

def main():
    parser = argparse.ArgumentParser(description="Notion MCP JSON to Markdown Parser")
    parser.add_argument("input", help="Path to the input JSON file")
    parser.add_argument("-o", "--output", help="Path to the output Markdown file")
    
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        blocks = data.get("results", data) if isinstance(data, dict) else data
        
        parser_obj = MCPNotionParser()
        result = parser_obj.parse_blocks(blocks)
        
        if isinstance(data, dict) and data.get("has_more"):
            print(f"<!-- WARNING: ARTICLE_NOT_COMPLETE. Next Cursor: {data.get('next_cursor')} -->\n", file=sys.stderr)
        
        if args.output:
            # 自动创建父目录
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ Markdown saved to: {args.output}")
        else:
            print(result)
        
    except Exception as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
