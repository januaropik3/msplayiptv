# 🚀 Deployment Guide untuk MSPlay IPTV

## Langkah-langkah Deploy ke GitHub

### 1. Persiapan Repository

1. **Buat Repository Baru di GitHub:**
   - Buka https://github.com/new
   - Nama repository: `msplayiptv`
   - Deskripsi: "Modern IPTV Channel Collection - Curated and validated daily"
   - Set sebagai **Public**
   - Jangan centang "Initialize with README" (karena kita sudah punya)

### 2. Upload Code

```bash
# Inisialisasi git di folder project
cd c:\Users\Masanto\Desktop\msplayiptv
git init

# Tambahkan semua file
git add .

# Commit pertama
git commit -m "🎉 Initial commit - MSPlay IPTV v2.0

✨ Features:
- Modern modular Python architecture
- Automated daily playlist updates via GitHub Actions
- Multi-threaded channel validation
- Professional README with live statistics
- M3U playlist generation with categories
- Comprehensive error handling and logging"

# Tambahkan remote dengan repository Anda
git remote add origin https://github.com/januaropik3/msplayiptv.git

# Push ke GitHub
git branch -M main
git push -u origin main
```

### 3. Konfigurasi GitHub Actions

Setelah code terupload, GitHub Actions akan otomatis berjalan:

1. **Workflow akan berjalan daily jam 06:00 UTC**
2. **Manual trigger juga tersedia** di tab Actions → "Update IPTV Playlist" → "Run workflow"

### 4. Setup GitHub Pages (Opsional)

Untuk hosting statistics page:

1. Buka repo settings
2. Scroll ke "Pages"  
3. Source: "Deploy from a branch"
4. Branch: `main` / `/ (root)`
5. Save

### 5. Personalisasi

Edit file berikut sesuai kebutuhan:

#### `src/config.py`
```python
# Tambah/hapus sumber M3U
M3U_SOURCES = {
    "YourSource": "https://example.com/playlist.m3u8"
}

# Sesuaikan kategori target
TARGET_CATEGORIES = ["Kids", "Movies", "Sports", "News", "Music"]
```

#### `README.md`
- Ganti semua `msanto/msplayiptv` dengan `januaropik3/msplayiptv`
- Update contact information
- Sesuaikan deskripsi

## 🎯 Hasil Yang Didapat

Setelah deployment, Anda akan memiliki:

### ✅ **Automated System**
- ⏰ Update harian otomatis jam 06:00 UTC
- 🔍 Validasi channel real-time
- 📊 Statistics update otomatis
- 🤖 README update otomatis

### ✅ **Professional Repository**
- 🏷️ Live badges dengan statistik
- 📚 Dokumentasi lengkap
- 🔧 Modular, maintainable code
- 📱 Mobile-friendly README

### ✅ **User Experience**
- 🔗 Direct playlist URL yang selalu update
- 📊 Real-time statistics
- 🏷️ Categorized channels
- 📱 Compatible dengan semua IPTV players

### ✅ **URLs yang Akan Tersedia**

1. **Main Playlist:**
   ```
   https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u
   ```

2. **Statistics API:**
   ```
   https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/stats.json
   ```

3. **Category Playlists:**
   ```
   https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_sports.m3u
   https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay_movies.m3u
   ```

## 🛠️ Maintenance

### Update Sources
Edit `src/config.py` dan commit changes.

### Manual Trigger
- Buka tab Actions di GitHub
- Pilih "Update IPTV Playlist"
- Click "Run workflow"

### Monitor Logs
- Check tab Actions untuk status updates
- Download artifacts untuk detailed logs

## 🔧 Local Development

```bash
# Clone repository
git clone https://github.com/januaropik3/msplayiptv.git
cd msplayiptv

# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
```

## 🎉 Selamat!

Repository MSPlay IPTV Anda sekarang siap dan akan:
- ✅ Update otomatis setiap hari
- ✅ Memberikan playlist berkualitas tinggi
- ✅ Terlihat professional seperti repo IPTV populer
- ✅ Mudah di-maintain dan dikembangkan

**URL Final Playlist Anda:**
`https://raw.githubusercontent.com/januaropik3/msplayiptv/main/static/msplay.m3u`