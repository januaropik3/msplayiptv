"""
Data models for MSPlay IPTV
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class ChannelCategory(Enum):
    """Channel categories"""
    KIDS = "Kids"
    MOVIES = "Movies"
    SPORTS = "Sports"
    NEWS = "News"
    MUSIC = "Music"
    ENTERTAINMENT = "Entertainment"
    DOCUMENTARY = "Documentary"
    GENERAL = "General"

@dataclass
class Channel:
    """Channel data model"""
    name: str
    url: str
    category: Optional[ChannelCategory] = None
    country: Optional[str] = None
    logo: Optional[str] = None
    group_title: Optional[str] = None
    language: Optional[str] = None
    extinf_line: Optional[str] = None
    
    @property
    def m3u_entry(self) -> str:
        """Generate M3U entry for this channel"""
        if self.extinf_line:
            # Use existing EXTINF line but ensure group-title is set
            extinf = self.extinf_line
            if self.category and 'group-title=' not in extinf.lower():
                # Add group-title
                parts = extinf.split(',', 1)
                if len(parts) == 2:
                    extinf = f'{parts[0]} group-title="{self.category.value}",{parts[1]}'
        else:
            # Create new EXTINF line
            extinf = f'#EXTINF:-1'
            if self.category:
                extinf += f' group-title="{self.category.value}"'
            if self.logo:
                extinf += f' tvg-logo="{self.logo}"'
            extinf += f',{self.name}'
            if self.country:
                extinf += f' [{self.country}]'
        
        return f"{extinf}\n{self.url}"

@dataclass
class ValidationResult:
    """Result of channel validation"""
    channel: Channel
    is_valid: bool
    reason: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None

@dataclass
class ScrapingStats:
    """Statistics for scraping operation"""
    total_sources: int = 0
    successful_sources: int = 0
    total_channels: int = 0
    channels_by_category: Dict[str, int] = None
    
    def __post_init__(self):
        if self.channels_by_category is None:
            self.channels_by_category = {}

@dataclass
class ValidationStats:
    """Statistics for validation operation"""
    total_checked: int = 0
    valid_channels: int = 0
    invalid_channels: int = 0
    success_rate: float = 0.0
    total_time: float = 0.0
    channels_per_second: float = 0.0
    
    def update(self):
        """Update calculated fields"""
        if self.total_checked > 0:
            self.success_rate = (self.valid_channels / self.total_checked) * 100
        if self.total_time > 0:
            self.channels_per_second = self.total_checked / self.total_time