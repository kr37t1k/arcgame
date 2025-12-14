"""Player entity for the DDNet clone"""
from ...base.vec2 import Vec2
from ..physics import CharacterPhysics


class Player:
    """Player entity with physics, input, and rendering properties"""
    def __init__(self, player_id, name="Player", pos=Vec2(0, 0)):
        self.player_id = player_id
        self.name = name
        self.team = 0  # 0 = red, 1 = blue, -1 = spectator
        self.score = 0
        self.lives = 3
        
        # Physics component
        self.physics = CharacterPhysics()
        self.physics.pos = pos
        
        # Appearance
        self.skin = "default"
        self.eye_emotion = "normal"  # normal, angry, happy, surprised, dead
        self.direction = 1  # 1 = right, -1 = left
        
        # Stats
        self.health = 10
        self.max_health = 10
        self.ammo_counts = {
            'hammer': float('inf'),  # Hammer has infinite ammo
            'gun': 10,
            'shotgun': 5,
            'grenade': 3,
            'rifle': 10
        }
        self.active_weapon = 'hammer'
        
        # Game state
        self.is_alive = True
        self.freeze_time = 0  # Time remaining frozen (for DDRace features)
        self.jumped_total = 0  # Total jumps performed (for DDRace)
        
        # Visual effects
        self.trail_effect = False
        self.emote = -1  # Current emote (-1 = none)
        self.emote_expire = 0
        
        # Input state
        self.input = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'jump': False,
            'fire': False,
            'hook': False
        }
        
    def update(self, dt):
        """Update player state"""
        # Update freeze timer
        if self.freeze_time > 0:
            self.freeze_time -= dt
            if self.freeze_time <= 0:
                self.freeze_time = 0
        
        # Update emote timer
        if self.emote_expire > 0:
            self.emote_expire -= dt
            if self.emote_expire <= 0:
                self.emote = -1
                self.emote_expire = 0
        
        # Update physics if not frozen
        if self.freeze_time <= 0 and self.is_alive:
            # Update physics input
            self.physics.update_input(self.input)
            self.physics.update(dt)
            
            # Update direction based on movement
            if self.physics.vel.x > 0.1:
                self.direction = 1
            elif self.physics.vel.x < -0.1:
                self.direction = -1
        
        # Update ammo for weapons that consume ammo
        if self.active_weapon in ['gun', 'shotgun', 'grenade', 'rifle']:
            if self.input['fire'] and self.ammo_counts[self.active_weapon] > 0:
                self.ammo_counts[self.active_weapon] -= 1
    
    def take_damage(self, amount, source_player=None):
        """Take damage from another player or environment"""
        if not self.is_alive or self.freeze_time > 0:
            return False
            
        self.health -= amount
        if self.health <= 0:
            self.die(source_player)
            return True
        return False
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
    
    def die(self, killer=None):
        """Kill the player"""
        self.is_alive = False
        self.health = 0
        self.eye_emotion = "dead"
        
        # Reset physics state
        self.physics.vel = Vec2(0, 0)
        self.physics.hook_state = 'IDLE'
        
        # If killed by another player, increase their score
        if killer and hasattr(killer, 'score'):
            killer.score += 1
    
    def respawn(self, spawn_pos):
        """Respawn the player at a position"""
        self.is_alive = True
        self.health = self.max_health
        self.eye_emotion = "normal"
        self.physics.pos = spawn_pos
        self.physics.vel = Vec2(0, 0)
        self.freeze_time = 0
        self.jumped_total = 0
        self.physics.jumped = [False, False]
        self.physics.double_jumped = False
    
    def set_input(self, input_dict):
        """Set input state from input dictionary"""
        # Only update allowed inputs
        for key in ['left', 'right', 'up', 'down', 'jump', 'fire', 'hook']:
            if key in input_dict:
                self.input[key] = input_dict[key]
    
    def get_position(self):
        """Get player position"""
        return self.physics.pos
    
    def get_velocity(self):
        """Get player velocity"""
        return self.physics.vel
    
    def get_direction(self):
        """Get facing direction"""
        return self.direction
    
    def fire_weapon(self):
        """Fire the current weapon"""
        if not self.is_alive or self.freeze_time > 0:
            return False
            
        if self.active_weapon == 'hammer':
            return self.use_hammer()
        elif self.active_weapon == 'gun':
            return self.use_gun()
        elif self.active_weapon == 'shotgun':
            return self.use_shotgun()
        elif self.active_weapon == 'grenade':
            return self.use_grenade()
        elif self.active_weapon == 'rifle':
            return self.use_rifle()
        else:
            return False
    
    def use_hammer(self):
        """Use hammer weapon (melee)"""
        # Hammer has infinite ammo and hits nearby enemies
        # This would check for nearby enemies in a real implementation
        return True
    
    def use_gun(self):
        """Use gun weapon (projectile)"""
        if self.ammo_counts['gun'] <= 0:
            return False
        # Create bullet entity in a real implementation
        return True
    
    def use_shotgun(self):
        """Use shotgun weapon (spread)"""
        if self.ammo_counts['shotgun'] <= 0:
            return False
        # Create multiple bullet entities in a real implementation
        return True
    
    def use_grenade(self):
        """Use grenade weapon (explosive projectile)"""
        if self.ammo_counts['grenade'] <= 0:
            return False
        # Create grenade entity in a real implementation
        return True
    
    def use_rifle(self):
        """Use rifle weapon (sniper/long range)"""
        if self.ammo_counts['rifle'] <= 0:
            return False
        # Create rifle bullet entity in a real implementation
        return True
    
    def switch_weapon(self, weapon_name):
        """Switch to a different weapon"""
        if weapon_name in self.ammo_counts:
            self.active_weapon = weapon_name
            return True
        return False
    
    def add_ammo(self, weapon_name, amount):
        """Add ammo to a weapon"""
        if weapon_name in self.ammo_counts:
            self.ammo_counts[weapon_name] = min(10, self.ammo_counts[weapon_name] + amount)  # Cap at 10
            return True
        return False
    
    def freeze(self, duration):
        """Freeze the player for DDRace functionality"""
        self.freeze_time = duration
    
    def unfreeze(self):
        """Unfreeze the player"""
        self.freeze_time = 0
    
    def reset_score(self):
        """Reset player score"""
        self.score = 0
    
    def add_score(self, points):
        """Add points to player score"""
        self.score += points


