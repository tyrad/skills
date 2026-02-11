import os
import re
import sys
import ssl
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse

# Bypass SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://sosumi.ai/documentation/FoundationModels"
DOMAIN = "https://sosumi.ai"

def clean_filename(name):
    """Sanitize filename."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def download_content(url):
    """Fetch content from URL."""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
        )
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def download_file(url, filepath):
    """Download a single file."""
    print(f"Downloading {url} -> {filepath}...")
    content = download_content(url)
    if content:
        # Simple check if it looks like HTML error page
        if "<!DOCTYPE html>" in content[:100] and "404" in content:
             print(f"WARNING: {url} served HTML likely error, saving anyway.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  Success.")
    else:
        print("  FAILED: No content.")

def main():
    root_dir = "FoundationModels"
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    print(f"Fetching index from {BASE_URL}...")
    index_content = download_content(BASE_URL)
    
    if not index_content:
        print("Critical: Could not fetch index.")
        sys.exit(1)

    # Save the index page itself
    with open(os.path.join(root_dir, "Introduction.md"), 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    current_section = "Uncategorized"
    
    # Simple line-by-line parser for the specific Markdown structure
    lines = index_content.splitlines()
    for line in lines:
        line = line.strip()
        
        # Detect Section Header (Level 2)
        if line.startswith('## '):
            section_name = line[3:].strip()
            current_section = clean_filename(section_name)
            # Create directory for section
            section_path = os.path.join(root_dir, current_section)
            if not os.path.exists(section_path):
                os.makedirs(section_path)
            print(f"\nFound Section: {current_section}")
            continue
            
        # Detect Links: - [Title](url) or * [Title](url)
        # Regex to capture [Title] and (url) - using greedy match for URL to handle parentheses
        match = re.search(r'\[([^\]]+)\]\((.+)\)', line)
        if match:
            # title = match.group(1) 
            link = match.group(2)
            
            # Sanitize link (in case of trailing whitespace or content after last paren)
            link = link.strip()
            
            # Form absolute URL
            full_url = urljoin(DOMAIN, link)
            
            # Determine filename from URL path
            path = urlparse(full_url).path
            filename = os.path.basename(path)
            if not filename.endswith('.md'):
                filename += '.md'
            
            # If section folder doesn't exist (link found before any H2), put in root
            target_dir = os.path.join(root_dir, current_section)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            filepath = os.path.join(target_dir, filename)
            
            download_file(full_url, filepath)

    print("\nDownload complete.")

if __name__ == "__main__":
    main()
