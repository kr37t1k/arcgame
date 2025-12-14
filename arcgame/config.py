"""Game configuration and constants from DDNet source"""
import math


# Server constants
SERVER_TICK_SPEED = 50
SERVER_TICK_TIME = 1.0 / SERVER_TICK_SPEED

# Character physical constants
CHARACTER_PHYSICAL_SIZE = 28.0
CHARACTER_PHYSICAL_RADIUS = CHARACTER_PHYSICAL_SIZE / 2.0

# Hook states (from DDNet)
HOOK_RETRACTED = -1
HOOK_IDLE = 0
HOOK_RETRACT_START = 1
HOOK_RETRACT_END = 3
HOOK_FLYING = 4
HOOK_GRABBED = 5

# Core events (from DDNet)
COREEVENT_GROUND_JUMP = 0x01
COREEVENT_AIR_JUMP = 0x02
COREEVENT_HOOK_LAUNCH = 0x04
COREEVENT_HOOK_ATTACH_PLAYER = 0x08
COREEVENT_HOOK_ATTACH_GROUND = 0x10
COREEVENT_HOOK_HIT_NOHOOK = 0x20
COREEVENT_HOOK_RETRACT = 0x40

# Movement restrictions (from DDNet)
CANTMOVE_LEFT = 1 << 0
CANTMOVE_RIGHT = 1 << 1
CANTMOVE_UP = 1 << 2
CANTMOVE_DOWN = 1 << 3

# Max clients (from DDNet)
MAX_CLIENTS = 64

# Number of weapons (from DDNet)
NUM_WEAPONS = 10

# Weapon IDs (from DDNet)
WEAPON_HAMMER = 0
WEAPON_GUN = 1
WEAPON_SHOTGUN = 2
WEAPON_GRENADE = 3
WEAPON_LASER = 4
WEAPON_NINJA = 5

# Character flags (from DDNet)
CHARACTERFLAG_SOLO = 1 << 0
CHARACTERFLAG_JETPACK = 1 << 1
CHARACTERFLAG_COLLISION_DISABLED = 1 << 2
CHARACTERFLAG_ENDLESS_HOOK = 1 << 3
CHARACTERFLAG_ENDLESS_JUMP = 1 << 4
CHARACTERFLAG_HAMMER_HIT_DISABLED = 1 << 5
CHARACTERFLAG_SHOTGUN_HIT_DISABLED = 1 << 6
CHARACTERFLAG_GRENADE_HIT_DISABLED = 1 << 7
CHARACTERFLAG_LASER_HIT_DISABLED = 1 << 8
CHARACTERFLAG_HOOK_HIT_DISABLED = 1 << 9
CHARACTERFLAG_SUPER = 1 << 10
CHARACTERFLAG_INVINCIBLE = 1 << 11
CHARACTERFLAG_TELEGUN_GRENADE = 1 << 12
CHARACTERFLAG_TELEGUN_GUN = 1 << 13
CHARACTERFLAG_TELEGUN_LASER = 1 << 14
CHARACTERFLAG_WEAPON_HAMMER = 1 << 15
CHARACTERFLAG_WEAPON_GUN = 1 << 16
CHARACTERFLAG_WEAPON_SHOTGUN = 1 << 17
CHARACTERFLAG_WEAPON_GRENADE = 1 << 18
CHARACTERFLAG_WEAPON_LASER = 1 << 19
CHARACTERFLAG_WEAPON_NINJA = 1 << 20
CHARACTERFLAG_IN_FREEZE = 1 << 21
CHARACTERFLAG_MOVEMENTS_DISABLED = 1 << 22

