# MSPlay IPTV

![Channels](https://img.shields.io/badge/Channels-Loading...-brightgreen)
![Updated](https://img.shields.io/badge/Updated-Daily-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Format](https://img.shields.io/badge/Format-M3U-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![GitHub Stars](https://img.shields.io/github/stars/januaropik3/msplayiptv?style=social)

🌟 **Modern IPTV Channel Collection** - Curated and validated daily via automated systems

## 🚀 Quick Start

### 📺 Direct Playlist URL
```
https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u
```

### 📱 For Mobile/TV Apps
Simply copy the URL above and paste it into your IPTV player:
- **VLC Media Player**: Media → Open Network Stream
- **Kodi**: TV → Enter add-on browser → PVR IPTV Simple Client
- **Perfect Player**: Settings → Playlist → Add Playlist
- **TiviMate**: Add Playlist → M3U Playlist

## 📊 Statistics

*Statistics are automatically updated daily*

## 🎯 Features

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

**Made with ❤️ by januaropik3**

🔄 *Last updated: Check the badges above for real-time information*

</div>