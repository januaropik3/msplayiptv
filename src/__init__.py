"""
MSPlay IPTV Package
"""

from .config import config
from .models import Channel, ChannelCategory, ValidationResult, ScrapingStats, ValidationStats
from .utils import CategoryExtractor, StreamValidator, M3UParser
from .scraper import scrape_channels
from .validator import validate_channels
from .generator import generate_playlist

__version__ = "2.0.0"
__author__ = "MSanto"
__description__ = "Modern IPTV Channel Scraper and Validator"

__all__ = [
    'config',
    'Channel',
    'ChannelCategory', 
    'ValidationResult',
    'ScrapingStats',
    'ValidationStats',
    'CategoryExtractor',
    'StreamValidator',
    'M3UParser',
    'scrape_channels',
    'validate_channels',
    'generate_playlist'
]