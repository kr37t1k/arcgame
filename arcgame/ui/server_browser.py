"""
DDNet Server Browser - LAN/Internet server list
"""
import pygame
import socket
import struct
import time
from typing import List, Dict, Optional
from ..server.master_server import MasterClient


class ServerInfo:
    """Information about a server"""
    def __init__(self, address: str, port: int, name: str = "", 
                 game_type: str = "", map_name: str = "", 
                 players: int = 0, max_players: int = 0):
        self.address = address
        self.port = port
        self.name = name
        self.game_type = game_type
        self.map_name = map_name
        self.players = players
        self.max_players = max_players
        self.ping = 0
        self.last_update = time.time()
    
    def get_player_ratio(self) -> float:
        """Get ratio of players to max players"""
        if self.max_players == 0:
            return 0.0
        return self.players / self.max_players


class ServerBrowser:
    """Server browser UI component"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.servers: List[ServerInfo] = []
        self.filtered_servers: List[ServerInfo] = []
        self.selected_index = 0
        self.refresh_time = 0
        self.refresh_interval = 30  # Refresh every 30 seconds
        self.search_text = ""
        self.filter_gametype = "all"  # "all", "dm", "ctf", "race", "ddrace"
        
        # UI elements
        self.font = None
        self.small_font = None
        self.title_font = None
        
        # Initialize pygame fonts when needed
        self._initialized = False
        
        # Master server client
        self.master_client = MasterClient()
    
    def initialize(self):
        """Initialize the server browser"""
        if not self._initialized:
            pygame.font.init()
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 36)
            self._initialized = True
    
    def refresh_servers(self):
        """Refresh the server list from master server"""
        self.initialize()
        
        # Query master server for internet servers
        internet_servers = self.master_client.query_servers()
        
        # Add internet servers to our list
        for server_data in internet_servers:
            server_info = ServerInfo(
                address=server_data.get('address', 'unknown'),
                port=server_data.get('port', 8303),
                name=server_data.get('name', 'Unknown Server'),
                game_type=server_data.get('gametype', 'DM'),
                map_name=server_data.get('map', 'unknown'),
                players=server_data.get('players', 0),
                max_players=server_data.get('max_players', 16)
            )
            # Ping the server to get response time
            server_info.ping = self._ping_server(server_info.address, server_info.port)
            self.servers.append(server_info)
        
        # Add LAN servers (simplified discovery)
        self._discover_lan_servers()
        
        # Apply filters
        self._apply_filters()
        self.refresh_time = time.time()
    
    def _discover_lan_servers(self):
        """Discover servers on local network"""
        # This is a simplified LAN discovery
        # In a real implementation, we would broadcast a discovery packet
        pass
    
    def _ping_server(self, address: str, port: int) -> int:
        """Ping a server to get response time"""
        try:
            start_time = time.time()
            # Create a UDP socket and send a simple ping packet
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)  # 2 second timeout
            
            # Send a simple ping packet (in real DDNet this would be a specific packet)
            ping_packet = b'ping'
            sock.sendto(ping_packet, (address, port))
            
            # Try to receive response
            data, server = sock.recvfrom(1024)
            response_time = int((time.time() - start_time) * 1000)  # Convert to ms
            sock.close()
            return response_time
        except:
            return 999  # High ping indicates server is not responding
    
    def _apply_filters(self):
        """Apply current filters to the server list"""
        self.filtered_servers = self.servers.copy()
        
        # Apply search filter
        if self.search_text:
            search_lower = self.search_text.lower()
            self.filtered_servers = [
                s for s in self.filtered_servers
                if search_lower in s.name.lower() or search_lower in s.map_name.lower()
            ]
        
        # Apply game type filter
        if self.filter_gametype != "all":
            self.filtered_servers = [
                s for s in self.filtered_servers
                if s.game_type.lower() == self.filter_gametype.lower()
            ]
        
        # Sort by ping (responsive servers first), then by player count (full servers last)
        self.filtered_servers.sort(key=lambda s: (s.ping, -s.get_player_ratio()))
    
    def set_search_text(self, text: str):
        """Set search text for filtering servers"""
        self.search_text = text
        self._apply_filters()
    
    def set_gametype_filter(self, gametype: str):
        """Set game type filter"""
        self.filter_gametype = gametype
        self._apply_filters()
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events, return server address:port if selected"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.filtered_servers) - 1, self.selected_index + 1)
            elif event.key == pygame.K_PAGEUP:
                self.selected_index = max(0, self.selected_index - 10)
            elif event.key == pygame.K_PAGEDOWN:
                self.selected_index = min(len(self.filtered_servers) - 1, self.selected_index + 10)
            elif event.key == pygame.K_RETURN and self.filtered_servers:
                selected_server = self.filtered_servers[self.selected_index]
                return f"{selected_server.address}:{selected_server.port}"
            elif event.key == pygame.K_F5:  # Refresh
                self.refresh_servers()
            elif event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
                self._apply_filters()
            elif event.key == pygame.K_ESCAPE:
                return None  # Cancel
            elif event.unicode.isprintable():
                self.search_text += event.unicode
                self._apply_filters()
        
        return None
    
    def handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """Handle mouse clicks on UI elements"""
        # Check if click is on a server in the list
        start_y = 120
        item_height = 30
        visible_items = min(15, len(self.filtered_servers))
        
        for i in range(visible_items):
            idx = self.selected_index // visible_items * visible_items + i
            if idx >= len(self.filtered_servers):
                break
                
            y_pos = start_y + i * item_height
            item_rect = pygame.Rect(20, y_pos, self.screen_width - 40, item_height)
            
            if item_rect.collidepoint(pos):
                self.selected_index = idx
                selected_server = self.filtered_servers[idx]
                return f"{selected_server.address}:{selected_server.port}"
        
        return None
    
    def draw(self, surface: pygame.Surface):
        """Draw the server browser UI"""
        self.initialize()
        
        # Clear the surface
        surface.fill((30, 30, 50))  # Dark blue background
        
        # Draw title
        title_text = self.title_font.render("Server Browser", True, (255, 255, 255))
        surface.blit(title_text, (20, 20))
        
        # Draw search box
        search_label = self.font.render("Search:", True, (200, 200, 200))
        surface.blit(search_label, (20, 70))
        
        search_bg = pygame.Rect(100, 70, 300, 30)
        pygame.draw.rect(surface, (50, 50, 70), search_bg)
        pygame.draw.rect(surface, (100, 100, 150), search_bg, 2)
        
        search_text = self.font.render(self.search_text, True, (255, 255, 255))
        surface.blit(search_text, (105, 75))
        
        # Draw game type filter
        filter_label = self.font.render("Game Type:", True, (200, 200, 200))
        surface.blit(filter_label, (420, 70))
        
        filter_options = ["All", "DM", "CTF", "Race", "DDRace"]
        for i, option in enumerate(filter_options):
            rect = pygame.Rect(520 + i * 80, 70, 70, 30)
            color = (100, 100, 150) if self.filter_gametype.lower() != option.lower() and option != "All" else (150, 150, 200)
            if option == "All" and self.filter_gametype == "all":
                color = (150, 150, 200)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (200, 200, 255), rect, 2)
            
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        
        # Draw refresh button
        refresh_rect = pygame.Rect(self.screen_width - 120, 70, 100, 30)
        pygame.draw.rect(surface, (70, 130, 70), refresh_rect)
        pygame.draw.rect(surface, (100, 200, 100), refresh_rect, 2)
        refresh_text = self.font.render("Refresh", True, (255, 255, 255))
        text_rect = refresh_text.get_rect(center=refresh_rect.center)
        surface.blit(refresh_text, text_rect)
        
        # Draw server list
        start_y = 120
        item_height = 30
        visible_items = min(15, len(self.filtered_servers))
        
        for i in range(visible_items):
            idx = self.selected_index // visible_items * visible_items + i
            if idx >= len(self.filtered_servers):
                break
                
            server = self.filtered_servers[idx]
            
            # Calculate position
            y_pos = start_y + i * item_height
            
            # Highlight selected item
            if idx == self.selected_index:
                highlight_rect = pygame.Rect(20, y_pos, self.screen_width - 40, item_height)
                pygame.draw.rect(surface, (70, 70, 120), highlight_rect)
            
            # Draw server name
            name_text = self.font.render(server.name, True, (255, 255, 255))
            surface.blit(name_text, (30, y_pos + 5))
            
            # Draw game type
            gametype_text = self.font.render(server.game_type, True, (150, 150, 255))
            surface.blit(gametype_text, (250, y_pos + 5))
            
            # Draw map name
            map_text = self.font.render(server.map_name, True, (200, 200, 200))
            surface.blit(map_text, (350, y_pos + 5))
            
            # Draw player count
            player_text = self.font.render(f"{server.players}/{server.max_players}", True, (180, 180, 180))
            surface.blit(player_text, (550, y_pos + 5))
            
            # Draw ping
            ping_color = (100, 255, 100) if server.ping < 100 else (255, 255, 100) if server.ping < 200 else (255, 100, 100)
            ping_text = self.font.render(f"{server.ping}ms", True, ping_color)
            surface.blit(ping_text, (680, y_pos + 5))
        
        # Draw scrollbar if needed
        if len(self.filtered_servers) > visible_items:
            scrollbar_height = (visible_items / len(self.filtered_servers)) * (visible_items * item_height)
            scrollbar_pos = ((self.selected_index / len(self.filtered_servers)) * 
                           (visible_items * item_height))
            scrollbar_rect = pygame.Rect(
                self.screen_width - 30, 
                start_y + scrollbar_pos, 
                10, 
                max(20, scrollbar_height)
            )
            pygame.draw.rect(surface, (100, 100, 150), scrollbar_rect)
        
        # Draw status info
        status_text = self.small_font.render(
            f"Servers: {len(self.filtered_servers)} | Selected: {self.selected_index + 1}",
            True, (200, 200, 200)
        )
        surface.blit(status_text, (20, self.screen_height - 30))
        
        # Draw instructions
        instructions = self.small_font.render(
            "UP/DOWN: Navigate | ENTER: Join | F5: Refresh | ESC: Back",
            True, (180, 180, 180)
        )
        surface.blit(instructions, (self.screen_width // 2 - instructions.get_width() // 2, self.screen_height - 60))
    
    def join_server(self, server_address: str) -> bool:
        """Attempt to join a server"""
        # This would connect to the game server
        # For now, just return True to simulate successful connection
        print(f"Attempting to join server: {server_address}")
        return True


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("DDNet Server Browser")
    
    browser = ServerBrowser(1024, 768)
    
    # Initial server refresh
    browser.refresh_servers()
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = browser.handle_input(event)
                if result:
                    print(f"Selected server: {result}")
                    # In a real implementation, this would connect to the server
        
        browser.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()