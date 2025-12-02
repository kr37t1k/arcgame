"""
DDNet Clone - Version 0.1
A Python implementation of DDNet (Teeworlds-based platformer) using Arcade
"""

import arcade
import math
import pymunk
import time
from version import __version__

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = f"DDNet Clone v{__version__}"

# Player constants
PLAYER_JUMP_FORCE = 12000
PLAYER_MOVE_FORCE = 8000
PLAYER_FRICTION = 0.8
PLAYER_DAMPING = 0.95
PLAYER_RADIUS = 12
PLAYER_MASS = 10

# Physics constants
GRAVITY = (0, -1000)

class Player(arcade.Sprite):
    """Player character with physics"""
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = PLAYER_RADIUS * 2
        self.height = PLAYER_RADIUS * 2
        self.color = arcade.color.BLUE
        self.physics_body = None
        self.physics_shape = None
        
    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, PLAYER_RADIUS, self.color)
        # Draw a simple face
        arcade.draw_circle_filled(self.center_x - 4, self.center_y + 3, 2, arcade.color.BLACK)
        arcade.draw_circle_filled(self.center_x + 4, self.center_y + 3, 2, arcade.color.BLACK)
        arcade.draw_arc_outline(self.center_x, self.center_y - 2, 8, 4, arcade.color.BLACK, 0, 180, 2)

class PhysicsSprite:
    """A sprite that integrates with pymunk physics"""
    def __init__(self, sprite, body, shape):
        self.sprite = sprite
        self.body = body
        self.shape = shape

