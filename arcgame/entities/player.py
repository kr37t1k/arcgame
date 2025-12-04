"""
Player entity for ArcGame
Handles player movement, physics, shooting, and hook mechanics
"""

from ursina import *
import math

class Player(Entity):
    def __init__(self, position=(0, 0, 0), config=None):
        super().__init__(
            position=position,
            collider='sphere'
        )
        
        # Create the main body (circle)
        self.body = Entity(
            parent=self,
            model='circle',
            color=color.orange,
            scale=0.6,
            z=-0.1  # Slightly behind other elements
        )
        
        # Create the two feet
        self.left_foot = Entity(
            parent=self,
            model='quad',
            color=color.gray,
            scale=(0.4, 0.2),
            position=Vec3(-0.3, -0.4, 0),
            origin_y=-0.5
        )
        
        self.right_foot = Entity(
            parent=self,
            model='circle',
            color=color.gray,
            scale=0.3,
            position=Vec3(0.3, -0.4, 0),
            origin_y=-0.5
        )
        
        self.config = config
        self.health = 10
        self.max_health = 10
        self.velocity = Vec3(0, 0, 0)
        self.jumping = False
        self.on_ground = False
        self.gravity = -0.5
        self.jump_force = 8
        self.move_speed = 4
        self.friction = 0.8
        self.air_resistance = 0.99
        
        # Hook variables
        self.hook_active = False
        self.hook_pos = None
        self.hook_length = 100
        self.hook_reel_speed = 15
        self.hook_extend_speed = 20
        self.hook_connected = False
        self.hook_target = None
        self.hook_entity = None
        
        # Shooting variables
        self.can_shoot = True
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 10  # frames
        
        # Player appearance (for customization)
        self.skin_colors = {
            'body': color.orange,
            'feet': color.gray
        }
        
        # Animation variables for feet rotation
        self.foot_rotation_speed = 100  # degrees per second when moving
        self.foot_angle = 0
        self.is_moving = False
        self.last_move_direction = 0
        
    def update(self):
        """Update player state"""
        self.handle_physics()
        self.handle_hook()
        self.update_cooldowns()
        self.animate_feet()
        
    def handle_physics(self):
        """Handle player physics and movement"""
        # Apply gravity
        self.velocity.y += self.gravity
        
        # Apply friction when on ground
        if self.on_ground:
            self.velocity.x *= self.friction
        else:
            self.velocity.x *= self.air_resistance
            self.velocity.z *= self.air_resistance
            
        # Handle keyboard input for movement
        direction = 0
        if held_keys['a'] or held_keys['left arrow']:
            direction -= 1
        if held_keys['d'] or held_keys['right arrow']:
            direction += 1
            
        if direction != 0:
            self.velocity.x = direction * self.move_speed
            # Set moving state for foot animation
            self.is_moving = True
            self.last_move_direction = direction
        else:
            self.is_moving = False
        
        # Update position based on velocity
        self.position += self.velocity * time.dt
        
        # Check if player is on ground
        ray = raycast(self.position, Vec3(0, -1, 0), distance=1.3, ignore=[self])
        self.on_ground = ray.hit
        
        # Prevent falling through the ground
        if self.on_ground and self.velocity.y <= 0:
            self.velocity.y = 0
            self.jumping = False
            
    def jump(self):
        """Make the player jump"""
        if self.on_ground:
            self.velocity.y = self.jump_force
            self.jumping = True
            self.on_ground = False
            
    def move_left(self):
        """Move player left"""
        self.velocity.x = -self.move_speed
        
    def move_right(self):
        """Move player right"""
        self.velocity.x = self.move_speed
        
    def shoot(self, target_pos):
        """Shoot at target position"""
        if not self.can_shoot:
            return
            
        # Calculate direction vector
        direction = target_pos - self.position
        direction.y = 0  # Ignore height difference for now
        direction.normalize()
        
        # Create projectile
        projectile = Entity(
            parent=scene,
            model='circle',
            color=color.red,
            scale=0.2,
            position=self.position + Vec3(0, 0.3, 0),  # Position at body level
            collider='sphere'
        )
        
        # Set projectile velocity
        projectile.velocity = direction * 15
        
        # Update cooldown
        self.can_shoot = False
        self.shoot_cooldown = self.shoot_cooldown_max
        
        # Projectile update function
        def update_proj():
            if projectile.enabled:
                projectile.position += projectile.velocity * time.dt
                # Destroy projectile after some time or if it goes too far
                if abs(projectile.x - self.x) > 50 or abs(projectile.y - self.y) > 30:
                    destroy(projectile)
        
        projectile.update = update_proj
        
    def use_hook(self, target_pos):
        """Use the hook to target position"""
        if self.hook_active:
            return
            
        # Calculate direction to target
        direction = target_pos - self.position
        distance = direction.length()
        
        if distance > self.hook_length:
            # Normalize direction and set to max hook length
            direction.normalize()
            self.hook_target = self.position + direction * self.hook_length
        else:
            self.hook_target = target_pos
            
        # Create hook visual
        self.hook_entity = Entity(
            parent=scene,
            model='circle',
            color=color.yellow,
            scale=0.15,
            position=self.position,
            collider='sphere'
        )
        
        self.hook_active = True
        self.hook_connected = False
        
    def handle_hook(self):
        """Handle hook mechanics"""
        if not self.hook_active:
            return
            
        # Update hook entity position if it exists
        if self.hook_entity:
            if not self.hook_connected:
                # Extend hook towards target
                direction = self.hook_target - self.position
                distance = direction.length()
                
                if distance < 0.5:
                    # Hook reached target
                    self.hook_connected = True
                    self.hook_pos = self.hook_target
                    if self.hook_entity:
                        self.hook_entity.position = self.hook_pos
                else:
                    # Move hook towards target
                    direction.normalize()
                    hook_speed = self.hook_extend_speed * time.dt
                    if hook_speed > distance:
                        self.hook_pos = self.hook_target
                        self.hook_connected = True
                        if self.hook_entity:
                            self.hook_entity.position = self.hook_pos
                    else:
                        if not self.hook_pos:
                            self.hook_pos = self.position + direction * hook_speed
                        else:
                            self.hook_pos += direction * hook_speed
                        if self.hook_entity:
                            self.hook_entity.position = self.hook_pos
            else:
                # Reel in the hook, pulling player towards hook position
                if self.hook_pos:
                    direction = self.hook_pos - self.position
                    distance = direction.length()
                    
                    if distance < 0.5:
                        # Reached hook position
                        self.hook_active = False
                        self.hook_connected = False
                        self.hook_pos = None
                        # Destroy hook entity
                        if self.hook_entity:
                            destroy(self.hook_entity)
                            self.hook_entity = None
                    else:
                        # Pull player towards hook
                        direction.normalize()
                        pull_speed = self.hook_reel_speed * time.dt
                        self.velocity += direction * pull_speed * 2  # Extra force to pull player
        else:
            # If hook entity doesn't exist, deactivate hook
            self.hook_active = False
            self.hook_connected = False
            self.hook_pos = None
                    
    def animate_feet(self):
        """Animate feet rotation when moving"""
        if self.is_moving:
            # Rotate feet when moving
            rotation_amount = self.foot_rotation_speed * time.dt
            self.foot_angle += rotation_amount * self.last_move_direction
            
            # Apply rotation to feet - they rotate in opposite directions
            self.left_foot.rotation_z = self.foot_angle
            self.right_foot.rotation_z = -self.foot_angle
        else:
            # Gradually reset feet to normal position when not moving
            if abs(self.foot_angle) > 1:
                rotation_amount = self.foot_rotation_speed * time.dt
                if self.foot_angle > 0:
                    self.foot_angle -= rotation_amount
                    if self.foot_angle < 0:
                        self.foot_angle = 0
                else:
                    self.foot_angle += rotation_amount
                    if self.foot_angle > 0:
                        self.foot_angle = 0
            
            # Apply rotation to feet
            self.left_foot.rotation_z = self.foot_angle
            self.right_foot.rotation_z = -self.foot_angle

    def update_cooldowns(self):
        """Update cooldown timers"""
        if not self.can_shoot:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.can_shoot = True
                
    def take_damage(self, amount):
        """Take damage and update health"""
        self.health -= amount
        if self.health <= 0:
            self.die()
            
    def die(self):
        """Handle player death"""
        self.health = self.max_health
        self.position = Vec3(0, 5, 0)  # Reset to spawn
        self.velocity = Vec3(0, 0, 0)
        
        # Clean up hook if active
        if self.hook_entity:
            destroy(self.hook_entity)
            self.hook_entity = None
        self.hook_active = False
        self.hook_connected = False
        self.hook_pos = None
        
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        
    def update_skin(self, body_color=None, feet_color=None):
        """Update player skin colors"""
        if body_color:
            self.skin_colors['body'] = body_color
            self.body.color = body_color
        if feet_color:
            self.skin_colors['feet'] = feet_color
            self.left_foot.color = feet_color
            self.right_foot.color = feet_color