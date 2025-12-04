"""
Core game class for ArcGame
Handles the main game loop, state management, and entity spawning
"""

from ursina import *
from entities.player import Player
from entities.world import World
from ui.scoreboard import Scoreboard
from ui.hud import HUD
from maps.loader import MapLoader
from settings.config import GameConfig
from editor.map_editor import MapEditor
import numpy as np

class ArcGame(Entity):
    def __init__(self, config: GameConfig):
        super().__init__()
        self.config = config
        self.players = []
        self.world = None
        self.scoreboard = None
        self.hud = None
        self.map_loader = MapLoader()
        self.map_editor = None
        self.current_map = None
        self.game_state = "MENU"  # MENU, PLAYING, PAUSED, EDITOR
        self.camera_mode = "FOLLOW"  # FOLLOW, FREE
        
        # Initialize the game
        self.init_game()
        
    def init_game(self):
        """Initialize the game components"""
        # Set up camera
        camera.orthographic = True
        camera.fov = 10
        
        # Load default map
        self.load_map("default")
        
        # Create player
        self.create_player()
        
        # Create UI elements
        self.create_ui()
        
        # Create map editor
        self.map_editor = MapEditor(self)
        
        # Set up input handling
        self.setup_input()
        
        # Set game state to playing
        self.game_state = "PLAYING"
        
    def load_map(self, map_name):
        """Load a map by name"""
        self.current_map = self.map_loader.load_map(map_name)
        if self.world:
            destroy(self.world)
        self.world = World(self.current_map, self.config)
        
    def create_player(self):
        """Create a player entity"""
        player = Player(position=(0, 5, 0), config=self.config)
        self.players.append(player)
        
        # Set player reference in config for real-time updates
        self.config.player_ref = player
        
        # Apply skin colors from config
        skin_colors = self.config.get_skin_colors()
        player.update_skin(
            body_color=skin_colors.get('body', color.orange),
            feet_color=skin_colors.get('feet', color.gray)
        )
        
        # Set camera to follow player
        if self.camera_mode == "FOLLOW":
            camera.world_parent = player
            
    def create_ui(self):
        """Create UI elements like scoreboard and HUD"""
        self.scoreboard = Scoreboard()
        self.hud = HUD()
        
    def setup_input(self):
        """Set up input handling for the game"""
        # Keyboard controls
        self.key_map = {
            'a': 'left',
            'd': 'right', 
            'space': 'jump',
            'escape': 'pause',
            'tab': 'scoreboard',
            'e': 'editor',
            'f1': 'toggle_camera'
        }
        
        # Mouse controls
        mouse.locked = True
        
    def update(self):
        """Main game update loop"""
        if self.game_state == "PLAYING":
            self.update_playing()
        elif self.game_state == "PAUSED":
            self.update_paused()
        elif self.game_state == "EDITOR":
            self.update_editor()
            
    def update_playing(self):
        """Update game logic when playing"""
        # Handle keyboard input
        for key, action in self.key_map.items():
            if held_keys.get(key, False):
                self.handle_input(action)
                
        # Handle mouse input for aiming and shooting
        if mouse.left:
            self.handle_shoot()
        if mouse.right:
            self.handle_hook()
            
        # Update camera to follow player
        if self.camera_mode == "FOLLOW" and self.players:
            player = self.players[0]
            camera.position = player.position + Vec3(0, 0, -15)
            
    def update_paused(self):
        """Update when game is paused"""
        if held_keys.get('escape', False):
            self.toggle_pause()
            
    def update_editor(self):
        """Update when in map editor"""
        # Editor specific updates
        if self.map_editor:
            self.map_editor.update()
        
    def handle_input(self, action):
        """Handle input actions"""
        if self.players:
            player = self.players[0]
            if action == 'left':
                player.move_left()
            elif action == 'right':
                player.move_right()
            elif action == 'jump':
                player.jump()
            elif action == 'pause':
                self.toggle_pause()
            elif action == 'scoreboard':
                self.toggle_scoreboard()
            elif action == 'editor':
                self.toggle_editor()
            elif action == 'toggle_camera':
                self.toggle_camera_mode()
                
    def handle_shoot(self):
        """Handle shooting action"""
        if self.players:
            player = self.players[0]
            player.shoot(mouse.world_point)
            
    def handle_hook(self):
        """Handle hook action"""
        if self.players:
            player = self.players[0]
            player.use_hook(mouse.world_point)
            
    def toggle_pause(self):
        """Toggle pause state"""
        if self.game_state == "PLAYING":
            self.game_state = "PAUSED"
            self.hud.show_pause_menu()
        elif self.game_state == "PAUSED":
            self.game_state = "PLAYING"
            self.hud.hide_pause_menu()
            
    def toggle_scoreboard(self):
        """Toggle scoreboard visibility"""
        if self.scoreboard:
            self.scoreboard.toggle_visibility()
            
    def toggle_editor(self):
        """Toggle map editor"""
        if self.game_state == "EDITOR":
            self.game_state = "PLAYING"
            if self.map_editor:
                self.map_editor.hide()
        else:
            self.game_state = "EDITOR"
            if self.map_editor:
                self.map_editor.show()
            
    def toggle_camera_mode(self):
        """Toggle between camera modes"""
        if self.camera_mode == "FOLLOW":
            self.camera_mode = "FREE"
            camera.world_parent = None
        else:
            self.camera_mode = "FOLLOW"
            if self.players:
                camera.world_parent = self.players[0]
                
    def quit_game(self):
        """Quit the game"""
        application.quit()