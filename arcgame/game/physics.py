"""DDNet-compatible physics engine for character movement and hook mechanics"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base.vec2 import Vec2
from base.collision import CollisionWorld


class CharacterPhysics:
    """Character physics matching DDNet's movement system"""
    def __init__(self, collision_world=None):
        # Position and velocity
        self.pos = Vec2(0, 0)
        self.vel = Vec2(0, 0)
        
        # Input state
        self.input = {
            'left': False,
            'right': False,
            'up': False,
            'down': False,
            'jump': False,
            'hook': False
        }
        
        # Movement constants matching DDNet
        self.air_jump_impulse = 50.0
        self.air_control = 250.0
        self.air_friction = 0.95
        self.ground_friction = 0.92
        self.max_speed = 100.0
        self.jump_impulse = 6.0
        self.gravity = Vec2(0, 500.0)
        
        # Hook physics
        self.hook_state = 'IDLE'  # IDLE, FLYING, GRABBED
        self.hook_pos = Vec2(0, 0)
        self.hook_vel = Vec2(0, 0)
        self.hook_max_distance = 384.0  # Standard DDNet hook distance
        self.hook_fire_speed = 800.0
        self.hook_drag_accel = 3.0
        self.hook_drag_speed = 60.0
        
        # State tracking
        self.jumped = [False, False]  # For double jump
        self.double_jumped = False
        self.on_ground = False
        self.collision = collision_world
        
        # For input prediction
        self.tick_rate = 50  # Ticks per second (DDNet default)
        self.time_step = 1.0 / self.tick_rate

    def update_input(self, input_dict):
        """Update input state from input dictionary"""
        self.input.update(input_dict)

    def update(self, dt):
        """Update physics with time delta"""
        # Update hook first if active
        if self.hook_state == 'FLYING':
            self.update_hook_flying(dt)
        elif self.hook_state == 'GRABBED':
            self.update_hook_grabbed(dt)
            
        # Apply gravity
        self.vel = self.vel + self.gravity * dt
        
        # Determine friction
        friction = self.air_friction if not self.on_ground else self.ground_friction
        
        # Apply input forces
        self.apply_input_forces(dt)
        
        # Apply friction
        self.vel = self.vel * friction
        
        # Clamp speed
        self.vel = self.vel.clamp_length(self.max_speed)
        
        # Move character with collision
        self.move_with_collision(dt)

    def apply_input_forces(self, dt):
        """Apply forces based on input"""
        # Horizontal movement
        if self.input['left'] or self.input['right']:
            direction = -1 if self.input['left'] else 1
            acceleration = self.air_control if not self.on_ground else 200.0
            self.vel.x += direction * acceleration * dt
            
        # Jumping
        if self.input['jump'] and self.on_ground:
            self.vel.y = -self.jump_impulse
            self.on_ground = False
            self.jumped = [False, False]  # Reset jump state when leaving ground
        elif self.input['jump'] and not self.jumped[0]:
            # Air jump
            self.vel.y = -self.jump_impulse
            self.jumped[0] = True
        elif self.input['jump'] and not self.jumped[1] and self.jumped[0]:
            # Second air jump
            self.vel.y = -self.jump_impulse
            self.jumped[1] = True

    def move_with_collision(self, dt):
        """Move character with collision detection"""
        if not self.collision:
            self.pos = self.pos + self.vel * dt
            return
            
        # Predict new position
        new_pos = self.pos + self.vel * dt
        
        # Check if moving into solid tile
        char_size = Vec2(20, 20)  # Approximate character size
        if not self.collision.collide_rect(new_pos, char_size):
            self.pos = new_pos
            self.on_ground = self.is_on_ground()
        else:
            # Handle collision by moving along axes separately
            # First try X-only movement
            test_pos_x = Vec2(new_pos.x, self.pos.y)
            if not self.collision.collide_rect(test_pos_x, char_size):
                self.pos.x = new_pos.x
            else:
                self.vel.x = 0  # Stop horizontal movement
                
            # Then try Y-only movement
            test_pos_y = Vec2(self.pos.x, new_pos.y)
            if not self.collision.collide_rect(test_pos_y, char_size):
                self.pos.y = new_pos.y
                self.on_ground = self.is_on_ground()
            else:
                self.vel.y = 0  # Stop vertical movement
                # If stopped vertically and velocity was downward, we're on ground
                if self.vel.y >= 0:
                    self.on_ground = True

    def is_on_ground(self):
        """Check if character is on ground"""
        if not self.collision:
            return False
            
        # Check if there's solid ground right below
        char_size = Vec2(20, 20)
        test_pos = Vec2(self.pos.x, self.pos.y + char_size.y + 1)
        return self.collision.collide_rect(test_pos, char_size)

    def fire_hook(self, target_pos):
        """Fire the hook towards target position"""
        if self.hook_state != 'IDLE':
            return False
            
        # Calculate direction to target
        dir_to_target = (target_pos - self.pos).normalize()
        self.hook_pos = self.pos + dir_to_target * 24  # Start hook slightly away from player
        self.hook_vel = dir_to_target * self.hook_fire_speed
        self.hook_state = 'FLYING'
        return True

    def update_hook_flying(self, dt):
        """Update hook while flying"""
        # Move hook
        old_hook_pos = self.hook_pos.copy()
        self.hook_pos = self.hook_pos + self.hook_vel * dt
        
        # Check if hook hit something or went too far
        distance_from_player = (self.hook_pos - self.pos).length()
        if distance_from_player > self.hook_max_distance:
            self.hook_state = 'IDLE'
            return
            
        # Check collision with map
        if self.collision and self.collision.collide_point(self.hook_pos):
            # Hook hit a wall, now it's grabbed
            self.hook_state = 'GRABBED'
            # Adjust position to be exactly on the surface
            self.hook_pos = old_hook_pos

    def update_hook_grabbed(self, dt):
        """Update hook when grabbed to surface"""
        # Calculate direction from player to hook
        dir_to_hook = (self.hook_pos - self.pos).normalize()
        
        # Calculate distance from player to hook
        dist_to_hook = (self.hook_pos - self.pos).length()
        
        # If the player is beyond the hook distance, apply drag force
        if dist_to_hook > self.hook_max_distance:
            # Apply hook drag acceleration towards the hook
            drag_force = dir_to_hook * self.hook_drag_accel * dt * 100
            self.vel = self.vel + drag_force
            
            # Also pull the hook position toward the player if needed
            # This helps keep the hook attached properly
            hook_pull = -dir_to_hook * self.hook_drag_speed * dt
            # Don't actually move hook in this simplified model

    def release_hook(self):
        """Release the hook"""
        self.hook_state = 'IDLE'

    def reset_jumps(self):
        """Reset jump status when landing on ground"""
        if self.on_ground:
            self.jumped = [False, False]
            self.double_jumped = False


