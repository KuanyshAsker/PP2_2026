import pygame


class MusicPlayer:
    def __init__(self, music_folder):
        self.playlist = sorted(
            f for f in music_folder.iterdir()
            if f.suffix.lower() in [".mp3", ".wav", ".ogg"]
        )

        if not self.playlist:
            raise FileNotFoundError("Put at least one audio file in the music folder.")

        self.index = 0
        self.status = "Stopped"
        self.pause_pos = 0
        self.length_cache = {}

        self.title_font = pygame.font.SysFont("arial", 38, bold=True)
        self.text_font = pygame.font.SysFont("arial", 24)
        self.small_font = pygame.font.SysFont("arial", 18)

    def current_track(self):
        return self.playlist[self.index]

    def current_name(self):
        return self.current_track().stem

    def track_length(self):
        track = self.current_track()
        if track not in self.length_cache:
            try:
                self.length_cache[track] = pygame.mixer.Sound(str(track)).get_length()
            except:
                self.length_cache[track] = 0
        return self.length_cache[track]

    def play(self):
        if self.status == "Paused":
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.load(str(self.current_track()))
            pygame.mixer.music.play()
            self.pause_pos = 0
        self.status = "Playing"

    def pause(self):
        if self.status == "Playing":
            pos = pygame.mixer.music.get_pos()
            if pos != -1:
                self.pause_pos = pos / 1000
            pygame.mixer.music.pause()
            self.status = "Paused"
        elif self.status == "Paused":
            pygame.mixer.music.unpause()
            self.status = "Playing"

    def stop(self):
        pygame.mixer.music.stop()
        self.pause_pos = 0
        self.status = "Stopped"

    def change_track(self, step):
        self.index = (self.index + step) % len(self.playlist)
        self.play()

    def next_track(self):
        self.change_track(1)

    def previous_track(self):
        self.change_track(-1)

    def update(self):
        if self.status == "Playing" and not pygame.mixer.music.get_busy():
            self.status = "Finished"

    def position(self):
        if self.status == "Paused":
            return self.pause_pos
        if self.status == "Playing":
            pos = pygame.mixer.music.get_pos()
            if pos != -1:
                return pos / 1000
        if self.status == "Finished":
            return self.track_length()
        return 0

    def format_time(self, seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def draw(self, screen):
        w, h = screen.get_size()
        screen.fill((30, 30, 40))

        card = pygame.Rect(40, 40, w - 80, h - 80)
        pygame.draw.rect(screen, (245, 245, 245), card, border_radius=20)

        screen.blit(self.title_font.render("Music Player", True, (20, 20, 20)), (70, 70))
        screen.blit(self.text_font.render(f"Track: {self.current_name()}", True, (70, 70, 180)), (70, 140))
        screen.blit(self.text_font.render(f"Playlist: {self.index + 1}/{len(self.playlist)}", True, (20, 20, 20)), (70, 180))
        screen.blit(self.text_font.render(f"Status: {self.status}", True, (20, 20, 20)), (70, 220))

        current = self.position()
        total = self.track_length()
        time_text = f"{self.format_time(current)} / {self.format_time(total)}"
        screen.blit(self.text_font.render(time_text, True, (20, 20, 20)), (70, 270))

        bar_x, bar_y, bar_w, bar_h = 70, 320, w - 140, 18
        pygame.draw.rect(screen, (210, 210, 210), (bar_x, bar_y, bar_w, bar_h), border_radius=9)

        if total > 0:
            fill = int(bar_w * min(current / total, 1))
            pygame.draw.rect(screen, (80, 140, 255), (bar_x, bar_y, fill, bar_h), border_radius=9)

        controls = "P Play/Resume   S Pause   X Stop   N Next   B Previous   Q Quit"
        screen.blit(self.small_font.render(controls, True, (90, 90, 90)), (70, 380))