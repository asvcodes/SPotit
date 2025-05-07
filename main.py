import os
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

# Define Spotify scope
SCOPE = "playlist-modify-public"

# Function to process text input
def process_text(text):
    # Remove punctuation and split into words
    text = re.sub(r'[^\w\s]', '', text)
    words = text.strip().split()
    return words

# Function to search for a song by title
def search_song(sp, title):
    results = sp.search(q=f'track:{title}', type='track', limit=1)
    tracks = results.get('tracks', {}).get('items', [])
    if tracks:
        return tracks[0]['uri']
    return None

# Streamlit application
def main():
    st.title("🎵 Text-to-Spotify Playlist Generator")

    # Authenticate with Spotify
    if 'token_info' not in st.session_state:
        sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                                client_secret=CLIENT_SECRET,
                                redirect_uri=REDIRECT_URI,
                                scope=SCOPE)
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(f"[Click here to authorize Spotify]({auth_url})")
        code = st.text_input("Enter the URL you were redirected to after authorization:")
        if code:
            code = code.split("?code=")[-1]
            token_info = sp_oauth.get_access_token(code)
            st.session_state.token_info = token_info
            st.experimental_rerun()
        return

    # Create Spotify client
    sp = spotipy.Spotify(auth=st.session_state.token_info['access_token'])

    # User input
    user_input = st.text_area("Enter your message:", "Life is a journey with highs and lows.")

    if st.button("Generate Playlist"):
        words = process_text(user_input)
        track_uris = []
        for word in words:
            uri = search_song(sp, word)
            if uri:
                track_uris.append(uri)
            else:
                st.warning(f"No song found for: {word}")

        if track_uris:
            user_id = sp.current_user()['id']
            playlist = sp.user_playlist_create(user=user_id, name="Text-Based Playlist", public=True)
            sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
            st.success(f"Playlist created: [Open in Spotify]({playlist['external_urls']['spotify']})")
        else:
            st.error("No songs found to create a playlist.")

if __name__ == "__main__":
    main()
