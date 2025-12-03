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

    # Build minimalist full-screen page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activity Heatmap</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            background: #fafafa;
        }}

        .map-container {{
            flex: 1;
            position: relative;
            overflow: hidden;
            background: #f5f5f5;
        }}

        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #737373;
            font-size: 14px;
            font-weight: 300;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            display: block;
            touch-action: manipulation;
            -webkit-overflow-scrolling: touch;
            background: transparent;
        }}

        .footer {{
            background: #f5f5f5;
            padding: 18px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #d4d4d4;
            font-size: 13px;
            letter-spacing: 0.02em;
        }}

        .footer-name {{
            font-weight: 400;
            color: #171717;
        }}

        .footer-count {{
            font-weight: 300;
            color: #737373;
        }}

        @media (max-width: 640px) {{
            .footer {{
                padding: 14px 18px;
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="map-container">
        <div class="loading" id="loading">Loading map...</div>
        <iframe src="heatmap.html" title="Activity Heatmap" id="map-iframe" onload="hideLoading()"></iframe>
    </div>
    <div class="footer">
        <span class="footer-name">Jesse Alloy</span>
        <span class="footer-count">{stats.get('total_activities', 0)} activities</span>
    </div>
    <script>
        function hideLoading() {{
            const loading = document.getElementById('loading');
            if (loading) {{
                loading.style.display = 'none';
            }}
        }}

        // Fallback timeout - if map doesn't load in 10 seconds, show error
        setTimeout(function() {{
            const loading = document.getElementById('loading');
            if (loading && loading.style.display !== 'none') {{
                loading.textContent = 'Map failed to load. Try refreshing.';
            }}
        }}, 10000);

        // Also try to detect iframe load errors
        const iframe = document.getElementById('map-iframe');
        iframe.onerror = function() {{
            const loading = document.getElementById('loading');
            if (loading) {{
                loading.textContent = 'Error loading map';
                loading.style.display = 'block';
            }}
        }};
    </script>
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
