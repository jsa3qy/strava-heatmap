# Strava Activity Heatmap Generator

A Python toolkit to fetch your Strava activities and generate beautiful interactive heatmap visualizations of all your GPS tracks.

## Features

- 📥 Import all historical activities from Strava bulk export
- 🔄 Incrementally update with new activities via Strava API
- 🗺️ Generate interactive HTML heatmaps with multiple color schemes
- 💾 Efficient GeoJSON storage format
- 🎨 Customizable visualizations with multiple map styles
- 🌐 **Deploy as auto-updating website with GitHub Pages**
- 🤖 **Automated daily updates via GitHub Actions**

## Quick Links

- **[Local Setup](#setup)** - Run scripts locally
- **[Deploy Website](DEPLOYMENT.md)** - Host on GitHub Pages with auto-updates
- **[Customization](#customization)** - Adjust colors, styles, and settings

## Setup

### 1. Get Strava API Credentials

1. Go to https://www.strava.com/settings/api
2. Create a new application:
   - **Application Name**: "My Activity Heatmap"
   - **Authorization Callback Domain**: `localhost`
3. Note your **Client ID** and **Client Secret**

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Credentials

```bash
cp config.example.json config.json
```

Edit `config.json` and add your Client ID and Client Secret.

## Workflow

### Step 1: Import Historical Activities

**Export your Strava data:**

1. Go to https://www.strava.com/account
2. Click "Get Started" under "Download or Delete Your Account"
3. Click "Request Your Archive"
4. Wait for email (usually takes a few hours)
5. Download and extract the ZIP file

**Import GPX files:**

```bash
python import_gpx.py /path/to/extracted/activities/
```

This will process all your GPX files and create `activities.geojson`.

### Step 2: Generate Your First Heatmap

```bash
python generate_heatmap.py
```

This creates `heatmap.html` and opens it in your browser!

**Color schemes available:**
```bash
python generate_heatmap.py default  # Blue → Cyan → Lime → Yellow → Red
python generate_heatmap.py heat     # Navy → Blue → Red → Orange → Yellow
python generate_heatmap.py purple   # Purple → Violet → Pink
python generate_heatmap.py green    # Dark Green → Lime → Yellow
```

### Step 3: Update with New Activities

After new activities are recorded on Strava:

```bash
python update_activities.py
```

This fetches new activities via the API and adds them to `activities.geojson`.

Then regenerate your heatmap:

```bash
python generate_heatmap.py
```

## Scripts

### `strava_activities.py`
Simple activity viewer - displays your 10 most recent activities with stats.

```bash
python strava_activities.py
```

### `import_gpx.py`
Processes GPX files from Strava bulk export into GeoJSON format.

```bash
python import_gpx.py <directory_with_gpx_files>
```

### `update_activities.py`
Fetches new activities from Strava API and updates the GeoJSON file incrementally.

```bash
python update_activities.py
```

### `generate_heatmap.py`
Creates an interactive HTML heatmap from your GeoJSON data.

```bash
python generate_heatmap.py [color_scheme]
```

## Website Deployment

Want to host your heatmap as a live website that updates automatically?

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions.**

Quick overview:
1. Push this repo to GitHub
2. Add Strava credentials as GitHub Secrets
3. Enable GitHub Pages
4. GitHub Actions will automatically update your heatmap daily!

Your website will include:
- Beautiful landing page with statistics
- Interactive embedded heatmap
- Activity breakdown by type
- Auto-updates every day at 6 AM UTC

## Customization

### Heatmap Appearance

Edit `generate_heatmap.py` (lines 91-97):

```python
HeatMap(
    self.all_points,
    min_opacity=0.4,  # Transparency: 0.0-1.0
    radius=2,         # Line thickness: 1-10
    blur=1,           # Sharpness: 0 (sharp) - 10 (fuzzy)
    ...
)
```

### Color Schemes

Use different color schemes when generating:

```bash
python3 generate_heatmap.py default  # Blue to red
python3 generate_heatmap.py heat     # Navy to yellow
python3 generate_heatmap.py purple   # Purple to pink
python3 generate_heatmap.py green    # Dark green to yellow
```

### Website Design

Edit `build_website.py` to customize:
- Colors and fonts (CSS in the `<style>` section)
- Statistics displayed
- Page layout and text

## Files

- `strava_activities.py` - Activity viewer
- `import_gpx.py` - GPX to GeoJSON converter
- `update_activities.py` - Incremental activity updater
- `generate_heatmap.py` - Heatmap visualization generator
- `generate_stats.py` - Statistics generator for website
- `build_website.py` - Website builder
- `refresh_token.py` - Token refresher for automation
- `config.json` - API credentials (not in git)
- `strava_tokens.json` - Auth tokens (not in git)
- `activities.geojson` - Your GPS data
- `heatmap.html` - Generated visualization
- `index.html` - Website landing page
- `stats.json` - Activity statistics

## Tips

- **First time setup**: Use bulk export to get all historical data, then use API for updates
- **Rate limits**: Strava API has rate limits (100 requests per 15 minutes), bulk export bypasses this
- **Storage**: GeoJSON files can get large with many activities - consider keeping backups
- **Testing locally**: Run all scripts locally before deploying to catch any issues
