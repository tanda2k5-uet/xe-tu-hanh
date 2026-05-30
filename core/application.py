"""
This is a main class for an application to simulate an amr in the enviroment.
An application has three stages:
- Initializing.
- Goto the main loop.
- Exit.
The main loop of an application has four stages:
- Updating Input from outsides.
- Sensoring the environment.
- Amr Processing.
- Updating orientation and position of the amr.
"""
import pygame
import sys
import random
import colorsys
from core.input import Input
from core.map import Maps
from core.graphic import Graphics
from core.amr import Amrs
from component.sensor import Sensors
from component.processor import Processors
from utils.utils import *

def generate_colors(n):
    """Generate N visually distinct bold colors using HSV color wheel"""
    amr_colors = []
    target_colors = []
    for i in range(n):
        hue = i / n  # evenly spaced hues
        # Bold AMR color
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.85)
        amr_colors.append((int(r*255), int(g*255), int(b*255)))
        # Lighter target color
        r2, g2, b2 = colorsys.hsv_to_rgb(hue, 0.4, 1.0)
        target_colors.append((int(r2*255), int(g2*255), int(b2*255)))
    return amr_colors, target_colors

def generate_start_nodes(n, map_size):
    """Generate N spread-out start positions on a map_size x map_size grid"""
    import math
    nodes = []
    # Calculate grid layout
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    margin = 2
    available = map_size - 2 * margin  # inner space (excluding border)
    
    for i in range(n):
        r = i // cols
        c = i % cols
        row = margin + int((r + 0.5) * available / rows)
        col = margin + int((c + 0.5) * available / cols)
        # Clamp to valid range
        row = max(2, min(map_size - 3, row))
        col = max(2, min(map_size - 3, col))
        nodes.append((row, col))
    return nodes

import threading
import tkinter as tk
from tkinter import ttk

