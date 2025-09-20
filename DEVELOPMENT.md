# MSPlay IPTV - Development Guide

## Project Structure

```
msplayiptv/
├── .github/
│   └── workflows/
│       └── update-playlist.yml    # GitHub Actions workflow
├── src/                           # Source code modules
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Configuration settings
│   ├── models.py                 # Data models and types
│   ├── utils.py                  # Utility functions
│   ├── scraper.py                # Channel scraping logic
│   ├── validator.py              # Channel validation logic
│   └── generator.py              # M3U file generation
├── scripts/                      # Helper scripts
│   └── update_readme_stats.py    # README statistics updater
├── static/                       # Generated files (Git tracked)
│   ├── msplay.m3u               # Main playlist
│   ├── stats.json               # Statistics JSON
│   └── msplay_*.m3u             # Category-specific playlists
├── main.py                       # Main application entry point
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── LICENSE                       # MIT License
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/msanto/msplayiptv.git
cd msplayiptv
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Configuration

Edit `src/config.py` to customize:

- **M3U_SOURCES**: Add or remove IPTV sources
- **TARGET_CATEGORIES**: Which categories to include
- **MAX_WORKERS**: Concurrent validation threads
- **TIMEOUT**: Validation timeout per channel
- **OUTPUT_FILE**: Output filename

## Architecture

### Modular Design
- **Scraper**: Asynchronously fetches M3U playlists
- **Validator**: Multi-threaded channel validation
- **Generator**: Creates organized M3U files
- **Models**: Type-safe data structures

### Key Features
- Async/await for network operations
- Thread pool for channel validation
- Type hints throughout
- Comprehensive error handling
- Rich console output
- JSON statistics generation

## Testing

Run basic validation:
```bash
python -c "from src import scrape_channels; import asyncio; print(asyncio.run(scrape_channels()))"
```

## GitHub Actions

The workflow runs daily at 06:00 UTC and:
1. Scrapes channels from all sources
2. Validates each channel for availability
3. Generates M3U playlist and statistics
4. Updates README with current stats
5. Commits changes to repository

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Performance Tips

- Adjust `MAX_WORKERS` based on your system
- Lower `TIMEOUT` for faster validation
- Add more sources in `config.py`
- Use category filtering to reduce processing time