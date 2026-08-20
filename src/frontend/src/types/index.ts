// src/types/index.ts

export interface User {
  id: string;
  display_name: string | null;
  email: string | null;
  images: { url: string; height: number; width: number }[];
}

export interface Playlist {
  id: string;
  name: string;
  description: string | null;
  track_count: number;
  images: { url: string; height: number; width: number }[];
  last_modified: string | null;
  snapshot_id: string | null;
  has_issues: boolean;
  issues_count: number;
}

export interface PlaylistTrack {
  track_id: string;
  track_name: string;
  artist_names: string[];
  artist_ids: string[];
  album_name: string | null;
  album_id: string | null;
  duration_ms: number;
  added_at: string;
  is_available: boolean;
  release_year: number | null;
  position: number;
}

export interface PlaylistDetail extends Playlist {
  tracks: PlaylistTrack[];
}

export interface LibraryStats {
  total_tracks: number;
  total_artists: number;
  total_hours: number;
  top_artist: { name: string; track_count: number } | null;
  genre_distribution: Record<string, number>;
  decade_distribution: Record<string, number>;
}

export interface LibraryIssues {
  duplicates_intra_count: number;
  duplicates_intra_playlists_affected: number;
  duplicates_cross_count: number;
  abandoned_playlists_count: number;
  unavailable_tracks_count: number;
  duplicates_intra?: IntraDuplicate[];
  duplicates_cross?: CrossDuplicate[];
  abandoned_playlists?: AbandonedPlaylist[];
  unavailable_tracks?: UnavailableTrack[];
}

export interface IntraDuplicate {
  playlist_id: string;
  track_id: string;
  track_name: string;
  positions: number[];
  count: number;
}

export interface CrossDuplicate {
  track_id: string;
  track_name: string;
  artist_names: string[];
  playlist_ids: string[];
  playlist_count: number;
}

export interface AbandonedPlaylist {
  id: string;
  name: string;
  track_count: number;
  last_modified: string | null;
  days_abandoned: number | null;
}

export interface UnavailableTrack {
  track_id: string;
  track_name: string | null;
  artist_names: string[];
  playlist_id: string;
  playlist_name: string;
  added_at: string;
}

export interface PlaylistIssues {
  duplicates_intra_count: number;
  unavailable_count: number;
  duplicates_intra?: IntraDuplicate[];
  unavailable_tracks?: UnavailableTrack[];
}

export interface ActionResponse {
  playlist_id: string;
  name: string;
  track_count: number;
}

export interface CreateFilterRequest {
  genres?: string[];
  decades?: string[];
  artist_ids?: string[];
  max_duration_ms?: number;
  name?: string;
}

export interface MergeRequest {
  playlist_id_1: string;
  playlist_id_2: string;
  name?: string;
}