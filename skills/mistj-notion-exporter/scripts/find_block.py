#!/usr/bin/env python3
import json
import sys
import os
import re

class BlockLocator:
    def __init__(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.blocks = data.get("results", data) if isinstance(data, dict) else data
        self.flat_list = []
        self._flatten(self.blocks)

    def _extract_text(self, block):
        """从各种类型的 Block 中提取纯文本"""
        b_type = block.get("type")
        if not b_type: return ""
        
        # 处理大部分带有 rich_text 的块
        content_data = block.get(b_type, {})
        if isinstance(content_data, dict) and "rich_text" in content_data:
            return "".join([rt.get("plain_text", "") for rt in content_data["rich_text"]])
        
        # 处理 table_row
        if b_type == "table_row":
            return " | ".join(["".join([c.get("plain_text", "") for c in cell]) for cell in content_data.get("cells", [])])
        
        return ""

    def _flatten(self, blocks, parent_info="Root"):
        """递归平铺所有块，建立索引"""
        for i, block in enumerate(blocks):
            text = self._extract_text(block)
            b_id = block.get("id", "no-id")
            b_type = block.get("type", "unknown")
            
            self.flat_list.append({
                "id": b_id,
                "type": b_type,
                "text": text,
                "index": i,
                "parent": parent_info
            })
            
            if block.get("children"):
                self._flatten(block["children"], parent_info=f"{b_type}({b_id[:8]})")

    def find(self, query, b_type=None, limit=5):
        """搜索逻辑：支持关键词匹配、类型过滤"""
        results = []
        query = query.lower().strip()
        
        for item in self.flat_list:
            if b_type and item["type"] != b_type:
                continue
            
            text = item["text"].lower()
            # 基础匹配得分：完全包含 > 部分匹配
            score = 0
            if query in text:
                score = 100
            elif any(word in text for word in query.split()):
                score = 50
                
            if score > 0:
                results.append((score, item))
        
        # 按得分排序
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:limit]

def main():
    if len(sys.argv) < 3:
        print("Usage: python find_block.py <raw.json> <query_text> [block_type]")
        sys.exit(1)

    json_file = sys.argv[1]
    query = sys.argv[2]
    target_type = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(json_file):
        print(f"Error: File {json_file} not found.")
        sys.exit(1)

    locator = BlockLocator(json_file)
    matches = locator.find(query, b_type=target_type)

    if not matches:
        print(f"No blocks found matching: '{query}'")
        return

    print(json.dumps([
        {
            "id": m[1]["id"],
            "type": m[1]["type"],
            "text_preview": (m[1]["text"][:50] + "...") if len(m[1]["text"]) > 50 else m[1]["text"],
            "score": m[0]
        } for m in matches
    ], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
