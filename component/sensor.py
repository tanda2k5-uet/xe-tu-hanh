# from core.map import Maps
from utils.utils import *

class Sensors(object):

    # initialize a simple sensor
    def __init__(self, position=[0, 0]):
        # position of the sensor on global coordinate system
        self.pos = position

    # set the current position of the sensor
    def setPos(self, position):
        self.pos = position

    # check the current position, whether it is a border postion or not
    def isWall(self, map, current_mposition): 
        return (current_mposition[0] == 0) | (current_mposition[0] == len(map) - 1) | (current_mposition[1] == 0) | (current_mposition[1] == len(map[0]) - 1) 

    # get sensory outputs: find all (four) solutions with no obstacles
    def getOutput(self, input, width, height):
        nodePos = turn2node(input, width, height, self.pos[0], self.pos[1])
        output = []
        if (input[nodePos[0] - 1][nodePos[1]] == 0): 
            output.append(270) 
        if (input[nodePos[0] + 1][nodePos[1]] == 0): 
            output.append(90) 
        if (input[nodePos[0]][nodePos[1] -1] == 0): 
            output.append(180) 
        if (input[nodePos[0]][nodePos[1] + 1] == 0): 
            output.append(0) 
        return output