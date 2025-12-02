#!/usr/bin/env python3
"""
Generate a static PNG heatmap for mobile devices.
Uses matplotlib and contextily for a static map with basemap.
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches


class StaticHeatmapGenerator:
    """Generate static PNG heatmap"""

    def __init__(self, geojson_file='activities.geojson', output_file='heatmap_static.png'):
        self.geojson_file = geojson_file
        self.output_file = output_file
        self.all_coords = []

    def load_geojson(self):
        """Load GeoJSON file and extract coordinates"""
        if not os.path.exists(self.geojson_file):
            print(f"Error: {self.geojson_file} not found!")
            return False

        with open(self.geojson_file, 'r') as f:
            data = json.load(f)

        if not data.get('features'):
            print("No activities found in GeoJSON file")
            return False

        # Extract all coordinates
        for feature in data['features']:
            if feature['geometry']['type'] == 'LineString':
                coords = feature['geometry']['coordinates']
                # coords are [lon, lat, alt]
                self.all_coords.extend([[c[1], c[0]] for c in coords])

        print(f"Loaded {len(self.all_coords):,} GPS points")
        return True

    def create_heatmap(self, center_lat=61.2181, center_lon=-149.9003, zoom=10):
        """Create static heatmap image

        Args:
            center_lat: Center latitude (default: Anchorage)
            center_lon: Center longitude (default: Anchorage)
            zoom: Zoom level approximation (higher = closer)
        """
        if not self.all_coords:
            return None

        # Extract lats and lons
        lats = [c[0] for c in self.all_coords]
        lons = [c[1] for c in self.all_coords]

        # Calculate bounds with padding
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        padding = 0.1  # 10% padding

        lat_min = min(lats) - lat_range * padding
        lat_max = max(lats) + lat_range * padding
        lon_min = min(lons) - lon_range * padding
        lon_max = max(lons) + lon_range * padding

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10), dpi=150)

        # Create custom colormap (blue -> cyan -> lime -> yellow -> red)
        colors = ['#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('heatmap', colors, N=n_bins)

        # Create 2D histogram for heatmap
        H, xedges, yedges = np.histogram2d(
            lons, lats,
            bins=200,
            range=[[lon_min, lon_max], [lat_min, lat_max]]
        )

        # Apply gaussian blur effect
        from scipy.ndimage import gaussian_filter
        H = gaussian_filter(H, sigma=1.5)

        # Plot heatmap
        extent = [lon_min, lon_max, lat_min, lat_max]
        im = ax.imshow(
            H.T,
            extent=extent,
            origin='lower',
            cmap=cmap,
            alpha=0.7,
            aspect='auto',
            interpolation='bilinear'
        )

        # Set limits
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)

        # Add gridlines
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        # Labels
        ax.set_xlabel('Longitude', fontsize=10)
        ax.set_ylabel('Latitude', fontsize=10)
        ax.set_title('Activity Heatmap', fontsize=14, fontweight='bold', pad=20)

        # Add scale indicator
        ax.text(
            0.02, 0.98,
            f'{len(self.all_coords):,} GPS points',
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        # Tight layout
        plt.tight_layout()

        # Save
        plt.savefig(
            self.output_file,
            dpi=150,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none'
        )
        plt.close()

        print(f"✓ Static heatmap saved to {self.output_file}")
        return True


def main():
    """Main function"""
    # Check for scipy
    try:
        from scipy.ndimage import gaussian_filter
    except ImportError:
        print("Installing scipy for image processing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'scipy'])

    generator = StaticHeatmapGenerator()
    if generator.load_geojson():
        # Auto-calculate center from data
        lats = [c[0] for c in generator.all_coords]
        lons = [c[1] for c in generator.all_coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        generator.create_heatmap(center_lat=center_lat, center_lon=center_lon)


if __name__ == "__main__":
    main()
