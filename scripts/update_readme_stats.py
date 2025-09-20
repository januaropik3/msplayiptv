#!/usr/bin/env python3
"""
Update README.md with current statistics
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone

def load_stats():
    """Load statistics from stats.json"""
    stats_file = Path("static/stats.json")
    if not stats_file.exists():
        return None
    
    with open(stats_file, 'r') as f:
        return json.load(f)

def update_readme_badges(readme_content, stats):
    """Update badges in README with current stats"""
    if not stats:
        return readme_content
    
    total_channels = stats.get('total_channels', 0)
    updated_date = stats.get('generated_at', '')
    
    if updated_date:
        try:
            # Parse ISO format and convert to readable date
            dt = datetime.fromisoformat(updated_date.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
        except:
            date_str = updated_date[:10]  # Fallback to first 10 chars
    else:
        date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Update or add badges
    badge_updates = {
        r'!\[Channels\]\([^)]*\)': f'![Channels](https://img.shields.io/badge/Channels-{total_channels:,}-brightgreen)',
        r'!\[Updated\]\([^)]*\)': f'![Updated](https://img.shields.io/badge/Updated-{date_str}-blue)',
        r'!\[Status\]\([^)]*\)': '![Status](https://img.shields.io/badge/Status-Active-success)',
        r'!\[Format\]\([^)]*\)': '![Format](https://img.shields.io/badge/Format-M3U-orange)'
    }
    
    for pattern, replacement in badge_updates.items():
        if re.search(pattern, readme_content):
            readme_content = re.sub(pattern, replacement, readme_content)
        else:
            # If badge doesn't exist, add it after the title
            title_pattern = r'(# MSPlay IPTV.*?\n)'
            if re.search(title_pattern, readme_content):
                readme_content = re.sub(
                    title_pattern,
                    f'\\1\n{replacement}\n',
                    readme_content
                )
    
    return readme_content

def update_stats_table(readme_content, stats):
    """Update statistics table in README"""
    if not stats:
        return readme_content
    
    # Create stats table
    table_content = """
## 📊 Statistics

| Metric | Value |
|--------|-------|
| 📺 Total Channels | {:,} |
| 🏷️ Categories | {} |
| 🌍 Sources | {} |
| 🕐 Last Updated | {} |

### 📁 Categories

| Category | Channels |
|----------|----------|
""".format(
        stats.get('total_channels', 0),
        len(stats.get('categories', {})),
        len(stats.get('sources', [])),
        stats.get('generated_at', 'Unknown')[:19].replace('T', ' ')
    )
    
    # Add category breakdown
    categories = stats.get('categories', {})
    for category, count in sorted(categories.items()):
        table_content += f"| {category} | {count:,} |\n"
    
    # Replace existing stats section or add new one
    stats_pattern = r'## 📊 Statistics.*?(?=##|\Z)'
    if re.search(stats_pattern, readme_content, re.DOTALL):
        readme_content = re.sub(stats_pattern, table_content.strip(), readme_content, flags=re.DOTALL)
    else:
        # Add stats section before usage section
        usage_pattern = r'(## 🚀 Usage)'
        if re.search(usage_pattern, readme_content):
            readme_content = re.sub(usage_pattern, f'{table_content}\n\\1', readme_content)
        else:
            readme_content += f'\n{table_content}'
    
    return readme_content

def main():
    """Main function"""
    readme_file = Path("README.md")
    
    if not readme_file.exists():
        print("README.md not found, skipping stats update")
        return
    
    # Load current stats
    stats = load_stats()
    if not stats:
        print("No stats found, skipping README update")
        return
    
    # Read current README
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update README
    content = update_readme_badges(content, stats)
    content = update_stats_table(content, stats)
    
    # Write updated README
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated README.md with {stats.get('total_channels', 0):,} channels")

if __name__ == "__main__":
    main()