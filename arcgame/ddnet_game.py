"""
Main DDNet game controller
Implements the complete DDNet game experience with physics, collision, and game entities
"""
from ursina import *
from base.collision import CollisionWorld
from game.map import DDNetMap
from game.entities.character import Character
from game.entities.projectile import Projectile
from base.vec2 import Vec2


class DDNetGame(Ursina):
    """Main DDNet game controller"""
    
    def __init__(self):
        super().__init__()
        
        # Game state
        self.running = True
        self.paused = False
        self.game_mode = "race"  # race, dm, tdm, ctf
        
        # Create game systems
        self.map = DDNetMap(width=100, height=75, tile_size=32)
        self.collision_world = self.map.collision_world
        
        # Create player character
        self.player = Character(position=(100, 500, 0), collision_world=self.collision_world)
        
        # Camera setup
        self.camera = camera
        self.camera_position = Vec2(self.player.position.x, self.player.position.y)
        
        # Game entities
        self.entities = [self.player]
        self.projectiles = []
        
        # Input handling
        self.setup_input()
        
        # Visual setup
        self.setup_visuals()
    
    def setup_input(self):
        """Setup game input handling"""
        # Player movement
        self.player_controls = {
            'left': 'a',
            'right': 'd',
            'jump': 'space',
            'hook': 'right mouse down',
            'shoot': 'left mouse down'
        }
        
        # Bind input events
        self.bind_inputs()
    
    def bind_inputs(self):
        """Bind input events to actions"""
        # Movement is handled in the character update
        # Jump handling
        def on_jump():
            if self.player.alive:
                self.player.jump()
        
        def on_shoot():
            if self.player.alive and mouse.world_point:
                self.player.fire_weapon()
        
        def on_hook():
            if self.player.alive and mouse.world_point:
                self.player.use_hook(mouse.world_point)
        
        # Since Ursina doesn't have an easy way to bind keys directly in this context,
        # we'll handle input in the update method
    
    def setup_visuals(self):
        """Setup visual elements"""
        # Set background color to match DDNet
        window.color = color.black
        
        # Set up camera
        self.camera.orthographic = True
        self.camera.fov = 20  # Adjust for 2D view
    
    def update(self):
        """Main game update loop"""
        if not self.running or self.paused:
            return
            
        # Handle input
        self.handle_input()
        
        # Update camera to follow player
        self.update_camera()
        
        # Update all entities
        for entity in self.entities[:]:  # Use slice to avoid modification during iteration
            if hasattr(entity, 'update'):
                entity.update()
        
        # Update projectiles
        for proj in self.projectiles[:]:
            if hasattr(proj, 'update'):
                proj.update()
            # Check collision with player (in a real game, check against all characters)
            if proj.check_collision_with_character(self.player):
                self.projectiles.remove(proj)
            elif not hasattr(proj, 'lifetime') or proj.lifetime <= 0:
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
    
    def handle_input(self):
        """Handle game input"""
        # Jump input
        if held_keys['space'] or held_keys['w'] or held_keys['up arrow']:
            self.player.jump()
        
        # Shooting input
        if mouse.left:
            if self.player.alive:
                self.player.fire_weapon()
        
        # Hook input
        if mouse.right and mouse.world_point:
            if self.player.alive:
                self.player.use_hook(mouse.world_point)
    
    def update_camera(self):
        """Update camera position to follow player"""
        # Smooth camera following
        target_x = self.player.position.x
        target_y = self.player.position.y
        
        # Apply smoothing
        self.camera_position.x = lerp(self.camera_position.x, target_x, time.dt * 5)
        self.camera_position.y = lerp(self.camera_position.y, target_y, time.dt * 5)
        
        # Update camera position
        self.camera.position = Vec3(self.camera_position.x, self.camera_position.y, -20)
    
    def spawn_projectile(self, position, velocity, weapon_type, owner=None):
        """Spawn a projectile in the game"""
        proj = Projectile(
            position=position,
            velocity=velocity,
            weapon_type=weapon_type,
            owner=owner,
            collision_world=self.collision_world
        )
        self.projectiles.append(proj)
        return proj
    
    def spawn_character(self, position, **kwargs):
        """Spawn a character in the game"""
        char = Character(
            position=position,
            collision_world=self.collision_world,
            **kwargs
        )
        self.entities.append(char)
        return char
    
    def run(self):
        """Start the game loop"""
        self.running = True
        self.run_app()
    
    def stop(self):
        """Stop the game"""
        self.running = False
        application.quit()


# Create a simple main function for running the game
def main():
    """Main function to run the DDNet game"""
    app = DDNetGame()
    app.run()


if __name__ == "__main__":
    main()