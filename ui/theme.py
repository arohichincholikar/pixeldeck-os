BG = (22, 18, 30)
PANEL = (30, 26, 42)
CARD = (38, 33, 54)
HOVER_CARD = (50, 44, 70)

BORDER = (180, 120, 130)
BORDER_DIM = (80, 60, 80)

TEXT = (240, 210, 200)
TEXT_DIM = (140, 110, 120)

ACCENT = (220, 140, 140)
ACCENT2 = (255, 180, 160)

BAR_BG = (50, 42, 64)
BAR_FILL = (200, 130, 130)

STAR = (200, 160, 180)

def draw_panel(surf, rect, fill=PANEL, border_color=BORDER, border_width=2, radius=12):
    import pygame
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    pygame.draw.rect(surf, border_color, rect, border_width, border_radius=radius)