"""
HUD (Heads-Up Display) for ArcGame
Displays player health, ammo, and other game information
"""

from ursina import *

class HUD(Entity):
    def __init__(self):
        super().__init__()
        self.enabled = True
        
        # Create health display
        self.health_bg = Entity(
            parent=camera.ui,
            model='quad',
            color=color.black66,
            scale=(0.2, 0.05),
            position=(-0.7, 0.45),
            origin=(-0.5, 0)
        )
        
        self.health_bar = Entity(
            parent=self.health_bg,
            model='quad',
            color=color.red,
            scale=(0.95, 0.8),
            position=(-0.025, 0),
            origin=(-0.5, 0)
        )
        
        self.health_text = Text(
            parent=camera.ui,
            text='HEALTH: 10/10',
            scale=1,
            position=(-0.68, 0.43),
            color=color.white
        )
        
        # Create ammo display
        self.ammo_text = Text(
            parent=camera.ui,
            text='AMMO: ∞',
            scale=1,
            position=(-0.68, 0.38),
            color=color.white
        )
        
        # Create weapon display
        self.weapon_text = Text(
            parent=camera.ui,
            text='WEAPON: Shotgun',
            scale=1,
            position=(-0.68, 0.33),
            color=color.white
        )
        
        # Create name display
        self.name_text = Text(
            parent=camera.ui,
            text='ArcGame Player',
            scale=1.2,
            position=(-0.68, 0.48),
            color=color.light_blue
        )
        
        # Create pause menu (initially hidden)
        self.pause_menu = Panel(
            parent=camera.ui,
            model=Quad(radius=0.025),
            scale=(0.4, 0.5),
            origin=(-0.5, 0.5),
            position=(-0.2, 0.25),
            color=color.black66,
            enabled=False
        )
        
        # Pause menu title
        self.pause_title = Text(
            parent=self.pause_menu,
            text='PAUSED',
            scale=2,
            position=(0.1, -0.05),
            color=color.white
        )
        
        # Pause menu buttons
        self.resume_button = Button(
            parent=self.pause_menu,
            text='RESUME',
            scale=(0.25, 0.08),
            position=(0.05, -0.2),
            color=color.gray,
            on_click=self.hide_pause_menu
        )
        
        self.options_button = Button(
            parent=self.pause_menu,
            text='OPTIONS',
            scale=(0.25, 0.08),
            position=(0.05, -0.32),
            color=color.gray,
            on_click=self.show_options
        )
        
        self.quit_button = Button(
            parent=self.pause_menu,
            text='QUIT',
            scale=(0.25, 0.08),
            position=(0.05, -0.44),
            color=color.red,
            on_click=application.quit
        )
        
        # Create chat display (initially hidden)
        self.chat_panel = Panel(
            parent=camera.ui,
            model=Quad(radius=0.025),
            scale=(0.5, 0.3),
            origin=(-0.5, 0.5),
            position=(-0.45, -0.35),
            color=color.black66,
            enabled=False
        )
        
        self.chat_text = Text(
            parent=self.chat_panel,
            text='',
            scale=0.8,
            position=(0.02, -0.05),
            color=color.white,
            line_height=1.1
        )
        
        # Create crosshair
        self.crosshair = Entity(
            parent=camera.ui,
            model='quad',
            color=color.red,
            scale=0.01,
            position=(0, 0)
        )
        
    def update_health(self, health, max_health=10):
        """Update the health display"""
        self.health_text.text = f'HEALTH: {health}/{max_health}'
        
        # Update health bar width based on health percentage
        health_ratio = health / max_health
        self.health_bar.scale_x = 0.95 * health_ratio
        
        # Change color based on health
        if health_ratio > 0.6:
            self.health_bar.color = color.green
        elif health_ratio > 0.3:
            self.health_bar.color = color.orange
        else:
            self.health_bar.color = color.red
            
    def update_ammo(self, ammo, max_ammo=None):
        """Update the ammo display"""
        if max_ammo is None:
            self.ammo_text.text = f'AMMO: ∞'
        else:
            self.ammo_text.text = f'AMMO: {ammo}/{max_ammo}'
            
    def update_weapon(self, weapon_name):
        """Update the weapon display"""
        self.weapon_text.text = f'WEAPON: {weapon_name}'
        
    def show_pause_menu(self):
        """Show the pause menu"""
        self.pause_menu.enabled = True
        
    def hide_pause_menu(self):
        """Hide the pause menu"""
        self.pause_menu.enabled = False
        
    def show_chat(self):
        """Show the chat panel"""
        self.chat_panel.enabled = True
        
    def hide_chat(self):
        """Hide the chat panel"""
        self.chat_panel.enabled = False
        
    def add_chat_message(self, message):
        """Add a message to the chat display"""
        # Add the new message to the top of the chat
        current_text = self.chat_text.text
        if current_text:
            self.chat_text.text = f"{message}\n{current_text}"
        else:
            self.chat_text.text = message
            
        # Limit chat history to 5 lines
        lines = self.chat_text.text.split('\n')
        if len(lines) > 5:
            self.chat_text.text = '\n'.join(lines[:5])
            
    def show_options(self):
        """Placeholder for options menu - will be implemented later"""
        print("Options menu would open here")
        
    def toggle_chat(self):
        """Toggle chat visibility"""
        if self.chat_panel.enabled:
            self.hide_chat()
        else:
            self.show_chat()