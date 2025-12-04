"""
World entity for ArcGame
Handles the game map, tiles, and environment
"""

from ursina import *
import numpy as np

class World(Entity):
    def __init__(self, map_data=None, config=None):
        super().__init__()
        self.config = config
        self.map_data = map_data
        self.tiles = []
        self.platforms = []
        self.destructibles = []
        
        # Create the world based on map data
        self.generate_world()
        
    def generate_world(self):
        """Generate the world from map data"""
        if self.map_data:
            self.create_from_map_data()
        else:
            # Create a default/basic world if no map data
            self.create_default_world()
            
    def create_from_map_data(self):
        """Create world from loaded map data"""
        # For now, create a simple representation based on map data
        # This would be expanded when we implement DDNet map loading
        width = self.map_data.get('width', 100)
        height = self.map_data.get('height', 50)
        tiles = self.map_data.get('tiles', [])
        
        # Create ground tiles
        for y in range(height):
            for x in range(width):
                tile_type = tiles[y][x] if y < len(tiles) and x < len(tiles[y]) else 0
                
                if tile_type == 1:  # Solid tile
                    tile = Entity(
                        parent=scene,
                        model='quad',
                        color=color.gray,
                        scale=(1, 1),
                        position=(x - width//2, height//2 - y),
                        origin=(-0.5, 0.5),
                        collider='box'
                    )
                    self.tiles.append(tile)
                    
                elif tile_type == 2:  # Platform tile
                    tile = Entity(
                        parent=scene,
                        model='quad',
                        color=color.brown,
                        scale=(1, 0.2),
                        position=(x - width//2, height//2 - y),
                        origin=(-0.5, 0.5),
                        collider='box'
                    )
                    self.platforms.append(tile)
                    
                elif tile_type == 3:  # Spike/death tile
                    tile = Entity(
                        parent=scene,
                        model='quad',
                        color=color.red,
                        scale=(1, 1),
                        position=(x - width//2, height//2 - y),
                        origin=(-0.5, 0.5),
                        collider='box'
                    )
                    self.tiles.append(tile)
                    
    def create_default_world(self):
        """Create a default world if no map data is provided"""
        # Create a simple platformer level
        # Ground
        ground = Entity(
            parent=scene,
            model='quad',
            color=color.green,
            scale=(50, 1),
            position=(0, -5),
            origin_x=-0.5,
            collider='box'
        )
        self.tiles.append(ground)
        
        # Platforms
        for i in range(5):
            platform = Entity(
                parent=scene,
                model='quad',
                color=color.brown,
                scale=(5, 0.5),
                position=(-20 + i*10, -2 + (i%2)*3),
                collider='box'
            )
            self.platforms.append(platform)
            
        # Walls
        left_wall = Entity(
            parent=scene,
            model='quad',
            color=color.gray,
            scale=(1, 20),
            position=(-25, 5),
            collider='box'
        )
        right_wall = Entity(
            parent=scene,
            model='quad',
            color=color.gray,
            scale=(1, 20),
            position=(25, 5),
            collider='box'
        )
        self.tiles.extend([left_wall, right_wall])
        
    def destroy_world(self):
        """Destroy all world entities"""
        for tile in self.tiles:
            destroy(tile)
        for platform in self.platforms:
            destroy(platform)
        for destructible in self.destructibles:
            destroy(destructible)
            
        self.tiles = []
        self.platforms = []
        self.destructibles = []
        
    def update(self):
        """Update world state"""
        # Handle world-specific updates
        pass