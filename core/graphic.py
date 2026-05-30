import pygame
import math
import numpy
# from core.map import Maps
from utils.utils import *

class Graphics(object):

    # initialize all objects to draw
    def __init__(self, screenSize):
        # initialize all pygame modules
        pygame.init()
        # indicate rendering details
        displayFlags = pygame.RESIZABLE
        # create and display the window
        self.screen = pygame.display.set_mode(screenSize, displayFlags)
        # set the text that appears in the title bar of the window
        pygame.display.set_caption("AMR in Pygame")      
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 40)

    # draw dot line
    def drawDottedLine(self, color, start_pos, end_pos, dot_length=5, space_length=15):
        # Calculate total distance
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            return

        # Calculate unit vector
        dx /= distance
        dy /= distance

        # Draw dots
        num_dots = int(distance // (dot_length + space_length))
        for i in range(num_dots + 1):
            start_x = start_pos[0] + (dot_length + space_length) * i * dx
            start_y = start_pos[1] + (dot_length + space_length) * i * dy
            end_x = start_x + dot_length * dx
            end_y = start_y + dot_length * dy
            pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), 2)

    # draw the map by pygame 
    def drawMap(self, map, color=(107, 107, 105)): 
        cell_w = self.screen.get_width() / len(map[0])
        cell_h = self.screen.get_height() / len(map)
        
        # Draw horizontal grid lines
        for row in range(len(map) + 1):
            y = row * cell_h
            pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y), 1)
            
        # Draw vertical grid lines
        for col in range(len(map[0]) + 1):
            x = col * cell_w
            pygame.draw.line(self.screen, color, (x, 0), (x, self.screen.get_height()), 1)
            
        # Draw obstacles as solid blocks filling the cell
        for row in range(len(map)): 
            for col in range(len(map[row])): 
                if map[row][col] != 0: 
                    # Fill the cell completely with a dark wall
                    rect = pygame.Rect(col * cell_w, row * cell_h, cell_w, cell_h)
                    # Add a slight gap for grid lines to still show
                    rect.inflate_ip(-2, -2)
                    pygame.draw.rect(self.screen, (80, 80, 80), rect)
                    pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)

    # draw amr in pixel map
    def drawAmr(self, amr):
        # 4 points on amr coordinate system
        points = numpy.array([[- amr.width/2, - amr.height/2],
                              [amr.width/2, - amr.height/2],
                              [amr.width/2, amr.height/2],
                              [-amr.width/2, amr.height/2]])
        angle = amr.heading
        tMatrix = transformationMatrix2d(rotation_deg=angle, translation=amr.pos)
        # 4 points of amr on the global coordinate system
        tPoints = apply_transformation(points, tMatrix)
        # Draw filled body with AMR color
        pygame.draw.polygon(self.screen, amr.color, tPoints)
        # Draw thick border around the body
        pygame.draw.polygon(self.screen, (0, 0, 0), tPoints, 3)
        # two axis on amr coordinate system
        axisPoints = numpy.array([[0, 0],
                                 [amr.width, 0],
                                 [0, 0],
                                 [0, amr.height]])
        aPoints = apply_transformation(axisPoints, tMatrix)
        # draw amr x axis (heading direction)
        pygame.draw.line(self.screen, (255, 255, 255), aPoints[0], aPoints[1], 3)

        # draw coordinate origin of the amr in pixel        
        pygame.draw.circle(self.screen, (255, 255, 255), (int(amr.pos[0]), int(amr.pos[1])), 4)
        
        # draw path
        if len(amr.path_points) > 1:
            for index in range(len(amr.path_points) - 1):
                self.drawDottedLine((245, 149, 5), amr.path_points[index], amr.path_points[index + 1])

    def drawTarget(self, node_pos, map_data, color=(255, 215, 0)):
        if node_pos is not None:
            cell_w = self.screen.get_width() / len(map_data[0])
            cell_h = self.screen.get_height() / len(map_data)
            radius = max(2, int(min(cell_w, cell_h) * 0.3))
            pixelPos = turn2pixel(map_data, self.screen.get_height(), self.screen.get_width(), node_pos[0], node_pos[1])
            pygame.draw.circle(self.screen, color, (int(pixelPos[0]), int(pixelPos[1])), radius)
            pygame.draw.circle(self.screen, (0, 0, 0), (int(pixelPos[0]), int(pixelPos[1])), radius, max(1, int(radius/5)))
            
    def drawText(self, text, position, color=(0, 0, 0)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def drawSelectedAmr(self, amr, pulse_tick):
        """Draw a glowing selection ring around a manually controlled AMR."""
        pulse = abs(math.sin(pulse_tick * 0.05)) * 6
        radius = int(max(amr.width, amr.height) * 0.75 + pulse)
        cx, cy = int(amr.pos[0]), int(amr.pos[1])
        pygame.draw.circle(self.screen, (255, 255, 80), (cx, cy), radius + 4, 2)
        pygame.draw.circle(self.screen, (255, 220, 0), (cx, cy), radius, 3)

    def drawWaitingForCommand(self, amr, pulse_tick):
        """Draw a blinking 'CLICK MAP' label above the selected AMR when waiting for destination."""
        alpha = int(128 + 127 * math.sin(pulse_tick * 0.1))
        cx = int(amr.pos[0])
        cy = int(amr.pos[1] - max(amr.height, amr.width) - 12)
        font_small = pygame.font.SysFont(None, 22)
        surf = font_small.render("CLICK MAP", True, (255, 220, 0))
        surf.set_alpha(alpha)
        self.screen.blit(surf, (cx - surf.get_width() // 2, cy))
