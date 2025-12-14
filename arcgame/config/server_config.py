"""
DDNet Server Configuration - Server settings (max players, map rotation)
"""
import json
import os
from typing import Any, Dict, List


class ServerConfig:
    """Server settings (max players, map rotation)"""
    
    def __init__(self):
        self.config_file = "arcgame/config/server.cfg"
        self.config = self._get_default_config()
        self.load()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default server configuration values"""
        return {
            # Server identification
            "sv_name": "DDNet Pygame Server",
            "sv_hostname": "localhost",
            "sv_port": 8303,
            "sv_max_clients": 16,
            "sv_max_clients_per_ip": 4,
            
            # Game settings
            "sv_gametype": "DM",  # DM, CTF, Race, DDRace
            "sv_map": "dm1",
            "sv_scorelimit": 10,
            "sv_timelimit": 0,  # 0 = no time limit
            
            # Map rotation
            "sv_map_rotation": [
                "dm1", "dm2", "dm6", "ctf1", "ctf2", "ctf3"
            ],
            "sv_map_vote": True,
            "sv_map_voting": True,
            
            # Player settings
            "sv_player_demo_record": False,
            "sv_player_name": "unnamed",
            "sv_emoticon_delay": 500,
            
            # Anticheat and security
            "sv_tournament_mode": 0,  # 0=normal, 1=tournament, 2=practice
            "sv_spam": 5,
            "sv_inactivekick": 0,  # 0 = disabled
            "sv_inactivekick_time": 3,
            
            # Gameplay settings
            "sv_team_damage": False,
            "sv_team": 2,  # 0=off, 1=forced, 2=on
            "sv_powerups": True,
            "sv_warmup": False,
            "sv_warmup_duration": 30,
            
            # RCON settings
            "sv_rcon_password": "",
            "sv_rcon_max_tries": 3,
            "sv_rcon_bantime": 5,
            
            # Broadcasting
            "sv_register": True,  # Register with master server
            "sv_broadcast": False,
            
            # Save settings
            "sv_save_games": True,
            "sv_save_chat": True,
        }
    
    def load(self):
        """Load server configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # Update defaults with loaded config
                    self.config.update(file_config)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults if file is corrupted
    
    def save(self):
        """Save server configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self.config.copy()
    
    def add_map_to_rotation(self, map_name: str):
        """Add a map to the rotation list"""
        if map_name not in self.config["sv_map_rotation"]:
            self.config["sv_map_rotation"].append(map_name)
    
    def remove_map_from_rotation(self, map_name: str):
        """Remove a map from the rotation list"""
        if map_name in self.config["sv_map_rotation"]:
            self.config["sv_map_rotation"].remove(map_name)
    
    def set_map_rotation(self, maps: List[str]):
        """Set the entire map rotation list"""
        self.config["sv_map_rotation"] = maps


# Global server config instance
server_config = ServerConfig()