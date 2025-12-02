#!/usr/bin/env python3
"""
Helper script to refresh Strava access token using a refresh token.
Used in automated workflows (GitHub Actions).
"""

import requests
import json
import os
import sys


def refresh_access_token():
    """Refresh the access token using refresh token"""

    # Try to load from environment first (GitHub Actions)
    client_id = os.environ.get('STRAVA_CLIENT_ID')
    client_secret = os.environ.get('STRAVA_CLIENT_SECRET')
    refresh_token = os.environ.get('STRAVA_REFRESH_TOKEN')

    # Fall back to config and tokens files
    if not client_id or not client_secret:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                client_id = config.get('client_id')
                client_secret = config.get('client_secret')

    if not refresh_token:
        if os.path.exists('strava_tokens.json'):
            with open('strava_tokens.json', 'r') as f:
                tokens = json.load(f)
                refresh_token = tokens.get('refresh_token')

    if not all([client_id, client_secret, refresh_token]):
        print("Error: Missing credentials for token refresh")
        print("Need: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN")
        return None

    # Request new access token
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )

    if response.status_code != 200:
        print(f"Error refreshing token: {response.status_code}")
        print(response.text)
        return None

    data = response.json()

    # Save new tokens
    tokens = {
        'access_token': data['access_token'],
        'refresh_token': data['refresh_token']
    }

    with open('strava_tokens.json', 'w') as f:
        json.dump(tokens, f)

    print("✓ Token refreshed successfully")
    return tokens


if __name__ == "__main__":
    result = refresh_access_token()
    sys.exit(0 if result else 1)
