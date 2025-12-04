"""
Map Editor for ArcGame
Advanced map editor with DDNet compatibility
"""

from ursina import *
import numpy as np

class MapEditor(Entity):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.enabled = False
        self.edit_mode = "TILES"  # TILES, ENTITIES, PROPERTIES
        self.selected_tool = "BRUSH"  # BRUSH, ERASER, FILL, SELECT
        self.selected_tile = 1  # 0=Air, 1=Solid, 2=Platform, 3=Spike
        self.map_width = 100
        self.map_height = 50
        self.tile_size = 1
        self.grid_enabled = True
        self.snap_to_grid = True
        
        # Create the map data
        self.map_data = self.create_empty_map()
        
        # Editor UI
        self.create_editor_ui()
        
        # Tile palette
        self.create_tile_palette()
        
        # Create grid visualization
        self.create_grid()
        
    def create_empty_map(self):
        """Create an empty map filled with air tiles"""
        return [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
    
    def create_editor_ui(self):
        """Create the editor UI"""
        # Main editor panel
        self.editor_panel = Panel(
            parent=camera.ui,
            model=Quad(radius=0.025),
            scale=(0.9, 0.9),
            origin=(-0.5, 0.5),
            position=(-0.45, 0.45),
            color=color.black66,
            enabled=False
        )
        
        # Title
        self.title = Text(
            parent=self.editor_panel,
            text='MAP EDITOR',
            scale=2,
            position=(0.1, -0.05),
            color=color.white
        )
        
        # Tool buttons
        self.brush_tool = Button(
            parent=self.editor_panel,
            text='BRUSH',
            scale=(0.1, 0.05),
            position=(0.05, -0.15),
            color=color.gray,
            on_click=lambda: self.set_tool('BRUSH')
        )
        
        self.eraser_tool = Button(
            parent=self.editor_panel,
            text='ERASER',
            scale=(0.1, 0.05),
            position=(0.17, -0.15),
            color=color.gray,
            on_click=lambda: self.set_tool('ERASER')
        )
        
        self.fill_tool = Button(
            parent=self.editor_panel,
            text='FILL',
            scale=(0.1, 0.05),
            position=(0.29, -0.15),
            color=color.gray,
            on_click=lambda: self.set_tool('FILL')
        )
        
        # Mode buttons
        self.tiles_mode = Button(
            parent=self.editor_panel,
            text='TILES',
            scale=(0.1, 0.05),
            position=(0.45, -0.15),
            color=color.gray,
            on_click=lambda: self.set_mode('TILES')
        )
        
        self.entities_mode = Button(
            parent=self.editor_panel,
            text='ENTITIES',
            scale=(0.1, 0.05),
            position=(0.57, -0.15),
            color=color.gray,
            on_click=lambda: self.set_mode('ENTITIES')
        )
        
        # Grid toggle
        self.grid_toggle = Button(
            parent=self.editor_panel,
            text='GRID: ON',
            scale=(0.1, 0.05),
            position=(0.75, -0.15),
            color=color.green,
            on_click=self.toggle_grid
        )
        
        # File buttons
        self.save_button = Button(
            parent=self.editor_panel,
            text='SAVE',
            scale=(0.1, 0.05),
            position=(0.05, -0.25),
            color=color.green,
            on_click=self.save_map
        )
        
        self.load_button = Button(
            parent=self.editor_panel,
            text='LOAD',
            scale=(0.1, 0.05),
            position=(0.17, -0.25),
            color=color.blue,
            on_click=self.load_map
        )
        
        self.test_button = Button(
            parent=self.editor_panel,
            text='TEST',
            scale=(0.1, 0.05),
            position=(0.29, -0.25),
            color=color.orange,
            on_click=self.test_map
        )
        
        self.exit_button = Button(
            parent=self.editor_panel,
            text='EXIT',
            scale=(0.1, 0.05),
            position=(0.75, -0.25),
            color=color.red,
            on_click=self.exit_editor
        )
        
        # Coordinates display
        self.coords_text = Text(
            parent=self.editor_panel,
            text='X: 0, Y: 0',
            scale=0.8,
            position=(0.45, -0.25),
            color=color.white
        )
        
    def create_tile_palette(self):
        """Create the tile selection palette"""
        # Tile selection area
        self.palette_panel = Entity(
            parent=self.editor_panel,
            model='quad',
            color=color.dark_gray,
            scale=(0.2, 0.3),
            position=(0.7, -0.4),
            origin=(-0.5, 0.5)
        )
        
        # Palette title
        Text(
            parent=self.palette_panel,
            text='TILES',
            scale=1,
            position=(0.02, -0.02),
            color=color.white
        )
        
        # Tile buttons
        tile_names = ['Air', 'Solid', 'Platform', 'Spike']
        tile_colors = [color.black, color.gray, color.brown, color.red]
        
        for i, (name, col) in enumerate(zip(tile_names, tile_colors)):
            y_pos = -0.1 - (i * 0.06)
            
            tile_btn = Button(
                parent=self.palette_panel,
                text=name,
                scale=(0.15, 0.04),
                position=(0.02, y_pos),
                color=col,
                on_click=lambda t=i: self.select_tile(t)
            )
            
            # Highlight selected tile
            if i == self.selected_tile:
                tile_btn.color = color.white
                tile_btn.highlight_color = color.light_gray
    
    def create_grid(self):
        """Create grid visualization for the map"""
        # For now, we'll represent the map with entities
        self.tile_entities = []
        
        for y in range(self.map_height):
            row = []
            for x in range(self.map_width):
                # Create a tile entity
                tile_entity = Entity(
                    parent=scene,
                    model='quad',
                    color=self.get_tile_color(self.map_data[y][x]),
                    scale=self.tile_size,
                    position=(x * self.tile_size, -y * self.tile_size),
                    origin=(-0.5, 0.5),
                    collider='box',
                    visible=False  # Initially hidden in editor mode
                )
                row.append(tile_entity)
            self.tile_entities.append(row)
    
    def get_tile_color(self, tile_type):
        """Get color for a tile type"""
        colors = {
            0: color.black,    # Air
            1: color.gray,     # Solid
            2: color.brown,    # Platform
            3: color.red       # Spike
        }
        return colors.get(tile_type, color.white)
    
    def set_tool(self, tool):
        """Set the current editing tool"""
        self.selected_tool = tool
        print(f"Selected tool: {tool}")
    
    def set_mode(self, mode):
        """Set the current editing mode"""
        self.edit_mode = mode
        print(f"Selected mode: {mode}")
        
        # Update UI to reflect mode
        if mode == "TILES":
            self.tiles_mode.color = color.white
            self.entities_mode.color = color.gray
        else:
            self.tiles_mode.color = color.gray
            self.entities_mode.color = color.white
    
    def select_tile(self, tile_type):
        """Select a tile type to place"""
        self.selected_tile = tile_type
        print(f"Selected tile: {tile_type}")
        
        # Update palette UI
        tile_names = ['Air', 'Solid', 'Platform', 'Spike']
        tile_colors = [color.black, color.gray, color.brown, color.red]
        
        for i, btn in enumerate(self.palette_panel.children):
            if i < 4:  # Skip the title text
                btn.color = tile_colors[i] if i != tile_type else color.white
    
    def toggle_grid(self):
        """Toggle grid visibility"""
        self.grid_enabled = not self.grid_enabled
        if self.grid_enabled:
            self.grid_toggle.text = 'GRID: ON'
            self.grid_toggle.color = color.green
        else:
            self.grid_toggle.text = 'GRID: OFF'
            self.grid_toggle.color = color.gray
    
    def update(self):
        """Update editor logic"""
        if not self.enabled:
            return
            
        # Update coordinates display
        if mouse.world_point:
            x, y, _ = mouse.world_point
            grid_x = int(x)
            grid_y = int(-y)  # Flip Y axis
            self.coords_text.text = f'X: {grid_x}, Y: {grid_y}'
            
            # Handle tile placement
            if mouse.left:
                self.handle_tile_placement(grid_x, grid_y)
    
    def handle_tile_placement(self, x, y):
        """Handle placing tiles based on current tool and mode"""
        if 0 <= x < self.map_width and 0 <= y < self.map_height:
            if self.selected_tool == "BRUSH":
                self.map_data[y][x] = self.selected_tile
                self.tile_entities[y][x].color = self.get_tile_color(self.selected_tile)
            elif self.selected_tool == "ERASER":
                self.map_data[y][x] = 0  # Air
                self.tile_entities[y][x].color = self.get_tile_color(0)
    
    def save_map(self):
        """Save the current map"""
        map_name = input("Enter map name: ") or "untitled"
        
        # Prepare map data
        map_data = {
            'name': map_name,
            'width': self.map_width,
            'height': self.map_height,
            'tiles': self.map_data,
            'entities': []  # Will implement entity saving later
        }
        
        # Use the game's map loader to save
        self.game.map_loader.save_map(map_data, map_name)
        print(f"Map '{map_name}' saved!")
    
    def load_map(self):
        """Load a map"""
        print("Load map functionality would be implemented here")
        # This would open a file dialog to select a map
    
    def test_map(self):
        """Test the current map in-game"""
        # Apply current map to the game
        map_data = {
            'name': 'editor_test',
            'width': self.map_width,
            'height': self.map_height,
            'tiles': self.map_data,
            'entities': []
        }
        
        # Temporarily replace the current map
        self.game.current_map = map_data
        if self.game.world:
            self.game.world.destroy_world()
        self.game.world = World(map_data, self.game.config)
        
        # Exit editor and go to playing state
        self.exit_editor()
        self.game.game_state = "PLAYING"
    
    def exit_editor(self):
        """Exit the map editor"""
        self.enabled = False
        self.editor_panel.enabled = False
        self.game.game_state = "PLAYING"
        
        # Hide all tile entities
        for row in self.tile_entities:
            for tile in row:
                tile.visible = False
    
    def show(self):
        """Show the map editor"""
        self.enabled = True
        self.editor_panel.enabled = True
        
        # Show all tile entities
        for row in self.tile_entities:
            for tile in row:
                tile.visible = True
                
        # Position camera appropriately
        camera.orthographic = True
        camera.fov = max(self.map_width, self.map_height) / 3
    
    def hide(self):
        """Hide the map editor"""
        self.enabled = False
        self.editor_panel.enabled = False
        
        # Hide all tile entities
        for row in self.tile_entities:
            for tile in row:
                tile.visible = False