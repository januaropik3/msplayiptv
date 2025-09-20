"""
M3U File Generator and Manager
"""
from typing import List, Dict
from pathlib import Path
import logging
from datetime import datetime, timezone

from .models import Channel, ChannelCategory
from .utils import ensure_directory, format_number
from .config import config

logger = logging.getLogger(__name__)

class M3UGenerator:
    """Generate M3U playlist files"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or config.OUTPUT_DIR)
        ensure_directory(self.output_dir)
    
    def generate_m3u(self, channels: List[Channel], filename: str = None) -> Path:
        """Generate M3U file from channels"""
        filename = filename or config.OUTPUT_FILE
        output_path = self.output_dir / filename
        
        # Group channels by category
        channels_by_category = self._group_channels_by_category(channels)
        
        # Generate M3U content
        content = self._generate_m3u_content(channels_by_category, len(channels))
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Generated M3U file: {output_path}")
        logger.info(f"📊 Total channels: {format_number(len(channels))}")
        
        return output_path
    
    def _group_channels_by_category(self, channels: List[Channel]) -> Dict[ChannelCategory, List[Channel]]:
        """Group channels by category"""
        grouped = {}
        
        for channel in channels:
            category = channel.category or ChannelCategory.GENERAL
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(channel)
        
        # Sort channels within each category
        for category in grouped:
            grouped[category].sort(key=lambda x: x.name.lower())
        
        return grouped
    
    def _generate_m3u_content(self, channels_by_category: Dict[ChannelCategory, List[Channel]], 
                            total_count: int) -> str:
        """Generate M3U file content"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        lines = [
            "#EXTM3U",
            "",
            f"# MSPlay IPTV Playlist",
            f"# Generated: {timestamp}",
            f"# Total Channels: {format_number(total_count)}",
            f"# Categories: {len(channels_by_category)}",
            f"# Source: https://github.com/januaropik3/msplayiptv",
            "",
        ]
        
        # Add channels by category
        for category in sorted(channels_by_category.keys(), key=lambda x: x.value):
            channels = channels_by_category[category]
            
            lines.extend([
                f"# ====== {category.value.upper()} ({len(channels)} channels) ======",
                ""
            ])
            
            for channel in channels:
                lines.append(channel.m3u_entry)
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_category_files(self, channels: List[Channel]) -> Dict[str, Path]:
        """Generate separate M3U files for each category"""
        channels_by_category = self._group_channels_by_category(channels)
        generated_files = {}
        
        for category, category_channels in channels_by_category.items():
            if not category_channels:
                continue
            
            filename = f"msplay_{category.value.lower()}.m3u"
            content = self._generate_m3u_content({category: category_channels}, len(category_channels))
            
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            generated_files[category.value] = output_path
            logger.info(f"✅ Generated {category.value} file: {output_path}")
        
        return generated_files
    
    def generate_stats_json(self, channels: List[Channel]) -> Path:
        """Generate JSON file with statistics"""
        import json
        
        channels_by_category = self._group_channels_by_category(channels)
        
        stats = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_channels": len(channels),
            "categories": {
                category.value: len(category_channels)
                for category, category_channels in channels_by_category.items()
            },
            "sources": list(set(ch.country for ch in channels if ch.country)),
            "playlist_url": f"https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/{config.OUTPUT_FILE}"
        }
        
        stats_path = self.output_dir / "stats.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"✅ Generated stats file: {stats_path}")
        return stats_path

def generate_playlist(channels: List[Channel], 
                     output_dir: str = None,
                     filename: str = None,
                     generate_categories: bool = False,
                     generate_stats: bool = True) -> Dict[str, Path]:
    """Main function to generate playlist files"""
    generator = M3UGenerator(output_dir)
    
    generated_files = {}
    
    # Generate main playlist
    main_file = generator.generate_m3u(channels, filename)
    generated_files["main"] = main_file
    
    # Generate category files if requested
    if generate_categories:
        category_files = generator.generate_category_files(channels)
        generated_files.update(category_files)
    
    # Generate stats file if requested
    if generate_stats:
        stats_file = generator.generate_stats_json(channels)
        generated_files["stats"] = stats_file
    
    return generated_files