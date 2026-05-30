import math
from component.sensor import Sensors
from component.processor import Processors
from component.actuator import Actuators

class Amrs(object):

    # initialize a amr in pygame coordinate system
    def __init__(self, amrDimension=[30, 25], position=[0, 0], orientation=90):
        self.width = amrDimension[0]
        self.height = amrDimension[1]
        self.pos = position
        self.heading = orientation
        self.color = (0, 200, 0)
        self.path_points = []
        self.path_points.append(tuple(position))
        self.speed = 10

    def moveForward(self, distance):
        """Move turtle forward by distance in current direction."""
        rad = math.radians(self.heading)
        self.pos[0] += math.cos(rad) * distance
        self.pos[1] -= math.sin(rad) * distance  # Minus because y increases downward
        self.path_points.append(tuple(self.pos))

    def turnLeft(self):
        """Turn turtle left by angle degrees."""
        self.heading = 180

    def turnRight(self):
        """Turn turtle right by angle degrees."""
        self.heading = 0

    def turnUp(self):
        self.heading = 270

    def turnDown(self):
        self.heading = 90