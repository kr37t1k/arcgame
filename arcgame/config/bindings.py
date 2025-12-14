"""
DDNet Key Bindings - Load/save .cfg files for key bindings
"""
import json
import os
from typing import Any, Dict


class Bindings:
    """Key bindings (load/save .cfg files)"""
    
    def __init__(self):
        self.bindings_file = "arcgame/config/binds.cfg"
        self.bindings = self._get_default_bindings()
        self.load()
    
    def _get_default_bindings(self) -> Dict[str, str]:
        """Get default key bindings"""
        return {
            # Movement
            "a": "+left",
            "d": "+right", 
            "w": "+jump",
            "s": "+down",
            
            # Actions
            "SPACE": "+hook",
            "CTRL": "+fire",
            "SHIFT": "+weapon1",  # Hammer
            "1": "+weapon2",     # Gun
            "2": "+weapon3",     # Shotgun
            "3": "+weapon4",     # Grenade
            "4": "+weapon5",     # Rifle/Laser
            "5": "+weapon6",     # Ninja
            
            # Game controls
            "TAB": "+scoreboard",
            "T": "+chat",
            "Y": "+teamchat", 
            "F1": "+spectate",
            "F2": "+emote",
            "F3": "+tune",
            "F4": "+pause",
            "ESCAPE": "+menu",
            
            # Other
            "MOUSE1": "+fire",
            "MOUSE2": "+hook",
            "MWHEELUP": "+prevweapon",
            "MWHEELDOWN": "+nextweapon",
        }
    
    def load(self):
        """Load key bindings from file"""
        if os.path.exists(self.bindings_file):
            try:
                with open(self.bindings_file, 'r', encoding='utf-8') as f:
                    file_bindings = json.load(f)
                    # Update defaults with loaded bindings
                    self.bindings.update(file_bindings)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults if file is corrupted
    
    def save(self):
        """Save key bindings to file"""
        os.makedirs(os.path.dirname(self.bindings_file), exist_ok=True)
        try:
            with open(self.bindings_file, 'w', encoding='utf-8') as f:
                json.dump(self.bindings, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save
    
    def get_binding(self, key: str) -> str:
        """Get the action bound to a key"""
        return self.bindings.get(key.upper(), "")
    
    def set_binding(self, key: str, action: str):
        """Set a key binding"""
        self.bindings[key.upper()] = action
    
    def get_all_bindings(self) -> Dict[str, str]:
        """Get all key bindings"""
        return self.bindings.copy()
    
    def get_key_for_action(self, action: str) -> str:
        """Get the key bound to an action"""
        for key, bound_action in self.bindings.items():
            if bound_action == action:
                return key
        return ""
    
    def clear_bindings_for_action(self, action: str):
        """Remove all keys bound to an action"""
        keys_to_remove = []
        for key, bound_action in self.bindings.items():
            if bound_action == action:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.bindings[key]


# Global bindings instance
bindings = Bindings()