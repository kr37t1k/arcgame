"""
DDNet Map Editor - Pygame-based map editor
"""
import pygame
import os
from typing import List, Tuple, Dict, Optional
from ..map.map_parser import MapParser, MapData
from ..map.map_manager import MapManager


class TilePalette:
    """DDNet tiles palette (64x64)"""
    
    def __init__(self):
        self.tile_size = 32
        self.tiles = []
        self.selected_tile = 0
        self.load_default_tiles()
    
    def load_default_tiles(self):
        """Load default DDNet tile set"""
        # For now, we'll create some basic tile representations
        # In a real implementation, we'd load from graphics
        for i in range(256):  # Standard DDNet tile set
            # Create a surface representation for each tile
            # This is a simplified representation
            self.tiles.append(i)  # Just store the tile ID for now
    
    def get_tile(self, index: int):
        """Get a tile by index"""
        if 0 <= index < len(self.tiles):
            return self.tiles[index]
        return 0
    
    def set_selected_tile(self, index: int):
        """Set the currently selected tile"""
        if 0 <= index < len(self.tiles):
            self.selected_tile = index


class MapEditor:
    """Main map editor class"""
    
    def __init__(self, screen_width: int = 1024, screen_height: int = 768):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("DDNet Map Editor")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Map data
        self.map_data: Optional[MapData] = None
        self.map_width = 100
        self.map_height = 100
        self.tile_size = 32
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        
        # Editor state
        self.mode = "edit"  # 'edit', 'select', 'entity'
        self.tool = "brush"  # 'brush', 'eraser', 'fill'
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.drag_start = (0, 0)
        
        # Layers
        self.current_layer = "game"  # 'game', 'front', 'tele', 'speedup', 'switch', 'tune'
        self.layers = {
            "game": [],
            "front": [],
            "tele": [],
            "speedup": [],
            "switch": [],
            "tune": []
        }
        
        # Initialize
        self.tile_palette = TilePalette()
        self.map_manager = MapManager()
        self._create_new_map()
        
        # UI elements
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
    
    def _create_new_map(self):
        """Create a new empty map"""
        # Create empty tiles grid
        self.layers["game"] = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.layers["front"] = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        # Initialize other layers as well
        for layer_name in ["tele", "speedup", "switch", "tune"]:
            self.layers[layer_name] = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
    
    def load_map(self, map_path: str):
        """Load a map from file"""
        parser = MapParser()
        self.map_data = parser.parse(map_path)
        
        if self.map_data:
            self.map_width = self.map_data.width
            self.map_height = self.map_data.height
            # Load the tiles into our layers
            if self.map_data.tiles:
                self.layers["game"] = self.map_data.tiles
            print(f"Map loaded: {map_path}")
        else:
            print(f"Failed to load map: {map_path}")
    
    def save_map(self, map_path: str):
        """Save map to file (placeholder implementation)"""
        # This would need a full implementation to write the DDNet .map format
        # For now, we'll just create a simple representation
        print(f"Saving map to: {map_path}")
        
        # In a real implementation, we would serialize the map data
        # back to the DDNet .map binary format
        with open(map_path, 'wb') as f:
            # Write a simple header
            f.write(b'DDNetMap')  # Simple identifier
            f.write(self.map_width.to_bytes(4, 'little'))
            f.write(self.map_height.to_bytes(4, 'little'))
            
            # Write the tiles
            for layer_name, layer_data in self.layers.items():
                for row in layer_data:
                    for tile in row:
                        f.write(tile.to_bytes(4, 'little'))
        
        print(f"Map saved: {map_path}")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event)
    
    def _handle_keydown(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Save map (Ctrl+S)
            self.save_map("test_map.map")
        elif event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
            # Load map (Ctrl+L)
            # In a real implementation, this would open a file dialog
            pass
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            self.zoom = min(3.0, self.zoom * 1.1)
        elif event.key == pygame.K_MINUS:
            self.zoom = max(0.1, self.zoom / 1.1)
        elif event.key == pygame.K_1:
            self.current_layer = "game"
        elif event.key == pygame.K_2:
            self.current_layer = "front"
        elif event.key == pygame.K_3:
            self.current_layer = "tele"
        elif event.key == pygame.K_4:
            self.current_layer = "speedup"
        elif event.key == pygame.K_5:
            self.current_layer = "switch"
        elif event.key == pygame.K_6:
            self.current_layer = "tune"
    
    def _handle_mouse_down(self, event):
        """Handle mouse button down"""
        if event.button == 1:  # Left click
            # Place tile
            self._place_tile_at_mouse()
        elif event.button == 3:  # Right click
            # Select tile under cursor
            self._select_tile_at_mouse()
        elif event.button == 4:  # Scroll up
            self.zoom = min(3.0, self.zoom * 1.1)
        elif event.button == 5:  # Scroll down
            self.zoom = max(0.1, self.zoom / 1.1)
    
    def _handle_mouse_up(self, event):
        """Handle mouse button up"""
        if event.button == 1:
            self.dragging = False
    
    def _handle_mouse_motion(self, event):
        """Handle mouse movement"""
        self.mouse_pos = event.pos
        
        if event.buttons[0]:  # Left mouse button held
            if self.dragging:
                # Drag to draw
                self._place_tile_at_mouse()
            else:
                self.dragging = True
                self.drag_start = event.pos
    
    def _place_tile_at_mouse(self):
        """Place a tile at the current mouse position"""
        # Convert screen coordinates to map coordinates
        mouse_x, mouse_y = self.mouse_pos
        map_x = int((mouse_x + self.camera_x) / (self.tile_size * self.zoom))
        map_y = int((mouse_y + self.camera_y) / (self.tile_size * self.zoom))
        
        # Check bounds
        if (0 <= map_x < self.map_width and 0 <= map_y < self.map_height):
            # Place the selected tile
            self.layers[self.current_layer][map_y][map_x] = self.tile_palette.selected_tile
    
    def _select_tile_at_mouse(self):
        """Select the tile under the mouse cursor"""
        mouse_x, mouse_y = self.mouse_pos
        map_x = int((mouse_x + self.camera_x) / (self.tile_size * self.zoom))
        map_y = int((mouse_y + self.camera_y) / (self.tile_size * self.zoom))
        
        if (0 <= map_x < self.map_width and 0 <= map_y < self.map_height):
            selected = self.layers[self.current_layer][map_y][map_x]
            self.tile_palette.set_selected_tile(selected)
    
    def update(self):
        """Update editor state"""
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        move_speed = 5 / self.zoom
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += move_speed
        
        # Keep camera within reasonable bounds
        self.camera_x = max(0, self.camera_x)
        self.camera_y = max(0, self.camera_y)
    
    def render(self):
        """Render the editor"""
        # Clear screen
        self.screen.fill((50, 50, 50))  # Dark gray background
        
        # Render map
        self._render_map()
        
        # Render UI
        self._render_ui()
        
        pygame.display.flip()
    
    def _render_map(self):
        """Render the map tiles"""
        # Calculate visible area
        start_x = int(self.camera_x / (self.tile_size * self.zoom))
        start_y = int(self.camera_y / (self.tile_size * self.zoom))
        
        end_x = min(self.map_width, start_x + int(self.screen_width / (self.tile_size * self.zoom)) + 1)
        end_y = min(self.map_height, start_y + int(self.screen_height / (self.tile_size * self.zoom)) + 1)
        
        # Render current layer
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.layers[self.current_layer][y][x]
                
                if tile_id != 0:  # Only draw non-empty tiles
                    screen_x = x * self.tile_size * self.zoom - self.camera_x
                    screen_y = y * self.tile_size * self.zoom - self.camera_y
                    width = self.tile_size * self.zoom
                    height = self.tile_size * self.zoom
                    
                    # Draw tile with a color based on tile ID
                    color = self._get_tile_color(tile_id)
                    pygame.draw.rect(self.screen, color, (screen_x, screen_y, width, height))
                    pygame.draw.rect(self.screen, (100, 100, 100), (screen_x, screen_y, width, height), 1)
        
        # Draw grid
        self._draw_grid()
    
    def _get_tile_color(self, tile_id: int) -> Tuple[int, int, int]:
        """Get a color for a tile ID"""
        # Simple color mapping based on tile ID
        r = (tile_id * 17) % 256
        g = (tile_id * 23) % 256
        b = (tile_id * 31) % 256
        return (r, g, b)
    
    def _draw_grid(self):
        """Draw the grid overlay"""
        grid_color = (100, 100, 100)
        
        # Vertical lines
        start_x = int(self.camera_x / (self.tile_size * self.zoom))
        end_x = min(self.map_width, start_x + int(self.screen_width / (self.tile_size * self.zoom)) + 1)
        
        for x in range(start_x, end_x):
            screen_x = x * self.tile_size * self.zoom - self.camera_x
            pygame.draw.line(self.screen, grid_color, 
                           (screen_x, 0), (screen_x, self.screen_height), 1)
        
        # Horizontal lines
        start_y = int(self.camera_y / (self.tile_size * self.zoom))
        end_y = min(self.map_height, start_y + int(self.screen_height / (self.tile_size * self.zoom)) + 1)
        
        for y in range(start_y, end_y):
            screen_y = y * self.tile_size * self.zoom - self.camera_y
            pygame.draw.line(self.screen, grid_color, 
                           (0, screen_y), (self.screen_width, screen_y), 1)
    
    def _render_ui(self):
        """Render user interface elements"""
        # Draw selected tile info
        tile_info = self.font.render(f"Tile: {self.tile_palette.selected_tile}", True, (255, 255, 255))
        self.screen.blit(tile_info, (10, 10))
        
        # Draw current layer
        layer_info = self.font.render(f"Layer: {self.current_layer}", True, (255, 255, 255))
        self.screen.blit(layer_info, (10, 40))
        
        # Draw zoom level
        zoom_info = self.font.render(f"Zoom: {self.zoom:.1f}x", True, (255, 255, 255))
        self.screen.blit(zoom_info, (10, 70))
        
        # Draw controls help
        controls = [
            "Controls:",
            "Arrow Keys/WASD - Move camera",
            "+/- - Zoom in/out",
            "1-6 - Select layer",
            "Left Click - Place tile",
            "Right Click - Select tile",
            "Ctrl+S - Save map",
            "ESC - Quit"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(ctrl_text, (self.screen_width - 200, 10 + i * 20))
    
    def run(self):
        """Main editor loop"""
        print("DDNet Map Editor started")
        print("Controls: Arrow keys to move, +/- to zoom, 1-6 for layers, Left click to place tiles")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        print("DDNet Map Editor closed")


# Example usage
if __name__ == "__main__":
    editor = MapEditor()
    editor.run()