import pygame
import os
import json
import time
import math

# ── Window ────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 600

# ── Palette (from screenshot) ─────────────────────────────────────────────────
BG          = (22, 18, 30)       # very dark navy-purple background
PANEL       = (30, 26, 42)       # left / right panel fill
CARD        = (38, 33, 54)       # inner card / box fill
BORDER      = (180, 120, 130)    # pinkish-red border lines
BORDER_DIM  = (80, 60, 80)       # dimmer border for inner boxes
TEXT        = (240, 210, 200)    # warm off-white text
TEXT_DIM    = (140, 110, 120)    # muted label text
ACCENT      = (220, 140, 140)    # salmon-pink accent (titles, icons)
ACCENT2     = (255, 180, 160)    # slightly brighter accent for highlights
BAR_BG      = (50, 42, 64)       # stat bar background
BAR_FILL    = (200, 130, 130)    # stat bar fill  (pink)
BAR_FILL2   = (160, 100, 110)    # darker bar segment color
STAR        = (200, 160, 180)    # tiny sparkle stars
BUNNY_WHITE = (248, 242, 235)    # bunny body
BUNNY_OUTLINE = (48, 38, 52)     # bunny outline / eyes
DRESS_PINK  = (220, 155, 140)    # bunny dress
SHADOW      = (35, 28, 48)       # ground shadow under bunny
HOVER_CARD  = (50, 44, 70)       # button hover

DATA_FOLDER = "data"
PET_FILE    = os.path.join(DATA_FOLDER, "pixel_pet.json")

# ── Pixel-art helper: draw a scaled pixel ─────────────────────────────────────
def px(surf, color, x, y, size=3):
    pygame.draw.rect(surf, color, (x, y, size, size))

