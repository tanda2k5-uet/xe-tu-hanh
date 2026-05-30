from core.menu import run_menu
from core.editor import run_map_editor
from core.application import Application

class Test(Application):
    def initialize(self):
        print("Initializing program ...")
    def update(self):
        pass

# Show menu first, then get config
num_amrs, map_size, obs_ratio, custom_map = run_menu()

map_data = None
if custom_map:
    # Open map editor
    print(f"Opening Map Editor for {map_size}x{map_size} map...")
    map_data = run_map_editor(map_size, num_amrs)

print(f"Starting simulation with {num_amrs} AMRs on {map_size}x{map_size} map...")
Test(num_amrs=num_amrs, map_size=map_size, map_data=map_data, obstacle_ratio=obs_ratio).run()