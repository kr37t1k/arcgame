"""
Configuration and settings for ArcGame
Handles game settings, player customization, and preferences
"""

from ursina import *
import json
import os
from pathlib import Path

class GameConfig:
    def __init__(self):
        self.config_file = Path.home() / '.arcgame' / 'config.json'
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Default settings
        self.settings = {
            'player_name': 'ArcGame_Player',
            'skin_colors': {
                'body': [255, 165, 0],      # Orange (RGB)
                'feet': [100, 100, 100],    # Dark gray (RGB)
                'eyes': [0, 0, 0]           # Black (RGB)
            },
            'controls': {
                'move_left': 'a',
                'move_right': 'd',
                'jump': 'space',
                'shoot': 'left_mouse',
                'hook': 'right_mouse',
                'scoreboard': 'tab',
                'chat': 't',
                'pause': 'escape'
            },
            'graphics': {
                'resolution': [1280, 720],
                'fullscreen': False,
                'vsync': True,
                'render_distance': 50
            },
            'audio': {
                'master_volume': 1.0,
                'sfx_volume': 1.0,
                'music_volume': 0.7
            },
            'gameplay': {
                'sensitivity': 1.0,
                'show_fps': False,
                'auto_jump': False
            }
        }
        
        # Load saved settings if they exist
        self.load_settings()
        
        # Reference to player for real-time skin updates
        self.player_ref = None
        
    def load_settings(self):
        """Load settings from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    # Update defaults with saved settings
                    self.settings = {**self.settings, **saved_settings}
            except Exception as e:
                print(f"Error loading settings: {e}")
                
    def save_settings(self):
        """Save settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get_skin_colors(self):
        """Get player skin colors as Ursina Color objects"""
        colors = {}
        for part, rgb_vals in self.settings['skin_colors'].items():
            colors[part] = color.rgb(*rgb_vals)
        return colors
        
    def set_skin_color(self, part, r, g, b):
        """Set a specific skin color"""
        if part in self.settings['skin_colors']:
            self.settings['skin_colors'][part] = [r, g, b]
            self.save_settings()
            
            # Update player skin in real-time if player exists
            if self.player_ref:
                skin_colors = self.get_skin_colors()
                self.player_ref.update_skin(
                    body_color=skin_colors.get('body', color.orange),
                    feet_color=skin_colors.get('feet', color.gray)
                )
            
    def set_player_name(self, name):
        """Set the player's name"""
        self.settings['player_name'] = name
        self.save_settings()
        
    def update_controls(self, action, key):
        """Update a control mapping"""
        if action in self.settings['controls']:
            self.settings['controls'][action] = key
            self.save_settings()
            
    def get_control(self, action):
        """Get the key bound to an action"""
        return self.settings['controls'].get(action, '')
        
    def update_graphics_setting(self, setting, value):
        """Update a graphics setting"""
        if setting in self.settings['graphics']:
            self.settings['graphics'][setting] = value
            self.save_settings()
            
    def update_audio_setting(self, setting, value):
        """Update an audio setting"""
        if setting in self.settings['audio']:
            self.settings['audio'][setting] = value
            self.save_settings()
            
    def update_gameplay_setting(self, setting, value):
        """Update a gameplay setting"""
        if setting in self.settings['gameplay']:
            self.settings['gameplay'][setting] = value
            self.save_settings()


