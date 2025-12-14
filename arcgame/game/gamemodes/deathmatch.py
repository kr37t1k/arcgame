"""Deathmatch game mode for the DDNet clone"""
from ...base.vec2 import Vec2


class DeathmatchGameMode:
    """Deathmatch game mode - classic free-for-all"""
    def __init__(self, game_server=None):
        self.name = "Deathmatch"
        self.short_name = "DM"
        self.game_server = game_server
        
        # Game settings
        self.score_limit = 20
        self.time_limit = 600  # 10 minutes in seconds
        self.round_time = 0
        self.spawn_health = 10
        self.friendly_fire = False
        
        # Player scores
        self.player_scores = {}
        self.player_frags = {}
        self.player_deaths = {}
    
    def initialize(self, server):
        """Initialize the game mode with the server"""
        self.game_server = server
        self.reset_scores()
    
    def reset_scores(self):
        """Reset all player scores"""
        self.player_scores = {}
        self.player_frags = {}
        self.player_deaths = {}
        
        # Initialize scores for existing players
        if self.game_server:
            for player_id in self.game_server.entity_manager.players.keys():
                self.player_scores[player_id] = 0
                self.player_frags[player_id] = 0
                self.player_deaths[player_id] = 0
    
    def player_joined(self, player_id, player_name):
        """Called when a player joins the game"""
        self.player_scores[player_id] = 0
        self.player_frags[player_id] = 0
        self.player_deaths[player_id] = 0
    
    def player_left(self, player_id):
        """Called when a player leaves the game"""
        if player_id in self.player_scores:
            del self.player_scores[player_id]
        if player_id in self.player_frags:
            del self.player_frags[player_id]
        if player_id in self.player_deaths:
            del self.player_deaths[player_id]
    
    def player_killed(self, victim_id, killer_id=None, weapon_name=None):
        """Called when a player is killed"""
        # Update victim's death count
        if victim_id in self.player_deaths:
            self.player_deaths[victim_id] += 1
        
        # Update killer's frag count and score
        if killer_id and killer_id in self.player_frags:
            self.player_frags[killer_id] += 1
            self.player_scores[killer_id] += 1
    
    def player_respawned(self, player_id):
        """Called when a player respawns"""
        # Nothing special needed for DM
        pass
    
    def update(self, dt):
        """Update game mode logic"""
        self.round_time += dt
        
        # Check for game end conditions
        if self.check_game_end():
            self.end_game()
    
    def check_game_end(self):
        """Check if the game should end"""
        # Check score limit
        for score in self.player_scores.values():
            if score >= self.score_limit:
                return True
        
        # Check time limit
        if self.time_limit > 0 and self.round_time >= self.time_limit:
            return True
        
        return False
    
    def end_game(self):
        """End the current game"""
        print(f"Game ended after {self.round_time:.1f} seconds")
        
        # Find winner
        winner_id = max(self.player_scores.items(), key=lambda x: x[1], default=(None, 0))[0]
        if winner_id:
            winner_name = self.game_server.entity_manager.get_player(winner_id).name
            print(f"Winner: {winner_name} with {self.player_scores[winner_id]} points")
        
        # Reset for a new game if server supports it
        if self.game_server:
            self.reset_scores()
            self.round_time = 0
    
    def get_player_score(self, player_id):
        """Get a player's score"""
        return self.player_scores.get(player_id, 0)
    
    def get_player_stats(self, player_id):
        """Get detailed stats for a player"""
        return {
            'score': self.player_scores.get(player_id, 0),
            'frags': self.player_frags.get(player_id, 0),
            'deaths': self.player_deaths.get(player_id, 0),
            'kdr': self.player_frags.get(player_id, 0) / max(1, self.player_deaths.get(player_id, 0))
        }
    
    def get_leaderboard(self):
        """Get the current leaderboard"""
        leaderboard = []
        for player_id, score in self.player_scores.items():
            player = self.game_server.entity_manager.get_player(player_id)
            if player:
                leaderboard.append({
                    'id': player_id,
                    'name': player.name,
                    'score': score,
                    'frags': self.player_frags.get(player_id, 0),
                    'deaths': self.player_deaths.get(player_id, 0)
                })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        return leaderboard


