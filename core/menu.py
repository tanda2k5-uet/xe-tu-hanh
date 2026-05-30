import pygame
import sys

def run_menu():
    """Beautiful menu screen for AMR Simulator"""
    pygame.init()
    screen = pygame.display.set_mode([850, 750])
    pygame.display.set_caption("AMR Simulator - Cau hinh")
    clock = pygame.time.Clock()
    
    # Fonts
    font_title = pygame.font.SysFont("segoeui", 52, bold=True)
    font_subtitle = pygame.font.SysFont("segoeui", 22)
    font_label = pygame.font.SysFont("segoeui", 28)
    font_value = pygame.font.SysFont("segoeui", 36, bold=True)
    font_btn = pygame.font.SysFont("segoeui", 30, bold=True)
    font_hint = pygame.font.SysFont("segoeui", 18)
    
    # State
    num_amrs = 2
    map_size = 30
    obs_ratio = 20 # percentage
    custom_map = False
    
    # Limits
    MIN_AMRS, MAX_AMRS = 1, 15
    MIN_MAP, MAX_MAP = 10, 50
    MIN_OBS, MAX_OBS = 0, 50
    
    # Colors
    BG = (30, 30, 45)
    CARD_BG = (45, 45, 65)
    ACCENT_GREEN = (0, 200, 120)
    ACCENT_BLUE = (60, 140, 255)
    ACCENT_PURPLE = (160, 100, 255)
    TEXT_WHITE = (240, 240, 250)
    TEXT_DIM = (160, 160, 180)
    BTN_HOVER = (80, 200, 140)
    BTN_START = (0, 180, 100)
    BORDER = (70, 70, 100)
    
    # Button rects
    # Card 1
    amr_minus_rect = pygame.Rect(0, 0, 50, 50)
    amr_plus_rect = pygame.Rect(0, 0, 50, 50)
    # Card 2
    map_minus_rect = pygame.Rect(0, 0, 50, 50)
    map_plus_rect = pygame.Rect(0, 0, 50, 50)
    # Card 3 (Obstacle Ratio)
    obs_minus_rect = pygame.Rect(0, 0, 50, 50)
    obs_plus_rect = pygame.Rect(0, 0, 50, 50)
    # Card 4 (Custom Map Toggle)
    toggle_rect = pygame.Rect(0, 0, 100, 40)
    
    # Start button
    start_rect = pygame.Rect(0, 0, 280, 60)
    
    hover_start = False
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        hover_start = start_rect.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    running = False
                    
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if amr_minus_rect.collidepoint(mouse_pos):
                    num_amrs = max(MIN_AMRS, num_amrs - 1)
                elif amr_plus_rect.collidepoint(mouse_pos):
                    num_amrs = min(MAX_AMRS, num_amrs + 1)
                elif map_minus_rect.collidepoint(mouse_pos):
                    map_size = max(MIN_MAP, map_size - 5)
                elif map_plus_rect.collidepoint(mouse_pos):
                    map_size = min(MAX_MAP, map_size + 5)
                elif obs_minus_rect.collidepoint(mouse_pos):
                    obs_ratio = max(MIN_OBS, obs_ratio - 5)
                elif obs_plus_rect.collidepoint(mouse_pos):
                    obs_ratio = min(MAX_OBS, obs_ratio + 5)
                elif toggle_rect.collidepoint(mouse_pos):
                    custom_map = not custom_map
                elif start_rect.collidepoint(mouse_pos):
                    running = False
        
        # === DRAW ===
        screen.fill(BG)
        
        # Title
        title_surf = font_title.render("AMR Simulator", True, TEXT_WHITE)
        title_rect = title_surf.get_rect(centerx=425, y=30)
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        sub_surf = font_subtitle.render("Cau hinh mo phong", True, TEXT_DIM)
        sub_rect = sub_surf.get_rect(centerx=425, y=90)
        screen.blit(sub_surf, sub_rect)
        
        # Decorative line
        pygame.draw.line(screen, ACCENT_GREEN, (225, 130), (625, 130), 2)
        
        # === Card 1: Number of AMRs ===
        card1_rect = pygame.Rect(125, 160, 600, 100)
        pygame.draw.rect(screen, CARD_BG, card1_rect, border_radius=12)
        pygame.draw.rect(screen, BORDER, card1_rect, 2, border_radius=12)
        
        label1 = font_label.render("So luong xe:", True, TEXT_WHITE)
        screen.blit(label1, (165, 180))
        
        amr_minus_rect.center = (485, 210)
        color_m = ACCENT_BLUE if amr_minus_rect.collidepoint(mouse_pos) else BORDER
        pygame.draw.rect(screen, color_m, amr_minus_rect, border_radius=8)
        minus_surf = font_value.render("-", True, TEXT_WHITE)
        screen.blit(minus_surf, minus_surf.get_rect(center=amr_minus_rect.center))
        
        val1 = font_value.render(str(num_amrs), True, ACCENT_GREEN)
        screen.blit(val1, val1.get_rect(center=(570, 210)))
        
        amr_plus_rect.center = (655, 210)
        color_p = ACCENT_BLUE if amr_plus_rect.collidepoint(mouse_pos) else BORDER
        pygame.draw.rect(screen, color_p, amr_plus_rect, border_radius=8)
        plus_surf = font_value.render("+", True, TEXT_WHITE)
        screen.blit(plus_surf, plus_surf.get_rect(center=amr_plus_rect.center))
        
        # === Card 2: Map Size ===
        card2_rect = pygame.Rect(125, 280, 600, 100)
        pygame.draw.rect(screen, CARD_BG, card2_rect, border_radius=12)
        pygame.draw.rect(screen, BORDER, card2_rect, 2, border_radius=12)
        
        label2 = font_label.render("Kich thuoc map:", True, TEXT_WHITE)
        screen.blit(label2, (165, 300))
        
        map_minus_rect.center = (485, 330)
        color_m2 = ACCENT_BLUE if map_minus_rect.collidepoint(mouse_pos) else BORDER
        pygame.draw.rect(screen, color_m2, map_minus_rect, border_radius=8)
        minus_surf2 = font_value.render("-", True, TEXT_WHITE)
        screen.blit(minus_surf2, minus_surf2.get_rect(center=map_minus_rect.center))
        
        val2_text = f"{map_size} x {map_size}"
        val2 = font_value.render(val2_text, True, ACCENT_GREEN)
        screen.blit(val2, val2.get_rect(center=(570, 330)))
        
        map_plus_rect.center = (655, 330)
        color_p2 = ACCENT_BLUE if map_plus_rect.collidepoint(mouse_pos) else BORDER
        pygame.draw.rect(screen, color_p2, map_plus_rect, border_radius=8)
        plus_surf2 = font_value.render("+", True, TEXT_WHITE)
        screen.blit(plus_surf2, plus_surf2.get_rect(center=map_plus_rect.center))
        
        # === Card 3: Obstacle Ratio ===
        card3_rect = pygame.Rect(125, 400, 600, 100)
        pygame.draw.rect(screen, CARD_BG, card3_rect, border_radius=12)
        pygame.draw.rect(screen, BORDER, card3_rect, 2, border_radius=12)
        
        label3 = font_label.render("Ti le vat can:", True, TEXT_WHITE)
        screen.blit(label3, (165, 420))
        if custom_map:
            hint_t = font_hint.render("(Vo hieu hoa khi Tu Ve Map)", True, TEXT_DIM)
            screen.blit(hint_t, (165, 455))
        
        obs_minus_rect.center = (485, 450)
        color_m3 = (BORDER if custom_map else (ACCENT_BLUE if obs_minus_rect.collidepoint(mouse_pos) else BORDER))
        pygame.draw.rect(screen, color_m3, obs_minus_rect, border_radius=8)
        minus_surf3 = font_value.render("-", True, TEXT_WHITE if not custom_map else TEXT_DIM)
        screen.blit(minus_surf3, minus_surf3.get_rect(center=obs_minus_rect.center))
        
        val3_text = f"{obs_ratio}%"
        val3 = font_value.render(val3_text, True, ACCENT_GREEN if not custom_map else TEXT_DIM)
        screen.blit(val3, val3.get_rect(center=(570, 450)))
        
        obs_plus_rect.center = (655, 450)
        color_p3 = (BORDER if custom_map else (ACCENT_BLUE if obs_plus_rect.collidepoint(mouse_pos) else BORDER))
        pygame.draw.rect(screen, color_p3, obs_plus_rect, border_radius=8)
        plus_surf3 = font_value.render("+", True, TEXT_WHITE if not custom_map else TEXT_DIM)
        screen.blit(plus_surf3, plus_surf3.get_rect(center=obs_plus_rect.center))

        # === Card 4: Map Mode ===
        card4_rect = pygame.Rect(125, 520, 600, 80)
        pygame.draw.rect(screen, CARD_BG, card4_rect, border_radius=12)
        pygame.draw.rect(screen, BORDER, card4_rect, 2, border_radius=12)
        
        label4 = font_label.render("Che do Tu ve Map (Custom):", True, TEXT_WHITE)
        screen.blit(label4, (165, 545))
        
        toggle_rect.center = (570, 560)
        t_color = ACCENT_PURPLE if custom_map else BORDER
        pygame.draw.rect(screen, t_color, toggle_rect, border_radius=20)
        # Toggle knob
        knob_x = toggle_rect.right - 20 if custom_map else toggle_rect.left + 20
        pygame.draw.circle(screen, TEXT_WHITE, (knob_x, toggle_rect.centery), 16)
        
        # === Start Button ===
        start_rect.center = (425, 650)
        btn_color = BTN_HOVER if hover_start else BTN_START
        pygame.draw.rect(screen, btn_color, start_rect, border_radius=14)
        pygame.draw.rect(screen, (255, 255, 255), start_rect, 2, border_radius=14)
        
        start_text = font_btn.render("BAT DAU", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=start_rect.center))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    return num_amrs, map_size, obs_ratio / 100.0, custom_map
