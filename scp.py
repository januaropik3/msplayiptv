import requests
import os
import re
import time 
import threading
import signal
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# Rich components for modern UI
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.progress import TimeElapsedColumn, TimeRemainingColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich import box
from rich.align import Align
from rich.layout import Layout
from rich.style import Style
from rich.console import Group

# Initialize console
console = Console()

# Application state
class AppState:
    def __init__(self):
        self.results = []
        self.valid_count = 0
        self.invalid_count = 0
        self.start_time = 0
        self.output_base = ""
        self.autosave_interval = 30
        self.autosave_timer = None
        self.stop_event = threading.Event()
        self.save_valid_only = True
        self.total_channels = 0
        
app = AppState()

# Thread safety
results_lock = threading.Lock()

# Daftar URL M3U berdasarkan negara
m3u_urls = {
    "DrewLive": "https://raw.githubusercontent.com/Drewski2423/DrewLive/refs/heads/main/MergedPlaylist.m3u8"
}

def show_banner():
    """Show application banner"""
    banner = """
    ██╗██████╗ ████████╗██╗   ██╗    ███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗ 
    ██║██╔══██╗╚══██╔══╝██║   ██║    ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
    ██║██████╔╝   ██║   ██║   ██║    ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝
    ██║██╔═══╝    ██║   ╚██╗ ██╔╝    ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
    ██║██║        ██║    ╚████╔╝     ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║
    ╚═╝╚═╝        ╚═╝     ╚═══╝      ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
    """
    
    panel = Panel(
        Align.center(Text(banner, style="bold bright_blue")),
        title="[bold bright_green]IPTV Master Tool v1.0[/bold bright_green]",
        subtitle="[italic]Scrape, Process, and Validate IPTV Channels[/italic]",
        border_style="bright_blue",
        box=box.DOUBLE
    )
    console.print(panel)