class TeamDeathmatchGameMode:
    """Team Deathmatch game mode - teams compete against each other"""
    def __init__(self, game_server=None):
        self.name = "Team Deathmatch"
        self.short_name = "TDM"
        self.game_server = game_server
        
        # Game settings
        self.score_limit = 30
        self.time_limit = 900  # 15 minutes
        self.round_time = 0
        self.max_teams = 2
        self.team_names = ["Red Team", "Blue Team"]
        
        # Team scores
        self.team_scores = {0: 0, 1: 0}  # team_id: score
        self.player_teams = {}  # player_id: team_id
    
    def initialize(self, server):
        """Initialize the game mode with the server"""
        self.game_server = server
        self.reset_scores()
    
    def reset_scores(self):
        """Reset team scores"""
        self.team_scores = {0: 0, 1: 0}
        self.player_teams = {}
        
        # Assign existing players to teams
        if self.game_server:
            players = list(self.game_server.entity_manager.players.keys())
            for i, player_id in enumerate(players):
                team_id = i % self.max_teams
                self.player_teams[player_id] = team_id
    
    def player_joined(self, player_id, player_name):
        """Called when a player joins the game"""
        # Assign to the team with fewer players
        team_0_count = sum(1 for team in self.player_teams.values() if team == 0)
        team_1_count = sum(1 for team in self.player_teams.values() if team == 1)
        
        if team_0_count <= team_1_count:
            self.player_teams[player_id] = 0
        else:
            self.player_teams[player_id] = 1
    
    def player_left(self, player_id):
        """Called when a player leaves the game"""
        if player_id in self.player_teams:
            del self.player_teams[player_id]
    
    def player_killed(self, victim_id, killer_id=None, weapon_name=None):
        """Called when a player is killed"""
        victim_team = self.player_teams.get(victim_id)
        killer_team = self.player_teams.get(killer_id)
        
        # Don't award points for team kills (if friendly fire is disabled)
        if killer_team is not None and victim_team is not None:
            if killer_team != victim_team or self.friendly_fire_enabled():
                # Award point to killer's team
                self.team_scores[killer_team] += 1
    
    def friendly_fire_enabled(self):
        """Check if friendly fire is enabled"""
        # For now, always disabled in TDM
        return False
    
    def player_respawned(self, player_id):
        """Called when a player respawns"""
        pass
    
    def update(self, dt):
        """Update game mode logic"""
        self.round_time += dt
        
        # Check for game end conditions
        if self.check_game_end():
            self.end_game()
    
    def check_game_end(self):
        """Check if the game should end"""
        # Check score limit
        for score in self.team_scores.values():
            if score >= self.score_limit:
                return True
        
        # Check time limit
        if self.time_limit > 0 and self.round_time >= self.time_limit:
            return True
        
        return False
    
    def end_game(self):
        """End the current game"""
        print(f"Game ended after {self.round_time:.1f} seconds")
        
        # Find winning team
        winning_team = max(self.team_scores.items(), key=lambda x: x[1])[0]
        print(f"Winning team: {self.team_names[winning_team]} with {self.team_scores[winning_team]} points")
        
        # Reset for a new game if server supports it
        if self.game_server:
            self.reset_scores()
            self.round_time = 0
    
    def get_team_score(self, team_id):
        """Get a team's score"""
        return self.team_scores.get(team_id, 0)
    
    def get_player_team(self, player_id):
        """Get a player's team"""
        return self.player_teams.get(player_id, -1)
    
    def get_team_members(self, team_id):
        """Get all players on a team"""
        members = []
        for player_id, team in self.player_teams.items():
            if team == team_id:
                player = self.game_server.entity_manager.get_player(player_id)
                if player:
                    members.append(player)
        return members
    
    def get_leaderboard(self):
        """Get the current leaderboard by teams"""
        leaderboard = []
        for team_id, score in self.team_scores.items():
            members = self.get_team_members(team_id)
            leaderboard.append({
                'team_id': team_id,
                'team_name': self.team_names[team_id],
                'score': score,
                'members': [m.name for m in members]
            })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        return leaderboard


class GameModeManager:
    """Manages different game modes"""
    def __init__(self):
        self.game_modes = {
            'DM': DeathmatchGameMode(),
            'TDM': TeamDeathmatchGameMode()
        }
        self.active_mode = None
    
    def set_game_mode(self, mode_name, server=None):
        """Set the active game mode"""
        if mode_name in self.game_modes:
            self.active_mode = self.game_modes[mode_name]
            if server:
                self.active_mode.initialize(server)
            return True
        return False
    
    def get_active_mode(self):
        """Get the active game mode"""
        return self.active_mode
    
    def update(self, dt):
        """Update the active game mode"""
        if self.active_mode:
            self.active_mode.update(dt)


# Example usage and testing
if __name__ == "__main__":
    # Test the game modes
    print("Testing Deathmatch Game Mode:")
    
    # Create a simple mock server for testing
    class MockServer:
        def __init__(self):
            self.entity_manager = MockEntityManager()
    
    class MockEntityManager:
        def __init__(self):
            self.players = {1: MockPlayer(), 2: MockPlayer()}
    
    class MockPlayer:
        def __init__(self):
            self.name = "TestPlayer"
    
    mock_server = MockServer()
    
    # Test Deathmatch
    dm_mode = DeathmatchGameMode()
    dm_mode.initialize(mock_server)
    
    # Simulate some game events
    dm_mode.player_killed(victim_id=1, killer_id=2, weapon_name='gun')
    dm_mode.player_killed(victim_id=2, killer_id=1, weapon_name='hammer')
    
    print(f"Player 1 score: {dm_mode.get_player_score(1)}")
    print(f"Player 2 score: {dm_mode.get_player_score(2)}")
    
    print("\nLeaderboard:")
    for entry in dm_mode.get_leaderboard():
        print(f"  {entry['name']}: {entry['score']} points")
    
    print("\nTesting Team Deathmatch Game Mode:")
    
    tdm_mode = TeamDeathmatchGameMode()
    tdm_mode.initialize(mock_server)
    
    print(f"Team 0 score: {tdm_mode.get_team_score(0)}")
    print(f"Team 1 score: {tdm_mode.get_team_score(1)}")
    
    print(f"Player 1 team: {tdm_mode.get_player_team(1)}")
    print(f"Player 2 team: {tdm_mode.get_player_team(2)}")