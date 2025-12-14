"""
DDNet Server World - Server-side world simulation
"""
from typing import Dict
from ..game.character import CharacterPhysics
from ..map.map_parser import MapParser


class ServerWorld:
    """Server-side world simulation"""
    
    def __init__(self):
        self.players: Dict[int, CharacterPhysics] = {}
        self.entities = []
        self.map_data = None
        self.map_path = ""
        self.tick_rate = 50  # 50Hz like DDNet
    
    def load_from_map(self, map_path: str):
        """Load map data for the server world"""
        parser = MapParser()
        self.map_data = parser.parse(map_path)
        self.map_path = map_path
        
        # Initialize world based on map
        self._initialize_world_from_map()
    
    def _initialize_world_from_map(self):
        """Initialize world state from map data"""
        # In a real implementation, this would set up all the game entities
        # based on the map data (spawns, weapons, etc.)
        pass
    
    def update(self, dt: float):
        """Update the server world state"""
        # Update all player characters
        for client_id, character in self.players.items():
            # Update character physics
            character.update(dt, self)
        
        # Update other entities (projectiles, pickups, etc.)
        self._update_entities(dt)
    
    def process_player_input(self, client_id: int, input_data: dict):
        """Process input from a player"""
        if client_id not in self.players:
            # Create new character for player
            self.players[client_id] = CharacterPhysics()
        
        character = self.players[client_id]
        
        # Apply input to character
        if 'left' in input_data:
            character.input_left = input_data['left']
        if 'right' in input_data:
            character.input_right = input_data['right']
        if 'jump' in input_data:
            character.input_jump = input_data['jump']
        if 'fire' in input_data:
            character.input_fire = input_data['fire']
        if 'hook' in input_data:
            character.input_hook = input_data['hook']
        
        # Update character state based on input
        character.update_input()
    
    def _update_entities(self, dt: float):
        """Update non-player entities"""
        # Update projectiles, pickups, etc.
        pass
    
    def get_player_position(self, client_id: int):
        """Get the position of a player"""
        if client_id in self.players:
            return self.players[client_id].pos
        return None
    
    def set_player_position(self, client_id: int, x: float, y: float):
        """Set the position of a player"""
        if client_id in self.players:
            self.players[client_id].pos = (x, y)
    
    def check_collision(self, x: float, y: float, width: float = 28.0, height: float = 28.0):
        """Check for collision at a position"""
        if not self.map_data or not self.map_data.tiles:
            return False
        
        # Convert to tile coordinates
        tile_x = int(x / 32)
        tile_y = int(y / 32)
        
        # Check if tile coordinates are within bounds
        if (tile_x < 0 or tile_y < 0 or 
            tile_y >= len(self.map_data.tiles) or 
            tile_x >= len(self.map_data.tiles[0])):
            return True  # Treat out of bounds as collision
        
        tile_id = self.map_data.tiles[tile_y][tile_x]
        
        # In a real implementation, we would check the tile's collision properties
        # For now, just check if it's a non-zero tile (simplified)
        return tile_id != 0


# Alias for compatibility with game_server.py
World = ServerWorld