#!/usr/bin/env python3
"""
Build the website by combining the heatmap with a nice landing page.
"""

import json
import os
from datetime import datetime


def build_website():
    """Build the website HTML"""

    # Load stats
    stats = {}
    if os.path.exists('stats.json'):
        with open('stats.json', 'r') as f:
            stats = json.load(f)

    # Read heatmap HTML
    if not os.path.exists('heatmap.html'):
        print("Error: heatmap.html not found! Run generate_heatmap.py first.")
        return

    with open('heatmap.html', 'r') as f:
        heatmap_html = f.read()

    # Extract just the map portion (folium creates a full HTML doc)
    # We'll embed it in an iframe instead

    # Build the landing page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Strava Activity Heatmap</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            padding: 40px 20px;
            color: white;
        }}

        h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .map-container {{
            background: white;
            border-radius: 15px;
            padding: 0;
            box-shadow: 0 10px 50px rgba(0,0,0,0.3);
            overflow: hidden;
            margin: 30px 0;
        }}

        .map-header {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}

        .map-header h2 {{
            color: #333;
            font-size: 1.8em;
        }}

        .interactive-map {{
            width: 100%;
            height: 700px;
            border: none;
            display: block;
        }}

        .static-map {{
            display: none;
            width: 100%;
            max-width: 100%;
            height: auto;
        }}

        .activity-types {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 30px 0;
        }}

        .activity-types h3 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.5em;
        }}

        .activity-type {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .activity-type:last-child {{
            border-bottom: none;
        }}

        .activity-name {{
            font-weight: 500;
            color: #555;
        }}

        .activity-count {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }}

        footer {{
            text-align: center;
            padding: 40px 20px;
            color: white;
            opacity: 0.8;
        }}

        .last-updated {{
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 10px;
            display: inline-block;
            margin-top: 20px;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2em;
            }}

            .stats-container {{
                grid-template-columns: 1fr;
            }}

            /* Hide interactive map on mobile */
            .interactive-map {{
                display: none;
            }}

            /* Show static map on mobile */
            .static-map {{
                display: block;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🗺️ My Activity Heatmap</h1>
            <p class="subtitle">Visualizing my Strava adventures</p>
        </header>

        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_activities', 0)}</div>
                <div class="stat-label">Activities</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{f"{stats.get('total_gps_points', 0):,}" if stats.get('total_gps_points') else '0'}</div>
                <div class="stat-label">GPS Points</div>
            </div>
            {f'''<div class="stat-card">
                <div class="stat-value">{stats.get('total_distance_km', 0):,}</div>
                <div class="stat-label">Kilometers</div>
            </div>''' if stats.get('total_distance_km') else ''}
            <div class="stat-card">
                <div class="stat-value">{len(stats.get('activity_types', {}))}</div>
                <div class="stat-label">Activity Types</div>
            </div>
        </div>

        <div class="map-container">
            <div class="map-header">
                <h2>Interactive Heatmap</h2>
            </div>
            <iframe src="heatmap.html" title="Activity Heatmap" class="interactive-map"></iframe>
            <img src="heatmap_static.png" alt="Activity Heatmap" class="static-map">
        </div>

        {f'''<div class="activity-types">
            <h3>Activity Breakdown</h3>
            {''.join(f'<div class="activity-type"><span class="activity-name">{activity_type}</span><span class="activity-count">{count}</span></div>'
                     for activity_type, count in sorted(stats.get('activity_types', {}).items(), key=lambda x: x[1], reverse=True))}
        </div>''' if stats.get('activity_types') else ''}

        <footer>
            <p>Built with Python, Folium, and Strava API</p>
            {f'<div class="last-updated">Last updated: {datetime.fromisoformat(stats["generated"]).strftime("%B %d, %Y at %I:%M %p")}</div>' if stats.get('generated') else ''}
        </footer>
    </div>
</body>
</html>
"""

    # Save index.html
    with open('index.html', 'w') as f:
        f.write(html)

    print("✓ Website built: index.html")
    print("\nFiles needed for deployment:")
    print("  - index.html")
    print("  - heatmap.html")
    print("  - stats.json")


if __name__ == "__main__":
    build_website()
