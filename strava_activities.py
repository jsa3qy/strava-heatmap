#!/usr/bin/env python3
"""
Strava Activity Fetcher
A simple script to authenticate with Strava API and fetch your latest activities.
"""

import requests
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os


class StravaAuth:
    """Handle Strava OAuth authentication"""

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_code = None
        self.access_token = None
        self.refresh_token = None

    def authenticate(self):
        """Run the OAuth flow to get access token"""
        # Check if we have saved tokens
        if os.path.exists('strava_tokens.json'):
            with open('strava_tokens.json', 'r') as f:
                tokens = json.load(f)
                self.access_token = tokens.get('access_token')
                self.refresh_token = tokens.get('refresh_token')
                print("Loaded saved tokens")
                return

        # Start OAuth flow
        auth_url = (
            f"https://www.strava.com/oauth/authorize?"
            f"client_id={self.client_id}&"
            f"redirect_uri=http://localhost:8000/authorized&"
            f"response_type=code&"
            f"scope=activity:read_all"
        )

        print("Opening browser for Strava authorization...")
        print(f"If browser doesn't open, visit: {auth_url}")
        webbrowser.open(auth_url)

        # Start local server to receive callback
        self._start_callback_server()

        # Exchange code for token
        self._exchange_code_for_token()

    def _start_callback_server(self):
        """Start a local server to receive the OAuth callback"""
        auth_instance = self

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                query_components = parse_qs(urlparse(self.path).query)
                auth_instance.auth_code = query_components.get('code', [None])[0]

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Authorization successful!</h1><p>You can close this window and return to your terminal.</p></body></html>')

            def log_message(self, format, *args):
                pass  # Suppress server logs

        server = HTTPServer(('localhost', 8000), CallbackHandler)
        print("Waiting for authorization...")
        server.handle_request()

    def _exchange_code_for_token(self):
        """Exchange authorization code for access token"""
        if not self.auth_code:
            raise Exception("No authorization code received")

        response = requests.post(
            'https://www.strava.com/oauth/token',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': self.auth_code,
                'grant_type': 'authorization_code'
            }
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']

            # Save tokens for future use
            with open('strava_tokens.json', 'w') as f:
                json.dump({
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token
                }, f)

            print("Authentication successful!")
        else:
            raise Exception(f"Token exchange failed: {response.text}")


class StravaClient:
    """Interact with Strava API"""

    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://www.strava.com/api/v3"

    def get_athlete(self):
        """Get authenticated athlete info"""
        response = requests.get(
            f"{self.base_url}/athlete",
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        return response.json() if response.status_code == 200 else None

    def get_activities(self, per_page=10):
        """Get athlete's recent activities"""
        response = requests.get(
            f"{self.base_url}/athlete/activities",
            headers={'Authorization': f'Bearer {self.access_token}'},
            params={'per_page': per_page}
        )
        return response.json() if response.status_code == 200 else None

    def display_activities(self, activities):
        """Display activities in a readable format"""
        if not activities:
            print("No activities found")
            return

        print(f"\n{'='*80}")
        print(f"Your {len(activities)} Most Recent Activities")
        print(f"{'='*80}\n")

        for i, activity in enumerate(activities, 1):
            name = activity.get('name', 'Unnamed')
            activity_type = activity.get('type', 'Unknown')
            distance = activity.get('distance', 0) / 1000  # Convert to km
            moving_time = activity.get('moving_time', 0) / 60  # Convert to minutes
            date = activity.get('start_date_local', 'Unknown')[:10]

            print(f"{i}. {name}")
            print(f"   Type: {activity_type}")
            print(f"   Date: {date}")
            print(f"   Distance: {distance:.2f} km")
            print(f"   Duration: {moving_time:.0f} minutes")

            if activity.get('average_speed'):
                avg_pace = 1000 / (activity['average_speed'] * 60)  # min/km
                print(f"   Avg Pace: {int(avg_pace)}:{int((avg_pace % 1) * 60):02d} /km")

            print()


def main():
    """Main function"""
    # Load configuration
    if not os.path.exists('config.json'):
        print("Error: config.json not found!")
        print("Please create config.json with your Strava API credentials.")
        print("See config.example.json for template.")
        return

    with open('config.json', 'r') as f:
        config = json.load(f)

    client_id = config.get('client_id')
    client_secret = config.get('client_secret')

    if not client_id or not client_secret:
        print("Error: Missing client_id or client_secret in config.json")
        return

    # Authenticate
    auth = StravaAuth(client_id, client_secret)
    auth.authenticate()

    # Create client and fetch activities
    client = StravaClient(auth.access_token)

    # Get athlete info
    athlete = client.get_athlete()
    if athlete:
        print(f"\nHello, {athlete.get('firstname')} {athlete.get('lastname')}!")

    # Get and display activities
    activities = client.get_activities(per_page=10)
    client.display_activities(activities)


if __name__ == "__main__":
    main()