class ScoreboardWindow(threading.Thread):
    def __init__(self, num_amrs, amr_colors):
        super().__init__()
        self.num_amrs = num_amrs
        self.amr_colors = amr_colors
        self.scores = [0] * num_amrs
        self.states = ["SEEKING"] * num_amrs
        self.path_lengths = [0] * num_amrs
        self.running = True
        self.labels = []
        self.cards = []          # store card frames for highlight
        self.daemon = True
        # Thread-safe: index of manually selected AMR (-1 = none)
        self._selected_amr = -1
        self._lock = threading.Lock()

    def get_selected(self):
        """Read the currently selected AMR index (-1 if none). Thread-safe."""
        with self._lock:
            return self._selected_amr

    def set_selected(self, idx):
        """Set selected AMR from the main thread (pygame). Thread-safe."""
        with self._lock:
            self._selected_amr = idx
        
    def run(self):
        try:
            self.root = tk.Tk()
            self.root.title("Thong tin Xe (AMR)")
            self.root.geometry("320x600")
            self.root.configure(bg="#F3F4F6")
            
            # Title
            title_lbl = tk.Label(self.root, text="BANG DIEM AMR", font=("Segoe UI", 14, "bold"), fg="#1F2937", bg="#F3F4F6", pady=10)
            title_lbl.pack()
            
            # Create a frame with a canvas and scrollbar
            container = tk.Frame(self.root, bg="#F3F4F6")
            container.pack(fill="both", expand=True, padx=10, pady=5)
            
            canvas = tk.Canvas(container, bg="#F3F4F6", highlightthickness=0)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#F3F4F6")
            
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Dynamically update the scrollable region
            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            scrollable_frame.bind("<Configure>", on_frame_configure)
            
            # Make the frame width match the canvas width
            def on_canvas_configure(event):
                canvas.itemconfig(canvas_window, width=event.width)
            canvas.bind("<Configure>", on_canvas_configure)
            
            # Pack layout
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Mouse wheel scrolling binding
            def _on_mousewheel(event):
                try:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except Exception:
                    pass
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            for i in range(self.num_amrs):
                # Card frame
                card = tk.Frame(scrollable_frame, bg="white", bd=0, relief="flat", padx=10, pady=8,
                                cursor="hand2", highlightthickness=2, highlightbackground="white")
                card.pack(fill="x", expand=True, pady=4, padx=5)
                self.cards.append(card)

                # Click handler: toggle manual select/deselect
                def make_click_handler(idx, c):
                    def on_click(event):
                        with self._lock:
                            if self._selected_amr == idx:
                                # Deselect
                                self._selected_amr = -1
                            else:
                                self._selected_amr = idx
                        # Update highlight on all cards (must run in Tk thread)
                        for k, card_frame in enumerate(self.cards):
                            if k == self.get_selected():
                                card_frame.config(bg="#FEF9C3", highlightbackground="#EAB308")
                                for child in card_frame.winfo_children():
                                    child.config(bg="#FEF9C3")
                            else:
                                card_frame.config(bg="white", highlightbackground="white")
                                for child in card_frame.winfo_children():
                                    child.config(bg="white")
                    return on_click

                handler = make_click_handler(i, card)
                card.bind("<Button-1>", handler)
                for widget in card.winfo_children():
                    widget.bind("<Button-1>", handler)

                # Make the card look nice
                color_hex = '#%02x%02x%02x' % self.amr_colors[i]
                indicator = tk.Canvas(card, width=12, height=12, bg="white", highlightthickness=0,
                                      cursor="hand2")
                indicator.create_oval(1, 1, 11, 11, fill=color_hex, outline="#374151", width=1.5)
                indicator.pack(side="left", padx=(0, 10))
                indicator.bind("<Button-1>", handler)

                lbl = tk.Label(card, text=f"Xe {i+1}: 0", font=("Segoe UI", 11, "bold"),
                               fg="#374151", bg="white", cursor="hand2")
                lbl.pack(side="left")
                lbl.bind("<Button-1>", handler)
                self.labels.append(lbl)
                
            def check_update():
                try:
                    if not self.running:
                        self.root.destroy()
                        return
                    sel = self.get_selected()
                    for i in range(self.num_amrs):
                        txt = f"Xe {i+1}: {self.scores[i]}"
                        if self.states[i] == "WAITING":
                            txt += " (dang cho...)"
                        elif self.states[i] == "MANUAL_IDLE":
                            txt += "  [cho lenh]"
                        elif self.states[i] == "MANUAL_MOVING":
                            if self.path_lengths[i] <= 1:
                                txt += "  [dang tim duong...]"
                            else:
                                txt += "  [dang di]"
                        self.labels[i].config(text=txt)
                        # Sync highlight with pygame-side deselect
                        if i == sel:
                            self.cards[i].config(bg="#FEF9C3", highlightbackground="#EAB308")
                        else:
                            self.cards[i].config(bg="white", highlightbackground="white")
                    self.root.after(150, check_update)
                except Exception:
                    pass
                    
            self.root.after(150, check_update)
            self.root.mainloop()
        except Exception:
            pass
            
    def update_data(self, scores, states, paths):
        self.scores = list(scores)
        self.states = list(states)
        self.path_lengths = [len(p) if p else 0 for p in paths]
        
    def stop(self):
        self.running = False

