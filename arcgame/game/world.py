"""Game world and map handling for DDNet Pygame implementation"""
from arcgame.base.collision import TileMap, CollisionWorld
from arcgame.base.vec2 import Vec2
from arcgame.config import *
import os


class World:
    def __init__(self, map_path=None):
        self.width = 0
        self.height = 0
        self.tile_size = 32  # Standard DDNet tile size
        self.tiles = []  # 2D array of tile types
        self.collision_world = CollisionWorld()
        self.tile_map = None
        
        if map_path:
            self.load_ddnet_map(map_path)
    
    def load_ddnet_map(self, map_path):
        """Load a DDNet map file (.map) - simplified version"""
        if not os.path.exists(map_path):
            print(f"Map file not found: {map_path}")
            return False
        
        # For now, create a simple test map
        # In the future, we'll implement full .map parsing
        self.width = 50
        self.height = 30
        self.tile_size = 32
        
        # Create a simple test map with some platforms
        self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Create a simple level layout
        # Ground at the bottom
        for x in range(self.width):
            self.tiles[self.height - 1][x] = 1  # Solid ground
            if x > 5 and x < 15:
                self.tiles[self.height - 2][x] = 1  # Platform
            if x > 25 and x < 35:
                self.tiles[self.height - 3][x] = 1  # Higher platform
            if x > 40:
                self.tiles[self.height - 4][x] = 1  # Even higher platform
        
        # Create some platforms
        for x in range(5, 10):
            self.tiles[15][x] = 1  # Platform in the air
        for x in range(20, 25):
            self.tiles[10][x] = 1  # Another platform
        for x in range(30, 35):
            self.tiles[5][x] = 1   # High platform
        
        # Create tile map for collision
        self.tile_map = TileMap(self.width, self.height, self.tile_size)
        for y in range(self.height):
            for x in range(self.width):
                self.tile_map.set_tile(x * self.tile_size, y * self.tile_size, self.tiles[y][x])
        
        self.collision_world.set_map(self.tile_map)
        return True
    
    def get_tile(self, x, y):
        """Get tile at world coordinates"""
        tile_x = int(x / self.tile_size)
        tile_y = int(y / self.tile_size)
        
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return -1  # Out of bounds
        
        return self.tiles[tile_y][tile_x]
    
    def check_collision(self, pos, size=Vec2(28.0, 28.0)):
        """Check collision at position with given size"""
        return self.collision_world.collide_rect(pos, size)
    
    def move_box(self, pos, size, velocity):
        """Move a box with collision"""
        return self.collision_world.move_box(pos, size, velocity)
    
    def get_collision_world(self):
        """Get the collision world instance"""
        return self.collision_world


def clamp_vel(move_restrictions, vel):
    """Clamp velocity based on move restrictions (simplified)"""
    # This is a simplified version of DDNet's ClampVel function
    # In real implementation, this would handle wall jumping restrictions
    result = Vec2(vel.x, vel.y)
    
    if move_restrictions & 1:  # CANTMOVE_LEFT
        if result.x < 0:
            result.x = 0
    if move_restrictions & 2:  # CANTMOVE_RIGHT
        if result.x > 0:
            result.x = 0
    if move_restrictions & 4:  # CANTMOVE_UP
        if result.y < 0:
            result.y = 0
    if move_restrictions & 8:  # CANTMOVE_DOWN
        if result.y > 0:
            result.y = 0
            
    return result