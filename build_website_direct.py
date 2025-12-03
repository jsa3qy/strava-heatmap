#!/usr/bin/env python3
"""
Build website with map embedded directly (no iframe) for mobile compatibility.
"""

import json
import os
from datetime import datetime
import re


def build_website():
    """Build the website HTML with embedded map"""

    # Load stats
    stats = {}
    if os.path.exists('stats.json'):
        with open('stats.json', 'r') as f:
            stats = json.load(f)

    # Read the generated heatmap HTML
    if not os.path.exists('heatmap.html'):
        print("Error: heatmap.html not found! Run generate_heatmap.py first.")
        return

    with open('heatmap.html', 'r') as f:
        heatmap_content = f.read()

    # Extract the head content (CSS and JS libraries)
    head_match = re.search(r'<head>(.*?)</head>', heatmap_content, re.DOTALL)
    if not head_match:
        print("Error: Could not extract head from heatmap.html")
        return

    heatmap_head = head_match.group(1)

    # Extract the body content (map div and scripts)
    body_match = re.search(r'<body>(.*?)</body>', heatmap_content, re.DOTALL)
    if not body_match:
        print("Error: Could not extract body from heatmap.html")
        return

    heatmap_body = body_match.group(1)

    # Build the embedded page
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activity Heatmap</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400&display=swap" rel="stylesheet">

    {heatmap_head}

    <style>
        /* Override default folium styles for full-screen layout */
        html, body {{
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        body {{
            display: flex;
            flex-direction: column;
            background: #fafafa;
        }}

        .map-wrapper {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}

        /* Target the folium map div */
        .folium-map {{
            position: absolute !important;
            top: 0 !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: 100% !important;
            width: 100% !important;
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
            z-index: 1000;
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
    <div class="map-wrapper">
        {heatmap_body}
    </div>
    <div class="footer">
        <span class="footer-name">Jesse Alloy</span>
        <span class="footer-count">{stats.get('total_activities', 0)} activities</span>
    </div>
</body>
</html>
"""

    # Save index.html
    with open('index.html', 'w') as f:
        f.write(html)

    print("✓ Website built: index.html (map embedded directly)")
    print("\nFiles needed for deployment:")
    print("  - index.html (self-contained)")
    print("  - stats.json")


if __name__ == "__main__":
    build_website()
