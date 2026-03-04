#!/usr/bin/env python3
"""
Generate memory/index.md from the contents of the memory/ directory.
Scans all .md files, extracts first heading and date info, builds a searchable index.

Usage: python3 scripts/generate-memory-index.py
"""

import os
import re
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("/root/.openclaw/workspace/memory")
INDEX_FILE = MEMORY_DIR / "index.md"

# Files to skip (not useful to index)
SKIP_FILES = {"index.md", "context-engine-design.md"}

def extract_first_heading(filepath):
    """Get the first markdown heading from a file."""
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
                if line.startswith('## '):
                    return line[3:].strip()
        return filepath.stem
    except Exception:
        return filepath.stem

def extract_topics(filepath):
    """Extract key topics from ## headings in a file."""
    topics = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('## ') and len(topics) < 5:
                    heading = line[3:].strip()
                    # Skip generic headings
                    if heading.lower() not in ('overview', 'summary', 'notes', 'context', 'references'):
                        # Clean up heading
                        heading = re.sub(r'\s*[-—]\s*.*$', '', heading)  # Remove date suffixes
                        if len(heading) > 50:
                            heading = heading[:47] + "..."
                        topics.append(heading)
    except Exception:
        pass
    return topics

def get_file_date(filepath):
    """Extract date from filename (YYYY-MM-DD.md) or use mtime."""
    # Check for date in filename
    match = re.match(r'(\d{4}-\d{2}-\d{2})', filepath.name)
    if match:
        return match.group(1)
    # Fall back to modification time
    mtime = os.path.getmtime(filepath)
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

def categorize_file(filepath):
    """Categorize a file based on its path and content."""
    name = filepath.name.lower()

    if re.match(r'\d{4}-\d{2}-\d{2}\.md', name):
        return "daily"
    if 'draft' in str(filepath) or filepath.parent.name == 'content-drafts':
        return "draft"
    if any(kw in name for kw in ['research', 'analysis', 'brainstorm', 'report', 'summary', 'competitive', 'ideas']):
        return "research"
    if any(kw in name for kw in ['strategy', 'plan', 'prd', 'architecture', 'proposal']):
        return "strategy"
    if any(kw in name for kw in ['template', 'guide', 'prompt-pack']):
        return "template"
    return "reference"

def generate_index():
    """Scan memory/ and generate index.md."""
    files = {}

    for filepath in sorted(MEMORY_DIR.rglob("*.md")):
        if filepath.name in SKIP_FILES:
            continue
        if filepath == INDEX_FILE:
            continue

        rel_path = filepath.relative_to(MEMORY_DIR)
        category = categorize_file(filepath)
        date = get_file_date(filepath)
        title = extract_first_heading(filepath)
        topics = extract_topics(filepath)

        if category not in files:
            files[category] = []

        files[category].append({
            'path': str(rel_path),
            'title': title,
            'date': date,
            'topics': topics,
        })

    # Sort each category by date descending
    for cat in files:
        files[cat].sort(key=lambda x: x['date'], reverse=True)

    # Build the index
    lines = []
    lines.append(f"# Memory Index")
    lines.append(f"Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"")
    lines.append(f"Search this index first. Read only the specific file you need.")
    lines.append(f"")

    category_order = ['daily', 'research', 'strategy', 'draft', 'template', 'reference']
    category_labels = {
        'daily': 'Daily Logs',
        'research': 'Research & Analysis',
        'strategy': 'Strategy & Plans',
        'draft': 'Content Drafts',
        'template': 'Templates & Guides',
        'reference': 'Reference',
    }

    for cat in category_order:
        if cat not in files:
            continue

        lines.append(f"## {category_labels[cat]}")
        lines.append(f"")
        lines.append(f"| Date | Title | Key Topics | File |")
        lines.append(f"|------|-------|-----------|------|")

        for f in files[cat]:
            topics_str = ", ".join(f['topics'][:3]) if f['topics'] else ""
            lines.append(f"| {f['date']} | {f['title']} | {topics_str} | `{f['path']}` |")

        lines.append(f"")

    # Write it
    with open(INDEX_FILE, 'w') as out:
        out.write('\n'.join(lines))

    total = sum(len(v) for v in files.values())
    print(f"Generated memory/index.md: {total} files indexed across {len(files)} categories")

if __name__ == '__main__':
    generate_index()