# ── Draw pixel-art bunny sprite ───────────────────────────────────────────────
def draw_pixel_bunny(surf, cx, cy, mood="happy", scale=3):
    """Draw a Miffy-style pixel bunny centred at (cx, cy)."""
    W = BUNNY_WHITE
    O = BUNNY_OUTLINE
    D = DRESS_PINK
    s = scale

    def dot(gx, gy, color=W):
        pygame.draw.rect(surf, color, (cx + gx * s, cy + gy * s, s, s))

    # ── pixel grid (column x, row y) centred at (0,0) ──────────────────────
    # Ears
    for r in range(-16, -8):
        for c in [-4, -3]:
            dot(c, r, O if (c == -4 and r == -16) or (c == -3 and r == -16) else W)
        for c in [3, 4]:
            dot(c, r, O if (c == 4 and r == -16) or (c == 3 and r == -16) else W)

    # Ear outlines (sides)
    for r in range(-16, -8):
        dot(-5, r, O)
        dot(-2, r, O)
        dot(2,  r, O)
        dot(5,  r, O)
    dot(-5, -8, O); dot(-2, -8, O); dot(2, -8, O); dot(5, -8, O)
    dot(-4, -17, O); dot(-3, -17, O); dot(3, -17, O); dot(4, -17, O)

    # Head (oval ~12 wide, 10 tall)
    head_rows = {
        -8:  range(-4, 5),
        -7:  range(-6, 7),
        -6:  range(-7, 8),
        -5:  range(-7, 8),
        -4:  range(-7, 8),
        -3:  range(-7, 8),
        -2:  range(-7, 8),
        -1:  range(-6, 7),
         0:  range(-5, 6),
         1:  range(-4, 5),
    }
    for row, cols in head_rows.items():
        for c in cols:
            dot(c, row, W)

    # Head outline
    for row, cols in head_rows.items():
        col_list = list(cols)
        if col_list:
            dot(col_list[0] - 1, row, O)
            dot(col_list[-1] + 1, row, O)
    for c in range(-4, 5):  dot(c, -9, O)
    for c in range(-3, 4):  dot(c, 2, O)

    # Eyes (two small dots)
    dot(-3, -4, O); dot(-2, -4, O)
    dot(2,  -4, O); dot(3, -4, O)

    # Miffy X mouth
    dot(-1, -1, O); dot(1, -1, O)
    dot( 0,  0, O)
    dot(-1,  1, O); dot(1,  1, O)

    # Body / dress
    body_rows = {
        2:  range(-5, 6),
        3:  range(-6, 7),
        4:  range(-7, 8),
        5:  range(-7, 8),
        6:  range(-7, 8),
        7:  range(-7, 8),
        8:  range(-6, 7),
        9:  range(-5, 6),
        10: range(-4, 5),
    }
    for row, cols in body_rows.items():
        for c in cols:
            dot(c, row, D)

    # Body outline
    for row, cols in body_rows.items():
        col_list = list(cols)
        if col_list:
            dot(col_list[0] - 1, row, O)
            dot(col_list[-1] + 1, row, O)
    for c in range(-5, 6):  dot(c, 1,  O)
    for c in range(-4, 5):  dot(c, 11, O)

    # Arms
    for r in range(3, 8):
        dot(-8, r, W); dot(-9, r, O)
        dot(8,  r, W); dot(9, r, O)
    for r in range(3, 8):
        dot(-8, r, O) if r in (3, 7) else None
        dot(8,  r, O) if r in (3, 7) else None

    # Feet
    for c in range(-6, -1):  dot(c, 12, W)
    for c in range(1,  7):   dot(c, 12, W)
    for c in range(-7, 0):   dot(c, 11, O)
    for c in range(0,  8):   dot(c, 11, O)
    dot(-7, 12, O); dot(0,  12, O)
    dot(0,  12, O); dot(7,  12, O)

    # Mood extras
    if mood == "happy":
        # small heart top-right
        heart_cx = cx + 9 * s
        heart_cy = cy - 12 * s
        pygame.draw.rect(surf, ACCENT, (heart_cx,     heart_cy - s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx + s, heart_cy - s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx - s, heart_cy,    s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx,     heart_cy,    s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx + s, heart_cy,    s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx + 2*s, heart_cy,  s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx - s, heart_cy + s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx,     heart_cy + s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx + s, heart_cy + s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx + 2*s, heart_cy + s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx,     heart_cy + 2*s, s, s))
        pygame.draw.rect(surf, ACCENT, (heart_cx + s, heart_cy + 2*s, s, s))

    if mood == "hungry":
        # small exclamation / sweat drop top-left
        for i in range(4):
            pygame.draw.rect(surf, ACCENT2, (cx - 11*s, cy - (15+i)*s, s, s))

    if mood == "sleepy":
        # Z Z Z
        pass  # drawn separately below


def draw_sparkles(surf, positions):
    """Draw small + sparkles."""
    for (x, y, size) in positions:
        pygame.draw.line(surf, STAR, (x - size, y), (x + size, y), 1)
        pygame.draw.line(surf, STAR, (x, y - size), (x, y + size), 1)


# ── Pixel-art icons (8×8 grid drawn as small rects) ──────────────────────────
def draw_icon_feed(surf, x, y, s=3):
    """Bowl with two sparkle dots."""
    pts = [
        (1,4),(2,4),(3,4),(4,4),(5,4),(6,4),
        (0,5),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),
        (1,6),(2,6),(3,6),(4,6),(5,6),(6,6),
        (2,7),(3,7),(4,7),(5,7),
        (2,2),(4,1),(6,2),  # steam dots
    ]
    for (gx, gy) in pts:
        pygame.draw.rect(surf, ACCENT, (x + gx*s, y + gy*s, s, s))

def draw_icon_play(surf, x, y, s=3):
    """Smiley face."""
    circle_pts = [
        (2,0),(3,0),(4,0),(5,0),
        (1,1),(6,1),
        (0,2),(7,2),
        (0,3),(2,3),(5,3),(7,3),
        (0,4),(2,4),(5,4),(7,4),
        (1,5),(3,5),(4,5),(6,5),
        (2,6),(3,6),(4,6),(5,6),
    ]
    for (gx, gy) in circle_pts:
        pygame.draw.rect(surf, ACCENT, (x + gx*s, y + gy*s, s, s))