class Application(object):
    def __init__(self, screenSize=[800, 800], num_amrs=2, map_size=30, map_data=None, obstacle_ratio=0.2):
        
        self.num_amrs = num_amrs
        self.graphic = Graphics(screenSize)   
        
        # determine is main loop is active
        self.running = True
        # manage time-related data and operations
        self.clock = pygame.time.Clock()
        self.lastTime = pygame.time.get_ticks()
        # manage user input
        self.input = Input()
        self.map = Maps(mapSize=[map_size, map_size], map_data=map_data)
        if map_data is None:
            self.map.randomMap(obstacle_ratio=obstacle_ratio)
        
        # Generate colors and start positions dynamically
        self.amr_colors, self.target_colors = generate_colors(num_amrs)
        self.start_nodes = generate_start_nodes(num_amrs, map_size)
        
        # Ensure AMRs do not spawn inside walls without erasing the user's custom walls
        for i, node in enumerate(self.start_nodes):
            r, c = node[0], node[1]
            if 0 <= r < len(self.map.map) and 0 <= c < len(self.map.map[0]):
                if self.map.map[r][c] != 0:
                    # Target node is a wall. Find the nearest empty cell.
                    queue = [(r, c)]
                    visited = set([(r, c)])
                    found = False
                    while queue:
                        curr_r, curr_c = queue.pop(0)
                        if self.map.map[curr_r][curr_c] == 0 and (curr_r, curr_c) not in self.start_nodes[:i]:
                            self.start_nodes[i] = (curr_r, curr_c)
                            found = True
                            break
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = curr_r + dr, curr_c + dc
                            if 0 < nr < len(self.map.map) - 1 and 0 < nc < len(self.map.map[0]) - 1:
                                if (nr, nc) not in visited:
                                    visited.add((nr, nc))
                                    queue.append((nr, nc))
                    if not found:
                        self.map.map[r][c] = 0 # Fallback safety
        
        # Initialize N AMRs
        self.amrs = []
        cell_w = self.graphic.screen.get_width() / len(self.map.map[0])
        cell_h = self.graphic.screen.get_height() / len(self.map.map)
        amr_w = max(4, int(cell_w * 0.75))
        amr_h = max(4, int(cell_h * 0.75))
        
        self.sensors = []
        for i in range(num_amrs):
            row, col = self.start_nodes[i]
            px, py = turn2pixel(self.map.map, self.graphic.screen.get_height(), self.graphic.screen.get_width(), row, col)
            self.amrs.append(Amrs(amrDimension=[amr_w, amr_h], position=[px, py]))
            self.amrs[i].color = self.amr_colors[i]
            self.sensors.append(Sensors(position=[px, py]))
        
        self.processor = Processors()
        self.scores = [0] * num_amrs
        self.target_nodes = [None] * num_amrs
        self.states = ["SEEKING"] * num_amrs
        self.wait_start_times = [0] * num_amrs
        self.wait_reasons = [""] * num_amrs
        self.paths = [[] for _ in range(num_amrs)]
        
        # Smooth movement interpolation
        self.move_duration = max(10, 30 - num_amrs)  # faster with more AMRs
        self.move_progress = [0] * num_amrs
        self.is_moving = [False] * num_amrs
        self.move_start_pos = [None] * num_amrs
        self.move_end_pos = [None] * num_amrs
        self.current_nodes = list(self.start_nodes)

        # --- Manual control state ---
        # Index of the manually selected AMR, or None if none selected
        self.manual_amr = None
        self.manual_block_start_time = None
        # Pulse tick counter for visual animation
        self.pulse_tick = 0

    def unitDistance(self):
        row_segment = len(self.map.map) - 1 
        col_segment = len(self.map.map[0]) - 1 
        row_distance = self.graphic.screen.get_height()/row_segment 
        col_distance = self.graphic.screen.get_width()/col_segment
        return (row_distance, col_distance)
    
    def node2pixel(self, node):
        """Convert grid node (row, col) to pixel position (x, y)"""
        return turn2pixel(self.map.map, self.graphic.screen.get_height(), 
                         self.graphic.screen.get_width(), node[0], node[1])
    
    def pixel2node(self, px, py):
        """Convert a pixel position (px, py) to the nearest grid node (row, col)."""
        return turn2node(self.map.map, self.graphic.screen.get_width(),
                         self.graphic.screen.get_height(), px, py)

    def spawnTarget(self, amr_index):
        empty_nodes = []
        occupied = set(self.current_nodes)
        existing_targets = set(t for t in self.target_nodes if t is not None)
        for r in range(1, len(self.map.map) - 1):
            for c in range(1, len(self.map.map[0]) - 1):
                if self.map.map[r][c] == 0 and (r, c) not in occupied and (r, c) not in existing_targets:
                    empty_nodes.append((r, c))
        if empty_nodes:
            self.target_nodes[amr_index] = random.choice(empty_nodes)
        else:
            self.target_nodes[amr_index] = None
    
    def _amr_pixel_radius(self, i):
        """Return a click-detection radius in pixels for AMR i."""
        return max(self.amrs[i].width, self.amrs[i].height)

    def _handle_click(self, mx, my):
        """
        Process a left-mouse-button click at pixel (mx, my).
        Priority:
          1. If no AMR is manually selected: check if any AMR was clicked -> select it.
          2. If an AMR is selected and it is MANUAL_IDLE (waiting for destination):
             - treat the click as a map destination.
          3. If an AMR is selected and it is MANUAL_MOVING: ignore click.
        """
        if self.manual_amr is None:
            # Try to select an AMR
            for i in range(self.num_amrs):
                cx, cy = int(self.amrs[i].pos[0]), int(self.amrs[i].pos[1])
                r = self._amr_pixel_radius(i)
                dist2 = (mx - cx) ** 2 + (my - cy) ** 2
                if dist2 <= r * r:
                    # Select this AMR for manual control
                    self.manual_amr = i
                    # Pause auto-driving: keep its current path so it finishes the
                    # current move tick, then we override when it stops.
                    # Mark it as manual so the update loop ignores it for auto-planning.
                    if self.states[i] not in ("MANUAL_MOVING", "MANUAL_IDLE"):
                        # If it was auto-driving, let it reach current destination
                        # then we take over. Set state to MANUAL_IDLE once it stops.
                        self.states[i] = "MANUAL_MOVING" if (self.paths[i] and len(self.paths[i]) > 1) else "MANUAL_IDLE"
                    print(f"[Manual] AMR {i+1} selected.")
                    return  # only select one at a time
        else:
            i = self.manual_amr
            # Check if user clicked on the AMR itself -> deselect
            cx, cy = int(self.amrs[i].pos[0]), int(self.amrs[i].pos[1])
            r = self._amr_pixel_radius(i)
            dist2 = (mx - cx) ** 2 + (my - cy) ** 2
            if dist2 <= r * r:
                # Deselect: return to autonomous mode
                self.manual_amr = None
                self.states[i] = "SEEKING"
                self.paths[i] = []
                self.target_nodes[i] = None
                self.spawnTarget(i)
                print(f"[Manual] AMR {i+1} deselected. Returning to auto.")
                return

            # Accept map-destination clicks anytime the AMR is selected (even if moving/waiting)
            if self.states[i] in ["MANUAL_IDLE", "MANUAL_MOVING"]:
                self.manual_block_start_time = None # Reset timeout
                clicked_node = self.pixel2node(mx, my)
                row, col = clicked_node
                # Validate: must be inside map, not a wall
                if 0 <= row < len(self.map.map) and 0 <= col < len(self.map.map[0]):
                    if self.map.map[row][col] == 0:
                        self.target_nodes[i] = clicked_node
                        self.paths[i] = []  # force replan
                        self.states[i] = "MANUAL_MOVING"
                        print(f"[Manual] AMR {i+1} -> destination {clicked_node}")
                    else:
                        print(f"[Manual] Click on wall ({row},{col}), ignored.")
                else:
                    print(f"[Manual] Click out of bounds, ignored.")
            # If MANUAL_MOVING, clicks are ignored (input lock)

    # implement by extending class
    def initialize(self):
        pass

    # implement by extending class
    def update(self):
        pass

    # main loop
    def run(self):

        ## startup ##
        self.initialize()
        for i in range(self.num_amrs):
            self.spawnTarget(i)

        # Start Tkinter scoreboard window in background thread
        self.scoreboard_win = ScoreboardWindow(self.num_amrs, self.amr_colors)
        self.scoreboard_win.start()

        ## main loop ##
        while self.running:

            ## process input ##
            self.input.update()
            if self.input.quit:
                self.running = False

            # Handle mouse click on pygame window
            if self.input.mouse_clicked:
                mx, my = self.input.mouse_pos
                self._handle_click(mx, my)
                # Sync highlight back to scoreboard
                self.scoreboard_win.set_selected(self.manual_amr if self.manual_amr is not None else -1)

            # ---- Sync selection from Scoreboard window (Tkinter -> pygame) ----
            sb_sel = self.scoreboard_win.get_selected()
            if sb_sel == -1:
                # Scoreboard says deselect
                if self.manual_amr is not None:
                    _i = self.manual_amr
                    self.manual_amr = None
                    self.states[_i] = 'SEEKING'
                    self.paths[_i] = []
                    self.target_nodes[_i] = None
                    self.spawnTarget(_i)
            else:
                # Scoreboard says select sb_sel
                if self.manual_amr != sb_sel:
                    # Deselect old if any
                    if self.manual_amr is not None:
                        _old = self.manual_amr
                        self.states[_old] = 'SEEKING'
                        self.paths[_old] = []
                        self.target_nodes[_old] = None
                        self.spawnTarget(_old)
                    # Select new
                    self.manual_amr = sb_sel
                    if self.states[sb_sel] not in ('MANUAL_MOVING', 'MANUAL_IDLE'):
                        self.states[sb_sel] = 'MANUAL_MOVING' if self.paths[sb_sel] else 'MANUAL_IDLE'

            ## update ##                
            self.update()
            self.scoreboard_win.update_data(self.scores, self.states, self.paths)

            # ---- SMOOTH MOVEMENT INTERPOLATION ----
            for i in range(self.num_amrs):
                if self.is_moving[i]:
                    self.move_progress[i] += 1
                    t = self.move_progress[i] / self.move_duration
                    if t >= 1.0:
                        t = 1.0
                    # Smooth easing (ease-in-out)
                    t_smooth = t * t * (3 - 2 * t)
                    sx, sy = self.move_start_pos[i]
                    ex, ey = self.move_end_pos[i]
                    self.amrs[i].pos[0] = sx + (ex - sx) * t_smooth
                    self.amrs[i].pos[1] = sy + (ey - sy) * t_smooth
                    
                    if self.move_progress[i] >= self.move_duration:
                        self.amrs[i].pos[0] = ex
                        self.amrs[i].pos[1] = ey
                        self.is_moving[i] = False
                        self.move_progress[i] = 0
            
            # Check waiting timeouts (auto AMRs only) independent of all_idle
            current_time = pygame.time.get_ticks()
            for i in range(self.num_amrs):
                if i == self.manual_amr:
                    continue
                if self.states[i] == "WAITING":
                    if current_time - self.wait_start_times[i] > 5000:
                        self.spawnTarget(i)
                        self.states[i] = "SEEKING"
                        self.paths[i] = []
                        self.wait_reasons[i] = ""

            # ---- LOGIC TICK: only when ALL AMRs finished their move ----
            all_idle = all(not self.is_moving[i] for i in range(self.num_amrs))
            
            if all_idle:
                # Update current nodes
                for i in range(self.num_amrs):
                    self.current_nodes[i] = turn2node(self.map.map, self.graphic.screen.get_width(), 
                                                       self.graphic.screen.get_height(), 
                                                       self.amrs[i].pos[0], self.amrs[i].pos[1])
                
                amr_nodes = list(self.current_nodes)

                # ---------- MANUAL AMR POST-ARRIVAL LOGIC ----------
                if self.manual_amr is not None:
                    mi = self.manual_amr
                    if self.states[mi] == "MANUAL_MOVING":
                        # Check if reached manual destination
                        if self.target_nodes[mi] is not None and amr_nodes[mi] == self.target_nodes[mi]:
                            self.scores[mi] += 1
                            self.paths[mi] = []
                            self.target_nodes[mi] = None
                            # Become an obstacle (MANUAL_IDLE) and wait for next click
                            self.states[mi] = "MANUAL_IDLE"
                            print(f"[Manual] AMR {mi+1} arrived. Waiting for next destination.")
                    elif self.states[mi] == "MANUAL_IDLE":
                        # Make sure path is cleared so it doesn't drift
                        self.paths[mi] = [amr_nodes[mi]]

                # Check if auto AMR reached its target
                for i in range(self.num_amrs):
                    if i == self.manual_amr:
                        continue
                    if self.target_nodes[i] is not None and amr_nodes[i] == self.target_nodes[i]:
                        self.scores[i] += 1
                        self.spawnTarget(i)
                        self.paths[i] = []
                        self.states[i] = "SEEKING"
                        self.wait_reasons[i] = ""
                
                # ---- STEP 1: Plan manual AMR first (before auto loop) ----
                # This ensures auto AMRs always plan AFTER the manual AMR's
                # path is known, preventing priority ordering issues.
                manual_path_changed = False
                if self.manual_amr is not None:
                    mi = self.manual_amr
                    if self.states[mi] == "MANUAL_MOVING" and (not self.paths[mi] or len(self.paths[mi]) <= 1):
                        if self.target_nodes[mi] is not None:
                            # Build reserved list for manual AMR path planning.
                            # For AMRs with a multi-step path: use their path.
                            # For AMRs that are stopped/waiting (path empty or 1 node):
                            # create a static phantom path so ST-BFS treats them
                            # as permanent obstacles and never routes through them.
                            reserved_for_manual = []
                            for j in range(self.num_amrs):
                                if j == mi:
                                    continue
                                if self.paths[j] and len(self.paths[j]) > 1:
                                    # Moving AMR: respect its planned trajectory
                                    reserved_for_manual.append(self.paths[j])
                                else:
                                    # Stopped/waiting AMR: block its current cell
                                    reserved_for_manual.append([amr_nodes[j]] * 130)
                            result = self.processor.st_bfs(
                                amr_nodes[mi], self.target_nodes[mi],
                                self.map.map, reserved_paths=reserved_for_manual)
                            if result:
                                self.paths[mi] = result
                                manual_path_changed = True
                                self.manual_block_start_time = None
                                print(f"[Manual] AMR {mi+1} -> {self.target_nodes[mi]}")
                            else:
                                # Path temporarily blocked by other vehicles.
                                # Keep state as MANUAL_MOVING and RETRY next tick.
                                if self.manual_block_start_time is None:
                                    self.manual_block_start_time = pygame.time.get_ticks()
                                elif pygame.time.get_ticks() - self.manual_block_start_time > 5000:
                                    # Timeout after 5 seconds of being blocked!
                                    print(f"[Manual] AMR {mi+1} path blocked for >5s. Clearing destination.")
                                    self.states[mi] = "MANUAL_IDLE"
                                    self.target_nodes[mi] = None
                                    self.manual_block_start_time = None
                                
                                self.paths[mi] = [amr_nodes[mi]]


                # If the manual AMR just got a new path, clear ALL auto paths
                # BEFORE the auto-planning loop starts (not mid-loop) to avoid
                # priority-ordering collisions between auto AMRs.
                if manual_path_changed:
                    for _j in range(self.num_amrs):
                        if _j != self.manual_amr:
                            self.paths[_j] = []

                # ---- STEP 2: Priority-based cooperative planning for auto AMRs ----
                for pass_num in range(2):
                    for i in range(self.num_amrs):
                        # Skip the manually controlled AMR (already planned above)
                        if i == self.manual_amr:
                            continue

                        reserved = []
                        for j in range(self.num_amrs):
                            if i == j:
                                continue
                            should_respect = False
                            if j < i:
                                should_respect = True
                            elif pass_num == 1:
                                # In Pass 2, if we are forced to replan, we MUST respect ALL
                                # other AMRs (even lower priority ones) because they have already
                                # committed to their paths in Pass 1. If we don't, our new path
                                # will just plow through them!
                                should_respect = True
                            # Always respect manual AMR's reserved path
                            if j == self.manual_amr:
                                should_respect = True
                                
                            if should_respect:
                                if not self.paths[j] or len(self.paths[j]) <= 1:
                                    # Any stopped/waiting AMR acts as a permanent static obstacle
                                    reserved.append([amr_nodes[j]] * 130)
                                else:
                                    reserved.append(self.paths[j])
                        
                        need_replan = not self.paths[i]
                        if not need_replan and len(self.paths[i]) > 1:
                            # Check full path for collisions, not just t=1
                            for t in range(1, len(self.paths[i])):
                                my_pos_at_t = self.paths[i][t]
                                my_pos_at_prev = self.paths[i][t-1]
                                for j in range(self.num_amrs):
                                    if i == j:
                                        continue
                                    if not self.paths[j]:
                                        other_pos_at_t = amr_nodes[j]
                                        other_pos_at_prev = amr_nodes[j]
                                    else:
                                        other_pos_at_t = self.paths[j][t] if t < len(self.paths[j]) else self.paths[j][-1]
                                        other_pos_at_prev = self.paths[j][t-1] if (t-1) < len(self.paths[j]) else self.paths[j][-1]
                                        
                                    if my_pos_at_t == other_pos_at_t or (my_pos_at_t == other_pos_at_prev and my_pos_at_prev == other_pos_at_t):
                                        need_replan = True
                                        break
                                if need_replan:
                                    break
                        
                        force_replan = need_replan
                        if pass_num == 1 and (not self.paths[i] or len(self.paths[i]) == 1):
                            force_replan = True
                            
                        if force_replan:
                            can_search = True
                            if self.states[i] == "WAITING":
                                if self.wait_reasons[i] == "WALLED_OFF":
                                    can_search = False
                                elif current_time - self.wait_start_times[i] < (0.5 + i * 0.1):
                                    can_search = False
                                
                            result = None
                            if can_search:
                                result = self.processor.st_bfs(amr_nodes[i], self.target_nodes[i], self.map.map, reserved_paths=reserved)
                                
                            if result:
                                self.paths[i] = result
                                self.states[i] = "SEEKING"
                                self.wait_reasons[i] = ""
                            else:
                                self.paths[i] = [amr_nodes[i]]
                                if pass_num == 1 and can_search:
                                    # Final pass check: is it structurally walled off?
                                    struct_path = self.processor.bfs(amr_nodes[i], self.target_nodes[i], self.map.map)
                                    if struct_path is None:
                                        if self.states[i] != "WAITING":
                                            self.states[i] = "WAITING"
                                            self.wait_start_times[i] = current_time
                                            self.wait_reasons[i] = "WALLED_OFF"
                                    else:
                                        if self.states[i] != "WAITING":
                                            self.states[i] = "WAITING"
                                            self.wait_start_times[i] = current_time
                                            self.wait_reasons[i] = "TRAFFIC"

                # Start next move for each AMR
                for i in range(self.num_amrs):
                    if len(self.paths[i]) > 1:
                        next_node = self.paths[i][1]
                        dr = next_node[0] - amr_nodes[i][0]
                        dc = next_node[1] - amr_nodes[i][1]
                        
                        if dr == -1 and dc == 0:
                            self.amrs[i].heading = 270
                        elif dr == 1 and dc == 0:
                            self.amrs[i].heading = 90
                        elif dr == 0 and dc == -1:
                            self.amrs[i].heading = 180
                        elif dr == 0 and dc == 1:
                            self.amrs[i].heading = 0
                            
                        if dr != 0 or dc != 0:
                            self.is_moving[i] = True
                            self.move_progress[i] = 0
                            self.move_start_pos[i] = [self.amrs[i].pos[0], self.amrs[i].pos[1]]
                            end_pixel = self.node2pixel(next_node)
                            self.move_end_pos[i] = [end_pixel[0], end_pixel[1]]
                            
                        self.paths[i].pop(0)
                    # DO NOT pop if len == 1, keeping [current_node] correctly indicates AMR is stopped here

            ## actuator processing ##

            # Update pulse animation tick
            self.pulse_tick += 1

            # Update path points for drawing (manual AMR only)
            for i in range(self.num_amrs):
                if i == self.manual_amr and self.paths[i] and len(self.paths[i]) > 0:
                    pts = [[self.amrs[i].pos[0], self.amrs[i].pos[1]]]
                    for node in self.paths[i][1:]:
                        px, py = self.node2pixel(node)
                        pts.append([px, py])
                    self.amrs[i].path_points = pts
                else:
                    self.amrs[i].path_points = []

            ## draw ##
            self.graphic.screen.fill((255, 255, 255))
            
            # Draw map
            self.graphic.drawMap(self.map.map, (220, 220, 220))
            
            # Draw targets first (behind AMRs)
            for i in range(self.num_amrs):
                if self.target_nodes[i]:
                    self.graphic.drawTarget(self.target_nodes[i], self.map.map, self.target_colors[i])
            
            # Draw AMRs on top
            for i in range(self.num_amrs):
                self.graphic.drawAmr(self.amrs[i])

            # Draw manual control overlays
            if self.manual_amr is not None:
                mi = self.manual_amr
                self.graphic.drawSelectedAmr(self.amrs[mi], self.pulse_tick)
                if self.states[mi] == "MANUAL_IDLE":
                    self.graphic.drawWaitingForCommand(self.amrs[mi], self.pulse_tick)
            
            ## display image on screen ##
            pygame.display.flip()

            ## pause if necessary to achieve 60 FPS
            self.clock.tick(60)     
             
        ## shutdown ##
        self.scoreboard_win.stop()
        pygame.quit()
        sys.exit()