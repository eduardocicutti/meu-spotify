# app/spotify/endpoints.py
# Constantes de endpoints da Spotify API (pós-fev/2026)

BASE_URL = "https://api.spotify.com/v1"
AUTH_URL = "https://accounts.spotify.com"
TOKEN_URL = f"{AUTH_URL}/api/token"
AUTHORIZE_URL = f"{AUTH_URL}/authorize"

# Endpoints utilizados no V1
ENDPOINTS = {
    # Perfil
    "me": "/me",
    "me_playlists": "/me/playlists",
    "me_tracks": "/me/tracks",
    "me_albums": "/me/albums",
    "me_top_artists": "/me/top/artists",
    "me_top_tracks": "/me/top/tracks",
    "me_recently_played": "/me/player/recently-played",
    "me_following": "/me/following",
    
    # Playlists
    "playlist": "/playlists/{playlist_id}",
    "playlist_items": "/playlists/{playlist_id}/items",
    "playlist_cover": "/playlists/{playlist_id}/images",
    
    # Artistas (para buscar gêneros)
    "artist": "/artists/{artist_id}",
    "artists_batch": "/artists",
    
    # Tracks
    "track": "/tracks/{track_id}",
    "tracks_batch": "/tracks",
    "audio_features": "/audio-features",
    "audio_features_track": "/audio-features/{track_id}",
    
    # Search
    "search": "/search",
}

# Scopes necessários
SCOPES_V1 = [
    "user-read-private",
    "user-read-email",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
]

SCOPES_V2_WRITE = [
    "playlist-modify-public",
    "playlist-modify-private",
    "user-library-modify",
]

# Field masks para reduzir payload
FIELDS = {
    "playlist_list": "items(id,name,description,public,collaborative,owner,tracks.total,images,snapshot_id,external_urls),next,total",
    "playlist_items": "items(added_at,added_by,is_local,track(id,name,duration_ms,is_available,explicit,artists(id,name),album(id,name,release_date,release_date_precision,images,artists))),next,total",
    "saved_tracks": "items(added_at,track(id,name,duration_ms,is_available,explicit,artists(id,name),album(id,name,release_date,release_date_precision,images,artists))),next,total",
    "top_artists": "items(id,name,genres,popularity,followers.total,images,external_urls)",
    "top_tracks": "items(id,name,duration_ms,is_available,explicit,artists(id,name),album(id,name,release_date,release_date_precision,images,artists),external_urls)",
    "artist": "id,name,genres,popularity,followers.total,images,external_urls",
}

# Limites de paginação
PAGINATION_LIMITS = {
    "playlists": 50,
    "playlist_items": 100,
    "saved_tracks": 50,
    "top_items": 50,
    "search": 10,  # Reduzido para 10 em fev/2026
}