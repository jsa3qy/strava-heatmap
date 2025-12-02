#!/usr/bin/env python3
"""
Fetch new activities from Strava API and update GeoJSON file.
This script checks for activities newer than the latest one in the GeoJSON file.
"""

import requests
import json
import os
from datetime import datetime
from strava_activities import StravaAuth


class ActivityUpdater:
    """Update GeoJSON with new Strava activities"""

    def __init__(self, geojson_file='activities.geojson'):
        self.geojson_file = geojson_file
        self.access_token = None
        self.new_activities = 0

    def authenticate(self):
        """Authenticate with Strava"""
        if not os.path.exists('config.json'):
            print("Error: config.json not found!")
            return False

        with open('config.json', 'r') as f:
            config = json.load(f)

        auth = StravaAuth(config['client_id'], config['client_secret'])
        auth.authenticate()
        self.access_token = auth.access_token
        return True

    def get_latest_activity_time(self):
        """Get the timestamp of the most recent activity in GeoJSON"""
        if not os.path.exists(self.geojson_file):
            return None

        with open(self.geojson_file, 'r') as f:
            data = json.load(f)

        if not data.get('features'):
            return None

        # Find the most recent activity
        latest_time = None
        for feature in data['features']:
            time_str = feature['properties'].get('time')
            if time_str:
                time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                if not latest_time or time > latest_time:
                    latest_time = time

        return latest_time

    def fetch_activity_stream(self, activity_id):
        """Fetch GPS stream data for an activity"""
        response = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}/streams",
            headers={'Authorization': f'Bearer {self.access_token}'},
            params={
                'keys': 'latlng,altitude',
                'key_by_type': True
            }
        )

        if response.status_code != 200:
            return None

        return response.json()

    def fetch_new_activities(self):
        """Fetch activities from Strava API"""
        latest_time = self.get_latest_activity_time()

        print("Fetching new activities from Strava...")
        if latest_time:
            print(f"Looking for activities after {latest_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Fetch recent activities
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={'Authorization': f'Bearer {self.access_token}'},
            params={'per_page': 100}  # Adjust as needed
        )

        if response.status_code != 200:
            print(f"Error fetching activities: {response.status_code}")
            return []

        activities = response.json()

        # Filter for new activities
        new_activities = []
        for activity in activities:
            activity_time = datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))

            if latest_time and activity_time <= latest_time:
                continue

            # Only process activities with GPS data
            if not activity.get('map') or not activity['map'].get('summary_polyline'):
                continue

            new_activities.append(activity)

        return new_activities

    def activity_to_geojson_feature(self, activity, stream_data):
        """Convert Strava activity to GeoJSON feature"""
        if not stream_data or 'latlng' not in stream_data:
            return None

        # Build coordinates array
        latlng = stream_data['latlng']['data']
        altitude = stream_data.get('altitude', {}).get('data', [])

        coordinates = []
        for i, (lat, lng) in enumerate(latlng):
            alt = altitude[i] if i < len(altitude) else 0
            # GeoJSON uses [longitude, latitude, altitude]
            coordinates.append([lng, lat, alt])

        if not coordinates:
            return None

        # Create feature
        feature = {
            "type": "Feature",
            "properties": {
                "name": activity['name'],
                "time": activity['start_date'],
                "activity_id": activity['id'],
                "type": activity['type'],
                "distance": activity.get('distance', 0),
                "point_count": len(coordinates)
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            }
        }

        return feature

    def update_geojson(self):
        """Main update process"""
        if not self.authenticate():
            return

        # Fetch new activities
        new_activities = self.fetch_new_activities()

        if not new_activities:
            print("✓ No new activities found")
            return

        print(f"Found {len(new_activities)} new activities")

        # Load existing GeoJSON
        if os.path.exists(self.geojson_file):
            with open(self.geojson_file, 'r') as f:
                geojson = json.load(f)
        else:
            geojson = {
                "type": "FeatureCollection",
                "metadata": {},
                "features": []
            }

        # Process each new activity
        for i, activity in enumerate(new_activities, 1):
            print(f"Processing {i}/{len(new_activities)}: {activity['name']}")

            stream_data = self.fetch_activity_stream(activity['id'])
            if not stream_data:
                print(f"  ⚠ No GPS data available")
                continue

            feature = self.activity_to_geojson_feature(activity, stream_data)
            if feature:
                geojson['features'].append(feature)
                self.new_activities += 1
                print(f"  ✓ Added {len(feature['geometry']['coordinates'])} GPS points")

        # Update metadata
        total_points = sum(len(f['geometry']['coordinates']) for f in geojson['features'])
        geojson['metadata'] = {
            "last_updated": datetime.now().isoformat(),
            "total_activities": len(geojson['features']),
            "total_points": total_points
        }

        # Save updated GeoJSON
        with open(self.geojson_file, 'w') as f:
            json.dump(geojson, f, indent=2)

        print(f"\n{'='*60}")
        print(f"✓ Added {self.new_activities} new activities to {self.geojson_file}")
        print(f"Total activities: {len(geojson['features'])}")
        print(f"Total GPS points: {total_points:,}")
        print(f"{'='*60}")


def main():
    """Main function"""
    updater = ActivityUpdater()
    updater.update_geojson()


if __name__ == "__main__":
    main()
