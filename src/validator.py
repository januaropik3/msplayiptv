"""
IPTV Channel Validator
"""
import asyncio
import time
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .models import Channel, ValidationResult, ValidationStats
from .utils import StreamValidator, format_time
from .config import config

logger = logging.getLogger(__name__)

class IPTVValidator:
    """Validate IPTV channels"""
    
    def __init__(self, max_workers: int = None, timeout: int = None):
        self.max_workers = max_workers or config.MAX_WORKERS
        self.timeout = timeout or config.TIMEOUT
        self.validator = StreamValidator(timeout=self.timeout)
        self.stats = ValidationStats()
    
    def validate_channel(self, channel: Channel) -> ValidationResult:
        """Validate a single channel"""
        is_valid, reason, response_time, status_code = self.validator.validate_stream(channel.url)
        
        return ValidationResult(
            channel=channel,
            is_valid=is_valid,
            reason=reason,
            response_time=response_time,
            status_code=status_code
        )
    
    def validate_channels_batch(self, channels: List[Channel], 
                              progress_callback=None) -> Tuple[List[ValidationResult], ValidationStats]:
        """Validate multiple channels with threading"""
        start_time = time.time()
        results = []
        
        logger.info(f"🔄 Starting validation of {len(channels)} channels")
        logger.info(f"⚙️ Using {self.max_workers} workers, {self.timeout}s timeout")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_channel = {
                executor.submit(self.validate_channel, channel): channel 
                for channel in channels
            }
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_channel)):
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update stats
                    if result.is_valid:
                        self.stats.valid_channels += 1
                    else:
                        self.stats.invalid_channels += 1
                    
                    self.stats.total_checked += 1
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(i + 1, len(channels), result)
                    
                    # Log progress every 50 channels
                    if (i + 1) % 50 == 0:
                        logger.info(f"✅ Validated {i + 1}/{len(channels)} channels")
                
                except Exception as e:
                    logger.error(f"Error validating channel: {e}")
        
        # Update final stats
        self.stats.total_time = time.time() - start_time
        self.stats.update()
        
        logger.info(f"🎉 Validation completed in {format_time(self.stats.total_time)}")
        logger.info(f"📊 Results: {self.stats.valid_channels} valid, {self.stats.invalid_channels} invalid")
        logger.info(f"⚡ Speed: {self.stats.channels_per_second:.1f} channels/second")
        
        return results, self.stats
    
    def get_valid_channels(self, results: List[ValidationResult]) -> List[Channel]:
        """Extract only valid channels from results"""
        return [result.channel for result in results if result.is_valid]

def validate_channels(channels: List[Channel], 
                     max_workers: int = None, 
                     timeout: int = None,
                     progress_callback=None) -> Tuple[List[Channel], ValidationStats]:
    """Main function to validate channels"""
    validator = IPTVValidator(max_workers=max_workers, timeout=timeout)
    results, stats = validator.validate_channels_batch(channels, progress_callback)
    valid_channels = validator.get_valid_channels(results)
    
    return valid_channels, stats