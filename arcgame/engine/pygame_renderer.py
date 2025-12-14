"""Pygame renderer for DDNet implementation"""
import pygame
import math
from arcgame.base.vec2 import Vec2


class PygameRenderer:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("DDNet Pygame Implementation")
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        
        # Colors matching DDNet
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'gray': (128, 128, 128),
            'light_gray': (200, 200, 200),
            'dark_gray': (64, 64, 64),
            'sky_blue': (135, 206, 235),
            'ground_brown': (139, 69, 19)
        }
        
        # Create a simple sprite surface for the tee
        self.tee_surface = self.create_tee_sprite()
        
        # Create font for UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Camera
        self.camera_pos = Vec2(0, 0)
        self.target_camera_pos = Vec2(0, 0)
        
    def create_tee_sprite(self):
        """Create a simple tee sprite"""
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Body (circle)
        pygame.draw.circle(surface, (255, 255, 255), (16, 16), 12)
        
        # Eyes
        eye_offset = 4
        pygame.draw.circle(surface, (0, 0, 0), (16 - eye_offset, 14), 2)
        pygame.draw.circle(surface, (0, 0, 0), (16 + eye_offset, 14), 2)
        
        # Mouth (simple line)
        pygame.draw.line(surface, (0, 0, 0), (12, 20), (20, 20), 2)
        
        return surface
    
    def set_camera_target(self, target_pos):
        """Set the camera target position"""
        self.target_camera_pos = Vec2(target_pos.x - self.width // 2, target_pos.y - self.height // 2)
        
        # Clamp camera to reasonable bounds
        self.target_camera_pos.x = max(0, self.target_camera_pos.x)
        self.target_camera_pos.y = max(0, self.target_camera_pos.y)
    
    def update_camera(self, dt):
        """Smoothly update camera position"""
        # Simple interpolation for camera following
        smooth_factor = 0.1
        self.camera_pos.x += (self.target_camera_pos.x - self.camera_pos.x) * smooth_factor
        self.camera_pos.y += (self.target_camera_pos.y - self.camera_pos.y) * smooth_factor
    
    def world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        return (int(world_pos.x - self.camera_pos.x), int(world_pos.y - self.camera_pos.y))
    
    def screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates"""
        return Vec2(screen_pos.x + self.camera_pos.x, screen_pos.x + self.camera_pos.y)
    
    def render_world(self, world):
        """Render the game world"""
        # Fill background
        self.screen.fill(self.colors['sky_blue'])
        
        # Render tiles
        if world.tile_map:
            for y in range(world.height):
                for x in range(world.width):
                    if world.tiles[y][x] == 1:  # Solid tile
                        screen_x = x * world.tile_size - self.camera_pos.x
                        screen_y = y * world.tile_size - self.camera_pos.y
                        
                        # Only render if tile is visible
                        if (screen_x > -world.tile_size and screen_x < self.width and
                            screen_y > -world.tile_size and screen_y < self.height):
                            rect = pygame.Rect(screen_x, screen_y, world.tile_size, world.tile_size)
                            pygame.draw.rect(self.screen, self.colors['ground_brown'], rect)
                            pygame.draw.rect(self.screen, self.colors['dark_gray'], rect, 1)  # Border
    
    def render_character(self, character, name="Player"):
        """Render a character"""
        screen_pos = self.world_to_screen(character.m_Pos)
        
        # Draw tee sprite
        tee_rect = self.tee_surface.get_rect(center=(screen_pos[0], screen_pos[1] - 16))  # Offset for centering
        self.screen.blit(self.tee_surface, tee_rect)
        
        # Draw hook if active
        if character.m_HookState != 0:  # Not HOOK_IDLE
            hook_start = self.world_to_screen(character.m_Pos)
            hook_end = self.world_to_screen(character.m_HookPos)
            
            pygame.draw.line(self.screen, (200, 200, 0), hook_start, hook_end, 2)
        
        # Draw name tag
        name_surface = self.small_font.render(name, True, self.colors['white'])
        name_rect = name_surface.get_rect(center=(screen_pos[0], screen_pos[1] - 40))
        self.screen.blit(name_surface, name_rect)
        
        # Draw health bar (simplified)
        health_bar_width = 40
        health_bar_height = 6
        health_x = screen_pos[0] - health_bar_width // 2
        health_y = screen_pos[1] - 50
        
        pygame.draw.rect(self.screen, self.colors['red'], 
                        (health_x, health_y, health_bar_width, health_bar_height))
        pygame.draw.rect(self.screen, self.colors['green'], 
                        (health_x, health_y, health_bar_width * 0.8, health_bar_height))
    
    def render_ui(self, fps, player_pos):
        """Render UI elements"""
        # FPS counter
        fps_text = self.small_font.render(f"FPS: {int(fps)}", True, self.colors['white'])
        self.screen.blit(fps_text, (10, 10))
        
        # Position display
        pos_text = self.small_font.render(f"Pos: ({player_pos.x:.1f}, {player_pos.y:.1f})", True, self.colors['white'])
        self.screen.blit(pos_text, (10, 30))
        
        # Controls help
        controls = [
            "WASD: Move",
            "SPACE: Jump",
            "MOUSE: Aim",
            "LMB: Hook"
        ]
        
        for i, control in enumerate(controls):
            ctrl_surface = self.small_font.render(control, True, self.colors['white'])
            self.screen.blit(ctrl_surface, (self.width - 150, 10 + i * 20))
    
    def render(self, world, characters, dt):
        """Main render function"""
        # Update camera
        if characters and len(characters) > 0:
            self.set_camera_target(characters[0].m_Pos)  # Follow first character
        self.update_camera(dt)
        
        # Render world
        self.render_world(world)
        
        # Render characters
        for i, character in enumerate(characters):
            name = f"Player {i+1}"
            self.render_character(character, name)
        
        # Render UI
        fps = self.clock.get_fps()
        player_pos = characters[0].m_Pos if characters else Vec2(0, 0)
        self.render_ui(fps, player_pos)
        
        # Update display
        pygame.display.flip()
    
    def get_mouse_pos(self):
        """Get mouse position in world coordinates"""
        screen_pos = pygame.mouse.get_pos()
        return self.screen_to_world(screen_pos)
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()