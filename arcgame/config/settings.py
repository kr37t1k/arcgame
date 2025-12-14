"""
DDNet Configuration Settings - Graphics, Sound, Controls
"""
import json
import os
from typing import Any, Dict


class Settings:
    """Game settings (gfx, sound, controls)"""
    
    def __init__(self):
        self.settings_file = "arcgame/config/settings.cfg"
        self.settings = self._get_default_settings()
        self.load()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings values"""
        return {
            # Graphics settings
            "gfx_width": 1024,
            "gfx_height": 768,
            "gfx_fullscreen": False,
            "gfx_vsync": True,
            "gfx_texture_quality": 1,  # 0=low, 1=medium, 2=high
            "gfx_particles": True,
            "gfx_background": True,
            
            # Sound settings
            "snd_enable": True,
            "snd_volume": 0.8,
            "snd_music_volume": 0.6,
            
            # Controls
            "inp_mouse_sens": 1.0,
            "inp_joystick": False,
            "inp_joystick_sens": 0.5,
            
            # Network
            "net_port": 8303,
            "net_max_clients": 16,
            
            # Gameplay
            "cl_name": "DDNetPlayer",
            "cl_skin": "default",
            "cl_color_body": 0xFF0000,  # Red
            "cl_color_feet": 0x0000FF,  # Blue
        }
    
    def load(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    file_settings = json.load(f)
                    # Update defaults with loaded settings
                    self.settings.update(file_settings)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults if file is corrupted
    
    def save(self):
        """Save settings to file"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value"""
        self.settings[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()


# Global settings instance
settings = Settings()