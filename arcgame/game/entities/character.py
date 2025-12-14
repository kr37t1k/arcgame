"""DDNet Character entity - main player character with full DDNet mechanics"""
from ursina import *
import math
from base.vec2 import Vec2
from game.physics import DDNetPhysics, HookSystem, TuningParams


class Character(Entity):
    """DDNet character with complete physics and mechanics"""
    
    # Hook states
    HOOK_RETRACTED = -1
    HOOK_IDLE = 0
    HOOK_RETRACT_START = 1
    HOOK_RETRACT_END = 3
    HOOK_FLYING = 4
    HOOK_GRABBED = 5
    
    def __init__(self, position=(0, 0, 0), collision_world=None, **kwargs):
        super().__init__(
            position=position,
            model='quad',
            scale=(28, 28, 1),  # DDNet character physical size
            origin=(-0.5, -0.5),
            **kwargs
        )
        
        # Visual elements
        self.body = Entity(
            parent=self,
            model='circle',
            color=color.orange,
            scale=0.6,
            z=-0.1
        )
        
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
        
        # Physics state
        self.pos_2d = Vec2(self.position.x, self.position.y)
        self.velocity = Vec2(0, 0)
        self.on_ground = False
        self.jumped = 0  # Bit field tracking jump state
        self.jumped_total = 0  # Total air jumps performed
        self.jumps = 2  # Number of jumps allowed (2 = double jump)
        self.direction = 0  # -1 for left, 1 for right, 0 for neutral
        
        # Health and game state
        self.health = 10
        self.armor = 0
        self.alive = True
        
        # Weapons and equipment
        self.active_weapon = 0  # 0=hammer, 1=gun, 2=shotgun, 3=grenade, 4=laser, 5=ninja
        self.weapons = {
            0: {'got': True, 'ammo': -1},   # Hammer (infinite ammo)
            1: {'got': True, 'ammo': -1},   # Gun (infinite ammo)
            2: {'got': False, 'ammo': 10},  # Shotgun
            3: {'got': False, 'ammo': 10},  # Grenade
            4: {'got': False, 'ammo': 10},  # Laser
            5: {'got': False, 'ammo': 1},   # Ninja (special)
        }
        
        # DDNet physics parameters
        self.tuning = TuningParams()
        self.physics = DDNetPhysics(collision_world)
        self.collision_world = collision_world
        
        # Hook system
        self.hook_system = HookSystem(self.pos_2d, self.tuning)
        
        # Animation variables
        self.foot_rotation_speed = 100
        self.foot_angle = 0
        self.is_moving = False
        self.last_move_direction = 0
        
        # Shooting variables
        self.can_shoot = True
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 10  # frames
        
        # Emote state
        self.emote_type = -1  # -1 = normal, 0-9 = different emotes
        self.emote_stop_tick = 0
        
        # Time related
        self.last_action_tick = 0
        self.spawn_tick = 0
        
        # Visual updates
        self.update_visual()
    
    def update_visual(self):
        """Update visual representation based on state"""
        # Update feet animation
        self.left_foot.rotation_z = self.foot_angle
        self.right_foot.rotation_z = -self.foot_angle
        
        # Update character facing direction based on velocity
        if self.velocity.x > 0:
            self.scale_x = abs(self.scale_x)  # Face right
        elif self.velocity.x < 0:
            self.scale_x = -abs(self.scale_x)  # Face left
    
    def update(self):
        """Main update method called every frame"""
        if not self.alive:
            return
            
        self.handle_physics()
        self.update_cooldowns()
        self.animate_feet()
        self.update_visual()
    
    def handle_physics(self):
        """Handle character physics using DDNet mechanics"""
        # Apply gravity
        self.velocity.y -= self.tuning.gravity
        
        # Handle input for direction
        direction = 0
        if held_keys['a'] or held_keys['left arrow']:
            direction = -1
        elif held_keys['d'] or held_keys['right arrow']:
            direction = 1
            
        self.direction = direction
        
        # Determine max speed and acceleration based on ground/air state
        if self.on_ground:
            max_speed = self.tuning.ground_control_speed
            accel = self.tuning.ground_control_accel
            friction = self.tuning.ground_friction
        else:
            max_speed = self.tuning.air_control_speed
            accel = self.tuning.air_control_accel
            friction = self.tuning.air_friction
        
        # Apply acceleration based on input direction
        if direction != 0:
            # Accelerate in the input direction
            self.velocity.x = self.velocity.x + direction * accel
            # Clamp to max speed in the direction of movement
            if direction > 0:
                self.velocity.x = min(self.velocity.x, max_speed)
            else:
                self.velocity.x = max(self.velocity.x, -max_speed)
            # Set moving state for foot animation
            self.is_moving = True
            self.last_move_direction = direction
        else:
            # Apply friction when no input
            self.velocity.x *= friction
            # Check if velocity is very small to stop completely
            if abs(self.velocity.x) < 0.1:
                self.velocity.x = 0
            self.is_moving = False
        
        # Handle hook physics if hook is grabbed
        if self.hook_system.state == self.HOOK_GRABBED and self.hook_system.hooked_player == -1:
            # Apply hook drag physics
            hook_vec = self.hook_system.pos - self.pos_2d
            hook_dist = hook_vec.length()
            
            if hook_dist > 46.0:  # Apply drag if beyond this distance
                hook_vel = hook_vec.normalize() * self.tuning.hook_drag_accel
                
                # Apply vertical adjustments (easier to go up with hook)
                if hook_vel.y > 0:
                    hook_vel.y *= 0.3
                
                # Boost if moving in same direction as hook, dampen otherwise
                if (hook_vel.x < 0 and self.velocity.x < 0) or (hook_vel.x > 0 and self.velocity.x > 0):
                    hook_vel.x *= 0.95
                else:
                    hook_vel.x *= 0.75
                
                # Apply hook velocity
                new_vel = self.velocity + hook_vel
                new_vel_length = new_vel.length()
                
                # Only apply if we're not going faster than the drag speed or if it would slow us down
                if new_vel_length < self.tuning.hook_drag_speed or new_vel_length < self.velocity.length():
                    self.velocity = new_vel
        
        # Update position using DDNet physics system
        new_pos, new_vel, is_grounded = self.physics.move_character(
            self.pos_2d, 
            self.velocity,
            size=Vec2(28.0, 28.0)  # DDNet character physical size
        )
        
        # Update state
        self.pos_2d = new_pos
        self.velocity = new_vel
        self.on_ground = is_grounded
        
        # Update ursina position to match physics position
        self.position = Vec3(self.pos_2d.x, self.pos_2d.y, self.position.z)
        
        # Update jump state tracking
        if self.on_ground:
            # Reset jump counters when on ground
            self.jumped &= ~2  # Clear second bit (air jump indicator)
            self.jumped_total = 0
        else:
            # Check if we just left the ground (started jumping)
            if not self.on_ground and not (self.jumped & 1):
                self.jumped |= 1  # Set first bit (jump indicator)
    
    def jump(self):
        """Make the character jump using DDNet mechanics"""
        # Check if we can jump (on ground or have air jumps left)
        can_jump = False
        
        if self.on_ground:
            # Ground jump
            can_jump = True
            self.jumped &= ~2  # Reset air jump bit
            self.jumped_total = 0
        elif self.jumped_total < self.jumps - 1:
            # Air jump allowed
            can_jump = True
            self.jumped_total += 1
            self.jumped |= 2  # Set air jump bit
        
        if can_jump:
            # Apply jump impulse based on ground/air state
            if self.on_ground:
                self.velocity.y = -self.tuning.ground_jump_impulse  # Negative because DDNet uses positive Y as down
            else:
                # Air jump impulse
                self.velocity.y = -self.tuning.air_jump_impulse
                # Preserve some horizontal velocity during air jump
                if abs(self.velocity.x) < self.tuning.air_control_speed:
                    # Add a little horizontal boost on air jump
                    self.velocity.x *= 1.1
    
    def use_hook(self, target_pos):
        """Use the hook to target position using DDNet mechanics"""
        # Convert target position to Vec2 for physics
        target_2d = Vec2(target_pos.x, target_pos.y)
        
        # Calculate direction to target
        direction = target_2d - self.pos_2d
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = Vec2(1, 0)  # Default direction if target is same as player
        
        # Determine if hook button is being pressed
        hook_input = mouse.right  # Assuming right mouse button for hook
        
        # Update hook system
        self.hook_system.update(self.pos_2d, direction, hook_input, self.on_ground)
    
    def fire_weapon(self):
        """Fire the currently active weapon"""
        if not self.can_shoot:
            return
            
        weapon = self.active_weapon
        if not self.weapons[weapon]['got']:
            return  # Don't have this weapon
            
        # Check ammo if not infinite (-1)
        if self.weapons[weapon]['ammo'] != -1 and self.weapons[weapon]['ammo'] <= 0:
            return  # Out of ammo
            
        # Apply weapon cooldown
        self.can_shoot = False
        self.shoot_cooldown = self.get_weapon_fire_delay(weapon)
        
        # Consume ammo if not infinite
        if self.weapons[weapon]['ammo'] != -1:
            self.weapons[weapon]['ammo'] -= 1
    
    def get_weapon_fire_delay(self, weapon_type):
        """Get fire delay for weapon type"""
        if weapon_type == 0:  # Hammer
            return self.tuning.hammer_fire_delay
        elif weapon_type == 1:  # Gun
            return self.tuning.gun_fire_delay
        elif weapon_type == 2:  # Shotgun
            return self.tuning.shotgun_fire_delay
        elif weapon_type == 3:  # Grenade
            return self.tuning.grenade_fire_delay
        elif weapon_type == 4:  # Laser
            return self.tuning.laser_fire_delay
        elif weapon_type == 5:  # Ninja
            return self.tuning.ninja_fire_delay
        return 10  # Default delay
    
    def set_weapon(self, weapon_type):
        """Set the active weapon"""
        if weapon_type in self.weapons and self.weapons[weapon_type]['got']:
            self.active_weapon = weapon_type
    
    def give_weapon(self, weapon_type, ammo=10):
        """Give a weapon to the character"""
        if weapon_type in self.weapons:
            self.weapons[weapon_type]['got'] = True
            if self.weapons[weapon_type]['ammo'] != -1:
                self.weapons[weapon_type]['ammo'] += ammo
    
    def take_damage(self, amount, from_entity=None, weapon_type=None):
        """Take damage and update health"""
        if not self.alive:
            return
            
        # Apply damage to armor first, then health
        if self.armor > 0:
            armor_damage = min(self.armor, amount)
            self.armor -= armor_damage
            remaining_damage = amount - armor_damage
        else:
            remaining_damage = amount
            
        if remaining_damage > 0:
            self.health -= remaining_damage
            if self.health <= 0:
                self.die(from_entity, weapon_type)
    
    def die(self, killer=None, weapon=None):
        """Handle character death"""
        self.alive = False
        self.health = 0
        # Reset to spawn position
        self.pos_2d = Vec2(0, 0)  # Should be set to actual spawn
        self.position = Vec3(0, 0, self.position.z)
        self.velocity = Vec2(0, 0)
        self.on_ground = False
        self.jumped = 0
        self.jumped_total = 0
    
    def respawn(self):
        """Respawn the character"""
        self.alive = True
        self.health = 10
        self.armor = 0
        # Reset other states as needed
        self.spawn_tick = time.time()
    
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
    
    def update_skin(self, body_color=None, feet_color=None):
        """Update character skin colors"""
        if body_color:
            self.body.color = body_color
        if feet_color:
            self.left_foot.color = feet_color
            self.right_foot.color = feet_color