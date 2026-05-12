import time
from typing import List, Optional

# ----------------------------------------------------------------------
# Класс Трек
# ----------------------------------------------------------------------
class Track:
    """Музыкальный трек с метаданными и состоянием воспроизведения."""
    def __init__(self, title: str, duration_seconds: int, artist: str, album_year: int):
        self.title = title
        self.duration = duration_seconds  # длительность в секундах
        self.artist = artist
        self.album_year = album_year
        self._is_playing = False
        self._is_paused = False
        self._current_position = 0  # текущая позиция воспроизведения (сек)

    def play(self) -> None:
        """Начать воспроизведение трека с текущей позиции."""
        if self._is_playing:
            print(f"'{self.title}' уже воспроизводится.")
            return
        if self._is_paused:
            print(f"Возобновление воспроизведения '{self.title}' с {self._current_position} сек.")
            self._is_playing = True
            self._is_paused = False
        else:
            print(f"Начинаем воспроизведение '{self.title}' ({self._format_time(self.duration)})")
            self._is_playing = True
            self._current_position = 0

    def pause(self) -> None:
        """Поставить трек на паузу (сохранить позицию)."""
        if not self._is_playing:
            print(f"Трек '{self.title}' не воспроизводится, невозможно поставить на паузу.")
            return
        self._is_playing = False
        self._is_paused = True
        print(f"Трек '{self.title}' поставлен на паузу на {self._format_time(self._current_position)}.")

    def stop(self) -> None:
        """Остановить воспроизведение, сбросить позицию в начало."""
        if not self._is_playing and not self._is_paused:
            print(f"Трек '{self.title}' уже остановлен.")
            return
        self._is_playing = False
        self._is_paused = False
        self._current_position = 0
        print(f"Воспроизведение '{self.title}' остановлено.")

    def seek(self, seconds: int) -> None:
        """Перемотать на указанную секунду (если воспроизведение активно)."""
        if not self._is_playing and not self._is_paused:
            print("Перемотка доступна только во время воспроизведения или паузы.")
            return
        if seconds < 0:
            seconds = 0
        if seconds > self.duration:
            seconds = self.duration
        self._current_position = seconds
        print(f"Перемотка '{self.title}' на {self._format_time(seconds)}.")

    def simulate_play(self, seconds: int = 1) -> None:
        """Симулировать проигрывание нескольких секунд (для демонстрации)."""
        if not self._is_playing:
            print("Трек не воспроизводится, симуляция невозможна.")
            return
        remaining = self.duration - self._current_position
        if remaining <= 0:
            print("Трек уже закончился.")
            self.stop()
            return
        elapsed = min(seconds, remaining)
        self._current_position += elapsed
        print(f"Проиграно {elapsed} сек. Текущая позиция: {self._format_time(self._current_position)}")
        if self._current_position >= self.duration:
            print(f"Трек '{self.title}' закончился.")
            self.stop()

    def _format_time(self, seconds: int) -> str:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

    def __repr__(self) -> str:
        return f"Track('{self.title}', {self.duration}s, {self.artist}, {self.album_year})"


