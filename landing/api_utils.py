import requests
import base64
from django.conf import settings
import re

def get_spotify_access_token():
    auth_string = f"{settings.SPOTIFY_API_CLIENT_ID}:{settings.SPOTIFY_API_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')
    
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def fetch_spotify_track_details(track_url):
    try:
        # Extract track ID from URL
        track_id = None
        if 'spotify.com/track/' in track_url:
            track_id = track_url.split('spotify.com/track/')[1].split('?')[0]
        
        if not track_id:
            return None
            
        access_token = get_spotify_access_token()
        if not access_token:
            return None
            
        url = f'https://api.spotify.com/v1/tracks/{track_id}'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {
                'artist_name': ', '.join([artist['name'] for artist in data['artists']]),
                'song_title': data['name'],
                'album_cover': data['album']['images'][0]['url'] if data['album']['images'] else None,
                'duration_ms': data['duration_ms'],
                'isrc': data.get('external_ids', {}).get('isrc', '')
            }
    except Exception as e:
        print(f"Error fetching Spotify track: {e}")
    return None

def fetch_youtube_video_details(video_url):
    try:
        # Extract video ID from URL
        video_id = None
        if 'youtube.com/watch?v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1].split('?')[0]
        
        if not video_id:
            return None
            
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id={video_id}&key={settings.YOUTUBE_API_KEY}'
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                item = data['items'][0]
                return {
                    'artist_name': item['snippet']['channelTitle'],
                    'song_title': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'duration': item['contentDetails']['duration']
                }
    except Exception as e:
        print(f"Error fetching YouTube video: {e}")
    return None