class TuningParams:
    """DDNet tuning parameters matching those from tuning.h"""
    def __init__(self):
        # Physics tuning parameters
        self.ground_control_speed = 10.0
        self.ground_control_accel = 100.0 / 50  # SERVER_TICK_SPEED = 50
        self.ground_friction = 0.5
        self.ground_jump_impulse = 13.2
        self.air_jump_impulse = 12.0
        self.air_control_speed = 250.0 / 50
        self.air_control_accel = 1.5
        self.air_friction = 0.95
        self.hook_length = 380.0
        self.hook_fire_speed = 80.0
        self.hook_drag_accel = 3.0
        self.hook_drag_speed = 15.0
        self.gravity = 0.5
        
        # Velocity ramp
        self.velramp_start = 550
        self.velramp_range = 2000
        self.velramp_curvature = 1.4
        
        # Weapon tuning
        self.gun_curvature = 1.25
        self.gun_speed = 2200.0
        self.gun_lifetime = 2.0
        
        self.shotgun_curvature = 1.25
        self.shotgun_speed = 2750.0
        self.shotgun_speeddiff = 0.8
        self.shotgun_lifetime = 0.20
        
        self.grenade_curvature = 7.0
        self.grenade_speed = 1000.0
        self.grenade_lifetime = 2.0
        
        self.laser_reach = 800.0
        self.laser_bounce_delay = 150
        self.laser_bounce_num = 1000
        self.laser_bounce_cost = 0
        self.laser_damage = 5
        
        # Game settings
        self.player_collision = 1
        self.player_hooking = 1
        
        # DDNet specific
        self.jetpack_strength = 400.0
        self.shotgun_strength = 10.0
        self.explosion_strength = 6.0
        self.hammer_strength = 1.0
        self.hook_duration = 1.25
        
        # Fire delays (in milliseconds)
        self.hammer_fire_delay = 125
        self.gun_fire_delay = 125
        self.shotgun_fire_delay = 500
        self.grenade_fire_delay = 500
        self.laser_fire_delay = 800
        self.ninja_fire_delay = 800
        self.hammer_hit_fire_delay = 320


