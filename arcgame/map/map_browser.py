"""
DDNet Map Browser - UI for browsing and selecting maps
"""
import pygame
from typing import List, Optional
from .map_manager import MapManager, MapInfo


class MapBrowser:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_manager = MapManager()
        self.map_list = []
        self.filtered_list = []
        self.selected_index = 0
        self.search_text = ""
        self.filter_gametype = ""  # "all", "dm", "ctf", "race", "ddrace"
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        
        self.refresh_maps()
    
    def refresh_maps(self):
        """Scan all map directories and populate the list"""
        self.map_manager.scan_map_directories()
        self.map_list = self.map_manager.get_all_maps()
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply current filters to the map list"""
        self.filtered_list = self.map_list.copy()
        
        # Apply search filter
        if self.search_text:
            search_lower = self.search_text.lower()
            self.filtered_list = [
                m for m in self.filtered_list 
                if search_lower in m.name.lower() or search_lower in m.author.lower()
            ]
        
        # Apply gametype filter
        if self.filter_gametype and self.filter_gametype.lower() != "all":
            self.filtered_list = [
                m for m in self.filtered_list 
                if m.gametype.lower() == self.filter_gametype.lower()
            ]
        
        # Sort: official first, then by name
        self.filtered_list.sort(key=lambda m: (
            0 if m.path.startswith("arcgame/data/maps/official/") else
            1 if m.path.startswith("arcgame/data/maps/community/") else
            2 if m.path.startswith("arcgame/data/maps/downloaded/") else
            3,  # campaigns or others
            m.name.lower()
        ))
        
        # Adjust selection index if needed
        if self.selected_index >= len(self.filtered_list):
            self.selected_index = max(0, len(self.filtered_list) - 1)
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events and return selected map name if enter pressed"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.filtered_list) - 1, self.selected_index + 1)
            elif event.key == pygame.K_PAGEUP:
                self.selected_index = max(0, self.selected_index - 10)
            elif event.key == pygame.K_PAGEDOWN:
                self.selected_index = min(len(self.filtered_list) - 1, self.selected_index + 10)
            elif event.key == pygame.K_RETURN and self.filtered_list:
                return self.filtered_list[self.selected_index].name
            elif event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
                self._apply_filters()
            elif event.key == pygame.K_ESCAPE:
                return None  # Cancel
            elif event.unicode.isprintable():
                self.search_text += event.unicode
                self._apply_filters()
        
        return None
    
    def set_filter_gametype(self, gametype: str):
        """Set game type filter"""
        self.filter_gametype = gametype
        self._apply_filters()
    
    def set_search_text(self, text: str):
        """Set search text"""
        self.search_text = text
        self._apply_filters()
    
    def get_selected_map(self) -> Optional[MapInfo]:
        """Get currently selected map info"""
        if 0 <= self.selected_index < len(self.filtered_list):
            return self.filtered_list[self.selected_index]
        return None
    
    def draw(self, surface: pygame.Surface):
        """Draw the map browser UI"""
        # Clear the surface
        surface.fill((30, 30, 50))  # Dark blue background
        
        # Draw title
        title_text = self.title_font.render("Map Browser", True, (255, 255, 255))
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
        filter_rects = []
        for i, option in enumerate(filter_options):
            rect = pygame.Rect(520 + i * 80, 70, 70, 30)
            color = (100, 100, 150) if self.filter_gametype.lower() != option.lower() and option != "All" else (150, 150, 200)
            if option == "All" and not self.filter_gametype:
                color = (150, 150, 200)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (200, 200, 255), rect, 2)
            
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
            filter_rects.append((rect, option.lower()))
        
        # Draw map list
        start_y = 120
        item_height = 30
        visible_items = min(15, len(self.filtered_list))  # Show max 15 items
        
        for i in range(visible_items):
            idx = self.selected_index // visible_items * visible_items + i
            if idx >= len(self.filtered_list):
                break
                
            map_info = self.filtered_list[idx]
            
            # Calculate position
            y_pos = start_y + i * item_height
            
            # Highlight selected item
            if idx == self.selected_index:
                highlight_rect = pygame.Rect(20, y_pos, self.screen_width - 40, item_height)
                pygame.draw.rect(surface, (70, 70, 120), highlight_rect)
            
            # Determine color based on map source
            if map_info.path.startswith("arcgame/data/maps/official/"):
                color = (100, 255, 100)  # Green for official
            elif map_info.path.startswith("arcgame/data/maps/community/"):
                color = (255, 255, 100)  # Yellow for community
            elif map_info.path.startswith("arcgame/data/maps/downloaded/"):
                color = (100, 200, 255)  # Blue for downloaded
            else:
                color = (200, 200, 200)  # Gray for others
            
            # Draw map name
            name_text = self.font.render(f"{map_info.name}", True, color)
            surface.blit(name_text, (30, y_pos + 5))
            
            # Draw author
            author_text = self.font.render(f"by {map_info.author}", True, (180, 180, 180))
            surface.blit(author_text, (250, y_pos + 5))
            
            # Draw game type
            gametype_text = self.font.render(map_info.gametype, True, (150, 150, 255))
            surface.blit(gametype_text, (450, y_pos + 5))
            
            # Draw size
            size_text = self.font.render(f"{map_info.size[0]}x{map_info.size[1]}", True, (180, 180, 180))
            surface.blit(size_text, (550, y_pos + 5))
        
        # Draw scrollbar if needed
        if len(self.filtered_list) > visible_items:
            scrollbar_height = (visible_items / len(self.filtered_list)) * (visible_items * item_height)
            scrollbar_pos = ((self.selected_index / len(self.filtered_list)) * 
                           (visible_items * item_height))
            scrollbar_rect = pygame.Rect(
                self.screen_width - 30, 
                start_y + scrollbar_pos, 
                10, 
                max(20, scrollbar_height)
            )
            pygame.draw.rect(surface, (100, 100, 150), scrollbar_rect)
        
        # Draw status info
        status_text = self.font.render(
            f"Maps: {len(self.filtered_list)}/{len(self.map_list)} | Selected: {self.selected_index + 1}",
            True, (200, 200, 200)
        )
        surface.blit(status_text, (20, self.screen_height - 30))
    
    def handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """Handle mouse clicks on UI elements"""
        # Check if click is on a filter button
        filter_options = ["All", "DM", "CTF", "Race", "DDRace"]
        for i, option in enumerate(filter_options):
            rect = pygame.Rect(520 + i * 80, 70, 70, 30)
            if rect.collidepoint(pos):
                self.set_filter_gametype("" if option == "All" else option)
                return None
        
        # Check if click is on a map in the list
        start_y = 120
        item_height = 30
        visible_items = min(15, len(self.filtered_list))
        
        for i in range(visible_items):
            idx = self.selected_index // visible_items * visible_items + i
            if idx >= len(self.filtered_list):
                break
                
            y_pos = start_y + i * item_height
            item_rect = pygame.Rect(20, y_pos, self.screen_width - 40, item_height)
            
            if item_rect.collidepoint(pos):
                self.selected_index = idx
                return self.filtered_list[idx].name  # Return map name when clicked
        
        return None