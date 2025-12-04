"""
Map loader for ArcGame
Handles loading and parsing of DDNet-compatible maps
"""

import json
import os
from pathlib import Path

class MapLoader:
    def __init__(self):
        self.maps_dir = Path(__file__).parent.parent / "maps" / "data"
        self.maps_dir.mkdir(exist_ok=True)
        
    def load_map(self, map_name):
        """
        Load a map by name.
        Supports both custom format and DDNet .map files (will be implemented later)
        """
        # First try to load as a custom map file
        custom_map_path = self.maps_dir / f"{map_name}.json"
        if custom_map_path.exists():
            return self.load_custom_map(custom_map_path)
        
        # Then try DDNet format
        ddnet_map_path = self.maps_dir / f"{map_name}.map"
        if ddnet_map_path.exists():
            return self.load_ddnet_map(ddnet_map_path)
        
        # If no map found, create a default map
        print(f"Map {map_name} not found, creating default map")
        return self.create_default_map()
    
    def load_custom_map(self, path):
        """Load a custom map from JSON format"""
        with open(path, 'r') as f:
            map_data = json.load(f)
        
        return map_data
    
    def load_ddnet_map(self, path):
        """
        Load a DDNet map file.
        This is a simplified implementation - full DDNet format support would be more complex.
        """
        # For now, we'll implement a basic parser that creates a simple representation
        # Real DDNet maps use a custom binary format that would require more complex parsing
        
        # Create a simple map structure
        map_data = {
            'name': path.stem,
            'width': 100,
            'height': 50,
            'tiles': [],
            'entities': []
        }
        
        # Generate a simple level for demonstration
        for y in range(map_data['height']):
            row = []
            for x in range(map_data['width']):
                # Create a simple pattern
                if y == map_data['height'] - 1:  # Bottom row - ground
                    tile_type = 1  # Solid
                elif y >= map_data['height'] - 5 and (x % 10) < 2:  # Some obstacles
                    tile_type = 1  # Solid
                elif y == 10 and 20 <= x <= 80:  # Platform in middle
                    tile_type = 2  # Platform
                elif y == 5 and 30 <= x <= 32:  # Small platform
                    tile_type = 2  # Platform
                else:
                    tile_type = 0  # Air
                row.append(tile_type)
            map_data['tiles'].append(row)
        
        return map_data
    
    def create_default_map(self):
        """Create a default map if none exists"""
        map_data = {
            'name': 'default',
            'width': 50,
            'height': 30,
            'tiles': [],
            'entities': []
        }
        
        # Create a simple platformer level
        for y in range(map_data['height']):
            row = []
            for x in range(map_data['width']):
                if y == map_data['height'] - 1:  # Ground
                    tile_type = 1  # Solid
                elif y == map_data['height'] - 5 and 10 <= x <= 40:  # Platform
                    tile_type = 2  # Platform
                elif y == 15 and 5 <= x <= 9:  # Another platform
                    tile_type = 2  # Platform
                elif y == 10 and 35 <= x <= 39:  # Another platform
                    tile_type = 2  # Platform
                elif x == 0 or x == map_data['width'] - 1:  # Walls
                    tile_type = 1  # Solid
                else:
                    tile_type = 0  # Air
                row.append(tile_type)
            map_data['tiles'].append(row)
        
        return map_data
    
    def save_map(self, map_data, map_name):
        """Save a map to file"""
        path = self.maps_dir / f"{map_name}.json"
        with open(path, 'w') as f:
            json.dump(map_data, f, indent=2)
    
    def list_maps(self):
        """List all available maps"""
        maps = []
        for path in self.maps_dir.glob("*.json"):
            maps.append(path.stem)
        for path in self.maps_dir.glob("*.map"):
            maps.append(path.stem)
        return maps