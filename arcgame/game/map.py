"""DDNet map system with tile-based collision and game elements"""
from ursina import *
from base.collision import TileMap, CollisionWorld
from base.vec2 import Vec2
import random


class DDNetMap:
    """DDNet map with tiles, collision, and game elements"""
    
    # Tile types matching DDNet
    TILE_AIR = 0
    TILE_SOLID = 1
    TILE_DEATH = 2
    TILE_NOHOOK = 3
    TILE_NOLINE = 4
    TILE_FREEZE = 5
    TILE_UNFREEZE = 6
    TILE_DORIGHT = 7
    TILE_DOLEFT = 8
    TILE_DOUP = 9
    TILE_DODOWN = 10
    TILE_ROOFSLOPE = 11
    TILE_FLOORSLOPE = 12
    TILE_LOWSPEED = 13
    TILE_HIGHSPEED = 14
    TILE_TELEIN = 15
    TILE_TELEOUT = 16
    TILE_TELECHECK = 17
    TILE_TELECHECKOUT = 18
    TILE_TELEINEVIL = 19
    TILE_TELECHECKINEVIL = 20
    TILE_TELECHECKINEVIL = 21
    TILE_WALLJUMP = 22
    TILE_AIRJUMP = 23
    TILE_TELENOHOOK = 24
    TILE_THROUGH = 25
    TILE_THROUGH_CUT = 26
    TILE_THROUGH_ALL = 27
    TILE_JUMP = 28
    TILE_PENALTY = 29
    TILE_BOOST = 30
    TILE_TELEINWEAPON = 31
    TILE_TELEINHOOK = 32
    TILE_SPEEDUP = 33
    TILE_BONUS = 34
    TILE_NPC = 35
    TILE_PICKUP_HEALTH = 36
    TILE_PICKUP_ARMOR = 37
    TILE_PICKUP_WEAPON = 38
    TILE_PICKUP_NINJA = 39
    TILE_OWNED = 40
    TILE_END = 41
    TILE_BEGIN = 42
    TILE_CHECKPOINT = 43
    TILE_CHECKPOINT_FIRST = 44
    TILE_TELECHECKFIRST = 45
    TILE_TELECHECKFIRSTOUT = 46
    TILE_UNLOCK_TEAM = 47
    TILE_PENALTY_WEAK = 48
    TILE_PENALTY_STRONG = 49
    TILE_BONUS_WEAK = 50
    TILE_BONUS_STRONG = 51
    TILE_TELE_GUN = 52
    TILE_TELE_LASER = 53
    TILE_TELE_GRENADE = 54
    TILE_SWITCHTIMEDOPEN = 55
    TILE_SWITCHTIMEDCLOSE = 56
    TILE_SWITCHOPEN = 57
    TILE_SWITCHCLOSE = 58
    TILE_TELECHECKSHARED = 59
    TILE_TELECHECKOUTSHARED = 60
    TILE_TELECHECKFIRSTSHARED = 61
    TILE_TELECHECKFIRSTOUTSHARED = 62
    TILE_TELECHECKLASTSHARED = 63
    TILE_TELECHECKLASTOUTSHARED = 64
    TILE_TELELAST = 65
    TILE_TELELASTOUT = 66
    TILE_TELECHECKLAST = 67
    TILE_TELECHECKLASTOUT = 68
    TILE_TELECHECKFIRSTLAST = 69
    TILE_TELECHECKFIRSTLASTOUT = 70
    TILE_RESET = 71
    TILE_NPH_START = 72
    TILE_NPH_END = 73
    TILE_CREDITS_FIRST = 74
    TILE_CREDITS_LAST = 75
    TILE_NOLIVE = 76
    TILE_THROUGH_DIR = 77
    TILE_REFILL_JUMPS = 78
    TILE_NPC_START = 79
    TILE_NPC_END = 80
    TILE_OLDLASER = 81
    TILE_OLDLASER_END = 82
    TILE_UNLOCK_CURRENT = 83
    TILE_TELE_GUN_BIG = 84
    TILE_TELE_LASER_BIG = 85
    TILE_TELE_GRENADE_BIG = 86
    TILE_STOP = 87
    TILE_STOPS = 88
    TILE_STOPA = 89
    TILE_TELECHECKRC = 90
    
    def __init__(self, width=100, height=75, tile_size=32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        
        # Create tile map and collision world
        self.tile_map = TileMap(width, height, tile_size)
        self.collision_world = CollisionWorld(self.tile_map)
        
        # Visual entities for the map
        self.visual_tiles = []
        self.entities = []  # Game entities placed on the map
        
        # Create the map
        self.create_default_map()
    
    def create_default_map(self):
        """Create a default map with some basic elements"""
        # Create a simple platform layout
        # Ground
        for x in range(self.width):
            self.tile_map.set_tile(x * self.tile_size, (self.height - 1) * self.tile_size, self.TILE_SOLID)
            # Add some platforms
            if x % 15 == 0:  # Every 15 tiles
                platform_height = random.randint(self.height - 20, self.height - 10)
                platform_width = random.randint(3, 8)
                for px in range(platform_width):
                    if x + px < self.width:
                        self.tile_map.set_tile((x + px) * self.tile_size, platform_height * self.tile_size, self.TILE_SOLID)
        
        # Create visual representation of tiles
        self.create_visual_tiles()
    
    def create_visual_tiles(self):
        """Create visual entities for solid tiles"""
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.tile_map.get_tile_index(x * self.tile_size, y * self.tile_size)
                if tile_type != self.TILE_AIR:
                    # Create visual tile
                    tile_entity = Entity(
                        position=Vec3(x * self.tile_size, y * self.tile_size, 0),
                        model='quad',
                        texture='white_cube',  # Will be replaced with proper textures
                        color=self.get_tile_color(tile_type),
                        scale=self.tile_size,
                        origin=(-0.5, -0.5),
                        collider='box'
                    )
                    self.visual_tiles.append(tile_entity)
    
    def get_tile_color(self, tile_type):
        """Get color for tile type"""
        color_map = {
            self.TILE_SOLID: color.gray,
            self.TILE_DEATH: color.red,
            self.TILE_NOHOOK: color.blue,
            self.TILE_JUMP: color.green,
            self.TILE_BOOST: color.yellow,
            self.TILE_SPEEDUP: color.orange,
            self.TILE_PICKUP_HEALTH: color.green,
            self.TILE_PICKUP_ARMOR: color.blue,
            self.TILE_PICKUP_WEAPON: color.red,
            self.TILE_PICKUP_NINJA: color.black
        }
        return color_map.get(tile_type, color.gray)
    
    def place_entity(self, entity, x, y):
        """Place an entity at a specific position on the map"""
        entity.position = Vec3(x, y, 0)
        self.entities.append(entity)
    
    def spawn_character(self, character, x, y):
        """Spawn a character at a specific position"""
        character.position = Vec3(x, y, 0)
        character.pos_2d = Vec2(x, y)
        character.collision_world = self.collision_world
        character.physics.collision_world = self.collision_world
        self.entities.append(character)
    
    def is_solid(self, x, y):
        """Check if position is solid"""
        return self.collision_world.collide_point(Vec2(x, y))
    
    def get_tile_at(self, x, y):
        """Get tile type at position"""
        return self.tile_map.get_tile_index(x, y)
    
    def set_tile(self, x, y, tile_type):
        """Set tile type at position"""
        self.tile_map.set_tile(x, y, tile_type)
        # Update visual representation - in a real implementation, we'd update the specific tile