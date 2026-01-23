#!/usr/bin/env python3
import json
import sys
import os
import subprocess

def find_block_id(json_file, query):
    """
    调用 mistj-notion-exporter 中的 find_block.py 来查找对应的 block_id
    """
    # 获取当前脚本所在目录，确保找到同目录下的 find_block.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    finder_script = os.path.join(script_dir, "find_block.py")
    try:
        result = subprocess.run(
            ["python3", finder_script, json_file, query],
            capture_output=True,
            text=True,
            check=True
        )
        matches = json.loads(result.stdout)
        if matches and len(matches) > 0:
            # 返回分值最高的一个
            return matches[0]["id"]
    except Exception as e:
        print(f"Error finding block for '{query}': {e}", file=sys.stderr)
    return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 integrate_notion_blocks.py <raw.json> <outline.md>")
        sys.exit(1)

    json_file = sys.argv[1]
    outline_file = sys.argv[2]

    if not os.path.exists(json_file) or not os.path.exists(outline_file):
        print("Error: Files not found.")
        sys.exit(1)

    with open(outline_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 简单的解析 outline.md 中的插图位置
    # 查找模式: ## Illustration X ... **Insert Position**: [position] ... **Filename**: [filename]
    import re
    illustrations = []
    
    # 提取 Illustration 块
    blocks = re.split(r'---', content)
    for b in blocks:
        pos_match = re.search(r'\*\*Insert Position\*\*:\s*(.*)', b)
        file_match = re.search(r'\*\*Filename\*\*:\s*(.*)', b)
        
        if pos_match and file_match:
            pos_text = pos_match.group(1).strip()
            filename = file_match.group(1).strip()
            
            # 这里的 pos_text 可能是 "Heading Name / Paragraph Description"
            # 我们取前半部分或者完整的作为 Query
            query = pos_text.split('/')[-1].strip() if '/' in pos_text else pos_text
            
            block_id = find_block_id(json_file, query)
            
            illustrations.append({
                "position_text": pos_text,
                "query": query,
                "filename": filename,
                "matched_block_id": block_id
            })

    print(json.dumps(illustrations, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
