import pygame
import sys
from core.map import Maps
from core.graphic import Graphics

def run_map_editor(map_size, num_amrs):
    """Map Editor to let user draw obstacles"""
    pygame.init()
    screen_size = [800, 800]
    graphic = Graphics(screen_size)
    pygame.display.set_caption("AMR Simulator - Map Editor")
    clock = pygame.time.Clock()
    
    # Initialize empty map with borders
    map_obj = Maps(mapSize=[map_size, map_size])
    
    # Font
    font_hint = pygame.font.SysFont("segoeui", 24)
    
    running = True
    drawing = False
    erasing = False
    
    def get_cell_from_mouse(pos):
        cell_w = graphic.screen.get_width() / map_size
        cell_h = graphic.screen.get_height() / map_size
        
        c = int(pos[0] / cell_w)
        r = int(pos[1] / cell_h)
        
        # Prevent drawing on the outermost boundary (walls)
        if 0 < r < map_size - 1 and 0 < c < map_size - 1:
            return r, c
        return None
    
    last_cell = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    running = False # Exit editor and return map
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
                elif event.button == 3:
                    erasing = True
                last_cell = get_cell_from_mouse(event.pos)
                if last_cell:
                    map_obj.map[last_cell[0]][last_cell[1]] = 1 if drawing else 0
                    
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
                elif event.button == 3:
                    erasing = False
                last_cell = None
                
            if event.type == pygame.MOUSEMOTION:
                if drawing or erasing:
                    current_cell = get_cell_from_mouse(event.pos)
                    if current_cell and last_cell:
                        # Simple line interpolation to prevent skipping cells when moving mouse fast
                        r0, c0 = last_cell
                        r1, c1 = current_cell
                        steps = max(abs(r1 - r0), abs(c1 - c0))
                        for i in range(steps + 1):
                            t = i / steps if steps > 0 else 0
                            r = int(r0 + t * (r1 - r0))
                            c = int(c0 + t * (c1 - c0))
                            if 0 < r < map_size - 1 and 0 < c < map_size - 1:
                                map_obj.map[r][c] = 1 if drawing else 0
                    if current_cell:
                        last_cell = current_cell

        # === DRAW ===
        graphic.screen.fill((255, 255, 255))
        
        # Draw map
        graphic.drawMap(map_obj.map, (220, 220, 220))
        
        # Draw hints
        hint_text = "CHUOT TRAI: Ve tuong | CHUOT PHAI: Xoa tuong | ENTER: Bat dau"
        surf = font_hint.render(hint_text, True, (0, 0, 0))
        
        # Background for text
        bg_rect = surf.get_rect(topleft=(10, 10))
        bg_rect.inflate_ip(10, 10)
        pygame.draw.rect(graphic.screen, (255, 255, 255), bg_rect)
        pygame.draw.rect(graphic.screen, (0, 0, 0), bg_rect, 2)
        graphic.screen.blit(surf, (15, 15))
        
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    return map_obj.map