def draw_icon_clean(surf, x, y, s=3):
    """Shower / water drop grid."""
    pts = [
        (3,0),(4,0),(3,1),(4,1),
        (2,2),(5,2),
        (1,3),(3,3),(5,3),(7,3),
        (0,4),(2,4),(4,4),(6,4),
        (1,5),(3,5),(5,5),(7,5),
        (0,6),(2,6),(4,6),(6,6),
    ]
    for (gx, gy) in pts:
        pygame.draw.rect(surf, ACCENT, (x + gx*s, y + gy*s, s, s))

def draw_icon_sleep(surf, x, y, s=3):
    """Bed / moon."""
    pts = [
        (0,3),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3),
        (0,4),(7,4),
        (0,5),(1,5),(2,5),(3,5),(4,5),(5,5),(6,5),(7,5),
        (1,6),(2,6),(3,6),(4,6),(5,6),(6,6),
        # head on pillow
        (1,2),(2,2),(1,1),(2,1),
    ]
    for (gx, gy) in pts:
        pygame.draw.rect(surf, ACCENT, (x + gx*s, y + gy*s, s, s))

ICON_FUNCS = {
    "Feed":  draw_icon_feed,
    "Play":  draw_icon_play,
    "Clean": draw_icon_clean,
    "Sleep": draw_icon_sleep,
}


