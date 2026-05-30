from random import choice, randint

class Processors(object):

    def __init__(self, obstacleSolution=()):
        self.obstacleSolution = obstacleSolution
        self.path = []
        self.lastDecision = 90

    # rule for not repeating the previous position
    def rule1(self):
        pass

    def staticObstacleAvoidanceSolution(self, sensorInput)->tuple:
        self.obstacleSolution = tuple(sensorInput)
    
    def pathPlanning(self, path):
        self.path = path

    def makeDecision(self)->int:
        bestSolution = None
        if (solutionNumber:=len(self.obstacleSolution)) > 0:
            if solutionNumber > 1:
                obstacleSolution = list(self.obstacleSolution)
                if self.lastDecision in obstacleSolution:
                    obstacleSolution.remove(self.lastDecision)
                bestSolution = int(choice(obstacleSolution))
            else:
                bestSolution = int(self.obstacleSolution[0])
        self.lastDecision = bestSolution + 180
        if self.lastDecision >= 360:
            self.lastDecision %= 360
        return bestSolution
    
    def output(self):
        pass

    def bfs(self, start_node, goal_node, grid_map, other_obstacles=None):
        if other_obstacles is None:
            other_obstacles = []
        from collections import deque
        queue = deque([(start_node, [start_node])])
        visited = set([start_node])
        
        while queue:
            (row, col), path = queue.popleft()
            
            if (row, col) == goal_node:
                return path
            
            # Check 4 neighbors: up, down, left, right
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                # Check boundaries and obstacles (0 means free space)
                if 0 <= nr < len(grid_map) and 0 <= nc < len(grid_map[0]):
                    if grid_map[nr][nc] == 0 and (nr, nc) not in visited and (nr, nc) not in other_obstacles:
                        visited.add((nr, nc))
                        queue.append(((nr, nc), path + [(nr, nc)]))
        return None

    def st_bfs(self, start_node, goal_node, grid_map, reserved_paths=None):
        """Space-Time BFS to find a path while avoiding multiple moving obstacles"""
        if reserved_paths is None:
            reserved_paths = []
        from collections import deque
        # Queue stores: (current_node, time_step, path)
        queue = deque([(start_node, 0, [start_node])])
        # Visited stores: (node, time_step)
        visited = set([(start_node, 0)])
        
        max_time = 120 # limit search depth to prevent infinite loops
        
        def get_reserved_pos(rpath, t):
            """Get position of a reserved path at time t"""
            if not rpath:
                return None
            if t < len(rpath):
                return rpath[t]
            return rpath[-1]  # AMR stays at last position
        
        while queue:
            current_node, t, path = queue.popleft()
            
            # If we reach the goal and stay there safely
            if current_node == goal_node:
                safe_at_end = True
                for rpath in reserved_paths:
                    for future_t in range(t, min(t + 5, len(rpath))):
                        if rpath[future_t] == current_node:
                            safe_at_end = False
                            break
                    if not safe_at_end:
                        break
                if safe_at_end:
                    return path
            
            if t >= max_time:
                continue
                
            next_t = t + 1
            
            row, col = current_node
            # 4 neighbors + wait in place (0, 0)
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < len(grid_map) and 0 <= nc < len(grid_map[0]):
                    if grid_map[nr][nc] == 0:
                        
                        blocked = False
                        for rpath in reserved_paths:
                            # 1. Vertex collision: other AMR is at (nr, nc) at next_t
                            reserved_pos_at_next_t = get_reserved_pos(rpath, next_t)
                            if (nr, nc) == reserved_pos_at_next_t:
                                blocked = True
                                break
                                
                            # 2. Edge collision (swapping positions)
                            reserved_pos_at_t = get_reserved_pos(rpath, t)
                            if (nr, nc) == reserved_pos_at_t and current_node == reserved_pos_at_next_t:
                                blocked = True
                                break
                        
                        if blocked:
                            continue
                            
                        if ((nr, nc), next_t) not in visited:
                            visited.add(((nr, nc), next_t))
                            queue.append(((nr, nc), next_t, path + [(nr, nc)]))
        return None