# Default tuning parameters (from DDNet tuning.h)
TUNING_DEFAULTS = {
    # Physics tuning
    'ground_control_speed': 10.0,
    'ground_control_accel': 100.0 / SERVER_TICK_SPEED,
    'ground_friction': 0.5,
    'ground_jump_impulse': 13.2,
    'air_jump_impulse': 12.0,
    'air_control_speed': 250.0 / SERVER_TICK_SPEED,
    'air_control_accel': 1.5,
    'air_friction': 0.95,
    'hook_length': 380.0,
    'hook_fire_speed': 80.0,
    'hook_drag_accel': 3.0,
    'hook_drag_speed': 15.0,
    'gravity': 0.5,
    
    # Velocity ramp
    'velramp_start': 550,
    'velramp_range': 2000,
    'velramp_curvature': 1.4,
    
    # Weapon tuning
    'gun_curvature': 1.25,
    'gun_speed': 2200.0,
    'gun_lifetime': 2.0,
    
    'shotgun_curvature': 1.25,
    'shotgun_speed': 2750.0,
    'shotgun_speeddiff': 0.8,
    'shotgun_lifetime': 0.20,
    
    'grenade_curvature': 7.0,
    'grenade_speed': 1000.0,
    'grenade_lifetime': 2.0,
    
    'laser_reach': 800.0,
    'laser_bounce_delay': 150,
    'laser_bounce_num': 1000,
    'laser_bounce_cost': 0,
    'laser_damage': 5,
    
    # Game settings
    'player_collision': 1,
    'player_hooking': 1,
    
    # DDNet specific
    'jetpack_strength': 400.0,
    'shotgun_strength': 10.0,
    'explosion_strength': 6.0,
    'hammer_strength': 1.0,
    'hook_duration': 1.25,
    
    # Fire delays (in milliseconds)
    'hammer_fire_delay': 125,
    'gun_fire_delay': 125,
    'shotgun_fire_delay': 500,
    'grenade_fire_delay': 500,
    'laser_fire_delay': 800,
    'ninja_fire_delay': 800,
    'hammer_hit_fire_delay': 320,
    
    # Elasticity
    'ground_elasticity_x': 0,
    'ground_elasticity_y': 0,
}

# Game modes
GAMEMODE_DM = 0    # Deathmatch
GAMEMODE_TDM = 1   # Team Deathmatch
GAMEMODE_CTF = 2   # Capture The Flag
GAMEMODE_RACE = 3  # Race
GAMEMODE_DDRACE = 4 # DDRace

# Tile constants (from DDNet)
TILE_AIR = 0
TILE_SOLID = 1
TILE_DEATH = 2
TILE_NOHOOK = 3
TILE_NOLASER = 4
TILE_THROUGH_CUT = 5
TILE_THROUGH = 6
TILE_JUMP = 7
TILE_FREEZE = 8
TILE_UNFREEZE = 9
TILE_TELEINEVIL = 10
TILE_TELEIN = 11
TILE_TELEOUT = 12
TILE_BOOST = 13
TILE_TELECHECKINEVIL = 14
TILE_TELECHECKIN = 15
TILE_TELECHECKOUT = 16
TILE_TELECHECK = 17
TILE_WALLJUMP = 18
TILE_EHOOK_START = 19
TILE_EHOOK_END = 20
TILE_HIT_START = 21
TILE_HIT_END = 22
TILE_SOLO_START = 23
TILE_SOLO_END = 24
TILE_SWITCHTIMEDOPEN = 25
TILE_SWITCHTIMEDCLOSE = 26
TILE_SWITCHOPEN = 27
TILE_SWITCHCLOSE = 28
TILE_TELEINHOOK = 29
TILE_TELEINREMOTE = 30
TILE_TELECHECKINREMOTE = 31

# Physics constants
PHYSICS_ITERATIONS = 5  # Number of iterations for collision resolution
MAX_COLLISION_DEPTH = 10  # Maximum depth for collision resolution

# Rendering constants
RENDER_FPS = 60
PHYSICS_FPS = 50
PHYSICS_DT = 1.0 / PHYSICS_FPS

# Player constants
MAX_JUMPS_DEFAULT = 2
MAX_AIR_JUMPS = 2