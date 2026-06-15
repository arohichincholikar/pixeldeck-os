import pygame
import os
import json
import random
from mutagen import File as MutagenFile
from ui.theme import *

WIDTH, HEIGHT = 900, 600
MUSIC_FOLDER = "music"
DATA_FOLDER = "data"
SETTINGS_FILE = os.path.join(DATA_FOLDER, "music_player.json")
SUPPORTED_FORMATS = (".mp3", ".wav", ".ogg", ".flac")

PLAYER_STATE = {
    "current_path": None,
    "current_index": None,
    "playlist_index": 0,
    "is_paused": False,
    "volume": 0.7,
    "shuffle": False,
    "repeat": False,
    "position": 0,
    "started_ticks": 0,
}


class MusicPlayer:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 48)
        self.text_font = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf", 24)
        self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 18)
        self.tiny_font = pygame.font.Font("assets/fonts/PixelOperator.ttf", 16)

        os.makedirs(MUSIC_FOLDER, exist_ok=True)
        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.settings = self.load_settings()
        self.playlists = self.load_playlists()
        self.playlist_names = list(self.playlists.keys())

        if PLAYER_STATE["current_path"] is None:
            self.restore_from_settings()

        self.playlist_index = PLAYER_STATE["playlist_index"]
        if self.playlist_index >= len(self.playlist_names):
            self.playlist_index = 0
            PLAYER_STATE["playlist_index"] = 0

        self.selected_index = PLAYER_STATE["current_index"] or 0
        self.current_index = PLAYER_STATE["current_index"]
        self.is_paused = PLAYER_STATE["is_paused"]
        self.volume = PLAYER_STATE["volume"]
        self.shuffle = PLAYER_STATE["shuffle"]
        self.repeat = PLAYER_STATE["repeat"]

        pygame.mixer.music.set_volume(self.volume)

        self.message = "music ready"

    def current_playlist_name(self):
        return self.playlist_names[self.playlist_index]

    def songs(self):
        return self.playlists[self.current_playlist_name()]

    def load_playlists(self):
        playlists = {"all songs": []}

        for root, dirs, files in os.walk(MUSIC_FOLDER):
            songs = []

            for file in files:
                if file.lower().endswith(SUPPORTED_FORMATS):
                    full_path = os.path.join(root, file)
                    songs.append(full_path)
                    playlists["all songs"].append(full_path)

            if root != MUSIC_FOLDER and songs:
                playlists[os.path.basename(root).lower()] = sorted(songs)

        playlists["all songs"] = sorted(playlists["all songs"])
        return playlists

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {}

        try:
            with open(SETTINGS_FILE, "r") as file:
                return json.load(file)
        except:
            return {}

    def restore_from_settings(self):
        PLAYER_STATE["playlist_index"] = self.settings.get("playlist_index", 0)
        PLAYER_STATE["current_path"] = self.settings.get("current_path")
        PLAYER_STATE["position"] = self.settings.get("position", 0)
        PLAYER_STATE["is_paused"] = self.settings.get("is_paused", True)
        PLAYER_STATE["volume"] = self.settings.get("volume", 0.7)
        PLAYER_STATE["shuffle"] = self.settings.get("shuffle", False)
        PLAYER_STATE["repeat"] = self.settings.get("repeat", False)

        current_path = PLAYER_STATE["current_path"]

        if current_path:
            for playlist_name, songs in self.playlists.items():
                if current_path in songs:
                    if playlist_name in self.playlist_names:
                        PLAYER_STATE["playlist_index"] = self.playlist_names.index(playlist_name)
                    PLAYER_STATE["current_index"] = songs.index(current_path)
                    break

    def save_settings(self):
        data = {
            "playlist_index": self.playlist_index,
            "current_path": PLAYER_STATE["current_path"],
            "current_index": self.current_index,
            "position": self.get_elapsed_seconds(),
            "is_paused": self.is_paused,
            "volume": self.volume,
            "shuffle": self.shuffle,
            "repeat": self.repeat,
        }
        with open(SETTINGS_FILE, "w") as file:
            json.dump(data, file, indent=4)
        with open(SETTINGS_FILE, "w") as file:
            json.dump(data, file, indent=4)

    def blit(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def clean_song_name(self, path):
        filename = os.path.basename(path)
        name = os.path.splitext(filename)[0]
        return name.replace("_", " ").replace(" - ", " • ")

    def get_duration(self, path):
        try:
            audio = MutagenFile(path)
            if audio and audio.info:
                return int(audio.info.length)
        except:
            pass
        return 0

    def get_album_art_path(self, song_path):
        base = os.path.splitext(song_path)[0]

        for ext in [".png", ".jpg", ".jpeg"]:
            image_path = base + ext
            if os.path.exists(image_path):
                return image_path

        return None

    def play_song(self, index, start_at=0):
        if not self.songs():
            return

        self.current_index = index
        self.selected_index = index
        path = self.songs()[index]

        try:
            pygame.mixer.music.load(path)

            try:
                pygame.mixer.music.play(start=start_at)
            except:
                pygame.mixer.music.play()

            pygame.mixer.music.set_volume(self.volume)

            self.is_paused = False

            PLAYER_STATE["current_path"] = path
            PLAYER_STATE["current_index"] = index
            PLAYER_STATE["playlist_index"] = self.playlist_index
            PLAYER_STATE["is_paused"] = False
            PLAYER_STATE["position"] = start_at
            PLAYER_STATE["volume"] = self.volume
            PLAYER_STATE["shuffle"] = self.shuffle
            PLAYER_STATE["repeat"] = self.repeat

            self.message = f"now playing: {self.clean_song_name(path)}"
            self.save_settings()

        except Exception as e:
            self.message = f"could not play file: {e}"

    def toggle_pause(self):
        if self.current_index is None:
            if self.songs():
                self.play_song(self.selected_index)
            return
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            PLAYER_STATE["is_paused"] = False
            self.message = "resumed"
        else:
            PLAYER_STATE["position"] = self.get_elapsed_seconds()
            pygame.mixer.music.pause()
            self.is_paused = True
            PLAYER_STATE["is_paused"] = True
            self.message = "paused"
        self.save_settings()

    def next_song(self):
        if not self.songs():
            return
        if self.shuffle:
            self.play_song(random.randint(0, len(self.songs()) - 1))
        elif self.current_index is None:
            self.play_song(0)
        else:
            self.play_song((self.current_index + 1) % len(self.songs()))

    def previous_song(self):
        if not self.songs():
            return
        if self.current_index is None:
            self.play_song(0)
        else:
            self.play_song((self.current_index - 1) % len(self.songs()))

    def next_playlist(self):
        pygame.mixer.music.stop()
        self.playlist_index = (self.playlist_index + 1) % len(self.playlist_names)
        self.current_index = None
        self.selected_index = 0
        self.is_paused = False
        PLAYER_STATE["playlist_index"] = self.playlist_index
        PLAYER_STATE["current_path"] = None
        PLAYER_STATE["current_index"] = None
        PLAYER_STATE["position"] = 0
        PLAYER_STATE["is_paused"] = False
        self.message = f"playlist: {self.current_playlist_name()}"
        self.save_settings()

    def previous_playlist(self):
        pygame.mixer.music.stop()
        self.playlist_index = (self.playlist_index - 1) % len(self.playlist_names)
        self.current_index = None
        self.selected_index = 0
        self.is_paused = False
        PLAYER_STATE["playlist_index"] = self.playlist_index
        PLAYER_STATE["current_path"] = None
        PLAYER_STATE["current_index"] = None
        PLAYER_STATE["position"] = 0
        PLAYER_STATE["is_paused"] = False
        self.message = f"playlist: {self.current_playlist_name()}"
        self.save_settings()

    def change_volume(self, amount):
        self.volume = max(0, min(1, self.volume + amount))
        pygame.mixer.music.set_volume(self.volume)
        PLAYER_STATE["volume"] = self.volume
        self.message = f"volume: {int(self.volume * 100)}%"
        self.save_settings()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        PLAYER_STATE["shuffle"] = self.shuffle
        self.message = "shuffle on" if self.shuffle else "shuffle off"
        self.save_settings()

    def toggle_repeat(self):
        self.repeat = not self.repeat
        PLAYER_STATE["repeat"] = self.repeat
        self.message = "repeat on" if self.repeat else "repeat off"
        self.save_settings()

    def get_elapsed_seconds(self):
        if PLAYER_STATE["current_path"] is None:
            return 0
        pos = pygame.mixer.music.get_pos()
        if pos < 0:
            return int(PLAYER_STATE["position"])
        if self.is_paused:
            return int(PLAYER_STATE["position"])
        return pos // 1000

    def seek(self, amount):
        if self.current_index is None:
            return
        current_path = self.songs()[self.current_index]
        duration = self.get_duration(current_path)
        new_pos = max(0, min(duration, self.get_elapsed_seconds() + amount))
        self.play_song(self.current_index, new_pos)
        if self.is_paused:
            pygame.mixer.music.pause()
        PLAYER_STATE["position"] = new_pos
        self.save_settings()

    def format_time(self, seconds):
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes}:{secs:02d}"

    def draw_pixel_note(self, x, y, s=4):
        pts = [
            (3,0),(4,0),(5,0),
            (5,1),(5,2),(5,3),(5,4),
            (1,5),(2,5),(5,5),
            (0,6),(1,6),(2,6),(4,6),(5,6),
            (1,7),(2,7),(4,7),
        ]
        for gx, gy in pts:
            pygame.draw.rect(self.screen, ACCENT, (x + gx * s, y + gy * s, s, s))

    def draw_song_list(self):
        list_rect = pygame.Rect(35, 120, 400, 390)
        draw_panel(self.screen, list_rect, PANEL, BORDER, 2, 12)
        self.blit(f"playlist: {self.current_playlist_name()}", list_rect.x + 20, list_rect.y + 18, self.text_font, ACCENT)
        if not self.songs():
            self.blit("no songs found", list_rect.x + 22, list_rect.y + 80, self.text_font, TEXT)
            self.blit("add songs to music folder", list_rect.x + 22, list_rect.y + 115, self.small_font, TEXT_DIM)
            return
        start_y = list_rect.y + 60
        for i, song in enumerate(self.songs()[:8]):
            row = pygame.Rect(list_rect.x + 18, start_y + i * 38, list_rect.w - 36, 30)
            mouse = pygame.mouse.get_pos()
            is_selected = i == self.selected_index
            is_current = i == self.current_index and song == PLAYER_STATE["current_path"]
            color = HOVER_CARD if row.collidepoint(mouse) or is_selected else CARD
            pygame.draw.rect(self.screen, color, row, border_radius=6)
            if is_current:
                pygame.draw.rect(self.screen, BORDER, row, 1, border_radius=6)
                prefix = ">"
            else:
                prefix = " "
            label = prefix + " " + self.clean_song_name(song)[:32]
            self.blit(label, row.x + 10, row.y + 5, self.tiny_font, TEXT if is_current else TEXT_DIM)

    def draw_now_playing(self):
        card = pygame.Rect(465, 120, 400, 400)
        draw_panel(self.screen, card, PANEL, BORDER, 2, 12)
        self.blit("now playing", card.x + 22, card.y + 18, self.text_font, ACCENT)
        album = pygame.Rect(card.x + 110, card.y + 70, 180, 180)
        draw_panel(self.screen, album, CARD, BORDER_DIM, 1, 10)
        current_path = PLAYER_STATE["current_path"]
        art_path = self.get_album_art_path(current_path) if current_path else None
        if art_path:
            try:
                art = pygame.image.load(art_path).convert_alpha()
                art = pygame.transform.smoothscale(art, (160, 160))
                self.screen.blit(art, art.get_rect(center=album.center))
            except:
                self.draw_pixel_note(album.centerx - 26, album.centery - 34, s=7)
        else:
            self.draw_pixel_note(album.centerx - 26, album.centery - 34, s=7)
        if current_path is None:
            title = "nothing playing"
            status = "press enter to start"
            duration = 0
        else:
            title = self.clean_song_name(current_path)
            status = "paused" if self.is_paused else "playing"
            duration = self.get_duration(current_path)
        if " • " in title:
            song_name, artist = title.split(" • ", 1)
        else:
            song_name = title
            artist = ""
        song_surface = self.text_font.render(song_name, True, TEXT)
        song_rect = song_surface.get_rect(centerx=card.centerx, y=card.y + 265)
        self.screen.blit(song_surface, song_rect)
        artist_surface = self.small_font.render(artist, True, TEXT_DIM)
        artist_rect = artist_surface.get_rect(centerx=card.centerx, y=card.y + 285)
        text_surface = self.small_font.render(status, True, TEXT_DIM)
        text_rect = text_surface.get_rect(
        center=(card.centerx, card.y + 315)
        )
        self.screen.blit(text_surface, text_rect)
        self.screen.blit(artist_surface, artist_rect)
        elapsed = self.get_elapsed_seconds()
        progress_bg = pygame.Rect(card.x + 55, card.y + 335, 290, 10)
        pygame.draw.rect(self.screen, BAR_BG, progress_bg, border_radius=5)
        if duration > 0:
            progress_width = min(elapsed / duration, 1) * 290
        else:
            progress_width = 0
        progress_fill = pygame.Rect(card.x + 55, card.y + 335, int(progress_width), 10)
        pygame.draw.rect(self.screen, BAR_FILL, progress_fill, border_radius=5)
        self.blit(self.format_time(elapsed), card.x + 55, card.y + 355, self.tiny_font, TEXT_DIM)
        self.blit(self.format_time(duration), card.x + 305, card.y + 355, self.tiny_font, TEXT_DIM)
        volume_text = f"vol {int(self.volume * 100)}%"
        mode_text = f"{'shuffle' if self.shuffle else 'linear'} • {'loop' if self.repeat else 'once'}"
        self.blit(volume_text, card.x + 55, card.y + 375, self.tiny_font, TEXT_DIM)
        self.blit(mode_text, card.x + 180, card.y + 375, self.tiny_font, TEXT_DIM)

    def draw(self):
        self.screen.fill(BG)
        self.blit("music", 45, 38, self.title_font, ACCENT)
        self.blit("pixeldeck audio player", 45, 82, self.small_font, TEXT_DIM)
        self.draw_song_list()
        self.draw_now_playing()
        self.blit(self.message, 45, 535, self.small_font, ACCENT)
        self.blit("enter/click play • space pause • n/b song • p/o playlist • +/- volume • s shuffle • r loop • </> seek • esc back", 45, 560, self.tiny_font, TEXT_DIM)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.save_settings()
                return False
            if event.key == pygame.K_DOWN and self.songs():
                self.selected_index = (self.selected_index + 1) % len(self.songs())
            if event.key == pygame.K_UP and self.songs():
                self.selected_index = (self.selected_index - 1) % len(self.songs())
            if event.key == pygame.K_RETURN and self.songs():
                self.play_song(self.selected_index)
            if event.key == pygame.K_SPACE:
                self.toggle_pause()
            if event.key == pygame.K_n:
                self.next_song()
            if event.key == pygame.K_b:
                self.previous_song()
            if event.key == pygame.K_p:
                self.next_playlist()
            if event.key == pygame.K_o:
                self.previous_playlist()
            if event.key in [pygame.K_EQUALS, pygame.K_PLUS]:
                self.change_volume(0.1)
            if event.key == pygame.K_MINUS:
                self.change_volume(-0.1)
            if event.key == pygame.K_s:
                self.toggle_shuffle()
            if event.key == pygame.K_r:
                self.toggle_repeat()
            if event.key == pygame.K_PERIOD:
                self.seek(10)
            if event.key == pygame.K_COMMA:
                self.seek(-10)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            list_x, list_y = 35, 120
            start_y = list_y + 60
            for i, song in enumerate(self.songs()[:8]):
                row = pygame.Rect(list_x + 18, start_y + i * 38, 400 - 36, 30)
                if row.collidepoint(event.pos):
                    self.selected_index = i
                    self.play_song(i)
        return True

    def run(self):
        running = True
        while running:
            if self.current_index is not None and not self.is_paused:
                current_path = PLAYER_STATE["current_path"]
                if current_path:
                    duration = self.get_duration(current_path)
                    if duration > 0 and self.get_elapsed_seconds() >= duration:
                        if self.repeat:
                            self.play_song(self.current_index)
                        else:
                            self.next_song()
            self.draw()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings()
                    pygame.mixer.music.stop()
                    pygame.quit()
                    raise SystemExit
                running = self.handle_event(event)
            self.clock.tick(60)
def open_music_player(screen):
    player = MusicPlayer(screen)
    player.run()