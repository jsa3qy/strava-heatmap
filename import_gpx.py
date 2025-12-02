#!/usr/bin/env python3
"""
Import GPX files from Strava bulk export into GeoJSON format.
This script processes all GPX files and creates a combined GeoJSON file.
"""

import gpxpy
import json
import os
from pathlib import Path
from datetime import datetime


class GPXImporter:
    """Import and process GPX files into GeoJSON"""

    def __init__(self, output_file='activities.geojson'):
        self.output_file = output_file
        self.features = []
        self.stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'total_points': 0
        }

    def import_gpx_file(self, gpx_path):
        """Import a single GPX file and convert to GeoJSON feature"""
        try:
            with open(gpx_path, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)

            # Extract all track points
            coordinates = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        # GeoJSON uses [longitude, latitude] order
                        coordinates.append([
                            point.longitude,
                            point.latitude,
                            point.elevation if point.elevation else 0
                        ])

            if not coordinates:
                return None

            # Get metadata
            activity_name = gpx.tracks[0].name if gpx.tracks and gpx.tracks[0].name else os.path.basename(gpx_path)
            activity_time = None

            if gpx.tracks and gpx.tracks[0].segments and gpx.tracks[0].segments[0].points:
                activity_time = gpx.tracks[0].segments[0].points[0].time
                if activity_time:
                    activity_time = activity_time.isoformat()

            # Create GeoJSON feature
            feature = {
                "type": "Feature",
                "properties": {
                    "name": activity_name,
                    "time": activity_time,
                    "source_file": os.path.basename(gpx_path),
                    "point_count": len(coordinates)
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                }
            }

            self.stats['total_points'] += len(coordinates)
            return feature

        except Exception as e:
            print(f"Error processing {gpx_path}: {e}")
            return None

    def import_directory(self, directory_path):
        """Import all GPX files from a directory"""
        directory = Path(directory_path)

        if not directory.exists():
            print(f"Error: Directory {directory_path} does not exist")
            return

        gpx_files = list(directory.glob('*.gpx'))

        if not gpx_files:
            print(f"No GPX files found in {directory_path}")
            return

        print(f"Found {len(gpx_files)} GPX files")
        print("Processing...")

        for i, gpx_file in enumerate(gpx_files, 1):
            self.stats['total_files'] += 1

            if i % 10 == 0:
                print(f"Processed {i}/{len(gpx_files)} files...")

            feature = self.import_gpx_file(gpx_file)

            if feature:
                self.features.append(feature)
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1

        self.save_geojson()
        self.print_stats()

    def save_geojson(self):
        """Save features to GeoJSON file"""
        geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_activities": len(self.features),
                "total_points": self.stats['total_points']
            },
            "features": self.features
        }

        with open(self.output_file, 'w') as f:
            json.dump(geojson, f, indent=2)

        print(f"\n✓ Saved to {self.output_file}")

    def print_stats(self):
        """Print import statistics"""
        print(f"\n{'='*60}")
        print("Import Statistics")
        print(f"{'='*60}")
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"Successful imports: {self.stats['successful']}")
        print(f"Failed imports: {self.stats['failed']}")
        print(f"Total GPS points: {self.stats['total_points']:,}")
        print(f"{'='*60}")


def main():
    """Main function"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_gpx.py <path_to_gpx_directory>")
        print("\nExample:")
        print("  python import_gpx.py ./strava_export/activities")
        print("\nThis will create activities.geojson with all your GPS tracks")
        return

    directory_path = sys.argv[1]

    importer = GPXImporter(output_file='activities.geojson')
    importer.import_directory(directory_path)


if __name__ == "__main__":
    main()
