"""Client for the DDNet clone - handles input, rendering, and game state"""
import pygame
import sys
from .base.vec2 import Vec2
from .engine.graphics import Renderer, MapLoader
from .game.entities.player import Player, EntityManager
from .base.collision import CollisionWorld
from .game.physics import PhysicsWorld


class GameClient:
    """Main client class that handles the game client-side logic"""
    def __init__(self):
        self.renderer = Renderer(1024, 768)
        self.entity_manager = EntityManager()
        self.physics_world = PhysicsWorld()
        
        # Game state
        self.running = True
        self.dt = 1.0/60.0  # Delta time for updates (60 FPS)
        
        # Input state
        self.keys_pressed = {}
        self.mouse_pos = (0, 0)
        
        # Network simulation (will be expanded later)
        self.network_connected = False
        self.server_address = None
        
        # Load assets
        self.load_assets()
        
        # Create test level
        self.setup_level()
        
        # Create local player
        self.local_player_id = 1
        self.local_player = Player(self.local_player_id, "LocalPlayer", pos=self.spawn_points[0] if self.spawn_points else Vec2(100, 100))
        self.entity_manager.add_player(self.local_player)
        self.physics_world.add_character(self.local_player.physics)
    
    def load_assets(self):
        """Load game assets"""
        # Create simple sprites for testing
        self.renderer.create_simple_sprite('player', 20, 20, 'red')
        self.renderer.create_simple_sprite('enemy', 20, 20, 'blue')
        self.renderer.create_simple_sprite('bullet', 5, 5, 'yellow')
        self.renderer.create_simple_sprite('hook', 3, 3, 'white')
    
    def setup_level(self):
        """Setup the game level"""
        # Create a test map
        self.game_map = MapLoader.create_test_map(30, 20)
        self.physics_world.add_collision_map(self.game_map)
        
        # Define spawn points
        self.spawn_points = [
            Vec2(100, 300),
            Vec2(200, 300),
            Vec2(300, 300)
        ]
        
        # Add some test enemies
        enemy1 = Player(2, "Enemy1", pos=Vec2(400, 300))
        enemy1.team = 1  # Blue team
        self.entity_manager.add_player(enemy1)
        self.physics_world.add_character(enemy1.physics)
        
        enemy2 = Player(3, "Enemy2", pos=Vec2(500, 300))
        enemy2.team = 1  # Blue team
        self.entity_manager.add_player(enemy2)
        self.physics_world.add_character(enemy2.physics)
    
    def handle_input(self):
        """Handle user input"""
        # Get current keyboard state
        keys = pygame.key.get_pressed()
        
        # Process continuous input for the local player
        input_state = {
            'left': bool(keys[pygame.K_LEFT] or keys[pygame.K_a]),
            'right': bool(keys[pygame.K_RIGHT] or keys[pygame.K_d]),
            'up': bool(keys[pygame.K_UP] or keys[pygame.K_w]),
            'down': bool(keys[pygame.K_DOWN] or keys[pygame.K_s]),
            'jump': bool(keys[pygame.K_SPACE]),
            'fire': bool(keys[pygame.K_x]),  # Fire button
            'hook': bool(keys[pygame.K_LSHIFT])  # Hook button
        }
        
        # Apply input to local player
        self.local_player.set_input(input_state)
        
        # Check for discrete key presses (events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_1:
                    self.local_player.switch_weapon('hammer')
                elif event.key == pygame.K_2:
                    self.local_player.switch_weapon('gun')
                elif event.key == pygame.K_3:
                    self.local_player.switch_weapon('shotgun')
                elif event.key == pygame.K_4:
                    self.local_player.switch_weapon('grenade')
                elif event.key == pygame.K_5:
                    self.local_player.switch_weapon('rifle')
                elif event.key == pygame.K_r:
                    # Respawn if dead
                    if not self.local_player.is_alive:
                        self.local_player.respawn(self.spawn_points[0])
                elif event.key == pygame.K_t:
                    # Toggle team (for testing)
                    self.local_player.team = 1 - self.local_player.team
    
    def update(self):
        """Update game state"""
        # Update all entities
        self.entity_manager.update_all(self.dt)
        
        # Update physics world
        self.physics_world.update(self.dt)
        
        # Update renderer camera to follow local player
        self.renderer.set_camera_target(self.local_player.get_position(), 0.1)
    
    def render(self):
        """Render the game"""
        # Clear screen
        self.renderer.clear('light_gray')
        
        # Draw map
        self.renderer.draw_map(self.game_map)
        
        # Draw all players
        for player in self.entity_manager.players.values():
            pos = player.get_position()
            
            # Draw player based on team
            color = 'red' if player.team == 0 else 'blue' if player.team == 1 else 'white'
            self.renderer.draw_sprite('player', pos, scale=1.0)
            
            # Draw health bar above player
            health_ratio = player.health / player.max_health
            bar_width = 25
            bar_height = 4
            bar_pos = Vec2(pos.x - bar_width/2, pos.y - 20)
            self.renderer.draw_rect(bar_pos, Vec2(bar_width, bar_height), 'dark_gray', filled=True)
            self.renderer.draw_rect(bar_pos, Vec2(bar_width * health_ratio, bar_height), 'green', filled=True)
            
            # Draw player name
            self.renderer.draw_text(player.name, Vec2(pos.x, pos.y - 35), 'white', 16)
            
            # Draw hook if active
            if player.physics.hook_state != 'IDLE':
                hook_color = 'yellow' if player.physics.hook_state == 'FLYING' else 'orange'
                self.renderer.draw_line(pos, player.physics.hook_pos, hook_color, 1)
                self.renderer.draw_sprite('hook', player.physics.hook_pos, scale=0.5)
        
        # Draw HUD
        self.renderer.draw_text(f"Score: {self.local_player.score}", Vec2(-400, -300), 'white', 24)
        self.renderer.draw_text(f"Weapon: {self.local_player.active_weapon.title()}", Vec2(-400, -270), 'white', 24)
        self.renderer.draw_text(f"Ammo: {self.local_player.ammo_counts[self.local_player.active_weapon]}", Vec2(-400, -240), 'white', 24)
        self.renderer.draw_text(f"Health: {self.local_player.health}/{self.local_player.max_health}", Vec2(-400, -210), 'white', 24)
        self.renderer.draw_text("WASD/Arrows: Move | Space: Jump | Shift: Hook", Vec2(-400, 320), 'white', 18)
        self.renderer.draw_text("1-5: Weapons | R: Respawn | T: Team | ESC: Quit", Vec2(-400, 350), 'white', 18)
        
        # Present frame
        self.renderer.present()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running and self.renderer.handle_events():
            # Handle input
            self.handle_input()
            
            # Update game state
            self.update()
            
            # Render frame
            self.render()
            
            # Control frame rate
            clock.tick(60)
        
        # Cleanup
        self.renderer.cleanup()


def main():
    """Main entry point"""
    print("Starting ArcGame Client...")
    print("Controls:")
    print("  WASD or Arrow Keys: Move")
    print("  Space: Jump")
    print("  Left Shift: Hook")
    print("  1-5: Switch weapons")
    print("  R: Respawn if dead")
    print("  T: Toggle team")
    print("  ESC: Quit")
    print()
    
    try:
        client = GameClient()
        client.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("Game exited successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())