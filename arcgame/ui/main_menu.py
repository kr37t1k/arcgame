"""
DDNet Main Menu - Start/Join/Create/Options/Exit
"""
import pygame
from typing import Optional
from ..config.settings import settings
from ..map.map_browser import MapBrowser
from ..server.game_server import GameServer
from ..ui.server_browser import ServerBrowser


class MainMenu:
    """Main menu system for DDNet Pygame"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = None
        
        # Menu state
        self.running = True
        self.current_menu = "main"  # 'main', 'play', 'settings', 'map_browser', 'server_create'
        self.selected_option = 0
        
        # Sub-menus
        self.map_browser = None
        self.server_browser = None
        self.game_server = None
        
        # UI elements
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        # Initialize pygame fonts when screen is set
        self._initialized = False
    
    def initialize(self, screen):
        """Initialize menu with pygame screen"""
        self.screen = screen
        if not self._initialized:
            pygame.font.init()
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
            self._initialized = True
            
            # Initialize sub-components
            self.map_browser = MapBrowser(self.screen_width, self.screen_height)
            self.server_browser = ServerBrowser(self.screen_width, self.screen_height)
    
    def handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)
    
    def _handle_keydown(self, event):
        """Handle keyboard input"""
        if self.current_menu == "main":
            self._handle_main_menu_input(event)
        elif self.current_menu == "play":
            self._handle_play_menu_input(event)
        elif self.current_menu == "settings":
            self._handle_settings_menu_input(event)
        elif self.current_menu == "map_browser":
            result = self.map_browser.handle_input(event)
            if result:  # Map selected
                # Load the selected map and potentially start a local game
                pass
        elif self.current_menu == "server_create":
            self._handle_server_create_input(event)
    
    def _handle_main_menu_input(self, event):
        """Handle input for main menu"""
        if event.key == pygame.K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_option = min(4, self.selected_option + 1)
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Play
                self.current_menu = "play"
                self.selected_option = 0
            elif self.selected_option == 1:  # Settings
                self.current_menu = "settings"
                self.selected_option = 0
            elif self.selected_option == 2:  # Map Editor
                self.current_menu = "map_browser"
            elif self.selected_option == 3:  # Server Browser
                self.current_menu = "server_browser"
            elif self.selected_option == 4:  # Exit
                self.running = False
    
    def _handle_play_menu_input(self, event):
        """Handle input for play menu"""
        if event.key == pygame.K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_option = min(3, self.selected_option + 1)
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Start Local Game
                # Start a local game with default settings
                pass
            elif self.selected_option == 1:  # Create Server
                self.current_menu = "server_create"
            elif self.selected_option == 2:  # Join Server
                self.current_menu = "server_browser"
            elif self.selected_option == 3:  # Back
                self.current_menu = "main"
                self.selected_option = 0
        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
            self.selected_option = 0
    
    def _handle_settings_menu_input(self, event):
        """Handle input for settings menu"""
        if event.key == pygame.K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_option = min(4, self.selected_option + 1)
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Graphics
                # Switch to graphics settings
                pass
            elif self.selected_option == 1:  # Audio
                # Switch to audio settings
                pass
            elif self.selected_option == 2:  # Controls
                # Switch to controls settings
                pass
            elif self.selected_option == 3:  # Player Profile
                # Switch to player profile
                pass
            elif self.selected_option == 4:  # Back
                self.current_menu = "main"
                self.selected_option = 0
        elif event.key == pygame.K_ESCAPE:
            self.current_menu = "main"
            self.selected_option = 0
    
    def _handle_server_create_input(self, event):
        """Handle input for server creation menu"""
        if event.key == pygame.K_ESCAPE:
            self.current_menu = "play"
            self.selected_option = 1  # Return to 'Create Server' position
    
    def _handle_mouse_click(self, pos):
        """Handle mouse clicks"""
        if self.current_menu == "main":
            # Handle main menu button clicks
            button_height = 50
            start_y = self.screen_height // 2 - 50
            for i in range(5):
                button_rect = pygame.Rect(
                    self.screen_width // 2 - 100,
                    start_y + i * 60,
                    200,
                    button_height
                )
                if button_rect.collidepoint(pos):
                    self.selected_option = i
                    if i == 0:  # Play
                        self.current_menu = "play"
                        self.selected_option = 0
                    elif i == 1:  # Settings
                        self.current_menu = "settings"
                        self.selected_option = 0
                    elif i == 2:  # Map Editor
                        self.current_menu = "map_browser"
                    elif i == 3:  # Server Browser
                        self.current_menu = "server_browser"
                    elif i == 4:  # Exit
                        self.running = False
                    break
        elif self.current_menu == "map_browser":
            # Handle map browser clicks
            result = self.map_browser.handle_mouse_click(pos)
            if result:
                # Map selected, could start local game with this map
                pass
    
    def update(self, dt):
        """Update menu state"""
        if self.current_menu == "map_browser":
            # Update map browser if needed
            pass
        elif self.current_menu == "server_browser":
            # Update server browser
            pass
    
    def render(self):
        """Render the current menu"""
        self.screen.fill((30, 30, 50))  # Dark blue background
        
        if self.current_menu == "main":
            self._render_main_menu()
        elif self.current_menu == "play":
            self._render_play_menu()
        elif self.current_menu == "settings":
            self._render_settings_menu()
        elif self.current_menu == "map_browser":
            self.map_browser.draw(self.screen)
        elif self.current_menu == "server_browser":
            self.server_browser.draw(self.screen)
        elif self.current_menu == "server_create":
            self._render_server_create_menu()
        
        pygame.display.flip()
    
    def _render_main_menu(self):
        """Render the main menu"""
        # Title
        title = self.font_large.render("DDNet Pygame", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Menu options
        options = ["Play", "Settings", "Map Editor", "Server Browser", "Exit"]
        start_y = self.screen_height // 2 - 50
        
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            self.screen.blit(text, text_rect)
    
    def _render_play_menu(self):
        """Render the play menu"""
        # Title
        title = self.font_large.render("Play", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Menu options
        options = ["Start Local Game", "Create Server", "Join Server", "Back"]
        start_y = self.screen_height // 2 - 50
        
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 60))
            self.screen.blit(text, text_rect)
    
    def _render_settings_menu(self):
        """Render the settings menu"""
        # Title
        title = self.font_large.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Menu options
        options = ["Graphics", "Audio", "Controls", "Player Profile", "Back"]
        start_y = self.screen_height // 2 - 80
        
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_option else (200, 200, 200)
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, start_y + i * 50))
            self.screen.blit(text, text_rect)
    
    def _render_server_create_menu(self):
        """Render the server creation menu"""
        # Title
        title = self.font_large.render("Create Server", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Server settings
        y_pos = 200
        settings_text = [
            f"Server Name: {settings.get('sv_name', 'DDNet Server')}",
            f"Port: {settings.get('sv_port', 8303)}",
            f"Max Players: {settings.get('sv_max_clients', 16)}",
            f"Map: {settings.get('sv_map', 'dm1')}",
            "Press ESC to go back"
        ]
        
        for text in settings_text:
            rendered = self.font_small.render(text, True, (200, 200, 200))
            self.screen.blit(rendered, (self.screen_width // 2 - rendered.get_width() // 2, y_pos))
            y_pos += 40
        
        # Create button
        create_rect = pygame.Rect(self.screen_width // 2 - 75, y_pos, 150, 40)
        pygame.draw.rect(self.screen, (70, 130, 70), create_rect)
        pygame.draw.rect(self.screen, (100, 200, 100), create_rect, 2)
        create_text = self.font_medium.render("Create", True, (255, 255, 255))
        text_rect = create_text.get_rect(center=create_rect.center)
        self.screen.blit(create_text, text_rect)
    
    def run(self):
        """Main menu loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            
            events = pygame.event.get()
            self.handle_events(events)
            self.update(dt)
            self.render()
        
        return self.running  # Return whether to continue running the game


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("DDNet Pygame - Main Menu")
    
    menu = MainMenu(1024, 768)
    menu.initialize(screen)
    
    menu.run()
    
    pygame.quit()