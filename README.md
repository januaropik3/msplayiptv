# MSPlay IPTV

![Channels](ht### 📱 For Mobile/TV Apps
Simply copy any URL above and paste it into your IPTV player:
- **VLC Media Player**: Media → Open Network Stream
- **Kodi**: TV → Enter add-on browser → PVR IPTV Simple Client
- **Perfect Player**: Settings → Playlist → Add Playlist
- **TiviMate**: Add Playlist → M3U Playlist

## 🤖 Automated Updates

### ⏰ Daily Schedule
This project runs **completely automatically** - you don't need to do anything manually!

- **🕕 06:00 UTC Daily**: Automatic scraping and validation
- **⚡ Real-time**: GitHub Actions updates all playlists
- **🔄 Always Fresh**: Latest channels automatically added/removed
- **✅ Validated**: Only working channels included

### 🎯 What Happens Automatically:
1. **Scrape**: Collects channels from multiple sources
2. **Validate**: Tests each channel (10-second timeout)
3. **Filter**: Removes dead/broken channels
4. **Generate**: Creates M3U playlists by category
5. **Deploy**: Updates GitHub repository
6. **Statistics**: Updates channel counts and badges

### 💡 Manual Trigger (Optional)
If you want to update immediately, visit the [Actions](https://github.com/januaropik3/msplayiptv/actions) page and click "Run workflow"

**No maintenance required!** The system handles everything automatically.img.shields.io/badge/Channels-6,159-brightgreen)
![Updated](https://img.shields.io/badge/Updated-2025-09-20-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Format](https://img.shields.io/badge/Format-M3U-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![GitHub Stars](https://img.shields.io/github/stars/januaropik3/msplayiptv?style=social)

🌟 **Modern IPTV Channel Collection** - Curated and validated daily via automated systems

## 🚀 Quick Start

### 📺 Main Playlist (All 6,159 Channels)
```
https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u
```

### 🏷️ Category-Specific Playlists

| Category | Channels | Direct URL |
|----------|----------|------------|
| 🏃 **Sports** | 1,086 | [`msplay_sports.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_sports.m3u) |
| 📰 **News** | 1,087 | [`msplay_news.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_news.m3u) |
| 🎬 **Movies** | 712 | [`msplay_movies.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_movies.m3u) |
| 🎵 **Music** | 218 | [`msplay_music.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_music.m3u) |
| 👶 **Kids** | 80 | [`msplay_kids.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_kids.m3u) |
| � **Documentary** | 72 | [`msplay_documentary.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_documentary.m3u) |
| 📺 **Entertainment** | 39 | [`msplay_entertainment.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_entertainment.m3u) |
| 🌐 **General** | 2,865 | [`msplay_general.m3u`](https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_general.m3u) |

### �📱 For Mobile/TV Apps
Simply copy any URL above and paste it into your IPTV player:
- **VLC Media Player**: Media → Open Network Stream
- **Kodi**: TV → Enter add-on browser → PVR IPTV Simple Client
- **Perfect Player**: Settings → Playlist → Add Playlist
- **TiviMate**: Add Playlist → M3U Playlist

## 📊 Statistics

| Metric | Value |
|--------|-------|
| 📺 Total Channels | 6,159 |
| 🏷️ Categories | 8 |
| 🌍 Sources | 2 |
| 🕐 Last Updated | 2025-09-20 09:37:18 |

### 📁 Categories

| Category | Channels |
|----------|----------|
| Documentary | 72 |
| Entertainment | 39 |
| General | 2,865 |
| Kids | 80 |
| Movies | 712 |
| Music | 218 |
| News | 1,087 |
| Sports | 1,086 |## 🎯 Features

- ✅ **Daily Updates**: Automated channel validation and playlist generation
- 🔍 **Quality Assured**: All channels are tested for availability
- 📱 **Universal Format**: Standard M3U format compatible with all players
- 🌍 **Multi-Source**: Aggregated from multiple reliable IPTV sources
- 🏷️ **Categorized**: Organized by content type (Sports, News, Movies, etc.)
- 🚀 **High Performance**: Multi-threaded validation for faster updates
- 📊 **Detailed Stats**: Real-time statistics and channel information

## 📁 Channel Categories

Our playlist includes channels from these categories:

- 🎬 **Movies** - Cinema and film channels
- 📺 **Entertainment** - General entertainment content  
- 🏃 **Sports** - Sports networks and events
- 📰 **News** - News channels and networks
- 🎵 **Music** - Music videos and audio channels
- 👶 **Kids** - Children and family content
- 📚 **Documentary** - Educational and documentary content
- 🌐 **General** - Mixed content channels

## 🚀 Usage

### Option 1: Direct Download
```bash
wget https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u
```

### Option 2: Using curl
```bash
curl -o msplay.m3u https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u
```

### Option 3: Clone Repository
```bash
git clone https://github.com/januaropik3/msplayiptv.git
cd msplayiptv
# Playlist is in static/msplay.m3u
```

## 🔧 For Developers

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation
```bash
git clone https://github.com/januaropik3/msplayiptv.git
cd msplayiptv
pip install -r requirements.txt
```

### Running Locally
```bash
python main.py
```

### Configuration
Edit `src/config.py` to customize:
- Sources to scrape
- Target categories
- Validation settings
- Output preferences

## 📋 API Endpoints

## 📋 All Available URLs

### 📺 Main Playlist
- **All Channels**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u`

### 🏷️ Category Playlists
- **Sports**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_sports.m3u`
- **News**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_news.m3u`
- **Movies**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_movies.m3u`
- **Music**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_music.m3u`
- **Kids**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_kids.m3u`
- **Documentary**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_documentary.m3u`
- **Entertainment**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_entertainment.m3u`
- **General**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_general.m3u`

### 📊 API Endpoints
- **Statistics**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/stats.json`

We provide JSON API for developers:

- **Statistics**: `https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/stats.json`
- **Channel Data**: Available in M3U format

### Example API Response
```json
{
  "generated_at": "2024-01-15T06:00:00Z",
  "total_channels": 1250,
  "categories": {
    "Movies": 450,
    "Sports": 320,
    "News": 180,
    "Entertainment": 200,
    "Kids": 100
  },
  "sources": ["DrewLive", "Free-TV", "iptv-org"],
  "playlist_url": "https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u"
}
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Report Issues**: Found a broken channel? [Open an issue](https://github.com/januaropik3/msplayiptv/issues)
2. **💡 Suggest Sources**: Know a good IPTV source? Let us know!
3. **🔧 Submit PRs**: Improve our code, add features, fix bugs
4. **⭐ Star the Repo**: Help others discover this project

### Adding New Sources
Edit `src/config.py` and add your M3U source:
```python
M3U_SOURCES = {
    "YourSource": "https://example.com/playlist.m3u8"
}
```

## 📈 Update Schedule

- 🕕 **Daily**: 06:00 UTC (Automated via GitHub Actions)
- 🔄 **Real-time**: Triggered on code changes
- 📊 **Statistics**: Updated with every run

## ⚠️ Disclaimer

This project aggregates publicly available IPTV streams from various sources. We:

- ❌ **Do NOT host** any video content
- ❌ **Do NOT provide** pirated content  
- ✅ **Only aggregate** publicly available streams
- ✅ **Respect** content creators and broadcasters

**Users are responsible for ensuring they have the right to access any content.**

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

If this project helps you, please consider:

- ⭐ **Starring** the repository
- 🍴 **Forking** and contributing
- 📢 **Sharing** with others
- ☕ **Supporting** the developer

## 📞 Contact

- 📧 **Issues**: [GitHub Issues](https://github.com/januaropik3/msplayiptv/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/januaropik3/msplayiptv/discussions)

---

<div align="center">

**Made with ❤️ by Masanto**

🔄 *Last updated: Check the badges above for real-time information*

</div>