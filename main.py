import os
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

# Set up client credentials manager
auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Function to clean and process input text
def process_text(text):
    # Remove punctuation and split into words
    text = re.sub(r'[^\w\s]', '', text)
    words = text.lower().strip().split()
    # Optional: remove common stopwords
    stopwords = {"is", "a", "the", "and", "or", "with", "of", "in", "on", "to", "for"}
    filtered = [word for word in words if word not in stopwords]
    return filtered

# Function to search for a song
def search_song(sp, word):
    results = sp.search(q=word, type='track', limit=1)
    tracks = results.get('tracks', {}).get('items', [])
    if tracks:
        track = tracks[0]
        title = track['name']
        artist = track['artists'][0]['name']
        url = track['external_urls']['spotify']
        return {"title": title, "artist": artist, "url": url}
    return None

# Streamlit app
def main():
    st.set_page_config(page_title="Text to Spotify Search", layout="centered")
    st.title("🎧 Text to Spotify Song Finder")

    user_input = st.text_area("Enter your message:", "Life is a journey with highs and lows.")

    if st.button("Find Songs"):
        words = process_text(user_input)
        st.subheader("🎼 Matching Songs:")

        found = False
        for word in words:
            result = search_song(sp, word)
            if result:
                found = True
                st.markdown(f"**{result['title']}** by *{result['artist']}*  \n[Listen on Spotify]({result['url']})")
            else:
                st.warning(f"No track found for: **{word}**")

        if not found:
            st.error("No matching songs found for the input.")

if __name__ == "__main__":
    main()
