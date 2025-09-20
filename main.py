#!/usr/bin/env python3
"""
MSPlay IPTV - Modern IPTV Channel Scraper and Validator
GitHub: https://github.com/januaropik3/msplayiptv
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import (
    scrape_channels, validate_channels, generate_playlist,
    config, ScrapingStats, ValidationStats
)
from src.utils import format_time, format_number

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('msplay.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application function"""
    logger.info("🚀 MSPlay IPTV v2.0 - Starting...")
    logger.info(f"📂 Output directory: {config.OUTPUT_DIR}")
    logger.info(f"📝 Output file: {config.OUTPUT_FILE}")
    
    try:
        # Step 1: Scrape channels
        logger.info("=" * 60)
        logger.info("📡 STEP 1: Scraping channels from sources")
        logger.info("=" * 60)
        
        channels, scraping_stats = scrape_channels()
        
        if not channels:
            logger.error("❌ No channels found from any source!")
            return 1
        
        # Print scraping summary
        print_scraping_summary(scraping_stats)
        
        # Step 2: Validate channels
        logger.info("=" * 60)
        logger.info("🔍 STEP 2: Validating channels")
        logger.info("=" * 60)
        
        def progress_callback(current: int, total: int, result):
            """Progress callback for validation"""
            if current % 100 == 0 or current == total:
                progress = (current / total) * 100
                logger.info(f"⏳ Progress: {current}/{total} ({progress:.1f}%) - "
                          f"✅ {result.is_valid} - {result.channel.name}")
        
        valid_channels, validation_stats = validate_channels(
            channels,
            max_workers=config.MAX_WORKERS,
            timeout=config.TIMEOUT,
            progress_callback=progress_callback
        )
        
        if not valid_channels:
            logger.error("❌ No valid channels found!")
            return 1
        
        # Print validation summary
        print_validation_summary(validation_stats)
        
        # Step 3: Generate playlist files
        logger.info("=" * 60)
        logger.info("📄 STEP 3: Generating playlist files")
        logger.info("=" * 60)
        
        generated_files = generate_playlist(
            valid_channels,
            output_dir=config.OUTPUT_DIR,
            filename=config.OUTPUT_FILE,
            generate_categories=True,
            generate_stats=True
        )
        
        # Print final summary
        print_final_summary(scraping_stats, validation_stats, generated_files)
        
        logger.info("🎉 MSPlay IPTV completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1

def print_scraping_summary(stats: ScrapingStats):
    """Print scraping summary"""
    logger.info(f"📊 Scraping Summary:")
    logger.info(f"   Sources processed: {stats.successful_sources}/{stats.total_sources}")
    logger.info(f"   Total channels found: {format_number(stats.total_channels)}")
    logger.info(f"   Channels by category:")
    
    for category, count in sorted(stats.channels_by_category.items()):
        logger.info(f"     {category}: {format_number(count)}")

def print_validation_summary(stats: ValidationStats):
    """Print validation summary"""
    logger.info(f"📊 Validation Summary:")
    logger.info(f"   Total checked: {format_number(stats.total_checked)}")
    logger.info(f"   Valid channels: {format_number(stats.valid_channels)}")
    logger.info(f"   Invalid channels: {format_number(stats.invalid_channels)}")
    logger.info(f"   Success rate: {stats.success_rate:.1f}%")
    logger.info(f"   Processing time: {format_time(stats.total_time)}")
    logger.info(f"   Speed: {stats.channels_per_second:.1f} channels/second")

def print_final_summary(scraping_stats: ScrapingStats, validation_stats: ValidationStats, 
                       generated_files: dict):
    """Print final summary"""
    logger.info("=" * 60)
    logger.info("🎯 FINAL SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📡 Sources: {scraping_stats.successful_sources}/{scraping_stats.total_sources} successful")
    logger.info(f"📊 Channels: {format_number(validation_stats.valid_channels)} valid out of {format_number(scraping_stats.total_channels)} total")
    logger.info(f"💾 Files generated:")
    
    for file_type, file_path in generated_files.items():
        logger.info(f"   {file_type}: {file_path}")
    
    logger.info(f"⚡ Overall success rate: {validation_stats.success_rate:.1f}%")
    logger.info(f"⏱️ Total time: {format_time(validation_stats.total_time)}")

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        sys.exit(1)
    
    # Run the application
    exit_code = main()
    sys.exit(exit_code)