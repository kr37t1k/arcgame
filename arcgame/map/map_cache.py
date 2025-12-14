"""
DDNet Map Cache - Fast loading of map information
"""
import os
import json
import time
from typing import Dict, Optional
from .map_manager import MapInfo


class MapCache:
    def __init__(self):
        self.cache_file = "arcgame/data/maps/map_cache.json"
        self.cache = self.load_cache()
        self.cache_timeout = 3600 * 24 * 7  # 1 week timeout for cached entries
    
    def load_cache(self) -> Dict[str, dict]:
        """Load map cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Remove expired entries
                    current_time = time.time()
                    cleaned_data = {}
                    for key, value in data.items():
                        if current_time - value.get('timestamp', 0) < self.cache_timeout:
                            cleaned_data[key] = value
                    return cleaned_data
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_cache(self):
        """Save map cache to file"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save the cache
    
    def update_cache(self, map_name: str, map_info: MapInfo):
        """Update cache with new map information"""
        self.cache[map_name.lower()] = {
            'name': map_info.name,
            'path': map_info.path,
            'author': map_info.author,
            'version': map_info.version,
            'crc': map_info.crc,
            'size': map_info.size,
            'gametype': map_info.gametype,
            'tileset': map_info.tileset,
            'spawn_count': map_info.spawn_count,
            'entity_count': map_info.entity_count,
            'timestamp': time.time(),
            'mtime': os.path.getmtime(map_info.path) if os.path.exists(map_info.path) else 0
        }
        self.save_cache()
    
    def get_map_info_fast(self, map_name: str) -> Optional[MapInfo]:
        """Get cached map info without parsing the .map file"""
        map_name_lower = map_name.lower()
        if map_name_lower in self.cache:
            cache_entry = self.cache[map_name_lower]
            
            # Check if file still exists and hasn't been modified since caching
            if os.path.exists(cache_entry['path']):
                current_mtime = os.path.getmtime(cache_entry['path'])
                if current_mtime <= cache_entry['mtime']:
                    # Return cached info
                    return MapInfo(
                        name=cache_entry['name'],
                        path=cache_entry['path'],
                        author=cache_entry['author'],
                        version=cache_entry['version'],
                        crc=cache_entry['crc'],
                        size=cache_entry['size'],
                        gametype=cache_entry['gametype'],
                        tileset=cache_entry['tileset'],
                        spawn_count=cache_entry['spawn_count'],
                        entity_count=cache_entry['entity_count']
                    )
        
        return None
    
    def invalidate_map(self, map_name: str):
        """Remove a map from cache (when file is updated)"""
        map_name_lower = map_name.lower()
        if map_name_lower in self.cache:
            del self.cache[map_name_lower]
            self.save_cache()
    
    def clear_cache(self):
        """Clear the entire cache"""
        self.cache.clear()
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
    
    def refresh_cache_for_path(self, map_path: str):
        """Refresh cache entry for a specific map file"""
        if not os.path.exists(map_path):
            return
            
        # Parse the map to get fresh info
        from .map_parser import MapParser
        parser = MapParser()
        map_data = parser.parse(map_path)
        
        if map_data:
            map_name = os.path.basename(map_path).replace('.map', '')
            map_info = MapInfo(
                name=map_name,
                path=map_path,
                author=getattr(map_data, 'author', 'Unknown'),
                version=getattr(map_data, 'version', '1.0'),
                crc=hash(abs(hash(map_path))) % (10 ** 8),  # Simplified CRC
                size=(getattr(map_data, 'width', 0), getattr(map_data, 'height', 0)),
                gametype="",  # Would be determined from map data
                tileset=getattr(map_data, 'tileset', 'generic'),
                spawn_count=0,  # Would be counted from entities
                entity_count=0  # Would be counted from entities
            )
            self.update_cache(map_name, map_info)
    
    def get_cached_map_list(self) -> list:
        """Get list of all cached map names"""
        return list(self.cache.keys())