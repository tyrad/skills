#!/usr/bin/env python3
import json
import sys
import os
import re
import copy

def split_rich_text(rich_text, query):
    """
    在 rich_text 数组中搜索 query 字符串，并将其分割为两个 rich_text 数组。
    分割点位于 query 匹配内容的末尾。
    """
    # 提取所有文本用于匹配位置
    full_text = "".join([t.get("plain_text", "") for t in rich_text])
    
    # 搜索 query
    match = re.search(re.escape(query), full_text)
    if not match:
        return rich_text, None
    
    split_pos = match.end()
    
    part_a = []
    part_b = []
    current_pos = 0
    
    for item in rich_text:
        item_text = item.get("plain_text", "")
        item_len = len(item_text)
        
        if current_pos + item_len <= split_pos:
            # 整个条目都在分割点前
            part_a.append(item)
        elif current_pos >= split_pos:
            # 整个条目都在分割点后
            part_b.append(item)
        else:
            # 分割点在这个条目中间
            offset = split_pos - current_pos
            
            # 克隆并分割条目内容
            item_a = copy.deepcopy(item)
            item_b = copy.deepcopy(item)
            
            # 找到文本具体内容所在的 key (通常是 'text' 或 'mention' 等)
            text_type = item.get("type", "text")
            if text_type in item:
                content = item[text_type].get("content", "")
                if not content and text_type == "text":
                    content = item[text_type].get("text", {}).get("content", "") # 容错处理
                
                item_a[text_type]["content"] = content[:offset]
                item_b[text_type]["content"] = content[offset:]
                
                # 修正 plain_text
                if "plain_text" in item_a: item_a["plain_text"] = item_text[:offset]
                if "plain_text" in item_b: item_b["plain_text"] = item_text[offset:]
            
            if item_a.get(text_type, {}).get("content"):
                part_a.append(item_a)
            if item_b.get(text_type, {}).get("content"):
                part_b.append(item_b)
                
        current_pos += item_len
        
    return part_a, part_b

def generate_surgical_plan(raw_json_path, outline_md_path, illustrations_info):
    """
    根据大纲规划和原始数据，生成一个详细的 patch 方案。
    illustrations_info: 一个列表，包含 { "query": "xxx", "image_url": "yyy" }
    """
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    blocks = raw_data.get("results", [])
    page_id = raw_data.get("notion_page_id")
    
    plan = []
    
    for info in illustrations_info:
        query = info["query"]
        image_url = info["image_url"]
        
        # 查找包含 query 的 block
        target_block = None
        supported_types = ["paragraph", "quote", "heading_1", "heading_2", "heading_3", "numbered_list_item", "bulleted_list_item"]
        for b in blocks:
            b_type = b.get("type")
            if b_type in supported_types:
                rich_text = b.get(b_type, {}).get("rich_text", [])
                full_text = "".join([t.get("plain_text", "") for t in rich_text])
                if query in full_text:
                    target_block = b
                    break
        
        if not target_block:
            print(f"Warning: Could not find block for query: {query}")
            continue
            
        # 执行切割
        b_type = target_block["type"]
        original_rich_text = target_block[b_type]["rich_text"]
        part_a, part_b = split_rich_text(original_rich_text, query)
        
        if part_b:
            # 需要切割的情况
            plan.append({
                "action": "surgical_split",
                "target_block_id": target_block["id"],
                "target_block_type": b_type,
                "update_original_with": part_a,
                "insert_after": [
                    { "type": "image", "image": { "type": "external", "external": { "url": image_url } } },
                    { "type": b_type, b_type: { "rich_text": part_b } }
                ]
            })
        else:
            # 刚好在段落末尾的情况
            plan.append({
                "action": "simple_insert",
                "after_block_id": target_block["id"],
                "insert_after": [
                    { "type": "image", "image": { "type": "external", "external": { "url": image_url } } }
                ]
            })
            
    return plan

if __name__ == "__main__":
    # 该脚本可以作为工具函数导入，也可以扩展为命令行工具
    pass
