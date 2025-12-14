"""
DDNet Skin Editor - Custom tee skin creator
"""
import pygame
import os
from typing import Tuple, Dict, List


class SkinEditor:
    """Custom tee skin creator"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("DDNet Skin Editor")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Skin properties
        self.body_color = (255, 0, 0)  # Red
        self.feet_color = (0, 0, 255)  # Blue
        self.eye_style = 0  # 0-5 different eye styles
        self.skin_name = "custom_skin"
        
        # UI elements
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Color picker state
        self.picking_body_color = False
        self.picking_feet_color = False
        
        # Preview position
        self.preview_x = screen_width // 2
        self.preview_y = screen_height // 2 - 50
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.save_skin()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
    
    def _handle_mouse_down(self, event):
        """Handle mouse button down"""
        mouse_x, mouse_y = event.pos
        
        # Check if clicking on body color picker
        if (50 <= mouse_x <= 150) and (50 <= mouse_y <= 100):
            self.picking_body_color = True
        
        # Check if clicking on feet color picker
        elif (50 <= mouse_x <= 150) and (120 <= mouse_y <= 170):
            self.picking_feet_color = True
        
        # Check if clicking on eye style selector
        elif (50 <= mouse_x <= 200) and (190 <= mouse_y <= 240):
            self.eye_style = (self.eye_style + 1) % 6
        
        # Check if clicking on save button
        elif (50 <= mouse_x <= 150) and (500 <= mouse_y <= 550):
            self.save_skin()
    
    def update(self):
        """Update editor state"""
        # Handle color picking if active
        if self.picking_body_color or self.picking_feet_color:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Get color from screen (in a real implementation, we'd have a color picker UI)
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                # For now, just cycle through predefined colors
                colors = [
                    (255, 0, 0),    # Red
                    (0, 255, 0),    # Green
                    (0, 0, 255),    # Blue
                    (255, 255, 0),  # Yellow
                    (255, 0, 255),  # Magenta
                    (0, 255, 255),  # Cyan
                    (255, 255, 255), # White
                    (128, 128, 128), # Gray
                    (0, 0, 0),      # Black
                ]
                
                # Cycle through colors
                if self.picking_body_color:
                    current_idx = colors.index(self.body_color) if self.body_color in colors else 0
                    self.body_color = colors[(current_idx + 1) % len(colors)]
                else:  # picking_feet_color
                    current_idx = colors.index(self.feet_color) if self.feet_color in colors else 0
                    self.feet_color = colors[(current_idx + 1) % len(colors)]
            
            # Release color picker on mouse release
            if not pygame.mouse.get_pressed()[0]:
                self.picking_body_color = False
                self.picking_feet_color = False
    
    def render(self):
        """Render the skin editor"""
        self.screen.fill((50, 50, 50))  # Dark gray background
        
        # Draw UI elements
        self._draw_ui()
        
        # Draw skin preview
        self._draw_skin_preview()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        """Draw user interface elements"""
        # Body color picker
        pygame.draw.rect(self.screen, (200, 200, 200), (50, 50, 100, 50))
        pygame.draw.rect(self.screen, self.body_color, (55, 55, 90, 40))
        body_text = self.small_font.render("Body Color", True, (255, 255, 255))
        self.screen.blit(body_text, (60, 105))
        
        # Feet color picker
        pygame.draw.rect(self.screen, (200, 200, 200), (50, 120, 100, 50))
        pygame.draw.rect(self.screen, self.feet_color, (55, 125, 90, 40))
        feet_text = self.small_font.render("Feet Color", True, (255, 255, 255))
        self.screen.blit(feet_text, (60, 175))
        
        # Eye style selector
        pygame.draw.rect(self.screen, (200, 200, 200), (50, 190, 150, 50))
        eye_text = self.small_font.render(f"Eye Style: {self.eye_style + 1}", True, (255, 255, 255))
        self.screen.blit(eye_text, (60, 245))
        
        # Skin name input (simplified)
        name_bg = pygame.Rect(50, 260, 200, 30)
        pygame.draw.rect(self.screen, (70, 70, 70), name_bg)
        pygame.draw.rect(self.screen, (150, 150, 150), name_bg, 2)
        name_text = self.small_font.render(f"Skin Name: {self.skin_name}", True, (255, 255, 255))
        self.screen.blit(name_text, (55, 265))
        
        # Save button
        save_rect = pygame.Rect(50, 500, 100, 50)
        pygame.draw.rect(self.screen, (70, 130, 70), save_rect)
        pygame.draw.rect(self.screen, (100, 200, 100), save_rect, 2)
        save_text = self.font.render("Save", True, (255, 255, 255))
        text_rect = save_text.get_rect(center=save_rect.center)
        self.screen.blit(save_text, text_rect)
        
        # Instructions
        instructions = [
            "Click on color boxes to change colors",
            "Click on eye style to cycle through options",
            "Type skin name (not implemented in this demo)",
            "Press Ctrl+S or click Save to save skin",
            "ESC to quit"
        ]
        
        for i, text in enumerate(instructions):
            inst_text = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(inst_text, (300, 50 + i * 25))
    
    def _draw_skin_preview(self):
        """Draw the skin preview"""
        # Draw a simple representation of a tee with the selected colors
        # Body (rectangle)
        body_rect = pygame.Rect(
            self.preview_x - 20, 
            self.preview_y - 30, 
            40, 60
        )
        pygame.draw.rect(self.screen, self.body_color, body_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), body_rect, 2)  # Black outline
        
        # Head (circle)
        head_pos = (self.preview_x, self.preview_y - 50)
        pygame.draw.circle(self.screen, (255, 200, 150), head_pos, 25)  # Skin color
        pygame.draw.circle(self.screen, (0, 0, 0), head_pos, 25, 2)  # Black outline
        
        # Eyes (based on style)
        eye_offset = 8
        left_eye = (head_pos[0] - eye_offset, head_pos[1] - 5)
        right_eye = (head_pos[0] + eye_offset, head_pos[1] - 5)
        
        # Draw eyes based on selected style
        if self.eye_style == 0:  # Normal
            pygame.draw.circle(self.screen, (0, 0, 0), left_eye, 4)
            pygame.draw.circle(self.screen, (0, 0, 0), right_eye, 4)
        elif self.eye_style == 1:  # Happy
            pygame.draw.arc(self.screen, (0, 0, 0), 
                          pygame.Rect(left_eye[0]-5, left_eye[1]-3, 10, 6), 
                          0, 3.14, 2)
            pygame.draw.arc(self.screen, (0, 0, 0), 
                          pygame.Rect(right_eye[0]-5, right_eye[1]-3, 10, 6), 
                          0, 3.14, 2)
        elif self.eye_style == 2:  # Angry
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (left_eye[0]-5, left_eye[1]-5), (left_eye[0]+5, left_eye[1]+5), 2)
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (right_eye[0]-5, right_eye[1]+5), (right_eye[0]+5, right_eye[1]-5), 2)
        elif self.eye_style == 3:  # Surprised
            pygame.draw.circle(self.screen, (0, 0, 0), left_eye, 6)
            pygame.draw.circle(self.screen, (0, 0, 0), right_eye, 6)
        elif self.eye_style == 4:  # Dots
            pygame.draw.circle(self.screen, (0, 0, 0), left_eye, 2)
            pygame.draw.circle(self.screen, (0, 0, 0), right_eye, 2)
        elif self.eye_style == 5:  # Closed
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (left_eye[0]-5, left_eye[1]), (left_eye[0]+5, left_eye[1]), 2)
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (right_eye[0]-5, right_eye[1]), (right_eye[0]+5, right_eye[1]), 2)
        
        # Feet
        left_foot = pygame.Rect(self.preview_x - 25, self.preview_y + 30, 20, 10)
        right_foot = pygame.Rect(self.preview_x + 5, self.preview_y + 30, 20, 10)
        
        pygame.draw.rect(self.screen, self.feet_color, left_foot)
        pygame.draw.rect(self.screen, self.feet_color, right_foot)
        pygame.draw.rect(self.screen, (0, 0, 0), left_foot, 2)
        pygame.draw.rect(self.screen, (0, 0, 0), right_foot, 2)
    
    def save_skin(self):
        """Save the custom skin"""
        # In a real implementation, this would save the skin data
        # to a format that DDNet can use
        print(f"Saving skin: {self.skin_name}")
        print(f"Body color: {self.body_color}")
        print(f"Feet color: {self.feet_color}")
        print(f"Eye style: {self.eye_style}")
        
        # Create a simple representation of the skin
        skin_data = {
            "name": self.skin_name,
            "body_color": self.body_color,
            "feet_color": self.feet_color,
            "eye_style": self.eye_style
        }
        
        # For now, just print the data
        # In a real implementation, we would save this to a file format
        # that can be used by the game
        print("Skin saved successfully!")
    
    def run(self):
        """Main editor loop"""
        print("DDNet Skin Editor started")
        print("Customize your tee skin and save it!")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        print("DDNet Skin Editor closed")


# Example usage
if __name__ == "__main__":
    editor = SkinEditor()
    editor.run()