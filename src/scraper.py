"""
IPTV Channel Scraper
"""
import requests
import time
from typing import List, Dict, Tuple
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import Channel, ScrapingStats
from .utils import M3UParser, ensure_directory
from .config import config

logger = logging.getLogger(__name__)

class IPTVScraper:
    """Scrape IPTV channels from various sources"""
    
    def __init__(self):
        self.stats = ScrapingStats()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_source(self, source_name: str, url: str) -> Tuple[bool, List[Channel]]:
        """Scrape a single source"""
        try:
            logger.info(f"Scraping {source_name}: {url}")
            
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to fetch {source_name}: HTTP {response.status_code}")
                return False, []
            
            channels = M3UParser.parse_m3u_content(response.text, source_name)
            
            # Filter channels by target categories
            filtered_channels = [
                ch for ch in channels 
                if ch.category and ch.category.value in config.TARGET_CATEGORIES
            ]
            
            logger.info(f"✅ {source_name}: {len(filtered_channels)} channels")
            return True, filtered_channels
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ {source_name}: Timeout")
            return False, []
        except Exception as e:
            logger.error(f"❌ {source_name}: {str(e)}")
            return False, []
    
    def scrape_all_sources(self) -> List[Channel]:
        """Scrape all configured sources"""
        logger.info(f"🚀 Starting scraping from {len(config.M3U_SOURCES)} sources")
        
        self.stats.total_sources = len(config.M3U_SOURCES)
        all_channels = []
        
        # Use ThreadPoolExecutor for concurrent scraping
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_source = {
                executor.submit(self.scrape_source, name, url): name
                for name, url in config.M3U_SOURCES.items()
            }
            
            # Process completed tasks
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                
                try:
                    success, channels = future.result()
                    if success:
                        self.stats.successful_sources += 1
                        all_channels.extend(channels)
                        
                        # Update category stats
                        for channel in channels:
                            if channel.category:
                                category_name = channel.category.value
                                self.stats.channels_by_category[category_name] = \
                                    self.stats.channels_by_category.get(category_name, 0) + 1
                except Exception as e:
                    logger.error(f"❌ {source_name}: {str(e)}")
        
        # Remove duplicates based on URL
        unique_channels = {}
        for channel in all_channels:
            if channel.url not in unique_channels:
                unique_channels[channel.url] = channel
        
        final_channels = list(unique_channels.values())
        self.stats.total_channels = len(final_channels)
        
        logger.info(f"✅ Scraping completed: {self.stats.total_channels} unique channels")
        return final_channels
    
    def get_stats(self) -> ScrapingStats:
        """Get scraping statistics"""
        return self.stats

def scrape_channels() -> Tuple[List[Channel], ScrapingStats]:
    """Main function to scrape all channels"""
    scraper = IPTVScraper()
    channels = scraper.scrape_all_sources()
    stats = scraper.get_stats()
    return channels, stats