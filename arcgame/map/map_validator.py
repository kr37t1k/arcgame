"""
DDNet Map Validator - Validates map integrity and compatibility
"""
import os
from typing import List, Tuple, Dict, Any
from .map_parser import MapParser, MapData


class ValidationError(Exception):
    """Exception raised for map validation errors"""
    pass


class MapValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_map(self, map_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a map file for DDNet compatibility
        Returns: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        if not os.path.exists(map_path):
            self.errors.append(f"Map file does not exist: {map_path}")
            return False, self.errors, self.warnings
        
        # Check file extension
        if not map_path.lower().endswith('.map'):
            self.errors.append(f"Invalid file extension: {map_path}")
            return False, self.errors, self.warnings
        
        # Parse the map
        parser = MapParser()
        map_data = parser.parse(map_path)
        
        if not map_data:
            self.errors.append(f"Could not parse map file: {map_path}")
            return False, self.errors, self.warnings
        
        # Validate map structure
        self._validate_basic_structure(map_data, map_path)
        self._validate_required_layers(map_data)
        self._validate_spawn_points(map_data)
        self._validate_tile_integrity(map_data)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_basic_structure(self, map_data: MapData, map_path: str):
        """Validate basic map structure"""
        # Check version
        if map_data.version not in [3, 4]:
            self.warnings.append(f"Unusual map version {map_data.version}, expected 3 or 4")
        
        # Check dimensions
        if map_data.width <= 0 or map_data.height <= 0:
            self.errors.append("Map has invalid dimensions")
        elif map_data.width > 1000 or map_data.height > 1000:  # Common limit
            self.warnings.append("Map dimensions seem unusually large")
        
        # Check if file size is reasonable
        file_size = os.path.getsize(map_path)
        if file_size == 0:
            self.errors.append("Map file is empty")
        elif file_size > 50 * 1024 * 1024:  # 50MB
            self.warnings.append("Map file is very large (>50MB)")
    
    def _validate_required_layers(self, map_data: MapData):
        """Validate that required layers exist"""
        # A valid DDNet map should have at least a game layer with tiles
        has_game_layer = len(map_data.tiles) > 0 and len(map_data.tiles[0]) > 0
        
        if not has_game_layer:
            self.errors.append("Map has no game tiles (no game layer found)")
    
    def _validate_spawn_points(self, map_data: MapData):
        """Validate spawn points exist based on game type"""
        # Count different types of spawns
        player_spawns = 0
        red_spawns = 0
        blue_spawns = 0
        
        # For this simplified validator, we'll look at the map tiles
        # In a real implementation, we'd check the entities layer
        if hasattr(map_data, 'entities') and map_data.entities:
            for entity in map_data.entities:
                if 'type' in entity:
                    if entity['type'] in ['player_spawn', 'player']:
                        player_spawns += 1
                    elif entity['type'] in ['red_spawn', 'flag_red']:
                        red_spawns += 1
                    elif entity['type'] in ['blue_spawn', 'flag_blue']:
                        blue_spawns += 1
        
        # For DM mode, we need at least 2 player spawns
        # For CTF mode, we need red and blue spawns
        # For Race/DDRace, we might need start/finish entities
        
        # For now, just check for basic spawns
        if player_spawns == 0 and red_spawns == 0 and blue_spawns == 0:
            # Check if we have tiles that represent spawns
            spawn_tile_types = self._find_spawn_tiles(map_data)
            if spawn_tile_types == 0:
                self.errors.append("Map has no spawn points")
    
    def _find_spawn_tiles(self, map_data: MapData) -> int:
        """Look for spawn tiles in the map (simplified approach)"""
        spawn_count = 0
        if hasattr(map_data, 'tiles') and map_data.tiles:
            for row in map_data.tiles:
                for tile in row:
                    # In DDNet maps, certain tile IDs represent spawn points
                    # This is a simplified check - real implementation would be more complex
                    if tile in [1, 2, 3, 4]:  # These would be spawn tile IDs
                        spawn_count += 1
        return spawn_count
    
    def _validate_tile_integrity(self, map_data: MapData):
        """Validate tile data integrity"""
        if not hasattr(map_data, 'tiles') or not map_data.tiles:
            return
        
        height = len(map_data.tiles)
        if height == 0:
            return
        
        width = len(map_data.tiles[0])
        
        # Check if all rows have the same width
        for i, row in enumerate(map_data.tiles):
            if len(row) != width:
                self.errors.append(f"Row {i} has inconsistent width: {len(row)} vs expected {width}")
    
    def validate_compatibility_with_settings(self, map_data: MapData, 
                                           game_type: str = "DM") -> List[str]:
        """Validate map against specific game type requirements"""
        issues = []
        
        if game_type == "DM":
            # Deathmatch needs player spawns
            if self._find_spawn_tiles(map_data) < 2:
                issues.append("Deathmatch maps need at least 2 spawn points")
        elif game_type == "CTF":
            # Capture the Flag needs red/blue spawns and flags
            if self._find_spawn_tiles(map_data) < 4:  # At least 2 of each team
                issues.append("CTF maps need red and blue spawn points")
        elif game_type in ["Race", "DDRace"]:
            # Race modes need start and finish
            issues.append("Race mode validation requires special entity checking")
        
        return issues