# ── Stat-bar icon helpers ─────────────────────────────────────────────────────
def draw_stat_icon(surf, stat, x, y, s=2):
    if stat == "hunger":
        # small heart shape
        pts = [(1,0),(2,0),(4,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
               (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
               (1,3),(2,3),(3,3),(4,3),(5,3),(2,4),(3,4),(4,4),(3,5)]
        color = (200, 100, 110)
    elif stat == "happiness":
        pts = [(1,0),(2,0),(4,0),(5,0),(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
               (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
               (1,3),(2,3),(3,3),(4,3),(5,3),(2,4),(3,4),(4,4),(3,5)]
        color = ACCENT
    elif stat == "energy":
        # lightning bolt
        pts = [(3,0),(4,0),(5,0),(2,1),(3,1),(4,1),(1,2),(2,2),(3,2),(4,2),
               (1,3),(2,3),(3,3),(2,4),(3,4),(4,4),(2,5),(3,5),(4,5),(5,5)]
        color = ACCENT2
    else:  # cleanliness
        pts = [(3,0),(2,1),(4,1),(1,2),(5,2),(2,3),(4,3),(3,4),(3,5)]
        color = (160, 180, 210)
    for (gx, gy) in pts:
        pygame.draw.rect(surf, color, (x + gx*s, y + gy*s, s, s))


# ── Button ────────────────────────────────────────────────────────────────────
class ActionButton:
    def __init__(self, label, x, y, w, h, action, icon_fn=None):
        self.label   = label
        self.rect    = pygame.Rect(x, y, w, h)
        self.action  = action
        self.icon_fn = icon_fn

    def draw(self, surf, font):
        mouse  = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse)
        color  = HOVER_CARD if hovered else CARD

        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, BORDER, self.rect, 1, border_radius=6)

        if self.icon_fn:
            self.icon_fn(surf, self.rect.x + 14, self.rect.y + (self.rect.h // 2) - 12, s=3)

        lbl = font.render(self.label.lower(), True, TEXT if hovered else TEXT_DIM)
        surf.blit(lbl, (self.rect.x + 68, self.rect.centery - lbl.get_height() // 2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Rounded rect with border helper ──────────────────────────────────────────
def draw_panel(surf, rect, fill, border_color, border_width=1, radius=10):
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    pygame.draw.rect(surf, border_color, rect, border_width, border_radius=radius)


# ── Main game class ───────────────────────────────────────────────────────────
class Tamagotchi:
    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        # ── fonts ──────────────────────────────────────────────────────────
        try:
            self.title_font = pygame.font.Font("assets/fonts/PixelOperator-Bold.ttf", 42)
            self.text_font  = pygame.font.Font("assets/fonts/PixelOperatorSC.ttf",    24)
            self.small_font = pygame.font.Font("assets/fonts/PixelOperator.ttf",      18)
            self.tiny_font  = pygame.font.Font("assets/fonts/PixelOperator.ttf",      16)
        except FileNotFoundError:
            # fallback to system mono
            self.title_font = pygame.font.SysFont("monospace", 38, bold=True)
            self.text_font  = pygame.font.SysFont("monospace", 22)
            self.small_font = pygame.font.SysFont("monospace", 17)
            self.tiny_font  = pygame.font.SysFont("monospace", 14)

        os.makedirs(DATA_FOLDER, exist_ok=True)
        self.pet     = self.load_pet()
        self.message = ""
        self.last_saved_str = self._format_save_time()

        # ── layout constants ───────────────────────────────────────────────
        PAD = 14
        LW = 410
        RW = WIDTH - LW - PAD * 3
        PH = HEIGHT - PAD * 2
        LX = PAD
        RX = LW + PAD * 2
        LY = PAD
        RY = PAD

        self.left_rect  = pygame.Rect(LX, LY, LW, PH)
        self.right_rect = pygame.Rect(RX, RY, RW, PH)

        # ── sparkle positions (static, on left panel) ──────────────────────
        self.sparkles = [
            (80,  90,  4), (430, 80,  3), (70,  240, 3),
            (460, 200, 4), (120, 340, 3), (390, 350, 3),
            (50,  440, 3), (470, 430, 4),
        ]

        # ── action buttons ─────────────────────────────────────────────────
        bx = RX + 12
        bw = RW - 24
        bh = 58
        by_start = RY + 62
        gap = 10
        self.buttons = [
            ActionButton("Feed",  bx, by_start + 0*(bh+gap), bw, bh, self.feed,  draw_icon_feed),
            ActionButton("Play",  bx, by_start + 1*(bh+gap), bw, bh, self.play,  draw_icon_play),
            ActionButton("Clean", bx, by_start + 2*(bh+gap), bw, bh, self.clean, draw_icon_clean),
            ActionButton("Sleep", bx, by_start + 3*(bh+gap), bw, bh, self.sleep, draw_icon_sleep),
        ]

        # ── "about" card rect ──────────────────────────────────────────────
        about_y = by_start + 4*(bh+gap) + 10
        self.about_rect = pygame.Rect(RX + 12, about_y, RW - 24, 120)

        # ── "last saved" card rect ─────────────────────────────────────────
        saved_y = about_y + 130
        self.saved_rect = pygame.Rect(RX + 12, saved_y, RW - 24, 68)

    # ── Persistence ──────────────────────────────────────────────────────────
    def _format_save_time(self):
        t = time.localtime()
        months = ["jan","feb","mar","apr","may","jun",
                  "jul","aug","sep","oct","nov","dec"]
        return f"{t.tm_mday} {months[t.tm_mon-1]} {t.tm_year}  •  {t.tm_hour:02d}:{t.tm_min:02d}"

    def default_pet(self):
        return {
            "name":        "miffy",
            "hunger":      60,
            "happiness":   75,
            "energy":      40,
            "cleanliness": 55,
            "last_update": time.time(),
        }

    def load_pet(self):
        if not os.path.exists(PET_FILE):
            return self.default_pet()
        try:
            with open(PET_FILE) as f:
                return json.load(f)
        except Exception:
            return self.default_pet()

    def save_pet(self):
        with open(PET_FILE, "w") as f:
            json.dump(self.pet, f, indent=4)
        self.last_saved_str = self._format_save_time()

    def clamp(self):
        for k in ("hunger", "happiness", "energy", "cleanliness"):
            self.pet[k] = max(0, min(100, self.pet.get(k, 50)))

    def decay(self):
        # migrate old saves that lack cleanliness
        self.pet.setdefault("cleanliness", 70)
        now = time.time()
        last = self.pet.get("last_update", now)
        mins = int((now - last) // 60)
        if mins > 0:
            self.pet["hunger"]      -= mins
            self.pet["happiness"]   -= mins
            self.pet["energy"]      -= mins
            self.pet["cleanliness"] -= mins // 2
            self.pet["last_update"] = now
            self.clamp()
            self.save_pet()

    # ── Actions ───────────────────────────────────────────────────────────────
    def feed(self):
        self.pet["hunger"]    += 20
        self.pet["energy"]    += 3
        self.message = "miffy enjoyed a tiny snack ♥"
        self.clamp(); self.save_pet()

    def play(self):
        self.pet["happiness"]   += 18
        self.pet["energy"]      -= 12
        self.pet["hunger"]      -= 6
        self.message = "miffy played a little game!"
        self.clamp(); self.save_pet()

    def clean(self):
        self.pet["cleanliness"] += 25
        self.pet["happiness"]   += 5
        self.message = "miffy is squeaky clean now."
        self.clamp(); self.save_pet()

    def sleep(self):
        self.pet["energy"]      += 25
        self.pet["hunger"]      -= 4
        self.message = "miffy took a soft little nap."
        self.clamp(); self.save_pet()

    # ── Mood ──────────────────────────────────────────────────────────────────
    def mood(self):
        p = self.pet
        if p["hunger"]      < 25: return "hungry"
        if p["energy"]      < 25: return "sleepy"
        if p["happiness"]   < 25: return "sad"
        if p["cleanliness"] < 25: return "dirty"
        return "happy"

    # ── Drawing helpers ───────────────────────────────────────────────────────
    def blit(self, text, x, y, font, color=TEXT):
        self.screen.blit(font.render(str(text), True, color), (x, y))

    def draw_stat_bar(self, stat, label, value, x, y):
        # icon
        draw_stat_icon(self.screen, stat, x, y + 4, s=2)

        # label
        lbl = self.small_font.render(label, True, TEXT_DIM)
        self.screen.blit(lbl, (x + 22, y + 2))

        # bar background
        bx, by = x + 130, y + 5
        bw, bh = 220, 13
        # draw segmented background
        seg_w = 14
        seg_gap = 3
        for i in range(10):
            sx = bx + i * (seg_w + seg_gap)
            filled = (value / 100) * 10 > i
            color = BAR_FILL if filled else BAR_BG
            pygame.draw.rect(self.screen, color, (sx, by, seg_w, bh), border_radius=2)

    def draw_left_panel(self):
        surf = self.screen
        lr   = self.left_rect

        # panel bg + border
        draw_panel(surf, lr, PANEL, BORDER, 2, 12)

        # title
        self.blit("tamagotchi", lr.x + 22, lr.y + 18, self.title_font, ACCENT)

        # subtitle
        sub = self.small_font.render("take care of your virtual friend", True, TEXT_DIM)
        surf.blit(sub, (lr.x + 22, lr.y + 66))

        # heart top right corner of left panel
        hx, hy = lr.right - 50, lr.y + 22
        # pixel heart
        for (gx, gy) in [(1,0),(2,0),(4,0),(5,0),
                          (0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),
                          (0,2),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2),
                          (1,3),(2,3),(3,3),(4,3),(5,3),
                          (2,4),(3,4),(4,4),(3,5)]:
            pygame.draw.rect(surf, ACCENT, (hx + gx*3, hy + gy*3, 3, 3))

        # ── pet viewport ──────────────────────────────────────────────────
        pet_box = pygame.Rect(lr.x + 18, lr.y + 95, lr.w - 36, 260)
        draw_panel(surf, pet_box, CARD, BORDER_DIM, 1, 8)

        # sparkles inside pet box
        for (sx, sy, ss) in self.sparkles:
            if pet_box.collidepoint(sx + lr.x, sy + lr.y + 10):
                draw_sparkles(surf, [(sx + lr.x, sy + lr.y + 10, ss)])

        # ground shadow
        shadow_rect = pygame.Rect(lr.centerx - 55, pet_box.bottom - 30, 110, 14)
        pygame.draw.ellipse(surf, SHADOW, shadow_rect)

        # bunny
        mood = self.mood()
        draw_pixel_bunny(surf, lr.centerx, pet_box.centery + 20, mood=mood, scale=3)

        # name tag
        name_box = pygame.Rect(lr.centerx - 80, pet_box.bottom - 38, 160, 32)
        draw_panel(surf, name_box, CARD, BORDER, 1, 6)
        # diamonds
        self.blit("✦", name_box.x + 8, name_box.y + 4, self.small_font, BORDER)
        self.blit("✦", name_box.right - 26, name_box.y + 4, self.small_font, BORDER)
        name_lbl = self.text_font.render(self.pet["name"], True, TEXT)
        surf.blit(name_lbl, name_lbl.get_rect(center=name_box.center))

        # ── stat bars ─────────────────────────────────────────────────────
        stats_y = pet_box.bottom + 14
        stats = [
            ("hunger",      "hunger",      self.pet["hunger"]),
            ("happiness",   "happiness",   self.pet["happiness"]),
            ("energy",      "energy",      self.pet["energy"]),
            ("cleanliness", "cleanliness", self.pet.get("cleanliness", 50)),
        ]
        for i, (stat, label, val) in enumerate(stats):
            self.draw_stat_bar(stat, label, val, lr.x + 22, stats_y + i * 34)

        # ── footer ────────────────────────────────────────────────────────
        esc_lbl = self.tiny_font.render("esc = back to home", True, TEXT_DIM)
        surf.blit(esc_lbl, (lr.x + 18, lr.bottom - 28))

        # message
        if self.message:
            msg = self.tiny_font.render(self.message, True, ACCENT)
            surf.blit(msg, msg.get_rect(centerx=lr.centerx, y=lr.bottom - 28))

    def draw_right_panel(self):
        surf = self.screen
        rr   = self.right_rect

        draw_panel(surf, rr, PANEL, BORDER, 2, 12)

        # ── "actions" header ──────────────────────────────────────────────
        header_box = pygame.Rect(rr.x + 12, rr.y + 14, rr.w - 24, 38)
        # decorative line + title
        hline_y = rr.y + 33
        pygame.draw.line(surf, BORDER_DIM, (rr.x + 20, hline_y), (rr.x + 110, hline_y), 1)
        pygame.draw.line(surf, BORDER_DIM, (rr.right - 110, hline_y), (rr.right - 20, hline_y), 1)
        # small diamond decorators
        self.blit("·✦·", rr.x + 22, rr.y + 22, self.tiny_font, BORDER_DIM)
        self.blit("·✦·", rr.right - 70, rr.y + 22, self.tiny_font, BORDER_DIM)

        actions_lbl = self.text_font.render("actions", True, ACCENT)
        surf.blit(actions_lbl, actions_lbl.get_rect(centerx=rr.centerx, y=rr.y + 18))

        # action buttons
        for btn in self.buttons:
            btn.draw(surf, self.text_font)

        # ── about card ────────────────────────────────────────────────────
        ab = self.about_rect
        draw_panel(surf, ab, CARD, BORDER_DIM, 1, 8)

        # small bunny icon in about card
        draw_pixel_bunny(surf, ab.x + 38, ab.y + 46, mood="happy", scale=2)

        # about text
        about_name = self.small_font.render(f"about {self.pet['name']}", True, ACCENT)
        surf.blit(about_name, (ab.x + 80, ab.y + 12))

        desc_lines = [
            f"{self.pet['name']} is a gentle bunny",
            "who loves cuddles and",
            "quiet time.  ♥",
        ]
        for i, line in enumerate(desc_lines):
            self.blit(line, ab.x + 80, ab.y + 38 + i * 22, self.tiny_font, TEXT_DIM)

        # ── last saved card ────────────────────────────────────────────────
        sb = self.saved_rect
        draw_panel(surf, sb, CARD, BORDER_DIM, 1, 8)

        self.blit("✦  last saved", sb.x + 14, sb.y + 10, self.small_font, TEXT_DIM)
        self.blit(self.last_saved_str, sb.x + 22, sb.y + 36, self.small_font, TEXT)

    # ── Main draw ─────────────────────────────────────────────────────────────
    def draw(self):
        self.decay()
        self.screen.fill(BG)
        self.draw_left_panel()
        self.draw_right_panel()

    # ── Game loop ─────────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            self.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.save_pet()
                    running = False

                for btn in self.buttons:
                    if btn.clicked(event):
                        btn.action()
                        self.message = ""  # reset then action sets it

            self.clock.tick(60)


# ── Entry point ───────────────────────────────────────────────────────────────
def open_tamagotchi(screen):
    Tamagotchi(screen).run()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("tamagotchi")
    open_tamagotchi(screen)
    pygame.quit()