"""Collision detection system matching DDNet's tile-based collision system"""
from .vec2 import Vec2
import math


class TileMap:
    """Represents a tile map with collision data"""
    def __init__(self, width, height, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]  # 0 = empty, 1 = solid
        
    def get_tile_index(self, x, y):
        """Get the tile index at position (x, y)"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return -1  # Out of bounds
            
        return self.tiles[tile_y][tile_x]
    
    def set_tile(self, x, y, value):
        """Set the tile at position (x, y) to value"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            self.tiles[tile_y][tile_x] = value
    
    def is_solid(self, x, y):
        """Check if position (x, y) is solid"""
        return self.get_tile_index(x, y) == 1
    
    def closest_tile_pos(self, pos):
        """Get the position of the top-left corner of the tile at pos"""
        tile_x = int(pos.x // self.tile_size)
        tile_y = int(pos.y // self.tile_size)
        return Vec2(tile_x * self.tile_size, tile_y * self.tile_size)


class CollisionWorld:
    """Main collision detection system"""
    def __init__(self, map_data=None):
        self.map = map_data
        self.entities = []  # List of collidable entities
    
    def set_map(self, tile_map):
        """Set the tile map for collision"""
        self.map = tile_map
    
    def collide_point(self, pos):
        """Check if a point collides with solid tiles"""
        if not self.map:
            return False
        return self.map.is_solid(pos.x, pos.y)
    
    def collide_rect(self, pos, size):
        """Check if a rectangle collides with solid tiles"""
        if not self.map:
            return False
            
        # Check all 4 corners of the rectangle
        top_left = pos
        top_right = Vec2(pos.x + size.x, pos.y)
        bottom_left = Vec2(pos.x, pos.y + size.y)
        bottom_right = Vec2(pos.x + size.x, pos.y + size.y)
        
        return (self.collide_point(top_left) or 
                self.collide_point(top_right) or 
                self.collide_point(bottom_left) or 
                self.collide_point(bottom_right))
    
    def collide_circle(self, center, radius):
        """Check if a circle collides with solid tiles"""
        if not self.map:
            return False
            
        # Check multiple points around the circle
        for i in range(8):
            a = 2 * math.pi * i / 8
            p = Vec2(
                center.x + radius * math.cos(a),
                center.y + radius * math.sin(a)
            )
            if self.collide_point(p):
                return True
        return False
    
    def move_point(self, pos, delta):
        """Move a point with collision resolution"""
        if not self.map:
            return pos + delta
            
        new_pos = pos + delta
        
        # Simple collision: if new position is solid, don't move
        if not self.collide_point(new_pos):
            return new_pos
        else:
            # Try moving along X axis only
            test_pos = Vec2(new_pos.x, pos.y)
            if not self.collide_point(test_pos):
                return test_pos
            # Try moving along Y axis only
            test_pos = Vec2(pos.x, new_pos.y)
            if not self.collide_point(test_pos):
                return test_pos
            # Both axes blocked, return original position
            return pos
    
    def move_box(self, pos, size, velocity):
        """Move a box with collision resolution - similar to DDNet's collision system"""
        if not self.map:
            return pos + velocity, velocity

        new_pos = Vec2(pos.x, pos.y)
        
        # Calculate how many steps we need to take for accurate collision
        # This prevents tunneling through thin walls
        distance = max(abs(velocity.x), abs(velocity.y))
        steps = max(1, int(distance))
        
        # Fraction of velocity to move per step
        fraction_x = velocity.x / steps
        fraction_y = velocity.y / steps
        
        for step in range(steps):
            # Try X movement first
            test_pos_x = Vec2(new_pos.x + fraction_x, new_pos.y)
            if not self.collide_rect(test_pos_x, size):
                new_pos.x += fraction_x
            else:
                # X collision - stop x movement
                break
            
            # Then try Y movement
            test_pos_y = Vec2(new_pos.x, new_pos.y + fraction_y)
            if not self.collide_rect(test_pos_y, size):
                new_pos.y += fraction_y
            else:
                # Y collision - stop y movement
                break
        
        # Calculate remaining velocity based on how far we actually moved
        actual_delta = new_pos - pos
        remaining_velocity = Vec2(velocity.x, velocity.y)
        
        # If we hit a wall in X direction, stop X velocity
        if abs(actual_delta.x) < abs(velocity.x * steps) and steps > 0:
            remaining_velocity.x = 0
        # If we hit a wall in Y direction, stop Y velocity  
        if abs(actual_delta.y) < abs(velocity.y * steps) and steps > 0:
            remaining_velocity.y = 0
            
        return new_pos, remaining_velocity


def closest_point_on_line_segment(start, end, point):
    """Find the closest point on a line segment to a given point"""
    line_vec = end - start
    point_vec = point - start
    
    line_len_sq = line_vec.length_sq()
    if line_len_sq < 1e-8:  # Line is basically a point
        return start.copy()
    
    t = max(0.0, min(1.0, point_vec.dot(line_vec) / line_len_sq))
    return start + line_vec * t


def distance_to_line_segment(start, end, point):
    """Calculate the distance from a point to a line segment"""
    closest = closest_point_on_line_segment(start, end, point)
    return closest.distance(point)


def clamp_to_map_bounds(pos, map_width, map_height, tile_size=32):
    """Clamp position to map bounds"""
    min_x = 0
    max_x = map_width * tile_size
    min_y = 0
    max_y = map_height * tile_size
    
    return Vec2(
        max(min_x, min(pos.x, max_x)),
        max(min_y, min(pos.y, max_y))
    )


if __name__ == "__main__":
    # Test collision system
    tile_map = TileMap(20, 15)  # 20x15 tiles
    tile_map.set_tile(100, 100, 1)  # Set a tile at (100, 100) to solid
    
    collision_world = CollisionWorld(tile_map)
    
    # Test point collision
    pos = Vec2(100, 100)
    print(f"Point {pos} collides: {collision_world.collide_point(pos)}")
    
    # Test movement
    pos = Vec2(90, 90)
    vel = Vec2(15, 15)
    new_pos, remaining_vel = collision_world.move_box(pos, Vec2(10, 10), vel)
    print(f"Moved from {pos} with velocity {vel} -> new pos: {new_pos}, remaining vel: {remaining_vel}")