"""
DDNet Map Manager - Handles map discovery, loading, and caching
Replicates DDNet's exact map loading behavior
"""
import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .map_parser import MapParser
from ..base.collision import get_tile_flags


@dataclass
class MapInfo:
    """Information about a map"""
    name: str
    path: str
    author: str = ""
    version: str = ""
    crc: int = 0
    size: Tuple[int, int] = (0, 0)  # width, height in tiles
    gametype: str = ""  # DM, CTF, Race, DDRace
    tileset: str = ""
    spawn_count: int = 0
    entity_count: int = 0


class MapManager:
    def __init__(self):
        self.maps = {}  # dict: map_name -> MapInfo
        self.current_map = None
        self.base_path = "arcgame/data/maps"
        self.priority_order = [
            "",  # base maps directory
            "downloaded/",
            "community/",
            "official/",
            "campaigns/"
        ]
        self.scan_map_directories()
    
    def scan_map_directories(self):
        """Scan all map directories in DDNet priority order"""
        self.maps.clear()
        
        for subdir in self.priority_order:
            dir_path = os.path.join(self.base_path, subdir)
            if os.path.exists(dir_path):
                self._scan_directory(dir_path, subdir)
    
    def _scan_directory(self, dir_path: str, subdir: str):
        """Scan a specific directory for .map files"""
        try:
            for filename in os.listdir(dir_path):
                if filename.lower().endswith('.map'):
                    map_name = os.path.splitext(filename)[0].lower()
                    map_path = os.path.join(dir_path, filename)
                    
                    # Only add if not already in higher priority
                    if map_name not in self.maps:
                        map_info = self._get_map_info(map_path, subdir)
                        if map_info:
                            self.maps[map_name] = map_info
        except OSError:
            pass  # Directory doesn't exist
    
    def _get_map_info(self, map_path: str, subdir: str) -> Optional[MapInfo]:
        """Extract information from a map file"""
        try:
            parser = MapParser()
            map_data = parser.parse(map_path)
            
            if not map_data:
                return None
                
            # Calculate CRC-like hash for the map
            import hashlib
            with open(map_path, 'rb') as f:
                content = f.read()
                crc = int(hashlib.md5(content).hexdigest(), 16) % (10 ** 8)
            
            # Count spawns and entities
            spawn_count = 0
            entity_count = 0
            if hasattr(map_data, 'entities'):
                for entity in map_data.entities:
                    if entity['type'] in ['player_spawn', 'red_spawn', 'blue_spawn']:
                        spawn_count += 1
                    entity_count += 1
            
            # Determine game type based on entities and map structure
            gametype = self._determine_gametype(map_data)
            
            return MapInfo(
                name=os.path.basename(map_path).replace('.map', ''),
                path=map_path,
                author=getattr(map_data, 'author', 'Unknown'),
                version=getattr(map_data, 'version', '1.0'),
                crc=crc,
                size=(getattr(map_data, 'width', 0), getattr(map_data, 'height', 0)),
                gametype=gametype,
                tileset=getattr(map_data, 'tileset', 'generic'),
                spawn_count=spawn_count,
                entity_count=entity_count
            )
        except Exception:
            return None
    
    def _determine_gametype(self, map_data) -> str:
        """Determine game type based on map characteristics"""
        # This would be implemented based on entity types and map structure
        # For now, return a basic determination
        if hasattr(map_data, 'entities'):
            red_spawns = 0
            blue_spawns = 0
            race_entities = 0
            
            for entity in map_data.entities:
                if entity['type'] == 'red_spawn':
                    red_spawns += 1
                elif entity['type'] == 'blue_spawn':
                    blue_spawns += 1
                elif entity['type'] in ['checkpoint', 'start']:
                    race_entities += 1
            
            if red_spawns > 0 and blue_spawns > 0:
                return "CTF"
            elif race_entities > 0:
                return "Race"
            else:
                return "DM"
        
        return "DM"
    
    def load_map(self, map_name: str):
        """Try to load a map by name, checking all directories in priority order"""
        # First check if we have it cached
        if map_name.lower() in self.maps:
            return self.maps[map_name.lower()].path
        
        # Try different case variations and extensions
        possible_names = [
            map_name,
            map_name.lower(),
            map_name.upper(),
            map_name + '.map',
            map_name + '.MAP'
        ]
        
        for name in possible_names:
            for subdir in self.priority_order:
                dir_path = os.path.join(self.base_path, subdir)
                possible_paths = [
                    os.path.join(dir_path, name),
                    os.path.join(dir_path, name.lower()),
                    os.path.join(dir_path, name.upper())
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        # Parse and cache the map
                        map_info = self._get_map_info(path, subdir)
                        if map_info:
                            self.maps[map_name.lower()] = map_info
                            self.current_map = map_info
                            return path
        
        return None  # Map not found
    
    def has_map(self, map_name: str) -> bool:
        """Check if a map exists locally"""
        return self.load_map(map_name) is not None
    
    def get_map_info(self, map_name: str) -> Optional[MapInfo]:
        """Get cached map info, or parse the map if not cached"""
        map_name_lower = map_name.lower()
        if map_name_lower in self.maps:
            return self.maps[map_name_lower]
        
        # Try to find and cache the map
        map_path = self.load_map(map_name)
        if map_path:
            return self.maps.get(map_name_lower)
        
        return None
    
    def get_all_maps(self) -> List[MapInfo]:
        """Get list of all available maps"""
        return list(self.maps.values())
    
    def get_maps_by_type(self, gametype: str) -> List[MapInfo]:
        """Get maps filtered by game type"""
        return [info for info in self.maps.values() if info.gametype.lower() == gametype.lower()]