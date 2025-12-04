"""
Scoreboard UI for ArcGame
Displays player scores, names, and game information
"""

from ursina import *

class Scoreboard(Entity):
    def __init__(self):
        super().__init__()
        self.enabled = False  # Start hidden
        self.players = []
        self.score_elements = []
        
        # Create the scoreboard panel
        self.panel = Panel(
            parent=camera.ui,
            model=Quad(radius=0.025),
            scale=(0.6, 0.8),
            origin=(-0.5, 0.5),
            position=(-0.45, 0.45),
            color=color.black66,
            enabled=False
        )
        
        # Create title
        self.title = Text(
            parent=self.panel,
            text='SCOREBOARD',
            scale=2,
            position=(0.05, -0.05),
            color=color.white
        )
        
        # Create headers
        self.name_header = Text(
            parent=self.panel,
            text='NAME',
            scale=1.5,
            position=(0.1, -0.15),
            color=color.white
        )
        
        self.score_header = Text(
            parent=self.panel,
            text='SCORE',
            scale=1.5,
            position=(0.4, -0.15),
            color=color.white
        )
        
        self.ping_header = Text(
            parent=self.panel,
            text='PING',
            scale=1.5,
            position=(0.55, -0.15),
            color=color.white
        )
        
        # Create player entries (up to 16 players)
        self.player_entries = []
        for i in range(16):
            y_pos = -0.2 - (i * 0.04)
            
            name_text = Text(
                parent=self.panel,
                text=f'Player {i+1}',
                scale=1.2,
                position=(0.1, y_pos),
                color=color.light_gray
            )
            
            score_text = Text(
                parent=self.panel,
                text='0',
                scale=1.2,
                position=(0.42, y_pos),
                color=color.light_gray
            )
            
            ping_text = Text(
                parent=self.panel,
                text='0',
                scale=1.2,
                position=(0.57, y_pos),
                color=color.light_gray
            )
            
            self.player_entries.append({
                'name': name_text,
                'score': score_text,
                'ping': ping_text,
                'active': False
            })
        
        # Add close button
        self.close_button = Button(
            parent=self.panel,
            text='X',
            scale=(0.03, 0.03),
            position=(0.58, -0.05),
            color=color.red,
            on_click=self.hide
        )
        
    def update_scores(self, player_list):
        """
        Update the scoreboard with player information
        player_list should be a list of dicts with keys: name, score, ping, active
        """
        for i, entry in enumerate(self.player_entries):
            if i < len(player_list):
                player = player_list[i]
                entry['name'].text = player.get('name', f'Player {i+1}')
                entry['score'].text = str(player.get('score', 0))
                entry['ping'].text = str(player.get('ping', 0))
                entry['active'] = player.get('active', True)
                
                # Color based on activity
                if player.get('active', False):
                    entry['name'].color = color.white
                    entry['score'].color = color.white
                    entry['ping'].color = color.white
                else:
                    entry['name'].color = color.gray
                    entry['score'].color = color.gray
                    entry['ping'].color = color.gray
            else:
                entry['name'].text = ''
                entry['score'].text = ''
                entry['ping'].text = ''
                entry['active'] = False
    
    def show(self):
        """Show the scoreboard"""
        self.panel.enabled = True
        self.enabled = True
        
    def hide(self):
        """Hide the scoreboard"""
        self.panel.enabled = False
        self.enabled = False
        
    def toggle_visibility(self):
        """Toggle scoreboard visibility"""
        if self.enabled:
            self.hide()
        else:
            self.show()
            
    def add_player(self, name, score=0, ping=0):
        """Add a player to the scoreboard"""
        player_info = {
            'name': name,
            'score': score,
            'ping': ping,
            'active': True
        }
        
        if player_info not in self.players:
            self.players.append(player_info)
            self.update_scores(self.players)
            
    def update_player_score(self, name, score):
        """Update a specific player's score"""
        for player in self.players:
            if player['name'] == name:
                player['score'] = score
                break
        self.update_scores(self.players)
        
    def remove_player(self, name):
        """Remove a player from the scoreboard"""
        self.players = [p for p in self.players if p['name'] != name]
        self.update_scores(self.players)