"""Input handler for DDNet Pygame implementation"""
import pygame
from arcgame.base.vec2 import Vec2


class InputHandler:
    def __init__(self):
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.mouse_pos = Vec2(0, 0)
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_just_pressed = set()
        self.mouse_buttons_just_released = set()
        
        # Map pygame keys to DDNet actions
        self.key_map = {
            pygame.K_a: 'left',
            pygame.K_LEFT: 'left',
            pygame.K_d: 'right',
            pygame.K_RIGHT: 'right',
            pygame.K_SPACE: 'jump',
            pygame.K_w: 'jump',
            pygame.K_UP: 'jump',
            pygame.K_LCTRL: 'hook',
            pygame.K_RCTRL: 'hook',
            pygame.K_LSHIFT: 'fire',
            pygame.K_RSHIFT: 'fire',
            pygame.K_1: 'weapon_1',
            pygame.K_2: 'weapon_2',
            pygame.K_3: 'weapon_3',
            pygame.K_4: 'weapon_4',
            pygame.K_5: 'weapon_5',
        }
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_just_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
            self.keys_just_released.add(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_buttons_pressed.add(event.button)
            self.mouse_buttons_just_pressed.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse_buttons_pressed.discard(event.button)
            self.mouse_buttons_just_released.add(event.button)
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = Vec2(event.pos[0], event.pos[1])
    
    def get_ddnet_input(self, character):
        """Get input in DDNet character format"""
        input_state = {
            'm_Direction': 0,
            'm_Jump': 0,
            'm_Fire': 0,
            'm_Hook': 0,
            'm_TargetX': 0,
            'm_TargetY': -1  # Default to up
        }
        
        # Handle movement
        if any(key in self.keys_pressed for key in [pygame.K_a, pygame.K_LEFT]):
            input_state['m_Direction'] = -1
        elif any(key in self.keys_pressed for key in [pygame.K_d, pygame.K_RIGHT]):
            input_state['m_Direction'] = 1
        
        # Handle jumping
        if any(key in self.keys_pressed for key in [pygame.K_SPACE, pygame.K_w, pygame.K_UP]):
            input_state['m_Jump'] = 1
        
        # Handle firing
        if any(key in self.keys_pressed for key in [pygame.K_LSHIFT, pygame.K_RSHIFT]):
            input_state['m_Fire'] = 1
        
        # Handle hooking
        if any(key in self.keys_pressed for key in [pygame.K_LCTRL, pygame.K_RCTRL]):
            input_state['m_Hook'] = 1
        
        # Handle aiming
        input_state['m_TargetX'] = self.mouse_pos.x
        input_state['m_TargetY'] = self.mouse_pos.y
        
        return input_state
    
    def update_character_input(self, character, screen_to_world_func):
        """Update character input from current state"""
        # Convert mouse position from screen to world coordinates
        world_mouse_pos = screen_to_world_func(self.mouse_pos)
        
        # Calculate relative position for aiming
        rel_x = world_mouse_pos.x - character.m_Pos.x
        rel_y = world_mouse_pos.y - character.m_Pos.y
        
        # Update character input
        character.m_Input['m_Direction'] = 0
        character.m_Input['m_Jump'] = 0
        character.m_Input['m_Fire'] = 0
        character.m_Input['m_Hook'] = 0
        character.m_Input['m_TargetX'] = rel_x
        character.m_Input['m_TargetY'] = rel_y
        
        # Handle movement
        if any(key in self.keys_pressed for key in [pygame.K_a, pygame.K_LEFT]):
            character.m_Input['m_Direction'] = -1
        elif any(key in self.keys_pressed for key in [pygame.K_d, pygame.K_RIGHT]):
            character.m_Input['m_Direction'] = 1
        
        # Handle jumping
        if any(key in self.keys_pressed for key in [pygame.K_SPACE, pygame.K_w, pygame.K_UP]):
            character.m_Input['m_Jump'] = 1
        
        # Handle firing
        if any(key in self.keys_pressed for key in [pygame.K_LSHIFT, pygame.K_RSHIFT]):
            character.m_Input['m_Fire'] = 1
        
        # Handle hooking
        if any(key in self.keys_pressed for key in [pygame.K_LCTRL, pygame.K_RCTRL]):
            character.m_Input['m_Hook'] = 1
    
    def clear_just_pressed(self):
        """Clear the just pressed sets"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed.clear()
        self.mouse_buttons_just_released.clear()
    
    def is_key_pressed(self, key_name):
        """Check if a key is currently pressed by name"""
        for key, name in self.key_map.items():
            if name == key_name and key in self.keys_pressed:
                return True
        return False
    
    def is_key_just_pressed(self, key_name):
        """Check if a key was just pressed by name"""
        for key, name in self.key_map.items():
            if name == key_name and key in self.keys_just_pressed:
                return True
        return False