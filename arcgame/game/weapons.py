"""Weapon system for the DDNet clone"""
from ..base.vec2 import Vec2


class Weapon:
    """Base weapon class"""
    def __init__(self, name, fire_rate=0.5, damage=1, ammo=float('inf'), reload_time=0):
        self.name = name
        self.fire_rate = fire_rate  # Time between shots
        self.damage = damage
        self.max_ammo = ammo
        self.ammo = ammo
        self.reload_time = reload_time
        
        self.last_fire_time = 0
        self.reload_start_time = 0
        self.is_reloading = False
    
    def can_fire(self, current_time):
        """Check if weapon can fire"""
        if self.is_reloading:
            return False
        if self.ammo <= 0 and self.max_ammo != float('inf'):
            return False
        return current_time - self.last_fire_time >= self.fire_rate
    
    def fire(self, current_time, position, direction, shooter=None):
        """Fire the weapon - returns projectile or None"""
        if not self.can_fire(current_time):
            return None
            
        if self.max_ammo != float('inf'):
            self.ammo -= 1
            
        self.last_fire_time = current_time
        return self.create_projectile(position, direction, shooter)
    
    def create_projectile(self, position, direction, shooter):
        """Create a projectile - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement create_projectile")
    
    def reload(self, current_time):
        """Start reloading"""
        if self.is_reloading or self.ammo == self.max_ammo:
            return False
            
        self.is_reloading = True
        self.reload_start_time = current_time
        return True
    
    def update(self, current_time):
        """Update weapon state"""
        if self.is_reloading and current_time - self.reload_start_time >= self.reload_time:
            self.ammo = self.max_ammo
            self.is_reloading = False


class Hammer(Weapon):
    """Hammer weapon - melee attack"""
    def __init__(self):
        super().__init__("hammer", fire_rate=0.2, damage=3, ammo=float('inf'))
        self.range = 40  # Melee range
    
    def create_projectile(self, position, direction, shooter):
        """Hammer doesn't create projectiles, it does melee damage directly"""
        # In a real implementation, this would check for nearby enemies
        # and apply damage directly
        return None
    
    def get_attack_area(self, position, direction):
        """Get the area affected by the hammer swing"""
        # Calculate attack area based on position and direction
        attack_pos = position + direction.normalize() * (self.range / 2)
        return attack_pos, self.range / 2


class Gun(Weapon):
    """Standard gun weapon - creates bullets"""
    def __init__(self):
        super().__init__("gun", fire_rate=0.15, damage=1, ammo=10, reload_time=2.0)
        self.bullet_speed = 700
        self.bullet_lifetime = 2.0  # seconds
    
    def create_projectile(self, position, direction, shooter):
        """Create a bullet projectile"""
        return Bullet(
            position=position,
            velocity=direction.normalize() * self.bullet_speed,
            damage=self.damage,
            lifetime=self.bullet_lifetime,
            owner=shooter
        )


class Shotgun(Weapon):
    """Shotgun weapon - fires multiple pellets"""
    def __init__(self):
        super().__init__("shotgun", fire_rate=0.7, damage=1, ammo=5, reload_time=2.5)
        self.bullet_speed = 600
        self.spread_angle = 0.2  # Radians
        self.pellet_count = 8
        self.bullet_lifetime = 1.5
    
    def create_projectile(self, position, direction, shooter):
        """Create multiple bullet projectiles"""
        projectiles = []
        for i in range(self.pellet_count):
            # Calculate spread angle for this pellet
            angle_offset = self.spread_angle * (i - self.pellet_count/2) / (self.pellet_count/2)
            spread_direction = direction.rotate(angle_offset)
            
            bullet = Bullet(
                position=position,
                velocity=spread_direction.normalize() * self.bullet_speed,
                damage=self.damage,
                lifetime=self.bullet_lifetime,
                owner=shooter
            )
            projectiles.append(bullet)
        
        return projectiles


class Grenade(Weapon):
    """Grenade weapon - throws explosive projectiles"""
    def __init__(self):
        super().__init__("grenade", fire_rate=0.5, damage=5, ammo=3, reload_time=3.0)
        self.throw_speed = 500
        self.explosion_radius = 100
        self.explosion_delay = 2.0  # Time before explosion
    
    def create_projectile(self, position, direction, shooter):
        """Create a grenade projectile"""
        return GrenadeProjectile(
            position=position,
            velocity=direction.normalize() * self.throw_speed,
            damage=self.damage,
            explosion_radius=self.explosion_radius,
            explosion_delay=self.explosion_delay,
            owner=shooter
        )


class Rifle(Weapon):
    """Rifle weapon - high damage, accurate"""
    def __init__(self):
        super().__init__("rifle", fire_rate=0.8, damage=4, ammo=10, reload_time=2.5)
        self.bullet_speed = 1200
        self.bullet_lifetime = 3.0
    
    def create_projectile(self, position, direction, shooter):
        """Create a rifle bullet"""
        return Bullet(
            position=position,
            velocity=direction.normalize() * self.bullet_speed,
            damage=self.damage,
            lifetime=self.bullet_lifetime,
            owner=shooter,
            is_rifle=True
        )


