#!/usr/bin/env python3
"""
Generate statistics from activities.geojson for the website.
"""

import json
import os
from datetime import datetime
from collections import defaultdict


class StatsGenerator:
    """Generate activity statistics"""

    def __init__(self, geojson_file='activities.geojson'):
        self.geojson_file = geojson_file
        self.stats = {}

    def generate(self):
        """Generate all statistics"""
        if not os.path.exists(self.geojson_file):
            print(f"Error: {self.geojson_file} not found!")
            return None

        with open(self.geojson_file, 'r') as f:
            data = json.load(f)

        features = data.get('features', [])

        if not features:
            return None

        # Basic stats
        total_activities = len(features)
        total_points = sum(len(f['geometry']['coordinates']) for f in features)

        # Activity types
        activity_types = defaultdict(int)
        for feature in features:
            activity_type = feature['properties'].get('type', 'Unknown')
            activity_types[activity_type] += 1

        # Distance stats (if available)
        total_distance = 0
        activities_with_distance = 0
        for feature in features:
            distance = feature['properties'].get('distance', 0)
            if distance > 0:
                total_distance += distance
                activities_with_distance += 1

        # Time range and find last activity
        times_with_features = []
        for feature in features:
            time_str = feature['properties'].get('time')
            if time_str:
                try:
                    time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    times_with_features.append((time, feature))
                except:
                    pass

        first_activity = None
        last_activity = None
        last_activity_details = None

        if times_with_features:
            times_with_features.sort(key=lambda x: x[0])
            first_activity = times_with_features[0][0].strftime('%Y-%m-%d')

            # Get last activity details
            last_time, last_feature = times_with_features[-1]
            last_activity = last_time.strftime('%Y-%m-%d')

            last_activity_details = {
                'name': last_feature['properties'].get('name', 'Unnamed'),
                'type': last_feature['properties'].get('type', 'Activity'),
                'date': last_time.strftime('%b %d, %Y'),
                'distance_km': round(last_feature['properties'].get('distance', 0) / 1000, 1) if last_feature['properties'].get('distance') else None
            }

        # Calculate center point
        all_coords = []
        for feature in features:
            coords = feature['geometry']['coordinates']
            all_coords.extend(coords)

        avg_lat = sum(c[1] for c in all_coords) / len(all_coords)
        avg_lon = sum(c[0] for c in all_coords) / len(all_coords)

        # Build stats object
        self.stats = {
            'generated': datetime.now().isoformat(),
            'total_activities': total_activities,
            'total_gps_points': total_points,
            'total_distance_km': round(total_distance / 1000, 1) if total_distance > 0 else None,
            'activity_types': dict(activity_types),
            'date_range': {
                'first': first_activity,
                'last': last_activity
            },
            'last_activity': last_activity_details,
            'center': {
                'lat': round(avg_lat, 4),
                'lon': round(avg_lon, 4)
            }
        }

        return self.stats

    def save(self, output_file='stats.json'):
        """Save stats to JSON file"""
        if not self.stats:
            self.generate()

        if not self.stats:
            print("No stats to save")
            return

        with open(output_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

        print(f"✓ Stats saved to {output_file}")

    def print_stats(self):
        """Print stats to console"""
        if not self.stats:
            return

        print(f"\n{'='*60}")
        print("Activity Statistics")
        print(f"{'='*60}")
        print(f"Total Activities: {self.stats['total_activities']}")
        print(f"Total GPS Points: {self.stats['total_gps_points']:,}")

        if self.stats['total_distance_km']:
            print(f"Total Distance: {self.stats['total_distance_km']:,} km")

        print(f"\nDate Range: {self.stats['date_range']['first']} to {self.stats['date_range']['last']}")

        print(f"\nActivity Types:")
        for activity_type, count in sorted(self.stats['activity_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {activity_type}: {count}")

        print(f"\nMap Center: {self.stats['center']['lat']}, {self.stats['center']['lon']}")
        print(f"{'='*60}")


def main():
    """Main function"""
    generator = StatsGenerator()
    generator.generate()
    generator.print_stats()
    generator.save()


if __name__ == "__main__":
    main()
