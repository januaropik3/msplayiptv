"""
Utilities for MSPlay IPTV
"""
import re
import time
import requests
from typing import Optional, Tuple, List
from pathlib import Path
import logging

from .models import Channel, ChannelCategory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CategoryExtractor:
    """Extract categories from channel names and URLs"""
    
    CATEGORY_KEYWORDS = {
        ChannelCategory.SPORTS: [
            'sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 'boxing',
            'mma', 'ufc', 'espn', 'fox_sport', 'bein', 'eurosport', 'sky_sport',
            'nba', 'nfl', 'fifa', 'olympics', 'motor', 'racing', 'f1'
        ],
        ChannelCategory.NEWS: [
            'news', 'cnn', 'bbc', 'fox_news', 'msnbc', 'cnbc', 'bloomberg',
            'reuters', 'aljazeera', 'dw', 'france24', 'rt', 'sky_news',
            'headline', 'breaking', 'world_news'
        ],
        ChannelCategory.MOVIES: [
            'movie', 'cinema', 'film', 'hbo', 'netflix', 'prime', 'disney',
            'paramount', 'universal', 'warner', 'fox_movie', 'cinemax',
            'starz', 'showtime', 'action', 'thriller', 'drama', 'comedy'
        ],
        ChannelCategory.KIDS: [
            'kids', 'child', 'cartoon', 'disney', 'nickelodeon', 'nick_jr',
            'cartoon_network', 'boomerang', 'baby_tv', 'junior', 'family',
            'animated', 'children'
        ],
        ChannelCategory.MUSIC: [
            'music', 'mtv', 'vh1', 'vevo', 'radio', 'concert', 'karaoke',
            'youtube_music', 'hits', 'pop', 'rock', 'jazz', 'classical'
        ],
        ChannelCategory.ENTERTAINMENT: [
            'entertainment', 'variety', 'talk_show', 'reality', 'lifestyle',
            'cooking', 'travel', 'fashion', 'game_show', 'comedy_central'
        ],
        ChannelCategory.DOCUMENTARY: [
            'documentary', 'discovery', 'national_geographic', 'history',
            'science', 'nature', 'wildlife', 'biography', 'investigation'
        ]
    }
    
    @classmethod
    def extract_category(cls, channel_name: str, channel_url: str = "") -> Optional[ChannelCategory]:
        """Extract category from channel name and URL"""
        text_to_analyze = f"{channel_name} {channel_url}".lower()
        
        # Check keywords
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                keyword_variants = [
                    keyword.replace('_', ' '),
                    keyword.replace('_', ''),
                    keyword
                ]
                
                for variant in keyword_variants:
                    if variant in text_to_analyze:
                        return category
        
        # URL pattern matching
        url_patterns = {
            ChannelCategory.SPORTS: [r'sport', r'football', r'soccer', r'basket'],
            ChannelCategory.NEWS: [r'news', r'cnn', r'bbc', r'fox'],
            ChannelCategory.MOVIES: [r'movie', r'cinema', r'film', r'hbo'],
            ChannelCategory.KIDS: [r'kids', r'child', r'cartoon', r'disney'],
            ChannelCategory.MUSIC: [r'music', r'mtv', r'radio'],
            ChannelCategory.ENTERTAINMENT: [r'entertainment', r'variety'],
            ChannelCategory.DOCUMENTARY: [r'discovery', r'documentary', r'history']
        }
        
        for category, patterns in url_patterns.items():
            for pattern in patterns:
                if re.search(pattern, channel_url, re.IGNORECASE):
                    return category
        
        # Default to General if no specific category found
        return ChannelCategory.GENERAL

