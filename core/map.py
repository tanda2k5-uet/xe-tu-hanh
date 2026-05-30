import random

class Maps(object):
    
    # initialize a matrix map/virtual map, prepear map data including posible positions and mark border positions
    def __init__(self, mapSize=[30, 30], map_data=None):
        if map_data is not None:
            self.map = map_data
        else:
            self.map = [] 
            for row in range(mapSize[0]): 
                new_row = [] 
                for col in range(mapSize[1]): 
                    if (row == 0)|(row == mapSize[0] - 1)|(col == 0)|(col == mapSize[1] - 1): 
                        new_node = 1 
                    else: 
                        new_node = 0 
                    new_row.append(new_node) 
                self.map.append(new_row)

    # create obstacts by randoming on the map
    def randomMap(self, obstacle_ratio=0.2): 
        if self.map is not None:
            for row in range(1, len(self.map) - 1): 
                for col in range(1, len(self.map[row]) - 1): 
                    if random.random() < obstacle_ratio:
                        self.map[row][col] = 1
                    else:
                        self.map[row][col] = 0
        else:
            print("Please initialize a map.")
    

