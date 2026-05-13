"""
Module for music player classes: Track and Album.

Provides track-level playback control (play, pause, stop, seek, simulate) and
album-level playback (play album, next/previous track, pause/resume, stop).
"""

import time
from typing import List, Optional


# ----------------------------------------------------------------------
# Track class
# ----------------------------------------------------------------------
class Track:
    """A musical track with metadata and playback state."""

    def __init__(self, title: str, duration_seconds: int, artist: str, album_year: int) -> None:
        """
        Initialise a track.

        Args:
            title: Track title.
            duration_seconds: Duration in seconds.
            artist: Artist name.
            album_year: Year of the album.
        """
        self.title = title
        self.duration = duration_seconds   # duration in seconds
        self.artist = artist
        self.album_year = album_year
        self._is_playing = False
        self._is_paused = False
        self._current_position = 0         # current playback position (seconds)

    def play(self) -> None:
        """Start or resume playback from the current position."""
        if self._is_playing:
            print(f"'{self.title}' is already playing.")
            return
        if self._is_paused:
            print(f"Resuming '{self.title}' from {self._format_time(self._current_position)}.")
            self._is_playing = True
            self._is_paused = False
        else:
            print(f"Starting playback of '{self.title}' ({self._format_time(self.duration)})")
            self._is_playing = True
            self._current_position = 0

    def pause(self) -> None:
        """Pause playback, keeping the current position."""
        if not self._is_playing:
            print(f"Track '{self.title}' is not playing, cannot pause.")
            return
        self._is_playing = False
        self._is_paused = True
        print(f"Track '{self.title}' paused at {self._format_time(self._current_position)}.")

    def stop(self) -> None:
        """Stop playback and reset position to the beginning."""
        if not self._is_playing and not self._is_paused:
            print(f"Track '{self.title}' is already stopped.")
            return
        self._is_playing = False
        self._is_paused = False
        self._current_position = 0
        print(f"Playback of '{self.title}' stopped.")

    def seek(self, seconds: int) -> None:
        """
        Seek to a specific second (only while playing or paused).

        Args:
            seconds: Target position in seconds (clamped to [0, duration]).
        """
        if not self._is_playing and not self._is_paused:
            print("Seeking is only available during playback or pause.")
            return
        if seconds < 0:
            seconds = 0
        if seconds > self.duration:
            seconds = self.duration
        self._current_position = seconds
        print(f"Seeked '{self.title}' to {self._format_time(seconds)}.")

    def simulate_play(self, seconds: int = 1) -> None:
        """
        Simulate playing for a given number of seconds.

        Advances the current position and stops the track if it finishes.

        Args:
            seconds: Number of seconds to simulate (default 1).
        """
        if not self._is_playing:
            print("Track is not playing, cannot simulate.")
            return
        remaining = self.duration - self._current_position
        if remaining <= 0:
            print("Track already finished.")
            self.stop()
            return
        elapsed = min(seconds, remaining)
        self._current_position += elapsed
        print(f"Simulated {elapsed} sec. Current position: {self._format_time(self._current_position)}")
        if self._current_position >= self.duration:
            print(f"Track '{self.title}' finished.")
            self.stop()

    def _format_time(self, seconds: int) -> str:
        """Convert seconds to MM:SS format."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def __repr__(self) -> str:
        return f"Track('{self.title}', {self.duration}s, {self.artist}, {self.album_year})"


# ----------------------------------------------------------------------
# Album class
# ----------------------------------------------------------------------
class Album:
    """
    An album that contains a list of tracks.

    Can control playback of the whole album (play, next/previous, pause/resume, stop).
    """

    def __init__(self, title: str, artist: str, year: int) -> None:
        """
        Initialise an album.

        Args:
            title: Album title.
            artist: Artist name.
            year: Release year.
        """
        self.title = title
        self.artist = artist
        self.year = year
        self.tracks: List[Track] = []
        self._current_track_index = 0
        self._is_playing_album = False

    def add_track(self, track: Track) -> None:
        """Add a track to the album."""
        self.tracks.append(track)

    def remove_track(self, index: int) -> None:
        """
        Remove a track by its index (0‑based).

        Args:
            index: Index of the track to remove.
        """
        if 0 <= index < len(self.tracks):
            removed = self.tracks.pop(index)
            print(f"Removed track '{removed.title}'")
        else:
            print("Invalid track index.")

    def play_album(self) -> None:
        """Start playing the album from the first track."""
        if not self.tracks:
            print("Album is empty.")
            return
        self._current_track_index = 0
        self._is_playing_album = True
        print(f"\n▶ Playing album '{self.title}' - {self.artist} ({self.year})")
        self._play_current_track()

    def _play_current_track(self) -> None:
        """Internal: start playback of the current track."""
        if self._current_track_index >= len(self.tracks):
            self.stop_album()
            return
        track = self.tracks[self._current_track_index]
        print(f"\n--- Track {self._current_track_index + 1}: {track.title} ---")
        track.play()

    def next_track(self) -> None:
        """Switch to the next track in the album."""
        if not self._is_playing_album:
            print("Album is not playing. Use play_album() first.")
            return
        # Stop the current track if it is playing
        current = self.tracks[self._current_track_index]
        current.stop()
        # Move to the next track
        if self._current_track_index + 1 < len(self.tracks):
            self._current_track_index += 1
            self._play_current_track()
        else:
            print("Album finished.")
            self.stop_album()

    def previous_track(self) -> None:
        """Switch to the previous track."""
        if not self._is_playing_album:
            print("Album is not playing.")
            return
        current = self.tracks[self._current_track_index]
        current.stop()
        if self._current_track_index - 1 >= 0:
            self._current_track_index -= 1
            self._play_current_track()
        else:
            print("This is the first track of the album.")

    def pause_album(self) -> None:
        """Pause the album (pause the current track)."""
        if not self._is_playing_album:
            print("Album is not playing.")
            return
        track = self.tracks[self._current_track_index]
        track.pause()

    def resume_album(self) -> None:
        """Resume playback of the album from the current track."""
        if not self._is_playing_album:
            print("Album was not started. Use play_album() to begin.")
            return
        track = self.tracks[self._current_track_index]
        track.play()   # play() will resume from pause if paused

    def stop_album(self) -> None:
        """Stop album playback and reset to the first track."""
        if self._is_playing_album:
            # Stop the current track if it is playing
            if self._current_track_index < len(self.tracks):
                self.tracks[self._current_track_index].stop()
            self._is_playing_album = False
            self._current_track_index = 0
            print(f"Playback of album '{self.title}' stopped.")
        else:
            print("Album is not playing.")

    def show_tracks(self) -> None:
        """Print the list of tracks in the album."""
        print(f"\nAlbum: {self.title} - {self.artist} ({self.year})")
        for idx, track in enumerate(self.tracks, 1):
            print(f"{idx}. {track.title} ({track._format_time(track.duration)})")


# ----------------------------------------------------------------------
# Demonstration
# ----------------------------------------------------------------------
def demo() -> None:
    """Run a demonstration of the Track and Album classes."""
    # Create tracks
    track1 = Track("Bohemian Rhapsody", 355, "Queen", 1975)
    track2 = Track("Another One Bites the Dust", 215, "Queen", 1980)
    track3 = Track("We Will Rock You", 122, "Queen", 1977)
    track4 = Track("We Are the Champions", 179, "Queen", 1977)

    # Create an album and add tracks
    album = Album("Greatest Hits", "Queen", 1981)
    album.add_track(track1)
    album.add_track(track2)
    album.add_track(track3)
    album.add_track(track4)

    # Show the track list
    album.show_tracks()

    # Playback demonstration
    print("\n--- Demo ---")
    album.play_album()
    time.sleep(1)                # simulate real time (optional, for visual effect)
    track1.simulate_play(30)     # simulate 30 seconds of playback
    album.pause_album()
    time.sleep(0.5)
    album.resume_album()
    track1.simulate_play(320)    # play until the track ends
    album.next_track()           # switch to the second track
    track2.simulate_play(50)
    album.previous_track()       # go back to the first track (which already finished)
    # The first track is stopped, will restart from the beginning
    album.next_track()           # again to the second track
    album.stop_album()
    print("\n--- End of demo ---")


if __name__ == "__main__":
    demo()