class HookSystem:
    """DDNet hook system mechanics"""
    def __init__(self, character_pos, tuning_params):
        self.pos = character_pos.copy()
        self.tuning = tuning_params
        # Hook states (matching DDNet values)
        self.HOOK_RETRACTED = -1
        self.HOOK_IDLE = 0
        self.HOOK_RETRACT_START = 1
        self.HOOK_RETRACT_END = 3
        self.HOOK_FLYING = 4
        self.HOOK_GRABBED = 5
        self.state = self.HOOK_RETRACTED
        self.dir = Vec2(0, 0)
        self.tick = 0
        self.hooked_player = -1
        
    def update(self, character_pos, direction, hook_input, on_ground):
        """Update hook state based on input and conditions"""
        self.dir = direction
        
        if hook_input:
            if self.state == self.HOOK_IDLE:
                # Launch hook
                self.state = self.HOOK_FLYING
                self.pos = character_pos + direction * 28.0 * 1.5  # Physical size * 1.5
                self.tick = int(50 * (1.25 - self.tuning.hook_duration))  # SERVER_TICK_SPEED * (1.25 - hook_duration)
        else:
            if self.state == self.HOOK_GRABBED:
                # Release hook
                self.hooked_player = -1
            self.state = self.HOOK_IDLE
            self.pos = character_pos


class DDNetPhysics:
    """DDNet physics system for character movement"""
    def __init__(self, collision_world=None):
        self.collision_world = collision_world
    
    def move_character(self, pos, vel, size):
        """Move character with collision detection"""
        if not self.collision_world:
            # If no collision world, just apply velocity
            new_pos = pos + vel * 0.016  # Assume ~60fps update
            return new_pos, vel, False  # Return new position, velocity, and grounded status
        
        # Simple collision response
        # Calculate new position with velocity
        new_pos = pos + vel * 0.016  # Time step approximation
        
        # Check collision at new position
        # This is a simplified collision check - in reality would check each axis separately
        half_size = size / 2
        grounded = False
        
        # Check for ground collision (simplified)
        if self.collision_world.collide_point(Vec2(new_pos.x, new_pos.y + half_size.y + 1)):
            grounded = True
            new_pos.y = new_pos.y - (new_pos.y % 16) + 1  # Snap to grid, simplified
            if vel.y > 0:  # If moving down and hit ground, stop vertical movement
                vel.y = 0
        
        # Check for wall collision
        if self.collision_world.collide_point(Vec2(new_pos.x + half_size.x, new_pos.y)):
            new_pos.x = pos.x  # Revert x movement
            vel.x = 0
            
        if self.collision_world.collide_point(Vec2(new_pos.x - half_size.x, new_pos.y)):
            new_pos.x = pos.x  # Revert x movement
            vel.x = 0
        
        # Check if hitting ceiling
        if self.collision_world.collide_point(Vec2(new_pos.x, new_pos.y - half_size.y)):
            new_pos.y = pos.y  # Revert y movement
            vel.y = 0
            
        return new_pos, vel, grounded


class PhysicsWorld:
    """Physics simulation world containing multiple characters and objects"""
    def __init__(self):
        self.characters = []
        self.projectiles = []
        self.collision = CollisionWorld()
        self.time = 0.0
        
    def add_character(self, character):
        """Add a character to the physics world"""
        self.characters.append(character)
        if not character.collision:
            character.collision = self.collision
            
    def add_collision_map(self, tile_map):
        """Add a collision map to the world"""
        self.collision.set_map(tile_map)
        
    def update(self, dt):
        """Update all physics objects in the world"""
        self.time += dt
        
        # Update all characters
        for char in self.characters:
            char.update(dt)
            
        # Update projectiles
        for proj in self.projectiles[:]:  # Copy list to avoid modification during iteration
            proj.update(dt)
            # Remove projectiles that are out of bounds or collided
            if proj.should_remove():
                self.projectiles.remove(proj)


# Example usage and testing
if __name__ == "__main__":
    from ..base.collision import TileMap
    
    # Create a simple test scenario
    tile_map = TileMap(20, 15)
    # Add some platforms
    for x in range(5, 15):
        tile_map.set_tile(x * 32, 10 * 32, 1)  # Platform at y=320
    
    collision = CollisionWorld(tile_map)
    char_physics = CharacterPhysics(collision)
    
    # Place character above the platform
    char_physics.pos = Vec2(5 * 32, 9 * 32)
    
    print(f"Initial position: {char_physics.pos}")
    print(f"On ground initially: {char_physics.on_ground}")
    
    # Simulate falling for 0.1 seconds
    char_physics.update(0.1)
    print(f"After falling: {char_physics.pos}, on ground: {char_physics.on_ground}")
    
    # Test movement
    char_physics.update_input({'right': True})
    char_physics.update(0.1)
    print(f"After moving right: {char_physics.pos}")