def check_url_validity(url, timeout=10):
    """Check if URL is valid and accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        try:
            response = requests.get(url, timeout=timeout, headers={'Range': 'bytes=0-1023'})
            return response.status_code in [200, 206]
        except:
            return False

def check_stream_playability(url, timeout=10):
    """
    Advanced check if a stream is playable using multiple validation methods
    """
    try:
        # Faster timeout settings
        conn_timeout = min(3, timeout / 3)
        read_timeout = min(5, timeout / 2)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Connection': 'close', 
        }
        
        # Method 1: Quick HEAD request first
        try:
            response = requests.head(url, timeout=(conn_timeout, read_timeout), 
                                   headers=headers, allow_redirects=True)
            if response.status_code not in [200, 206]:
                return False, f"HEAD request failed: {response.status_code}"
        except requests.exceptions.RequestException:
            # Some servers don't support HEAD, continue with GET
            pass
        
        # Method 2: GET request with range for faster content check
        headers['Range'] = 'bytes=0-4096'
        
        try:
            response = requests.get(url, headers=headers, 
                                timeout=(conn_timeout, read_timeout), stream=True)
            
            if response.status_code not in [200, 206]:
                return False, f"GET request failed: {response.status_code}"
            
            # Method 3: Check Content-Type for valid stream types
            content_type = response.headers.get('Content-Type', '').lower()
            valid_types = [
                'video/', 'application/vnd.apple.mpegurl', 'application/x-mpegurl',
                'application/dash+xml', 'text/plain', 'application/octet-stream'
            ]
            
            # If content type matches known stream types, it's likely valid
            if any(vtype in content_type for vtype in valid_types):
                return True, "Valid content type detected"
                
            # Check content for M3U8 signatures
            chunk = next(response.iter_content(chunk_size=1024), b'')
            if not chunk:
                return False, "Empty response"
                
            content_sample = chunk.decode('utf-8', errors='ignore')
            if '#EXTM3U' in content_sample or '#EXT-X-' in content_sample:
                return True, "Valid M3U8 playlist"
            
            # Additional checks for binary streams
            if len(chunk) > 500:  # Non-empty binary data
                return True, "Stream contains data"
                
            return False, "Unrecognized content format"
            
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def extract_category(channel_name, channel_url=""):
    """Extract category from channel name and URL"""
    text_to_analyze = f"{channel_name} {channel_url}".lower()
    
    # Desired categories
    keywords = {
        'Sports': ['sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 'boxing', 'mma', 'ufc', 'espn', 'fox_sport', 'bein', 'eurosport', 'sky_sport'],
        'News': ['news', 'cnn', 'bbc', 'fox_news', 'msnbc', 'cnbc', 'bloomberg', 'reuters', 'aljazeera', 'dw', 'france24', 'rt', 'sky_news'],
        'Movies': ['movie', 'cinema', 'film', 'hbo', 'netflix', 'prime', 'disney', 'paramount', 'universal', 'warner', 'fox_movie', 'cinemax', 'starz'],
        'Kids': ['kids', 'child', 'cartoon', 'disney', 'nickelodeon', 'nick_jr', 'cartoon_network', 'boomerang', 'baby_tv', 'junior'],
        'Music': ['music', 'mtv', 'vh1', 'vevo', 'radio', 'concert', 'karaoke', 'youtube_music']
    }
    
    for category, keyword_list in keywords.items():
        for keyword in keyword_list:
            if keyword.replace('_', ' ') in text_to_analyze or keyword.replace('_', '') in text_to_analyze:
                return category
    
    # URL patterns for desired categories
    url_patterns = {
        'Sports': [r'sport', r'football', r'soccer', r'basket', r'tennis'],
        'News': [r'news', r'cnn', r'bbc', r'fox'],
        'Movies': [r'movie', r'cinema', r'film', r'hbo'],
        'Kids': [r'kids', r'child', r'cartoon', r'disney'],
        'Music': [r'music', r'mtv', r'radio']
    }
    
    for category, patterns in url_patterns.items():
        for pattern in patterns:
            if re.search(pattern, channel_url, re.IGNORECASE):
                return category
    
    # If not in desired categories, return None (will be filtered out)
    return None

def parse_m3u(content):
    """Parse M3U content and group by category"""
    channels = defaultdict(list)
    current_channel = None
    
    for line in content.splitlines():
        if line.startswith('#EXTINF'):
            channel_name = re.search(r'tvg-name="(.*?)"', line)
            if not channel_name:
                channel_name = line.split(',')[-1]
            else:
                channel_name = channel_name.group(1)
            current_channel = {'name': channel_name, 'info': line}
        elif line and not line.startswith('#') and current_channel:
            current_channel['url'] = line
            category = extract_category(current_channel['name'], current_channel['url'])
            if category is not None:  # Only add if category is not None
                channels[category].append(current_channel)
            current_channel = None
    
    return channels

def parse_m3u_file(filepath):
    """Parse M3U file and extract channel info"""
    try:
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        content = None
        
        # Try different encodings
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            # Fallback binary mode
            with open(filepath, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
        
        return parse_m3u(content)
    except Exception as e:
        console.print(f"[bright_red]❌ Error parsing file: {e}[/bright_red]")
        return defaultdict(list)

def download_and_process(country, url):
    """Download and process a playlist from URL"""
    try:
        console.print(f"[cyan]🔄 Processing {country}...[/cyan]")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        channels = parse_m3u(response.text)
        
        # Filter only desired categories
        allowed_categories = {'Kids', 'Movies', 'Sports', 'News', 'Music'}
        filtered_channels = {k: v for k, v in channels.items() if k in allowed_categories and k is not None}
        
        # Count statistics
        categories_count = len(filtered_channels)
        total_channels = sum(len(items) for items in filtered_channels.values())
        
        console.print(f"[green]✅ {country}: {categories_count} categories, {total_channels} channels[/green]")
        
        return True, categories_count, total_channels, filtered_channels
    except Exception as e:
        console.print(f"[red]❌ {country}: {str(e)}[/red]")
        return False, 0, 0, None

def create_stats_panel():
    """Create real-time statistics panel"""
    elapsed = time.time() - app.start_time if app.start_time > 0 else 0
    total = app.valid_count + app.invalid_count
    
    # Calculate speed (channels per second)
    speed = total / elapsed if elapsed > 0 else 0
    
    # Calculate estimated time remaining
    remaining = "N/A"
    if app.total_channels > 0 and speed > 0:
        channels_left = app.total_channels - total
        seconds_left = int(channels_left / speed) if speed > 0 else 0
        remaining = f"{seconds_left // 60}m {seconds_left % 60}s"
    
    panel = Panel(
        f"[bold]Current Status:[/bold]\n\n"
        f"[bright_green]✅ Valid: {app.valid_count}[/bright_green]\n"
        f"[bright_red]❌ Invalid: {app.invalid_count}[/bright_red]\n"
        f"[bright_blue]🔄 Total Processed: {total}[/bright_blue]\n"
        f"[bright_yellow]⏱️ Elapsed Time: {int(elapsed // 60)}m {int(elapsed % 60)}s[/bright_yellow]\n"
        f"[bright_cyan]⚡ Speed: {speed:.1f} ch/s[/bright_cyan]\n"
        f"[bright_magenta]🏁 Est. Remaining: {remaining}[/bright_magenta]",
        title="[bold bright_cyan]Real-time Statistics[/bold bright_cyan]",
        border_style="bright_blue",
        box=box.ROUNDED,
        padding=1
    )
    return panel

def format_channel_name(name, max_length=60):
    """Format channel name for display"""
    if len(name) > max_length:
        return name[:max_length-3] + "..."
    return name

def autosave_results():
    """Function to save results periodically"""
    if app.stop_event.is_set():
        return
    
    with results_lock:
        if app.results:
            try:
                console.print(f"\n[bright_cyan]🔄 Auto-saving current results ({len(app.results)} channels)...[/bright_cyan]")
                autosave_base = f"{app.output_base}_AUTOSAVE"
                save_results(app.results, f"{autosave_base}.m3u")
                console.print(f"[bright_green]📄 Auto-saved {app.valid_count} valid channels[/bright_green]")
            except Exception as e:
                console.print(f"[bright_red]❌ Auto-save error: {e}[/bright_red]")
    
    # Schedule next autosave if not stopped
    if not app.stop_event.is_set():
        app.autosave_timer = threading.Timer(app.autosave_interval, autosave_results)
        app.autosave_timer.daemon = True
        app.autosave_timer.start()

def check_channels_batch(channels, max_workers=50, timeout=15):
    """Check multiple channels with threading"""
    app.total_channels = len(channels)
    
    def check_single_channel(channel):
        if app.stop_event.is_set():
            return None
            
        url = channel['url']
        is_valid, reason = check_stream_playability(url, timeout)
        result = {
            'channel': channel,
            'is_valid': is_valid,
            'reason': reason,
            'url': url
        }
        
        # Update results with thread safety
        with results_lock:
            app.results.append(result)
            if is_valid:
                app.valid_count += 1
            else:
                app.invalid_count += 1
        
        return result
    
    # Layout for UI organization
    layout = Layout()
    layout.split_column(
        Layout(name="progress", size=5),
        Layout(name="stats", size=10),
        Layout(name="latest", size=8)
    )
    
    # Latest results display
    latest_results = []
    
    def get_latest_results_panel():
        title = "[bright_cyan]Latest Results[/bright_cyan]"
        if not latest_results:
            return Panel("Waiting for results...", title=title, border_style="bright_blue")
        
        content = "\n".join(latest_results[-7:])  # Show last 7 results
        return Panel(content, title=title, border_style="bright_blue")
    
    # Progress bar for tracking
    progress_panel = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="bright_green", finished_style="bright_green"),
        TaskProgressColumn(),
        TextColumn("({task.completed}/{task.total})"),
        TextColumn("✅{task.fields[valid]} ❌{task.fields[invalid]}"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )
    
    task = progress_panel.add_task(
        "[bright_cyan]Checking streams...", 
        total=len(channels),
        valid=0,
        invalid=0
    )
    
    # Update layout components
    layout["progress"].update(progress_panel)
    layout["stats"].update(create_stats_panel())
    layout["latest"].update(get_latest_results_panel())
    
    # Use a single Live display
    with Live(layout, refresh_per_second=4, screen=True) as live:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_channel = {executor.submit(check_single_channel, ch): ch for ch in channels}
            
            for future in as_completed(future_to_channel):
                if app.stop_event.is_set():
                    break
                    
                try:
                    result = future.result()
                    if result is None:  # Skip if we got None due to stopping
                        continue
                    
                    # Format output for the latest results panel
                    channel_name = format_channel_name(result['channel']['name'])
                    if result['is_valid']:
                        status_text = f"[bright_green]✅ VALID[/bright_green]"
                        latest_results.append(f"{channel_name} - {status_text}")
                    else:
                        reason = result['reason']
                        reason_short = reason[:30] + "..." if len(reason) > 30 else reason
                        status_text = f"[bright_red]❌ {reason_short}[/bright_red]"
                        latest_results.append(f"{channel_name} - {status_text}")
                    
                    # Update progress
                    progress_panel.update(
                        task, 
                        advance=1, 
                        valid=app.valid_count, 
                        invalid=app.invalid_count
                    )
                    
                    # Update UI components
                    layout["stats"].update(create_stats_panel())
                    layout["latest"].update(get_latest_results_panel())
                    
                except Exception as e:
                    console.print(f"[bright_red]Error processing channel: {e}[/bright_red]")
    
    return app.results, app.valid_count, app.invalid_count

def handle_sigint(signum, frame):
    """Handle Ctrl+C gracefully"""
    app.stop_event.set()
    console.print("\n[bold bright_yellow]⚠️ Process interrupted - Saving results...[/bold bright_yellow]")
    
    # Cancel autosave timer if it exists
    if app.autosave_timer:
        app.autosave_timer.cancel()
        app.autosave_timer = None
    
    # Save results so far
    save_and_report_results(interrupted=True)
    
    # Exit cleanly
    sys.exit(0)

def save_and_report_results(interrupted=False):
    """Save results and report"""
    check_time = time.time() - app.start_time
    
    # Prefix for interrupted files
    prefix = "PARTIAL_" if interrupted else ""
    output_base = app.output_base.replace('.m3u', f'_{prefix}CHECKED')
    
    try:
        # Save results
        console.print(f"\n[bright_cyan]💾 Saving results...[/bright_cyan]")
        valid_file = save_results(app.results, f"{output_base}.m3u")
        
        # Show summary
        if app.results:  # Only show report if we have results
            create_summary_report(app.results, app.valid_count, app.invalid_count, check_time)
        
        status = "Partial check" if interrupted else "Check"
        console.print(f"\n[bold bright_{'yellow' if interrupted else 'green'}]🎉 {status} completed![/bold bright_{'yellow' if interrupted else 'green'}]")
        console.print(f"[bright_green]📄 Valid channels saved: {valid_file}[/bright_green]")
        
    except Exception as e:
        console.print(f"[bright_red]❌ Error saving final results: {e}[/bright_red]")
        import traceback
        console.print(f"[bright_red]{traceback.format_exc()}[/bright_red]")

def save_results(results, output_file="checked_channels.m3u"):
    """Save check results to a new M3U file (valid only)"""
    if not results:
        console.print("[bright_yellow]⚠️ No results to save[/bright_yellow]")
        return output_file
    
    # Only save valid channels
    valid_channels = [r for r in results if r['is_valid']]
    
    # Check if we have valid channels
    if not valid_channels:
        console.print("[bright_yellow]⚠️ No valid channels found to save[/bright_yellow]")
        return output_file
    
    # Save only in static folder
    static_dir = Path("static")
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the output file path
    valid_file = static_dir / "live.m3u"
    
    try:
        with open(valid_file, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n\n")
            f.write("# ====== VALID CHANNELS ONLY ======\n")
            
            for result in valid_channels:
                channel = result['channel']
                f.write(f"{channel['info']}\n")
                f.write(f"{channel['url']}\n\n")
        
        console.print(f"[bright_green]✅ Successfully saved {len(valid_channels)} valid channels to {valid_file}[/bright_green]")
    except Exception as e:
        console.print(f"[bright_red]❌ Error writing to file: {str(e)}[/bright_red]")
    
    # Return the path as string for compatibility with rest of the code
    return str(valid_file)

def create_summary_report(results, valid_count, invalid_count, check_time):
    """Create a summary report"""
    if not results:
        console.print("[bright_yellow]⚠️ No results to report[/bright_yellow]")
        return
        
    # Group by category
    by_group = defaultdict(lambda: {'valid': 0, 'invalid': 0})
    
    for result in results:
        group = result['channel'].get('group', 'Unknown')
        if result['is_valid']:
            by_group[group]['valid'] += 1
        else:
            by_group[group]['invalid'] += 1
    
    # Summary table with modern styling
    table = Table(
        title="[bold bright_green]🔍 Stream Check Summary[/bold bright_green]", 
        box=box.ROUNDED,
        highlight=True,
        header_style="white on blue",  # Perbaikan dari "bright-white on blue"
        border_style="bright_blue"
    )
    
    table.add_column("Category", style="bright_cyan", no_wrap=True)
    table.add_column("Valid", justify="right", style="bright_green")
    table.add_column("Invalid", justify="right", style="bright_red")
    table.add_column("Total", justify="right", style="bright_blue")
    table.add_column("Success Rate", justify="right", style="bright_yellow")
    
    total_channels = len(results)
    
    for group, counts in sorted(by_group.items()):
        total_group = counts['valid'] + counts['invalid']
        success_rate = (counts['valid'] / total_group * 100) if total_group > 0 else 0;
        
        table.add_row(
            group or "Unknown",
            str(counts['valid']),
            str(counts['invalid']),
            str(total_group),
            f"{success_rate:.1f}%"
        )
    
    # Total row
    table.add_row("", "", "", "", style="bold")
    overall_success = (valid_count / total_channels * 100) if total_channels > 0 else 0
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold bright_green]{valid_count}[/bold bright_green]",
        f"[bold bright_red]{invalid_count}[/bold bright_red]",
        f"[bold bright_blue]{total_channels}[/bold bright_blue]",
        f"[bold bright_yellow]{overall_success:.1f}%[/bold bright_yellow]",
        style="bold"
    )
    
    console.print(table)
    
    # Stats panel with modern styling
    stats_panel = Panel(
        f"[bright_green]✅ Valid Streams: {valid_count}[/bright_green]\n"
        f"[bright_red]❌ Invalid Streams: {invalid_count}[/bright_red]\n"
        f"[bright_blue]📊 Total Checked: {total_channels}[/bright_blue]\n"
        f"[bright_yellow]⚡ Success Rate: {overall_success:.1f}%[/bright_yellow]\n"
        f"[bright_cyan]⏱️ Check Time: {int(check_time // 60)}m {int(check_time % 60)}s[/bright_cyan]",
        title="[bold]📈 Statistics[/bold]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=1
    )
    console.print(stats_panel)

def merge_into_single_file(all_country_data, validate_streams=True, max_workers=50, timeout=10):
    """Combine all country data into a single file and optionally validate streams"""
    console.print("\n[bold blue]🔄 Creating single merged file...[/bold blue]")
    
    # Categories to combine
    target_categories = ['Kids', 'Movies', 'Sports', 'News', 'Music']
    
    # Create output directory
    output_dir = os.path.join("IPTV_Playlists")
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store channels by category
    category_channels = {category: [] for category in target_categories}
    
    # Collect all channels from processed data
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Collecting channels...", total=len(all_country_data))
        
        for country, channels_data in all_country_data.items():
            if channels_data:
                for category in target_categories:
                    if category in channels_data:
                        for channel in channels_data[category]:
                            # Store category as 'group' field for the validator
                            channel['group'] = category
                            category_channels[category].append({
                                'info': channel['info'],
                                'url': channel['url'],
                                'name': channel.get('name', 'Unknown'),
                                'group': category,
                                'country': country
                            })
            
            progress.advance(task)
    
    # Combine all channels from all categories into a single list for validation
    all_channels = []
    for category, channels in category_channels.items():
        all_channels.extend(channels)
    
    # Remove duplicates based on URL
    unique_channels = {}
    for channel in all_channels:
        if channel['url'] not in unique_channels:
            unique_channels[channel['url']] = channel
    
    unique_channel_list = list(unique_channels.values())
    total_unique = len(unique_channel_list)
    
    console.print(f"[bright_green]✅ Found {total_unique} unique channels across all categories[/bright_green]")
    
    # Validate streams if requested
    if validate_streams:
        console.print(f"[bright_cyan]🔄 Starting validation of all channels...[/bright_cyan]")
        app.start_time = time.time()
        app.output_base = os.path.join(output_dir, "IPTV_ALL_CATEGORIES")
        
        # Set up autosave if enabled
        if app.autosave_interval > 0:
            console.print(f"[bright_cyan]⏱️ Auto-save enabled every {app.autosave_interval} seconds[/bright_cyan]")
            app.autosave_timer = threading.Timer(app.autosave_interval, autosave_results)
            app.autosave_timer.daemon = True
            app.autosave_timer.start()
        
        # Run validation
        results, valid_count, invalid_count = check_channels_batch(unique_channel_list, max_workers, timeout)
        
        # Stop autosave timer
        if app.autosave_timer:
            app.autosave_timer.cancel()
            app.autosave_timer = None
        
        # Save results
        save_and_report_results()
        
        return os.path.join(output_dir, "IPTV_ALL_CATEGORIES_CHECKED_VALID.m3u")
    
    else:
        # Just save all channels without validation
        final_filepath = os.path.join(output_dir, "IPTV_ALL_CATEGORIES.m3u")
        category_stats = {}
        
        with open(final_filepath, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n\n")
            
            for category in target_categories:
                channels = [ch for ch in unique_channel_list if ch['group'] == category]
                
                if channels:
                    # Write category header
                    f.write(f"# ====== {category.upper()} CHANNELS ======\n")
                    
                    for channel in channels:
                        # Modify info line to add group-title
                        info_line = channel['info']
                        
                        # Add group-title if not present
                        if 'group-title=' not in info_line.lower():
                            # Insert group-title after #EXTINF
                            if info_line.startswith('#EXTINF:'):
                                parts = info_line.split(',', 1)
                                if len(parts) == 2:
                                    extinf_part = parts[0]
                                    name_part = parts[1]
                                    
                                    # Add group-title and country info
                                    info_line = f'{extinf_part} group-title="{category}",{name_part} [{channel["country"]}]'
                                else:
                                    info_line = f'{info_line} group-title="{category}"'
                        else:
                            # Update existing group-title
                            info_line = re.sub(r'group-title="[^"]*"', f'group-title="{category}"', info_line)
                            # Add country if not present
                            if f'[{channel["country"]}]' not in info_line:
                                parts = info_line.split(',', 1)
                                if len(parts) == 2:
                                    info_line = f'{parts[0]},{parts[1]} [{channel["country"]}]'
                        
                        f.write(f"{info_line}\n")
                        f.write(f"{channel['url']}\n\n")
                    
                    category_stats[category] = len(channels)
                    console.print(f"[green]✅ {category}: {len(channels)} channels added[/green]")
                else:
                    console.print(f"[yellow]⚠️ {category}: No channels found[/yellow]")
                    category_stats[category] = 0
        
        total_channels = sum(category_stats.values())
        console.print(f"\n[bold green]🎉 Single file created: {total_channels} total channels[/bold green]")
        
        return final_filepath

def main():
    # Reset app state
    app.results = []
    app.valid_count = 0
    app.invalid_count = 0
    app.stop_event.clear()
    if app.autosave_timer:
        app.autosave_timer.cancel()
        app.autosave_timer = None
    
    # Setup signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)
    
    # Clear console and show banner
    console.clear()
    show_banner()
    
    # Ask for operational mode
    console.print("\n[bold bright_cyan]Select operation mode:[/bold bright_cyan]")
    console.print("[bright_white]1. Download and scrape channels from online sources[/bright_white]")
    console.print("[bright_white]2. Check existing M3U file[/bright_white]")
    console.print("[bright_white]3. Scrape online sources AND validate (all-in-one process)[/bright_white]")
    
    mode = console.input("\n[bold bright_cyan]Enter your choice (1-3): [/bold bright_cyan]").strip()
    
    if mode == "1":
        # Scrape only
        console.print("\n[bold bright_green]🚀 Starting channel scraping...[/bold bright_green]")
        console.print("[bold bright_cyan]📋 Processing only: Kids, Movies, Sports, News, Music[/bold bright_cyan]")
        
        results = []
        all_country_data = {}
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("[cyan]Processing countries...", total=len(m3u_urls))
            
            for country, url in m3u_urls.items():
                success, categories, total, channel_data = download_and_process(country, url)
                results.append((country, success, categories, total))
                
                # Save data for merging later
                if success and channel_data:
                    all_country_data[country] = channel_data
                
                progress.advance(main_task)
        
        # Merge into single file
        final_file = merge_into_single_file(all_country_data, validate_streams=False)
        
        # Show summary
        elapsed_time = time.time() - start_time
        successful = sum(1 for _, status, _, _ in results if status)
        
        console.print(f"\n[bold green]🎉 Processing completed in {elapsed_time:.2f} seconds![/bold green]")
        console.print(f"[bold cyan]📊 {successful}/{len(m3u_urls)} countries processed successfully[/bold cyan]")
        console.print(f"\n[bold blue]📁 Final result: {final_file}[/bold blue]")
        
    elif mode == "2":
        # Check existing file
        input_file = console.input("\n[bold bright_cyan]Enter M3U file path (or press Enter for default): [/bold bright_cyan]").strip()
        if not input_file:
            input_file = "IPTV_Playlists/IPTV_ALL_CATEGORIES.m3u"
        
        # Check if file exists
        if not os.path.exists(input_file):
            console.print(f"[bright_red]❌ File not found: {input_file}[/bright_red]")
            return
        
        # Settings
        console.print(f"\n[bright_green]📁 File found: {input_file}[/bright_green]")
        
        # Configuration options
        max_workers = console.input("[bright_cyan]Max concurrent checks (default: 50): [/bright_cyan]").strip()
        max_workers = int(max_workers) if max_workers.isdigit() else 50
        
        timeout = console.input("[bright_cyan]Timeout per check in seconds (default: 10): [/bright_cyan]").strip()
        timeout = int(timeout) if timeout.isdigit() and int(timeout) > 0 else 10
        
        autosave = console.input("[bright_cyan]Auto-save interval in seconds (default: 30, 0 to disable): [/bright_cyan]").strip()
        app.autosave_interval = int(autosave) if autosave.isdigit() else 30
        
        # Parse file
        with console.status("[bright_cyan]Parsing M3U file...[/bright_cyan]", spinner="dots"):
            channels = parse_m3u_file(input_file)
            # Convert to flat list for checker
            channel_list = []
            for category, category_channels in channels.items():
                for channel in category_channels:
                    channel['group'] = category  # Add group for report
                    channel_list.append(channel)
        
        if not channel_list:
            console.print("[bright_red]❌ No channels found in file[/bright_red]")
            return
        
        console.print(f"[bright_green]✅ Found {len(channel_list)} channels[/bright_green]")
        
        # Initialize output base
        app.output_base = str(Path(input_file).with_suffix(''))
        app.start_time = time.time()
        
        # Start autosave timer if enabled
        if app.autosave_interval > 0:
            console.print(f"[bright_cyan]⏱️ Auto-save enabled every {app.autosave_interval} seconds[/bright_cyan]")
            app.autosave_timer = threading.Timer(app.autosave_interval, autosave_results)
            app.autosave_timer.daemon = True
            app.autosave_timer.start()
        
        try:
            # Check channels
            results, valid_count, invalid_count = check_channels_batch(channel_list, max_workers, timeout)
            
            # Stop autosave timer
            if app.autosave_timer:
                app.autosave_timer.cancel()
                app.autosave_timer = None
            
            # Save final results
            save_and_report_results()
            
        except KeyboardInterrupt:
            # Handled by signal handler
            pass
        except Exception as e:
            if app.autosave_timer:
                app.autosave_timer.cancel()
                app.autosave_timer = None
            console.print(f"\n[bold bright_red]❌ Unexpected error: {e}[/bold bright_red]")
            import traceback
            console.print(f"[bright_red]{traceback.format_exc()}[/bright_red]")
            # Try to save results anyway
            save_and_report_results(interrupted=True)
            
    elif mode == "3":
        # All-in-one mode: scrape + validate
        console.print("\n[bold bright_green]🚀 Starting all-in-one process (scrape + validate)...[/bold bright_green]")
        console.print("[bold bright_cyan]📋 Processing only: Kids, Movies, Sports, News, Music[/bold bright_cyan]")
        
        # Configuration options
        max_workers = console.input("[bright_cyan]Max concurrent checks (default: 50): [/bright_cyan]").strip()
        max_workers = int(max_workers) if max_workers.isdigit() else 50
        
        timeout = console.input("[bright_cyan]Timeout per check in seconds (default: 10): [/bright_cyan]").strip()
        timeout = int(timeout) if timeout.isdigit() and int(timeout) > 0 else 10
        
        autosave = console.input("[bright_cyan]Auto-save interval in seconds (default: 30, 0 to disable): [/bright_cyan]").strip()
        app.autosave_interval = int(autosave) if autosave.isdigit() else 30
        
        start_time = time.time()
        
        # Step 1: Scrape channels
        console.print("\n[bold bright_cyan]Step 1/2: Scraping channels from all sources...[/bold bright_cyan]")
        
        results = []
        all_country_data = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("[cyan]Processing countries...", total=len(m3u_urls))
            
            for country, url in m3u_urls.items():
                success, categories, total, channel_data = download_and_process(country, url)
                results.append((country, success, categories, total))
                
                # Save data for validation
                if success and channel_data:
                    all_country_data[country] = channel_data
                
                progress.advance(main_task)
        
        # Step 2: Validate all channels
        console.print("\n[bold bright_cyan]Step 2/2: Validating all scraped channels...[/bold bright_cyan]")
        
        # Merge and validate
        final_file = merge_into_single_file(
            all_country_data, 
            validate_streams=True, 
            max_workers=max_workers,
            timeout=timeout
        )
        
        # Show summary
        total_time = time.time() - start_time
        console.print(f"\n[bold bright_green]🎉 All-in-one process completed in {int(total_time // 60)}m {int(total_time % 60)}s![/bold bright_green]")
        console.print(f"[bold bright_blue]📁 Final result with valid channels only: {final_file}[/bold bright_blue]")
    
    else:
        console.print("[bright_red]❌ Invalid choice, please run the program again.[/bright_red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Failsafe if signal handler doesn't catch it
        handle_sigint(None, None)
    except Exception as e:
        console.print(f"\n[bold bright_red]❌ Fatal error: {str(e)}[/bold bright_red]")
        import traceback
        console.print(f"[bright_red]{traceback.format_exc()}[/bright_red]")