class Game(arcade.Window):
    """Main game class"""
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Sprite lists
        self.player_list = None
        self.wall_list = None
        self.death_list = None
        self.teleporter_list = None
        
        # Physics
        self.space = None
        
        # Player
        self.player_sprite = None
        self.physics_player = None
        
        # Camera
        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()
        
        # Input state
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        
    def setup(self):
        """Set up the game variables"""
        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.death_list = arcade.SpriteList()
        self.teleporter_list = arcade.SpriteList()
        
        # Set up physics engine
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        
        # Create player
        self.player_sprite = Player(100, 300)
        self.player_list.append(self.player_sprite)
        
        # Create player physics body
        moment = pymunk.moment_for_circle(PLAYER_MASS, 0, PLAYER_RADIUS)
        body = pymunk.Body(PLAYER_MASS, moment)
        body.position = self.player_sprite.center_x, self.player_sprite.center_y
        shape = pymunk.Circle(body, PLAYER_RADIUS)
        shape.friction = 0.7
        shape.collision_type = 1  # Player collision type
        self.space.add(body, shape)
        
        self.physics_player = PhysicsSprite(self.player_sprite, body, shape)
        
        # Create level - a simple platform layout similar to DDNet
        self.create_level()
        
        # Set up camera
        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()
    
    def create_level(self):
        """Create a simple DDNet-style level"""
        # Ground
        for x in range(0, SCREEN_WIDTH + 1, 64):
            self.add_wall(x, 32, 64, 64, arcade.color.GRAY)
        
        # Platforms
        self.add_wall(200, 200, 128, 32, arcade.color.BROWN)
        self.add_wall(400, 300, 128, 32, arcade.color.BROWN)
        self.add_wall(600, 200, 128, 32, arcade.color.BROWN)
        self.add_wall(800, 400, 128, 32, arcade.color.BROWN)
        
        # Some obstacles
        self.add_wall(300, 400, 32, 32, arcade.color.RED)
        self.add_wall(500, 500, 32, 32, arcade.color.RED)
        
        # Teleporter
        teleporter = arcade.SpriteSolidColor(40, 40, arcade.color.PURPLE)
        teleporter.center_x = 900
        teleporter.center_y = 450
        self.teleporter_list.append(teleporter)
        
        # Some more platforms for challenge
        self.add_wall(100, 450, 64, 32, arcade.color.BROWN)
        self.add_wall(180, 550, 64, 32, arcade.color.BROWN)
        self.add_wall(260, 600, 64, 32, arcade.color.BROWN)
    
    def add_wall(self, x, y, width, height, color):
        """Add a wall to the level with physics"""
        wall = arcade.SpriteSolidColor(width, height, color)
        wall.center_x = x
        wall.center_y = y
        self.wall_list.append(wall)
        
        # Add physics body for the wall
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = x, y
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.friction = 0.7
        shape.collision_type = 2  # Wall collision type
        self.space.add(body, shape)
    
    def on_draw(self):
        """Render the screen"""
        self.clear()
        
        # Draw with camera
        self.camera_sprites.use()
        
        # Draw all sprites
        self.wall_list.draw()
        self.death_list.draw()
        self.teleporter_list.draw()
        self.player_list.draw()
        
        # Draw physics debug (for development)
        # self.draw_physics()
    
    def draw_physics(self):
        """Draw physics shapes for debugging"""
        for shape in self.space.shapes:
            if isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                radius = shape.radius
                arcade.draw_circle_outline(pos.x, pos.y, radius, arcade.color.RED, 2)
            elif isinstance(shape, pymunk.Poly):
                points = [shape.body.local_to_world(v) for v in shape.get_vertices()]
                if len(points) > 1:
                    arcade.draw_polygon(points, arcade.color.RED, line_width=2)
    
    def update_player_speed(self):
        """Update player speed based on input"""
        body = self.physics_player.body
        
        # Apply friction
        body.velocity.x *= PLAYER_FRICTION
        
        # Apply movement forces
        if self.left_pressed and not self.right_pressed:
            body.apply_force_at_local_point((-PLAYER_MOVE_FORCE, 0))
        elif self.right_pressed and not self.left_pressed:
            body.apply_force_at_local_point((PLAYER_MOVE_FORCE, 0))
        
        # Jumping
        if self.up_pressed:
            # Check if player is on ground
            if self.is_player_on_ground():
                body.apply_impulse_at_local_point((0, PLAYER_JUMP_FORCE))
    
    def is_player_on_ground(self):
        """Check if player is touching the ground"""
        # Simple check: if player is close to ground or platform
        player_pos = self.physics_player.body.position
        for wall in self.wall_list:
            # Rough check if player is near a platform
            if (abs(player_pos.y - (wall.center_y + wall.height/2)) < 20 and 
                player_pos.x > wall.center_x - wall.width/2 and 
                player_pos.x < wall.center_x + wall.width/2):
                # Check if player is above the platform
                if player_pos.y < wall.center_y + wall.height/2 + 15:
                    return True
        return False
    
    def center_camera_to_player(self):
        """Move camera to follow player"""
        screen_center_x = self.physics_player.body.position.x - SCREEN_WIDTH / 2
        screen_center_y = self.physics_player.body.position.y - SCREEN_HEIGHT / 2
        
        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
            
        player_centered = screen_center_x, screen_center_y
        self.camera_sprites.position = player_centered
    
    def on_update(self, delta_time):
        """Movement and game logic"""
        # Update physics
        self.space.step(delta_time)
        
        # Update player position from physics
        self.player_sprite.center_x = self.physics_player.body.position.x
        self.player_sprite.center_y = self.physics_player.body.position.y
        
        # Update player speed based on input
        self.update_player_speed()
        
        # Keep player in bounds
        if self.physics_player.body.position.x < PLAYER_RADIUS:
            self.physics_player.body.position.x = PLAYER_RADIUS
        if self.physics_player.body.position.y < PLAYER_RADIUS:
            self.physics_player.body.position.y = PLAYER_RADIUS
            # Reset downward velocity if on ground
            self.physics_player.body.velocity.y = 0
        
        # Check for collisions with death tiles
        player_pos = self.physics_player.body.position
        for death in self.death_list:
            if (abs(player_pos.x - death.center_x) < death.width/2 + PLAYER_RADIUS and
                abs(player_pos.y - death.center_y) < death.height/2 + PLAYER_RADIUS):
                # Reset player position
                self.physics_player.body.position = (100, 300)
                self.physics_player.body.velocity = (0, 0)
        
        # Check for teleporter collision
        for teleporter in self.teleporter_list:
            if (abs(player_pos.x - teleporter.center_x) < teleporter.width/2 + PLAYER_RADIUS and
                abs(player_pos.y - teleporter.center_y) < teleporter.height/2 + PLAYER_RADIUS):
                # Teleport player to start
                self.physics_player.body.position = (100, 300)
                self.physics_player.body.velocity = (0, 0)
        
        # Center camera on player
        self.center_camera_to_player()
    
    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.up_pressed = True
    
    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.up_pressed = False

def main():
    """Main function"""
    window = Game()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()