# ----------------------------------------------------------------------
# Класс Альбом
# ----------------------------------------------------------------------
class Album:
    """Альбом, содержащий список треков. Может управлять воспроизведением альбома целиком."""
    def __init__(self, title: str, artist: str, year: int):
        self.title = title
        self.artist = artist
        self.year = year
        self.tracks: List[Track] = []
        self._current_track_index = 0
        self._is_playing_album = False

    def add_track(self, track: Track) -> None:
        """Добавить трек в альбом."""
        self.tracks.append(track)

    def remove_track(self, index: int) -> None:
        """Удалить трек по индексу (0-based)."""
        if 0 <= index < len(self.tracks):
            removed = self.tracks.pop(index)
            print(f"Удалён трек '{removed.title}'")
        else:
            print("Неверный индекс трека.")

    def play_album(self) -> None:
        """Начать воспроизведение альбома с первого трека."""
        if not self.tracks:
            print("Альбом пуст.")
            return
        self._current_track_index = 0
        self._is_playing_album = True
        print(f"\n▶ Воспроизведение альбома '{self.title}' - {self.artist} ({self.year})")
        self._play_current_track()

    def _play_current_track(self) -> None:
        """Внутренний метод: запускает текущий трек."""
        if self._current_track_index >= len(self.tracks):
            self.stop_album()
            return
        track = self.tracks[self._current_track_index]
        print(f"\n--- Трек {self._current_track_index+1}: {track.title} ---")
        track.play()

    def next_track(self) -> None:
        """Переключиться на следующий трек в альбоме."""
        if not self._is_playing_album:
            print("Альбом не воспроизводится. Сначала запустите play_album().")
            return
        # Останавливаем текущий трек, если он играет
        current = self.tracks[self._current_track_index]
        current.stop()
        # Переход к следующему
        if self._current_track_index + 1 < len(self.tracks):
            self._current_track_index += 1
            self._play_current_track()
        else:
            print("Альбом закончился.")
            self.stop_album()

    def previous_track(self) -> None:
        """Переключиться на предыдущий трек."""
        if not self._is_playing_album:
            print("Альбом не воспроизводится.")
            return
        current = self.tracks[self._current_track_index]
        current.stop()
        if self._current_track_index - 1 >= 0:
            self._current_track_index -= 1
            self._play_current_track()
        else:
            print("Это первый трек альбома.")

    def pause_album(self) -> None:
        """Поставить весь альбом на паузу (текущий трек на паузу)."""
        if not self._is_playing_album:
            print("Альбом не воспроизводится.")
            return
        track = self.tracks[self._current_track_index]
        track.pause()

    def resume_album(self) -> None:
        """Возобновить воспроизведение альбома с текущего трека."""
        if not self._is_playing_album:
            print("Альбом не был запущен. Используйте play_album() для начала.")
            return
        track = self.tracks[self._current_track_index]
        track.play()  # play() возобновит с паузы if paused

    def stop_album(self) -> None:
        """Остановить воспроизведение альбома (сброс к первому треку)."""
        if self._is_playing_album:
            # Останавливаем текущий трек, если он играет
            if self._current_track_index < len(self.tracks):
                self.tracks[self._current_track_index].stop()
            self._is_playing_album = False
            self._current_track_index = 0
            print(f"Воспроизведение альбома '{self.title}' остановлено.")
        else:
            print("Альбом не воспроизводится.")

    def show_tracks(self) -> None:
        """Вывести список треков альбома."""
        print(f"\nАльбом: {self.title} - {self.artist} ({self.year})")
        for idx, track in enumerate(self.tracks, 1):
            print(f"{idx}. {track.title} ({track._format_time(track.duration)})")


# ----------------------------------------------------------------------
# Демонстрация
# ----------------------------------------------------------------------
def demo():
    # Создаём треки
    track1 = Track("Bohemian Rhapsody", 355, "Queen", 1975)
    track2 = Track("Another One Bites the Dust", 215, "Queen", 1980)
    track3 = Track("We Will Rock You", 122, "Queen", 1977)
    track4 = Track("We Are the Champions", 179, "Queen", 1977)

    # Создаём альбом и добавляем треки
    album = Album("Greatest Hits", "Queen", 1981)
    album.add_track(track1)
    album.add_track(track2)
    album.add_track(track3)
    album.add_track(track4)

    # Показываем список
    album.show_tracks()

    # Управление воспроизведением
    print("\n--- Демонстрация методов ---")
    album.play_album()
    time.sleep(1)           # симуляция времени (не нужно для логики, но для наглядности)
    track1.simulate_play(30) # прошло 30 секунд
    album.pause_album()
    time.sleep(0.5)
    album.resume_album()
    track1.simulate_play(320)  # дослушиваем трек до конца
    album.next_track()          # переключение на второй трек
    track2.simulate_play(50)
    album.previous_track()      # вернуться к первому треку (но он уже закончен)
    # Сейчас первый трек остановлен и будет запущен с начала
    album.next_track()          # снова второй трек
    album.stop_album()
    print("\n--- Конец демонстрации ---")

if __name__ == "__main__":
    demo()