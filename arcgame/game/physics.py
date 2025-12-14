"""DDNet-compatible physics engine for character movement and hook mechanics"""
from ..base.vec2 import Vec2
from ..base.collision import CollisionWorld


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