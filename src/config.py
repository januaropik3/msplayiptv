"""
Configuration module for MSPlay IPTV
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration"""
    
    # M3U sources
    M3U_SOURCES: Dict[str, str] = None
    
    # Target categories to include
    TARGET_CATEGORIES: List[str] = None
    
    # Output settings
    OUTPUT_FILE: str = "msplay.m3u"
    OUTPUT_DIR: str = "static"
    
    # Validation settings
    MAX_WORKERS: int = 50
    TIMEOUT: int = 10
    AUTOSAVE_INTERVAL: int = 30
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    def __post_init__(self):
        if self.M3U_SOURCES is None:
            self.M3U_SOURCES = {
                "DrewLive": "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/MergedPlaylist.m3u8",
                "Free-TV": "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8",
                "iptv-org": "https://raw.githubusercontent.com/iptv-org/iptv/master/streams.m3u",
                "Free-IPTV": "https://raw.githubusercontent.com/davidmuma/Canales_dobleM/master/TDT_list.m3u8"
            }
        
        if self.TARGET_CATEGORIES is None:
            self.TARGET_CATEGORIES = [
                "Kids", "Movies", "Sports", "News", "Music", 
                "Entertainment", "Documentary", "General"
            ]

# Global config instance
config = Config()