class Projectile:
    """Base projectile class"""
    def __init__(self, position, velocity, damage, lifetime, owner=None):
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.damage = damage
        self.lifetime = lifetime
        self.age = 0
        self.owner = owner
        self.should_remove = False
        self.has_collided = False
    
    def update(self, dt, collision_world=None):
        """Update projectile position and state"""
        if self.should_remove:
            return
            
        self.age += dt
        if self.age >= self.lifetime:
            self.should_remove = True
            return
            
        # Move projectile
        old_pos = self.position.copy()
        self.position = self.position + self.velocity * dt
        
        # Check collision with world
        if collision_world and collision_world.collide_point(self.position):
            self.has_collided = True
            self.should_remove = True
            # In a real implementation, this might create an explosion or effect
    
    def check_collision(self, other_entity):
        """Check collision with another entity"""
        # To be implemented by subclasses based on their collision requirements
        pass


class Bullet(Projectile):
    """Bullet projectile"""
    def __init__(self, position, velocity, damage, lifetime, owner=None, is_rifle=False):
        super().__init__(position, velocity, damage, lifetime, owner)
        self.is_rifle = is_rifle
        self.radius = 2 if not is_rifle else 1  # Rifle bullets are smaller
    
    def check_collision(self, entity):
        """Check collision with an entity"""
        if not hasattr(entity, 'get_position'):
            return False
            
        distance = self.position.distance(entity.get_position())
        # This is a simplified collision check - real implementation would use proper collision boxes
        return distance < 15  # Approximate player radius


class GrenadeProjectile(Projectile):
    """Grenade projectile that explodes after a delay"""
    def __init__(self, position, velocity, damage, explosion_radius, explosion_delay, owner=None):
        super().__init__(position, velocity, damage, explosion_delay, owner)
        self.explosion_radius = explosion_radius
        self.has_exploded = False
        self.gravity = Vec2(0, 400)  # Apply gravity to grenades
        self.bounce_factor = 0.4  # How much velocity is retained after bouncing
    
    def update(self, dt, collision_world=None):
        """Update grenade position and state"""
        if self.should_remove:
            return
            
        # Apply gravity
        self.velocity = self.velocity + self.gravity * dt
        
        # Store old position for bounce detection
        old_pos = self.position.copy()
        self.position = self.position + self.velocity * dt
        
        # Check collision with world
        if collision_world and collision_world.collide_point(self.position):
            # Simple bounce physics
            self.velocity.x *= -self.bounce_factor
            self.velocity.y *= -self.bounce_factor * 0.7  # Lose more energy vertically
            self.position = old_pos  # Move back to prevent going through walls
            
            # If velocity is very low, stop bouncing
            if self.velocity.length() < 50:
                self.velocity = Vec2(0, 0)
        
        # Check if explosion time has been reached
        self.age += dt
        if self.age >= self.lifetime:
            self.explode()
    
    def explode(self):
        """Explode the grenade"""
        self.has_exploded = True
        self.should_remove = True
        # In a real implementation, this would damage nearby entities


class WeaponManager:
    """Manages all weapons in the game"""
    def __init__(self):
        self.weapons = {
            'hammer': Hammer(),
            'gun': Gun(),
            'shotgun': Shotgun(),
            'grenade': Grenade(),
            'rifle': Rifle()
        }
        self.projectiles = []
    
    def get_weapon(self, weapon_name):
        """Get a weapon instance by name"""
        if weapon_name in self.weapons:
            # Return a copy so each player gets their own instance
            weapon_class = self.weapons[weapon_name].__class__
            return weapon_class()
        return None
    
    def update_projectiles(self, dt, collision_world=None):
        """Update all projectiles"""
        for projectile in self.projectiles[:]:  # Copy list to avoid modification during iteration
            projectile.update(dt, collision_world)
            
            # Remove projectiles that should be removed
            if projectile.should_remove:
                self.projectiles.remove(projectile)
    
    def add_projectile(self, projectile):
        """Add a projectile to the manager"""
        self.projectiles.append(projectile)
    
    def get_projectiles_in_radius(self, center_pos, radius):
        """Get all projectiles within a radius"""
        nearby_projectiles = []
        for projectile in self.projectiles:
            if projectile.position.distance(center_pos) <= radius:
                nearby_projectiles.append(projectile)
        return nearby_projectiles


# Example usage and testing
if __name__ == "__main__":
    from ..base.collision import CollisionWorld, TileMap
    
    # Create a weapon manager
    weapon_manager = WeaponManager()
    
    # Test creating and firing a gun
    player_pos = Vec2(100, 100)
    target_dir = Vec2(1, 0)  # Shooting to the right
    
    # Create a gun instance for a player
    player_gun = weapon_manager.get_weapon('gun')
    
    # Fire the gun
    import time
    current_time = time.time()
    projectile = player_gun.fire(current_time, player_pos, target_dir)
    
    if projectile:
        print(f"Fired projectile at {projectile.position}, velocity: {projectile.velocity}")
        weapon_manager.add_projectile(projectile)
    
    # Test shotgun
    player_shotgun = weapon_manager.get_weapon('shotgun')
    projectiles = player_shotgun.fire(current_time + 1, player_pos, target_dir)
    
    if projectiles:
        print(f"Shotgun fired {len(projectiles)} pellets")
        # This is wrong - fixing:
    
    # Actually add shotgun projectiles correctly
    if projectiles and isinstance(projectiles, list):
        for proj in projectiles:
            weapon_manager.add_projectile(proj)
    
    print(f"Total projectiles in world: {len(weapon_manager.projectiles)}")
    
    # Create a simple collision world for testing
    collision_world = CollisionWorld()
    
    # Update projectiles
    weapon_manager.update_projectiles(0.016, collision_world)  # ~60 FPS
    print(f"Projectiles after update: {len(weapon_manager.projectiles)}")