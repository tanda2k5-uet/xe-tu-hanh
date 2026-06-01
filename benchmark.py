import sys
import random
import time
from core.map import Maps
from component.processor import Processors
import math

class BenchmarkApp:
    def __init__(self, num_amrs=5, map_size=30, obstacle_ratio=0.2):
        self.num_amrs = num_amrs
        self.map_size = map_size
        self.map = Maps(mapSize=[map_size, map_size], map_data=None)
        self.map.randomMap(obstacle_ratio=obstacle_ratio)
        self.processor = Processors()
        
        self.current_nodes = []
        for i in range(num_amrs):
            while True:
                r, c = random.randint(1, map_size-2), random.randint(1, map_size-2)
                if self.map.map[r][c] == 0 and (r, c) not in self.current_nodes:
                    self.current_nodes.append((r, c))
                    break
                    
        self.target_nodes = [None] * num_amrs
        self.paths = [[] for _ in range(num_amrs)]
        self.states = ["SEEKING"] * num_amrs
        self.wait_ticks = [0] * num_amrs
        self.wait_reasons = [""] * num_amrs
        
        # Metrics
        self.scores = [0] * num_amrs
        self.timeouts = 0
        self.total_path_computations = 0
        self.total_computation_time = 0.0

    def spawnTarget(self, i):
        while True:
            r, c = random.randint(1, self.map_size-2), random.randint(1, self.map_size-2)
            if self.map.map[r][c] == 0 and (r, c) not in self.current_nodes and (r, c) not in self.target_nodes:
                self.target_nodes[i] = (r, c)
                break

    def run(self, max_ticks=2000):
        for i in range(self.num_amrs):
            self.spawnTarget(i)
            
        for tick in range(max_ticks):
            # 1. Update positions
            for i in range(self.num_amrs):
                if len(self.paths[i]) > 1:
                    self.current_nodes[i] = self.paths[i][1]
                    self.paths[i].pop(0)

            # 2. Check arrival
            for i in range(self.num_amrs):
                if self.target_nodes[i] is not None and self.current_nodes[i] == self.target_nodes[i]:
                    self.scores[i] += 1
                    self.spawnTarget(i)
                    self.paths[i] = []
                    self.states[i] = "SEEKING"
                    self.wait_ticks[i] = 0
                    
            # 3. Check timeouts (Wait 10 ticks ~ 5 seconds in real simulation)
            for i in range(self.num_amrs):
                if self.states[i] == "WAITING":
                    self.wait_ticks[i] += 1
                    if self.wait_ticks[i] > 10: 
                        self.timeouts += 1
                        self.spawnTarget(i)
                        self.states[i] = "SEEKING"
                        self.paths[i] = []
                        self.wait_ticks[i] = 0
                        
            # 4. Plan paths (2 passes)
            for pass_num in range(2):
                for i in range(self.num_amrs):
                    reserved = []
                    for j in range(self.num_amrs):
                        if i == j: continue
                        should_respect = False
                        if j < i: should_respect = True
                        elif pass_num == 1: should_respect = True
                        
                        if should_respect:
                            if not self.paths[j] or len(self.paths[j]) <= 1:
                                reserved.append([self.current_nodes[j]] * 130)
                            else:
                                reserved.append(self.paths[j])
                    
                    need_replan = not self.paths[i]
                    if not need_replan and len(self.paths[i]) > 1:
                        for t in range(1, len(self.paths[i])):
                            my_pos_at_t = self.paths[i][t]
                            my_pos_at_prev = self.paths[i][t-1]
                            for j in range(self.num_amrs):
                                if i == j: continue
                                if not self.paths[j]:
                                    other_pos_at_t = self.current_nodes[j]
                                    other_pos_at_prev = self.current_nodes[j]
                                else:
                                    other_pos_at_t = self.paths[j][t] if t < len(self.paths[j]) else self.paths[j][-1]
                                    other_pos_at_prev = self.paths[j][t-1] if (t-1) < len(self.paths[j]) else self.paths[j][-1]
                                    
                                if my_pos_at_t == other_pos_at_t or (my_pos_at_t == other_pos_at_prev and my_pos_at_prev == other_pos_at_t):
                                    need_replan = True
                                    break
                            if need_replan: break
                            
                    force_replan = need_replan
                    if pass_num == 1 and (not self.paths[i] or len(self.paths[i]) <= 1):
                        force_replan = True
                        
                    if force_replan:
                        can_search = True
                        if self.states[i] == "WAITING":
                            if self.wait_reasons[i] == "WALLED_OFF":
                                can_search = False
                                
                        if can_search:
                            start_time = time.perf_counter()
                            result = self.processor.st_bfs(self.current_nodes[i], self.target_nodes[i], self.map.map, reserved_paths=reserved)
                            elapsed = time.perf_counter() - start_time
                            self.total_computation_time += elapsed
                            self.total_path_computations += 1
                            
                            if result:
                                self.paths[i] = result
                                self.states[i] = "SEEKING"
                                self.wait_reasons[i] = ""
                            else:
                                self.paths[i] = [self.current_nodes[i]]
                                if pass_num == 1:
                                    struct_path = self.processor.bfs(self.current_nodes[i], self.target_nodes[i], self.map.map)
                                    if struct_path is None:
                                        self.states[i] = "WAITING"
                                        self.wait_reasons[i] = "WALLED_OFF"
                                    else:
                                        self.states[i] = "WAITING"
                                        self.wait_reasons[i] = "TRAFFIC"

        total_score = sum(self.scores)
        avg_comp = (self.total_computation_time / self.total_path_computations * 1000) if self.total_path_computations > 0 else 0
        return total_score, self.timeouts, avg_comp

if __name__ == "__main__":
    print("BAT DAU CHAY BENCHMARK...")
    print(f"{'So xe':<10} | {'Diem so (Throughput)':<22} | {'So lan ket (Timeouts)':<25} | {'TG tinh toan (ms)':<17} | {'Tong TG chay (s)'}")
    print("-" * 105)
    
    # Save the map picture
    try:
        import pygame
        pygame.init()
        random.seed(42)
        dummy_map = Maps(mapSize=[30, 30], map_data=None)
        dummy_map.randomMap(obstacle_ratio=0.2)
        cell_size = 20
        surf = pygame.Surface((30 * cell_size, 30 * cell_size))
        surf.fill((255, 255, 255))
        for r in range(30):
            for c in range(30):
                if dummy_map.map[r][c] == 1:
                    pygame.draw.rect(surf, (100, 100, 100), (c*cell_size, r*cell_size, cell_size, cell_size))
                pygame.draw.rect(surf, (200, 200, 200), (c*cell_size, r*cell_size, cell_size, cell_size), 1)
        pygame.image.save(surf, "benchmark_map.png")
        pygame.quit()
    except Exception as e:
        print("Loi luu anh:", e)

    # Chạy 3 lần để lấy trung bình hoặc chỉ chạy 1 lần kịch bản 1000 ticks
    for amrs in [5, 10, 15, 20]:
        random.seed(42)
        app = BenchmarkApp(num_amrs=amrs, map_size=30, obstacle_ratio=0.2)
        t0 = time.time()
        score, timeouts, avg_comp = app.run(max_ticks=1000)
        total_time_s = time.time() - t0
        print(f"{amrs:<10} | {score:<22} | {timeouts:<25} | {avg_comp:<14.2f} ms | {total_time_s:.2f} s")
