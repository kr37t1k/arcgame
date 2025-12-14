"""
DDNet Economy Configuration - Economy/points system (like DDNet points)
"""
import json
import os
from typing import Any, Dict


class EconConfig:
    """Economy/points system (like DDNet points)"""
    
    def __init__(self):
        self.econ_file = "arcgame/config/econ_config.cfg"
        self.econ = self._get_default_econ_config()
        self.load()
    
    def _get_default_econ_config(self) -> Dict[str, Any]:
        """Get default economy configuration"""
        return {
            # Point system
            "econ_points_per_kill": 1,
            "econ_points_per_death": -1,
            "econ_points_per_flag_capture": 10,
            "econ_points_per_flag_return": 2,
            "econ_points_per_checkpoint": 1,
            
            # Rank system
            "econ_rank_up_points": 100,  # Points needed to rank up
            "econ_rank_decay": True,     # Whether points decay over time
            "econ_rank_decay_rate": 0.01, # 1% per day
            
            # Rewards
            "econ_daily_login_bonus": 5,
            "econ_streak_bonus": True,
            "econ_streak_bonus_rate": 1.5,  # 50% bonus for streaks
            
            # Penalties
            "econ_team_kill_penalty": -5,
            "econ_disconnect_penalty": -2,
            "econ_spam_penalty": -1,
            
            # Shop system
            "econ_shop_enabled": True,
            "econ_skin_cost": 50,         # Points to buy a skin
            "econ_emote_cost": 10,        # Points to unlock an emote
            "econ_name_change_cost": 25,  # Points to change name
            
            # Tournaments
            "econ_tournament_prize_pool": 1000,
            "econ_tournament_entry_fee": 50,
            "econ_tournament_winner_prize": 700,  # 70% of pool
            "econ_tournament_second_prize": 200,  # 20% of pool
            "econ_tournament_third_prize": 100,   # 10% of pool
            
            # Achievement system
            "econ_achievement_kill_streak_5": 10,
            "econ_achievement_kill_streak_10": 25,
            "econ_achievement_kill_streak_20": 50,
            "econ_achievement_win_match": 15,
            "econ_achievement_survive_hour": 30,
            "econ_achievement_play_10_hours": 50,
            
            # Time-based rewards
            "econ_hourly_play_bonus": 2,
            "econ_daily_play_bonus": 10,
            "econ_weekly_play_bonus": 50,
            
            # Server donation system
            "econ_donation_enabled": True,
            "econ_donation_bonus_rate": 1.2,  # 20% bonus for donations
            "econ_donation_min_amount": 100,
        }
    
    def load(self):
        """Load economy configuration from file"""
        if os.path.exists(self.econ_file):
            try:
                with open(self.econ_file, 'r', encoding='utf-8') as f:
                    file_econ = json.load(f)
                    # Update defaults with loaded config
                    self.econ.update(file_econ)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults if file is corrupted
    
    def save(self):
        """Save economy configuration to file"""
        os.makedirs(os.path.dirname(self.econ_file), exist_ok=True)
        try:
            with open(self.econ_file, 'w', encoding='utf-8') as f:
                json.dump(self.econ, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get an economy configuration value"""
        return self.econ.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set an economy configuration value"""
        self.econ[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all economy configuration values"""
        return self.econ.copy()
    
    def calculate_kill_points(self, is_team_kill: bool = False) -> int:
        """Calculate points for a kill"""
        base_points = self.econ.get("econ_points_per_kill", 1)
        if is_team_kill:
            return base_points + self.econ.get("econ_team_kill_penalty", -5)
        return base_points
    
    def calculate_flag_capture_points(self) -> int:
        """Calculate points for flag capture"""
        return self.econ.get("econ_points_per_flag_capture", 10)


# Global econ config instance
econ_config = EconConfig()