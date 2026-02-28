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
    total = stats.get('total_activities', 0)
    last = stats.get('last_activity')

    last_activity_html = ''
    if last:
        last_activity_html = f'''<span class="footer-separator">&middot;</span>
        <div class="footer-item">
            <span class="footer-label">Latest:</span>
            <span class="footer-value">{last['name']}</span>
        </div>
        <span class="footer-separator">&middot;</span>
        <div class="footer-item">
            <span class="footer-value">{last['date']}</span>
        </div>'''

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
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

        html, body {{
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            background: #fafafa;
        }}

        body {{
            display: flex;
            flex-direction: column;
        }}

        .map-container {{
            flex: 1;
            min-height: 0;
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
            z-index: 1;
        }}

        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            display: block;
        }}

        .footer {{
            flex-shrink: 0;
            background: #f5f5f5;
            padding: 16px 28px;
            padding-bottom: max(16px, env(safe-area-inset-bottom));
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 32px;
            border-top: 1px solid #d4d4d4;
            font-size: 13px;
            letter-spacing: 0.02em;
        }}

        .footer-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .footer-label {{
            font-weight: 400;
            color: #171717;
        }}

        .footer-value {{
            font-weight: 300;
            color: #737373;
        }}

        .footer-separator {{
            color: #d4d4d4;
        }}

        @media (max-width: 768px) {{
            .footer {{
                padding: 12px 18px;
                padding-bottom: max(12px, env(safe-area-inset-bottom));
                font-size: 12px;
                flex-direction: column;
                gap: 6px;
            }}

            .footer-separator {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="map-container">
        <div class="loading" id="loading">Loading map...</div>
        <iframe src="heatmap.html" title="Activity Heatmap" id="map-iframe"
                allow="geolocation" loading="eager" onload="hideLoading()"></iframe>
    </div>
    <div class="footer">
        <div class="footer-item">
            <span class="footer-label">Jesse Alloy</span>
        </div>
        <span class="footer-separator">&middot;</span>
        <div class="footer-item">
            <span class="footer-value">{total} activities</span>
        </div>
        {last_activity_html}
    </div>
    <script>
        function hideLoading() {{
            document.getElementById('loading').style.display = 'none';
        }}
        setTimeout(function() {{
            var el = document.getElementById('loading');
            if (el && el.style.display !== 'none') {{
                el.textContent = 'Map failed to load. Try refreshing.';
            }}
        }}, 10000);
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
