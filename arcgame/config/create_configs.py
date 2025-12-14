"""
DDNet Configuration Files - settings.cfg, server.cfg, autoexec.cfg, binds.cfg
"""
import json
import os


def create_config_files():
    """Create default configuration files"""
    
    # Create config directory if it doesn't exist
    os.makedirs("arcgame/config", exist_ok=True)
    
    # 1. settings.cfg - Client settings
    settings_cfg = {
        # Graphics
        "gfx_width": 1024,
        "gfx_height": 768,
        "gfx_fullscreen": False,
        "gfx_vsync": True,
        "gfx_texture_quality": 1,
        "gfx_particles": True,
        "gfx_background": True,
        
        # Sound
        "snd_enable": True,
        "snd_volume": 0.8,
        "snd_music_volume": 0.6,
        
        # Input
        "inp_mouse_sens": 1.0,
        "inp_joystick": False,
        "inp_joystick_sens": 0.5,
        
        # Network
        "net_port": 8303,
        "net_max_clients": 16,
        
        # Gameplay
        "cl_name": "DDNetPlayer",
        "cl_skin": "default",
        "cl_color_body": 16711680,  # Red (0xFF0000)
        "cl_color_feet": 255,       # Blue (0x0000FF)
    }
    
    with open("arcgame/config/settings.cfg", "w") as f:
        json.dump(settings_cfg, f, indent=2)
    
    # 2. server.cfg - Server configuration
    server_cfg = {
        # Server identification
        "sv_name": "DDNet Pygame Server",
        "sv_hostname": "localhost",
        "sv_port": 8303,
        "sv_max_clients": 16,
        "sv_max_clients_per_ip": 4,
        
        # Game settings
        "sv_gametype": "DM",
        "sv_map": "dm1",
        "sv_scorelimit": 10,
        "sv_timelimit": 0,
        
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
        "sv_tournament_mode": 0,
        "sv_spam": 5,
        "sv_inactivekick": 0,
        "sv_inactivekick_time": 3,
        
        # Gameplay settings
        "sv_team_damage": False,
        "sv_team": 2,
        "sv_powerups": True,
        "sv_warmup": False,
        "sv_warmup_duration": 30,
        
        # RCON settings
        "sv_rcon_password": "",
        "sv_rcon_max_tries": 3,
        "sv_rcon_bantime": 5,
        
        # Broadcasting
        "sv_register": True,
        "sv_broadcast": False,
        
        # Save settings
        "sv_save_games": True,
        "sv_save_chat": True,
    }
    
    with open("arcgame/config/server.cfg", "w") as f:
        json.dump(server_cfg, f, indent=2)
    
    # 3. autoexec.cfg - Auto-execute commands
    autoexec_content = """# DDNet Pygame autoexec configuration
# This file is executed automatically when the game starts

# Set default player name
cl_name "DDNetPlayer"

# Enable vsync
gfx_vsync 1

# Set sound volume
snd_volume 0.8

# Mouse sensitivity
inp_mouse_sens 1.0

# Enable particles
gfx_particles 1

# Join server on startup (uncomment to use)
# connect "localhost:8303"
"""
    
    with open("arcgame/config/autoexec.cfg", "w") as f:
        f.write(autoexec_content)
    
    # 4. binds.cfg - Key bindings
    binds_cfg = {
        # Movement
        "A": "+left",
        "D": "+right",
        "W": "+jump",
        "S": "+down",
        
        # Actions
        "SPACE": "+hook",
        "CTRL": "+fire",
        "1": "+weapon1",  # Hammer
        "2": "+weapon2",  # Gun
        "3": "+weapon3",  # Shotgun
        "4": "+weapon4",  # Grenade
        "5": "+weapon5",  # Rifle
        "6": "+weapon6",  # Ninja
        
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
    
    with open("arcgame/config/binds.cfg", "w") as f:
        json.dump(binds_cfg, f, indent=2)
    
    print("Configuration files created successfully:")
    print("- arcgame/config/settings.cfg")
    print("- arcgame/config/server.cfg") 
    print("- arcgame/config/autoexec.cfg")
    print("- arcgame/config/binds.cfg")


if __name__ == "__main__":
    create_config_files()