class StreamValidator:
    """Validate stream URLs"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Connection': 'close'
        })
    
    def validate_stream(self, url: str) -> Tuple[bool, str, Optional[float], Optional[int]]:
        """
        Validate if a stream URL is accessible and playable
        Returns: (is_valid, reason, response_time, status_code)
        """
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                # Method 1: Quick HEAD request
                try:
                    response = self.session.head(
                        url, 
                        timeout=(3, 5), 
                        allow_redirects=True
                    )
                    if response.status_code in [200, 206]:
                        response_time = time.time() - start_time
                        return True, "Valid (HEAD)", response_time, response.status_code
                except requests.exceptions.RequestException:
                    pass
                
                # Method 2: GET request with range
                headers = {'Range': 'bytes=0-4096'}
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=(3, 7),
                    stream=True
                )
                
                response_time = time.time() - start_time
                
                if response.status_code not in [200, 206]:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    return False, f"HTTP {response.status_code}", response_time, response.status_code
                
                # Check content type
                content_type = response.headers.get('Content-Type', '').lower()
                valid_types = [
                    'video/', 'application/vnd.apple.mpegurl', 'application/x-mpegurl',
                    'application/dash+xml', 'text/plain', 'application/octet-stream'
                ]
                
                if any(vtype in content_type for vtype in valid_types):
                    return True, f"Valid ({content_type})", response_time, response.status_code
                
                # Check content for M3U8 signatures
                try:
                    chunk = next(response.iter_content(chunk_size=1024), b'')
                    if chunk:
                        content_sample = chunk.decode('utf-8', errors='ignore')
                        if '#EXTM3U' in content_sample or '#EXT-X-' in content_sample:
                            return True, "Valid M3U8", response_time, response.status_code
                        
                        if len(chunk) > 500:  # Non-empty binary data
                            return True, "Valid stream", response_time, response.status_code
                except:
                    pass
                
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                    
                return False, "Unrecognized format", response_time, response.status_code
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    continue
                return False, "Timeout", time.time() - start_time, None
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                return False, "Connection error", time.time() - start_time, None
            except Exception as e:
                if attempt < self.max_retries - 1:
                    continue
                return False, f"Error: {str(e)}", time.time() - start_time, None
        
        return False, "Max retries exceeded", time.time() - start_time, None

class M3UParser:
    """Parse M3U playlist files"""
    
    @staticmethod
    def parse_m3u_content(content: str, source_name: str = "") -> List[Channel]:
        """Parse M3U content and return list of channels"""
        channels = []
        current_extinf = None
        
        for line in content.splitlines():
            line = line.strip()
            
            if line.startswith('#EXTINF'):
                current_extinf = line
            elif line and not line.startswith('#') and current_extinf:
                # Extract channel info
                channel_name = M3UParser._extract_channel_name(current_extinf)
                logo = M3UParser._extract_logo(current_extinf)
                group_title = M3UParser._extract_group_title(current_extinf)
                
                # Determine category
                category = CategoryExtractor.extract_category(channel_name, line)
                
                channel = Channel(
                    name=channel_name,
                    url=line,
                    category=category,
                    country=source_name,
                    logo=logo,
                    group_title=group_title,
                    extinf_line=current_extinf
                )
                
                channels.append(channel)
                current_extinf = None
        
        return channels
    
    @staticmethod
    def _extract_channel_name(extinf_line: str) -> str:
        """Extract channel name from EXTINF line"""
        # Try tvg-name first
        tvg_name_match = re.search(r'tvg-name="([^"]*)"', extinf_line)
        if tvg_name_match:
            return tvg_name_match.group(1)
        
        # Fallback to text after last comma
        parts = extinf_line.split(',', 1)
        if len(parts) > 1:
            return parts[1].strip()
        
        return "Unknown"
    
    @staticmethod
    def _extract_logo(extinf_line: str) -> Optional[str]:
        """Extract logo URL from EXTINF line"""
        logo_match = re.search(r'tvg-logo="([^"]*)"', extinf_line)
        return logo_match.group(1) if logo_match else None
    
    @staticmethod
    def _extract_group_title(extinf_line: str) -> Optional[str]:
        """Extract group title from EXTINF line"""
        group_match = re.search(r'group-title="([^"]*)"', extinf_line)
        return group_match.group(1) if group_match else None

def ensure_directory(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)

def format_time(seconds: float) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def format_number(num: int) -> str:
    """Format number with thousand separators"""
    return f"{num:,}"