class EntityManager:
    """Manages all entities in the game world"""
    def __init__(self):
        self.players = {}  # player_id -> Player object
        self.projectiles = []
        self.pickups = []
        self.entities = []  # General entity list
        self.next_entity_id = 1
    
    def add_player(self, player):
        """Add a player to the manager"""
        self.players[player.player_id] = player
        self.entities.append(player)
    
    def remove_player(self, player_id):
        """Remove a player from the manager"""
        if player_id in self.players:
            player = self.players[player_id]
            self.entities.remove(player)
            del self.players[player_id]
    
    def get_player(self, player_id):
        """Get a player by ID"""
        return self.players.get(player_id)
    
    def update_all(self, dt):
        """Update all managed entities"""
        # Update players
        for player in list(self.players.values()):  # Use list() to avoid modification during iteration
            player.update(dt)
        
        # Update other entities
        for entity in self.entities:
            if entity not in self.players.values():  # Skip players since they're updated above
                if hasattr(entity, 'update'):
                    entity.update(dt)
    
    def get_players_in_radius(self, center_pos, radius):
        """Get all players within a certain radius of a position"""
        players_in_radius = []
        for player in self.players.values():
            if player.get_position().distance(center_pos) <= radius:
                players_in_radius.append(player)
        return players_in_radius


# Example usage and testing
if __name__ == "__main__":
    # Create a test player
    player = Player(1, "TestPlayer", Vec2(100, 100))
    
    print(f"Created player: {player.name} at {player.get_position()}")
    print(f"Health: {player.health}/{player.max_health}")
    print(f"Weapon: {player.active_weapon}")
    
    # Test taking damage
    player.take_damage(3)
    print(f"After taking 3 damage: Health = {player.health}")
    
    # Test healing
    player.heal(2)
    print(f"After healing 2: Health = {player.health}")
    
    # Test respawning
    player.take_damage(10)  # Kill player
    print(f"After killing: Alive = {player.is_alive}")
    
    player.respawn(Vec2(200, 200))
    print(f"After respawning: Alive = {player.is_alive}, Pos = {player.get_position()}")
    
    # Test input
    player.set_input({'left': True, 'jump': True})
    print(f"Input set: Left={player.input['left']}, Jump={player.input['jump']}")