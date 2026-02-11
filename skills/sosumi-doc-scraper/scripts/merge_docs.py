import os
import re

ROOT_DIR = "FoundationModels"
OUTPUT_FILE = "Sosumi_Full_Documentation.md"

def read_file(filepath):
    """Read file content and strip frontmatter if present."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return ""
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove YAML frontmatter (--- ... ---)
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    return content.strip()

def main():
    intro_path = os.path.join(ROOT_DIR, "Introduction.md")
    if not os.path.exists(intro_path):
        print("Error: Introduction.md not found in FoundationModels directory.")
        return

    print("Reading index...")
    index_content = read_file(intro_path)
    
    merged_content = []
    
    # Add Title
    merged_content.append("# Sosumi.ai Foundation Models Documentation\n")
    
    # Process the index line by line to maintain order
    lines = index_content.splitlines()
    
    current_section = "Uncategorized"
    
    for line in lines:
        line = line.strip()
        
        # Detect Section Header
        if line.startswith('## '):
            current_section = line[3:].strip()
            merged_content.append(f"\n\n## {current_section}\n")
            print(f"Processing Section: {current_section}")
            continue
            
        # Detect Links: - [Title](url) or * [Title](url) or [Title](url)
        # Matches [Title](link)
        match = re.search(r'\[([^\]]+)\]\((.+)\)', line)
        if match:
            title = match.group(1)
            link = match.group(2)
            
            # Extract filename from link
            # Link might be full URL or relative
            # We assume the download script naming convention: 
            # FoundationModels/{current_section_clean}/{filename}
            
            # Clean section name like in download script
            section_clean = re.sub(r'[<>:"/\\|?*]', '', current_section).strip()
            
            # Extract filename from the URL part of the link
            # The download script used urlparse(full_url).path then basename
            # Here link is likely "/documentation/..."
            filename = link.split('/')[-1]
            if not filename.endswith('.md'):
                filename += '.md'
            
            # Construct local path
            # Try specific section folder first
            file_path = os.path.join(ROOT_DIR, section_clean, filename)
            
            # If not found, try root (Introduction is there, maybe others)
            if not os.path.exists(file_path):
                file_path = os.path.join(ROOT_DIR, filename)
            
            if os.path.exists(file_path):
                print(f"  Merging: {filename}")
                file_content = read_file(file_path)
                
                # Add a sub-header using the link title if the file doesn't start with a header
                if not file_content.strip().startswith('#'):
                     merged_content.append(f"\n### {title}\n")
                
                merged_content.append(file_content)
                merged_content.append("\n\n---\n") # Separator
            else:
                print(f"  MISSING: {file_path}")

    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(merged_content))
    
    print("Done.")

if __name__ == "__main__":
    main()
