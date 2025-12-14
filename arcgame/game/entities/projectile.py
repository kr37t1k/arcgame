"""DDNet Projectile entity - represents fired weapons like guns, grenades, etc."""
from ursina import *
from base.vec2 import Vec2


class Projectile(Entity):
    """DDNet projectile with physics and collision"""
    
    def __init__(self, position=(0, 0, 0), velocity=(0, 0), weapon_type=1, 
                 owner=None, collision_world=None, **kwargs):
        super().__init__(
            position=position,
            model='circle',
            color=color.red,
            scale=0.2,
            **kwargs
        )
        
        # Physics properties
        self.pos_2d = Vec2(self.position.x, self.position.y)
        self.velocity = Vec2(velocity[0], velocity[1])
        self.start_pos = self.pos_2d.copy()
        
        # Projectile properties
        self.weapon_type = weapon_type  # 1=gun, 2=shotgun, 3=grenade, 4=laser
        self.owner = owner  # Character that fired this projectile
        self.collision_world = collision_world
        
        # Lifetime and state
        self.lifetime = self.get_weapon_lifetime(weapon_type)
        self.max_lifetime = self.lifetime
        self.damage = self.get_weapon_damage(weapon_type)
        self.bounces = 0
        self.max_bounces = self.get_weapon_bounces(weapon_type)
        
        # Physics parameters based on weapon type
        self.gravity = self.get_weapon_gravity(weapon_type)
        self.curvature = self.get_weapon_curvature(weapon_type)
        
        # Visual updates
        self.update_visual()
    
    def update_visual(self):
        """Update visual representation"""
        # Rotate based on velocity direction
        if self.velocity.length() > 0:
            angle = self.velocity.angle() * 180 / 3.14159
            self.rotation_z = angle
    
    def update(self):
        """Main update method called every frame"""
        if self.lifetime <= 0:
            self.destroy()
            return
            
        self.handle_physics()
        self.update_visual()
        self.lifetime -= time.dt
        
        # Check if projectile has gone too far from start
        if (self.pos_2d - self.start_pos).length() > 1000:  # Too far, destroy
            self.destroy()
    
    def handle_physics(self):
        """Handle projectile physics"""
        # Apply gravity if applicable
        if self.gravity != 0:
            self.velocity.y -= self.gravity * time.dt * 50  # Scale to match DDNet gravity
            
        # Apply curvature (for grenades)
        if self.curvature != 0:
            # Apply parabolic trajectory
            time_in_air = self.max_lifetime - self.lifetime
            self.pos_2d.y -= self.curvature * time_in_air * time_in_air * time.dt
            
        # Update position
        self.pos_2d += self.velocity * time.dt
        
        # Check collision with world
        if self.collision_world:
            if self.collision_world.collide_circle(self.pos_2d, 5):  # 5px radius
                # Hit wall, bounce or destroy based on weapon type
                if self.can_bounce():
                    self.bounce()
                else:
                    self.on_collision()
        
        # Update ursina position
        self.position = Vec3(self.pos_2d.x, self.pos_2d.y, self.position.z)
    
    def can_bounce(self):
        """Check if projectile can bounce"""
        return self.bounces < self.max_bounces
    
    def bounce(self):
        """Bounce the projectile off a surface"""
        # For now, just reduce velocity and increment bounce counter
        self.velocity.x *= -0.8  # Reverse and dampen X velocity
        self.velocity.y *= -0.8  # Reverse and dampen Y velocity
        self.bounces += 1
        
        # If max bounces reached, destroy
        if self.bounces >= self.max_bounces:
            self.on_collision()
    
    def on_collision(self):
        """Handle collision with wall or character"""
        # Create explosion effect for grenades
        if self.weapon_type == 3:  # Grenade
            self.create_explosion()
        
        # Destroy projectile
        self.destroy()
    
    def check_collision_with_character(self, character):
        """Check if projectile hits a character"""
        distance = (self.pos_2d - character.pos_2d).length()
        if distance < 14:  # Character radius
            character.take_damage(self.damage, from_entity=self.owner, weapon_type=self.weapon_type)
            if self.weapon_type != 4:  # Laser doesn't get destroyed on hit
                self.destroy()
            return True
        return False
    
    def create_explosion(self):
        """Create explosion effect for grenade"""
        # In a real implementation, this would create visual effects
        pass
    
    def get_weapon_lifetime(self, weapon_type):
        """Get lifetime for weapon type"""
        if weapon_type == 1:  # Gun
            return 1.0
        elif weapon_type == 2:  # Shotgun
            return 0.2
        elif weapon_type == 3:  # Grenade
            return 2.0
        elif weapon_type == 4:  # Laser
            return 1.5
        return 1.0
    
    def get_weapon_damage(self, weapon_type):
        """Get damage for weapon type"""
        if weapon_type == 1:  # Gun
            return 1
        elif weapon_type == 2:  # Shotgun
            return 2
        elif weapon_type == 3:  # Grenade
            return 5
        elif weapon_type == 4:  # Laser
            return 3
        return 1
    
    def get_weapon_bounces(self, weapon_type):
        """Get max bounces for weapon type"""
        if weapon_type == 3:  # Grenade
            return 1
        elif weapon_type == 4:  # Laser
            return 1000  # Effectively infinite for laser bounces
        return 0
    
    def get_weapon_gravity(self, weapon_type):
        """Get gravity for weapon type"""
        if weapon_type == 3:  # Grenade
            return 0.5
        return 0.0
    
    def get_weapon_curvature(self, weapon_type):
        """Get curvature for weapon type"""
        if weapon_type == 3:  # Grenade
            return 7.0
        return 0.0