class SettingsMenu(Entity):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.enabled = False
        
        # Create settings menu panel
        self.panel = Panel(
            parent=camera.ui,
            model=Quad(radius=0.025),
            scale=(0.7, 0.8),
            origin=(-0.5, 0.5),
            position=(-0.35, 0.4),
            color=color.black66,
            enabled=False
        )
        
        # Title
        self.title = Text(
            parent=self.panel,
            text='SETTINGS',
            scale=2,
            position=(0.1, -0.05),
            color=color.white
        )
        
        # Create tabs
        self.create_tabs()
        
        # Create close button
        self.close_button = Button(
            parent=self.panel,
            text='X',
            scale=(0.03, 0.03),
            position=(0.65, -0.05),
            color=color.red,
            on_click=self.hide
        )
        
    def create_tabs(self):
        """Create tab buttons for different setting categories"""
        # Tab buttons
        self.appearance_tab = Button(
            parent=self.panel,
            text='APPEARANCE',
            scale=(0.15, 0.05),
            position=(0.05, -0.15),
            color=color.gray,
            on_click=self.show_appearance_settings
        )
        
        self.controls_tab = Button(
            parent=self.panel,
            text='CONTROLS',
            scale=(0.15, 0.05),
            position=(0.22, -0.15),
            color=color.gray,
            on_click=self.show_controls_settings
        )
        
        self.graphics_tab = Button(
            parent=self.panel,
            text='GRAPHICS',
            scale=(0.15, 0.05),
            position=(0.39, -0.15),
            color=color.gray,
            on_click=self.show_graphics_settings
        )
        
        self.audio_tab = Button(
            parent=self.panel,
            text='AUDIO',
            scale=(0.15, 0.05),
            position=(0.56, -0.15),
            color=color.gray,
            on_click=self.show_audio_settings
        )
        
        # Content area
        self.content_area = Entity(
            parent=self.panel,
            model='quad',
            color=color.dark_gray,
            scale=(0.65, 0.55),
            position=(0.025, -0.25),
            origin=(-0.5, 0.5)
        )
        
        # Show appearance settings by default
        self.show_appearance_settings()
        
    def show_appearance_settings(self):
        """Show appearance/customization settings"""
        # Clear previous content
        for child in self.content_area.children:
            destroy(child)
            
        # Player name input
        Text(
            parent=self.content_area,
            text='Player Name:',
            scale=1,
            position=(0.05, -0.05),
            color=color.white
        )
        
        self.name_field = InputField(
            parent=self.content_area,
            default_value=self.config.settings['player_name'],
            scale=(0.3, 0.03),
            position=(0.25, -0.05),
            on_value_changed=self.update_player_name
        )
        
        # Skin customization title
        Text(
            parent=self.content_area,
            text='Skin Customization:',
            scale=1.2,
            position=(0.05, -0.15),
            color=color.white
        )
        
        # Body color picker
        self.create_color_picker('Body Color:', 0.25, 'body')
        self.create_color_picker('Eyes Color:', 0.35, 'eyes')
        self.create_color_picker('Feet Color:', 0.45, 'feet')
        
    def create_color_picker(self, label, y_pos, part):
        """Create a color picker for a specific body part"""
        Text(
            parent=self.content_area,
            text=label,
            scale=0.8,
            position=(0.05, -y_pos),
            color=color.white
        )
        
        # Current color preview
        current_color = self.config.get_skin_colors()[part]
        color_preview = Entity(
            parent=self.content_area,
            model='quad',
            color=current_color,
            scale=(0.03, 0.03),
            position=(0.25, -y_pos + 0.01)
        )
        
        # RGB sliders
        r_val = self.config.settings['skin_colors'][part][0]
        g_val = self.config.settings['skin_colors'][part][1] 
        b_val = self.config.settings['skin_colors'][part][2]
        
        Slider(
            parent=self.content_area,
            text='R',
            min=0,
            max=255,
            default=r_val,
            position=(0.3, -y_pos),
            dynamic=True,
            on_value_changed=lambda val, p=part, cp=color_preview: self.update_color_slider(val, p, 'r', cp)
        )
        
        Slider(
            parent=self.content_area,
            text='G',
            min=0,
            max=255,
            default=g_val,
            position=(0.45, -y_pos),
            dynamic=True,
            on_value_changed=lambda val, p=part, cp=color_preview: self.update_color_slider(val, p, 'g', cp)
        )
        
        Slider(
            parent=self.content_area,
            text='B',
            min=0,
            max=255,
            default=b_val,
            position=(0.6, -y_pos),
            dynamic=True,
            on_value_changed=lambda val, p=part, cp=color_preview: self.update_color_slider(val, p, 'b', cp)
        )
        
    def update_color_slider(self, value, part, component, color_preview):
        """Update color based on slider value"""
        colors = self.config.settings['skin_colors'][part]
        idx = {'r': 0, 'g': 1, 'b': 2}[component]
        colors[idx] = int(value)
        
        # Update preview color
        color_preview.color = color.rgb(*colors)
        
        # Save settings
        self.config.set_skin_color(part, *colors)
        
    def update_player_name(self):
        """Update player name from input field"""
        if hasattr(self, 'name_field'):
            self.config.set_player_name(self.name_field.text)
        
    def show_controls_settings(self):
        """Show controls settings"""
        # Clear previous content
        for child in self.content_area.children:
            destroy(child)
            
        Text(
            parent=self.content_area,
            text='Controls Settings (Coming Soon)',
            scale=1.5,
            position=(0.1, -0.1),
            color=color.white
        )
        
    def show_graphics_settings(self):
        """Show graphics settings"""
        # Clear previous content
        for child in self.content_area.children:
            destroy(child)
            
        Text(
            parent=self.content_area,
            text='Graphics Settings (Coming Soon)',
            scale=1.5,
            position=(0.1, -0.1),
            color=color.white
        )
        
    def show_audio_settings(self):
        """Show audio settings"""
        # Clear previous content
        for child in self.content_area.children:
            destroy(child)
            
        Text(
            parent=self.content_area,
            text='Audio Settings (Coming Soon)',
            scale=1.5,
            position=(0.1, -0.1),
            color=color.white
        )
        
    def show(self):
        """Show the settings menu"""
        self.panel.enabled = True
        self.enabled = True
        
    def hide(self):
        """Hide the settings menu"""
        self.panel.enabled = False
        self.enabled = False
        
    def toggle_visibility(self):
        """Toggle settings menu visibility"""
        if self.enabled:
            self.hide()
        else:
            self.show()