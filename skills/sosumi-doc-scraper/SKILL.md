---
name: sosumi-doc-scraper
description: A specialized skill to crawl, download, and merge documentation from Sosumi.ai into a single consolidated Markdown file for easy reading or PDF conversion. Use this when you need offline access to Sosumi documentation or want to print it.
---

# Sosumi Documentation Scraper

This skill automates the process of fetching the latest documentation from [Sosumi.ai](https://sosumi.ai) and combining it into a single, cohesive document.

## Overview

The skill provides two main scripts:

1.  **Download**: Recursively fetches Markdown files based on the `FoundationModels` index structure.
2.  **Merge**: Combines the downloaded files into one `Sosumi_Full_Documentation.md`.

## Usage

### 1. Download Documentation

Run the `download_docs.py` script. This will create a `FoundationModels` directory in your current working directory and populate it with the documentation structure.

```bash
python3 scripts/download_docs.py
```

_Note: The script automatically handles SSL bypass and User-Agent headers to ensure successful downloads._

### 2. Verify Downloads (Optional)

You can verify that all files linked in the index were successfully downloaded.

```bash
# (Optional) Verify completeness
python3 scripts/verify_downloads.py
```

### 3. Merge into Single File

Run the `merge_docs.py` script to combine everything.

```bash
python3 scripts/merge_docs.py
```

This will generate **`Sosumi_Full_Documentation.md`** in your current directory.

## Output

The final output is a clean Markdown file starting with `Introduction.md` and following the order defined in the documentation index. It is suitable for:

- Importing into knowledge bases (Obsidian, Notion).
- Converting to PDF (via VS Code, Typora, or browser print).
- Feeding into LLMs for RAG (Retrieval-Augmented Generation).

## Scripts Reference

### `scripts/download_docs.py`

- **Dependencies**: Standard library (`urllib`, `re`, `ssl`).
- **Logic**:
  - Fetches `https://sosumi.ai/documentation/FoundationModels`.
  - Parses H2 headers for directory structure.
  - Downloads linked MD files.

### `scripts/merge_docs.py`

- **Dependencies**: Standard library (`os`, `re`).
- **Logic**:
  - Reads the index file to determine correct chapter order.
  - Concatenates files, stripping YAML frontmatter.
  - Adds chapter separators.
