#!/usr/bin/env python3
"""
Generate an interactive heatmap from GeoJSON activity data.
Creates an HTML file with a zoomable, pannable heatmap visualization.
"""

import json
import folium
from folium.plugins import HeatMap
import webbrowser
import os


class HeatmapGenerator:
    """Generate interactive heatmap from activity data"""

    def __init__(self, geojson_file='activities.geojson', output_file='heatmap.html'):
        self.geojson_file = geojson_file
        self.output_file = output_file
        self.all_points = []

    def load_geojson(self):
        """Load GeoJSON file and extract all GPS points"""
        if not os.path.exists(self.geojson_file):
            print(f"Error: {self.geojson_file} not found!")
            print("Run import_gpx.py first to create the GeoJSON file")
            return False

        with open(self.geojson_file, 'r') as f:
            data = json.load(f)

        if not data.get('features'):
            print("No activities found in GeoJSON file")
            return False

        print(f"Loading {len(data['features'])} activities...")

        # Extract all coordinate points
        for feature in data['features']:
            if feature['geometry']['type'] == 'LineString':
                coords = feature['geometry']['coordinates']
                # Convert from [lon, lat, alt] to [lat, lon] for folium
                for coord in coords:
                    self.all_points.append([coord[1], coord[0]])

        print(f"Loaded {len(self.all_points):,} GPS points")
        return True

    def calculate_center(self):
        """Calculate center point of all activities"""
        if not self.all_points:
            return [0, 0]

        avg_lat = sum(p[0] for p in self.all_points) / len(self.all_points)
        avg_lon = sum(p[1] for p in self.all_points) / len(self.all_points)

        return [avg_lat, avg_lon]

    def create_heatmap(self, gradient=None, center=None, zoom_start=11):
        """Create the heatmap visualization

        Args:
            gradient: Color gradient dictionary
            center: [lat, lon] to center the map (default: Anchorage, AK)
            zoom_start: Initial zoom level
        """
        if not self.all_points:
            return None

        # Use Anchorage, Alaska as default center (1.5 miles SE of downtown)
        if center is None:
            center = [61.2027, -149.8691]  # Anchorage, AK

        print(f"Map center: {center[0]:.4f}, {center[1]:.4f}")

        # Create base map
        m = folium.Map(
            location=center,
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )

        # Add additional tile layers
        folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
        folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)

        # Default gradient (blue to red)
        if gradient is None:
            gradient = {
                0.0: 'blue',
                0.3: 'cyan',
                0.5: 'lime',
                0.7: 'yellow',
                1.0: 'red'
            }

        # Create heatmap layer
        print("Generating heatmap...")
        HeatMap(
            self.all_points,
            min_opacity=0.4,
            max_zoom=18,
            radius=2,
            blur=1,
            gradient=gradient
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        return m

    def _inject_mobile_fix(self):
        """Inject mobile fixes and footer directly into heatmap.html"""
        # Read the generated HTML
        with open(self.output_file, 'r') as f:
            html = f.read()

        # Fix the viewport meta tag for mobile (add viewport-fit=cover)
        html = html.replace(
            'width=device-width,\n                initial-scale=1.0, maximum-scale=1.0, user-scalable=no',
            'width=device-width, initial-scale=1.0, viewport-fit=cover'
        )

        # Fix body/html sizing - replace folium's default with explicit sizing
        html = html.replace(
            '<style>html, body {width: 100%;height: 100%;margin: 0;padding: 0;}</style>',
            '''<style>
html, body {
    width: 100%;
    height: 100vh;
    height: 100dvh;
    margin: 0;
    padding: 0;
    overflow: hidden;
}
</style>'''
        )

        # Add footer styles and content before </body>
        footer_content = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400&display=swap');
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #f5f5f5;
    padding: 18px 28px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 32px;
    border-top: 1px solid #d4d4d4;
    font-size: 13px;
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    letter-spacing: 0.02em;
    z-index: 1000;
}
.footer-item { display: flex; align-items: center; gap: 6px; }
.footer-label { font-weight: 400; color: #171717; }
.footer-value { font-weight: 300; color: #737373; }
.footer-separator { color: #d4d4d4; }
@media (max-width: 768px) {
    .footer {
        padding: 14px 18px;
        font-size: 12px;
        flex-direction: column;
        gap: 8px;
        padding-bottom: max(14px, env(safe-area-inset-bottom));
    }
    .footer-separator { display: none; }
}
/* Force map container to fill viewport minus footer */
.folium-map {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 70px !important;
    width: auto !important;
    height: calc(100vh - 70px) !important;
    height: calc(100dvh - 70px) !important;
}
@media (max-width: 768px) {
    .folium-map {
        bottom: 85px !important;
        height: calc(100vh - 85px) !important;
        height: calc(100dvh - 85px) !important;
    }
}
</style>
<div class="footer">
    <div class="footer-item">
        <span class="footer-label">Jesse Alloy</span>
    </div>
    <span class="footer-separator">·</span>
    <div class="footer-item">
        <span class="footer-value">84 activities</span>
    </div>
    <span class="footer-separator">·</span>
    <div class="footer-item">
        <span class="footer-label">Latest:</span>
        <span class="footer-value">Afternoon Trail Run</span>
    </div>
    <span class="footer-separator">·</span>
    <div class="footer-item">
        <span class="footer-value">Dec 01, 2025</span>
    </div>
</div>
'''
        # Add script to invalidate map size after load
        resize_script = '''
<script>
// Wait for map to initialize then fix size
window.addEventListener('load', function() {
    setTimeout(function() {
        for (var key in window) {
            try {
                if (key.indexOf('map_') === 0 && window[key] && window[key].invalidateSize) {
                    window[key].invalidateSize();
                }
            } catch(e) {}
        }
    }, 100);
});
</script>
'''
        html = html.replace('</body>', footer_content + resize_script + '</body>')

        # Write back
        with open(self.output_file, 'w') as f:
            f.write(html)

        print("Injected mobile fixes and footer")

    def generate(self, open_browser=True):
        """Main generation process"""
        if not self.load_geojson():
            return False

        # Create heatmap
        m = self.create_heatmap()

        if not m:
            print("Failed to create heatmap")
            return False

        # Save to HTML
        m.save(self.output_file)

        # Post-process to add mobile resize handling
        self._inject_mobile_fix()

        print(f"\n{'='*60}")
        print(f"✓ Heatmap saved to {self.output_file}")
        print(f"{'='*60}")

        # Open in browser
        if open_browser:
            abs_path = os.path.abspath(self.output_file)
            print(f"\nOpening in browser...")
            webbrowser.open(f'file://{abs_path}')

        return True


def main():
    """Main function"""
    import sys

    # Optional: custom color gradients
    gradients = {
        'default': {
            0.0: 'blue',
            0.3: 'cyan',
            0.5: 'lime',
            0.7: 'yellow',
            1.0: 'red'
        },
        'heat': {
            0.0: 'navy',
            0.25: 'blue',
            0.5: 'red',
            0.75: 'orange',
            1.0: 'yellow'
        },
        'purple': {
            0.0: 'purple',
            0.5: 'violet',
            1.0: 'pink'
        },
        'green': {
            0.0: 'darkgreen',
            0.5: 'lime',
            1.0: 'yellow'
        }
    }

    # Check for color scheme argument
    gradient = gradients['default']
    if len(sys.argv) > 1:
        scheme = sys.argv[1].lower()
        if scheme in gradients:
            gradient = gradients[scheme]
            print(f"Using '{scheme}' color scheme")
        else:
            print(f"Unknown color scheme '{scheme}', using default")
            print(f"Available schemes: {', '.join(gradients.keys())}")

    generator = HeatmapGenerator()
    generator.create_heatmap(gradient=gradient)
    generator.generate()


if __name__ == "__main__":
    main()
