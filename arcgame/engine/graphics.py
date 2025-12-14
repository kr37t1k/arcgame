"""Graphics rendering system for the DDNet clone using pygame"""
import pygame
import math
from ..base.vec2 import Vec2
from ..base.collision import TileMap


class Renderer:
    """Main renderer using pygame for 2D graphics"""
    def __init__(self, screen_width=1024, screen_height=768):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("ArcGame - DDNet Clone")
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        
        # Asset storage
        self.sprites = {}
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Camera
        self.camera_pos = Vec2(0, 0)
        self.zoom = 1.0
        
        # Colors (RGB tuples)
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
            'light_gray': (200, 200, 200),
            'dark_gray': (64, 64, 64)
        }
        
    def world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        rel_x = world_pos.x - self.camera_pos.x
        rel_y = world_pos.y - self.camera_pos.y
        return (
            int((rel_x * self.zoom) + self.screen_width // 2),
            int((rel_y * self.zoom) + self.screen_height // 2)
        )
    
    def screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates"""
        screen_x, screen_y = screen_pos
        world_x = (screen_x - self.screen_width // 2) / self.zoom + self.camera_pos.x
        world_y = (screen_y - self.screen_height // 2) / self.zoom + self.camera_pos.y
        return Vec2(world_x, world_y)
    
    def load_sprite(self, name, path_or_surface):
        """Load a sprite either from file path or directly as a surface"""
        if isinstance(path_or_surface, str):
            self.sprites[name] = pygame.image.load(path_or_surface).convert_alpha()
        else:
            self.sprites[name] = path_or_surface
    
    def create_simple_sprite(self, name, width, height, color='white'):
        """Create a simple colored rectangle sprite"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        color_rgb = self.colors[color]
        surface.fill(color_rgb)
        self.sprites[name] = surface
    
    def draw_sprite(self, name, pos, rotation=0, scale=1.0):
        """Draw a sprite at position with rotation and scale"""
        if name not in self.sprites:
            return
            
        sprite = self.sprites[name]
        
        # Scale sprite
        if scale != 1.0:
            new_size = (int(sprite.get_width() * scale), int(sprite.get_height() * scale))
            sprite = pygame.transform.scale(sprite, new_size)
        
        # Rotate sprite
        if rotation != 0:
            sprite = pygame.transform.rotate(sprite, math.degrees(rotation))
        
        # Convert position to screen coordinates
        screen_pos = self.world_to_screen(pos)
        # Adjust position for sprite center
        screen_pos = (screen_pos[0] - sprite.get_width() // 2, 
                      screen_pos[1] - sprite.get_height() // 2)
        
        self.screen.blit(sprite, screen_pos)
    
    def draw_circle(self, pos, radius, color='white', filled=True):
        """Draw a circle at world position"""
        screen_pos = self.world_to_screen(pos)
        color_rgb = self.colors[color]
        scaled_radius = int(radius * self.zoom)
        
        if filled:
            pygame.draw.circle(self.screen, color_rgb, screen_pos, scaled_radius)
        else:
            pygame.draw.circle(self.screen, color_rgb, screen_pos, scaled_radius, max(1, int(2 * self.zoom)))
    
    def draw_rect(self, pos, size, color='white', filled=True):
        """Draw a rectangle at world position"""
        screen_pos = self.world_to_screen(pos)
        screen_size = (int(size.x * self.zoom), int(size.y * self.zoom))
        
        # Adjust position for top-left corner
        screen_pos = (screen_pos[0] - screen_size[0] // 2, screen_pos[1] - screen_size[1] // 2)
        
        color_rgb = self.colors[color]
        rect = pygame.Rect(screen_pos, screen_size)
        
        if filled:
            pygame.draw.rect(self.screen, color_rgb, rect)
        else:
            pygame.draw.rect(self.screen, color_rgb, rect, max(1, int(2 * self.zoom)))
    
    def draw_line(self, start_pos, end_pos, color='white', width=1):
        """Draw a line between two world positions"""
        start_screen = self.world_to_screen(start_pos)
        end_screen = self.world_to_screen(end_pos)
        color_rgb = self.colors[color]
        pygame.draw.line(self.screen, color_rgb, start_screen, end_screen, max(1, int(width * self.zoom)))
    
    def draw_text(self, text, pos, color='white', font_size=None):
        """Draw text at world position"""
        screen_pos = self.world_to_screen(pos)
        color_rgb = self.colors[color]
        
        if font_size and font_size != self.font.get_height():
            font = pygame.font.Font(None, font_size)
        else:
            font = self.font
            
        text_surface = font.render(str(text), True, color_rgb)
        self.screen.blit(text_surface, screen_pos)
    
    def draw_map(self, tile_map, tile_colors=None):
        """Draw the tile map"""
        if tile_colors is None:
            tile_colors = {0: 'black', 1: 'gray'}  # 0 = empty, 1 = solid
        
        for y in range(tile_map.height):
            for x in range(tile_map.width):
                tile_value = tile_map.tiles[y][x]
                if tile_value in tile_colors:
                    pos = Vec2(x * tile_map.tile_size, y * tile_map.tile_size)
                    size = Vec2(tile_map.tile_size, tile_map.tile_size)
                    
                    # Only draw tiles that are visible in the camera view
                    screen_center = self.world_to_screen(Vec2(0, 0))
                    visible_area = pygame.Rect(
                        self.camera_pos.x - self.screen_width // (2 * self.zoom),
                        self.camera_pos.y - self.screen_height // (2 * self.zoom),
                        self.screen_width // self.zoom,
                        self.screen_height // self.zoom
                    )
                    
                    tile_rect = pygame.Rect(pos.x, pos.y, size.x, size.y)
                    if visible_area.colliderect(tile_rect):
                        self.draw_rect(pos, size, tile_colors[tile_value])
    
    def clear(self, color='black'):
        """Clear the screen with a color"""
        color_rgb = self.colors[color]
        self.screen.fill(color_rgb)
    
    def present(self):
        """Present the rendered frame"""
        pygame.display.flip()
        self.clock.tick(self.fps)
    
    def handle_events(self):
        """Handle pygame events and return True if still running"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        return self.running
    
    def get_mouse_pos(self):
        """Get mouse position in world coordinates"""
        screen_pos = pygame.mouse.get_pos()
        return self.screen_to_world(screen_pos)
    
    def get_keys_pressed(self):
        """Get currently pressed keys"""
        return pygame.key.get_pressed()
    
    def set_camera_target(self, target_pos, smooth_factor=0.1):
        """Smoothly move camera to follow a target position"""
        self.camera_pos = self.camera_pos + (target_pos - self.camera_pos) * smooth_factor
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()


class MapLoader:
    """Simple map loader for DDNet-style maps"""
    @staticmethod
    def create_test_map(width=20, height=15):
        """Create a simple test map"""
        tile_map = TileMap(width, height)
        
        # Create a simple layout
        # Ground at bottom
        for x in range(width):
            tile_map.set_tile(x * 32, (height - 1) * 32, 1)
        
        # Some platforms
        for x in range(5, 10):
            tile_map.set_tile(x * 32, 8 * 32, 1)
        
        for x in range(12, 17):
            tile_map.set_tile(x * 32, 6 * 32, 1)
        
        # Left wall
        for y in range(height - 1):
            tile_map.set_tile(0, y * 32, 1)
        
        # Right wall
        for y in range(height - 1):
            tile_map.set_tile((width - 1) * 32, y * 32, 1)
        
        return tile_map
    
    @staticmethod
    def load_from_file(file_path):
        """Load map from a file (placeholder for future implementation)"""
        # This would parse DDNet .map files
        # For now, just return a test map
        print(f"Loading map from {file_path} - using test map instead")
        return MapLoader.create_test_map()


# Example usage
if __name__ == "__main__":
    # Initialize renderer
    renderer = Renderer(1024, 768)
    
    # Create a test map
    map_loader = MapLoader()
    game_map = map_loader.create_test_map()
    
    # Create simple sprites
    renderer.create_simple_sprite('player', 20, 20, 'red')
    renderer.create_simple_sprite('hook', 5, 5, 'yellow')
    
    # Player position
    player_pos = Vec2(320, 320)
    player_vel = Vec2(0, 0)
    
    # Main loop
    while renderer.handle_events():
        # Clear screen
        renderer.clear('light_gray')
        
        # Draw map
        renderer.draw_map(game_map)
        
        # Simple movement for demo
        keys = renderer.get_keys_pressed()
        move_speed = 5
        if keys[pygame.K_LEFT]:
            player_vel.x = -move_speed
        elif keys[pygame.K_RIGHT]:
            player_vel.x = move_speed
        else:
            player_vel.x = 0
            
        if keys[pygame.K_UP]:
            player_vel.y = -move_speed
        elif keys[pygame.K_DOWN]:
            player_vel.y = move_speed
        else:
            player_vel.y = 0
        
        # Update player position
        player_pos = player_pos + player_vel
        
        # Set camera to follow player
        renderer.set_camera_target(player_pos)
        
        # Draw player
        renderer.draw_sprite('player', player_pos)
        
        # Draw some example text
        renderer.draw_text("ArcGame - DDNet Clone", Vec2(player_pos.x, player_pos.y - 100))
        
        # Present frame
        renderer.present()
    
    renderer.cleanup()