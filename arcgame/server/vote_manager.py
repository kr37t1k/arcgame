"""
DDNet Vote Manager - Map/kick votes
"""
import time
from typing import Dict, List, Optional
from ..config.server_config import server_config


class Vote:
    """Represents a vote in progress"""
    def __init__(self, vote_type: str, subject: str, initiator: str, time_limit: int = 30):
        self.type = vote_type  # 'map', 'kick', 'option', etc.
        self.subject = subject  # Map name, player name, or option
        self.initiator = initiator  # Player who started the vote
        self.start_time = time.time()
        self.time_limit = time_limit  # Seconds until vote expires
        self.votes_yes = 0
        self.votes_no = 0
        self.voters: Dict[str, bool] = {}  # player_name -> vote (True=Yes, False=No)
        self.active = True
        self.executed = False
    
    def time_remaining(self) -> int:
        """Get seconds remaining before vote expires"""
        elapsed = time.time() - self.start_time
        return max(0, int(self.time_limit - elapsed))
    
    def is_expired(self) -> bool:
        """Check if vote has expired"""
        return self.time_remaining() <= 0
    
    def get_result(self) -> Optional[bool]:
        """Get vote result if completed (True=passed, False=failed, None=not completed)"""
        if not self.active:
            return None
        
        if self.is_expired():
            return self._calculate_result()
        
        # Check if vote can be decided early
        # For now, we'll just return None to continue
        return None
    
    def _calculate_result(self) -> bool:
        """Calculate vote result"""
        total_votes = self.votes_yes + self.votes_no
        if total_votes == 0:
            return False  # No votes = fail
        
        # Require majority to pass
        return self.votes_yes > self.votes_no


class VoteManager:
    """Manages voting system for maps, kicks, etc."""
    
    def __init__(self):
        self.current_vote: Optional[Vote] = None
        self.vote_cooldown = 10  # Seconds between votes
        self.last_vote_time = 0
        self.max_votes_per_player = 1  # Max concurrent votes per player
        self.voting_enabled = server_config.get("sv_map_voting", True)
        self.vote_threshold = 0.5  # 50% needed to pass
        self.min_voters = 2  # Minimum number of voters for vote to be valid
    
    def start_vote(self, vote_type: str, subject: str, initiator: str) -> bool:
        """Start a new vote"""
        if not self.voting_enabled:
            return False
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_vote_time < self.vote_cooldown:
            return False
        
        # Check if there's already an active vote
        if self.current_vote and self.current_vote.active:
            return False
        
        # Validate vote type and subject
        if vote_type not in ['map', 'kick', 'option']:
            return False
        
        # Create new vote
        self.current_vote = Vote(vote_type, subject, initiator)
        self.last_vote_time = current_time
        return True
    
    def vote(self, player_name: str, vote: bool) -> bool:
        """Register a vote from a player"""
        if not self.current_vote or not self.current_vote.active:
            return False
        
        # Check if player has already voted
        if player_name in self.current_vote.voters:
            # Allow changing vote
            old_vote = self.current_vote.voters[player_name]
            if old_vote:
                self.current_vote.votes_yes -= 1
            else:
                self.current_vote.votes_no -= 1
        
        # Record the vote
        self.current_vote.voters[player_name] = vote
        if vote:
            self.current_vote.votes_yes += 1
        else:
            self.current_vote.votes_no += 1
        
        # Check if vote has passed or failed
        result = self.current_vote.get_result()
        if result is not None:
            self.current_vote.active = False
            self.current_vote.executed = True
            return self.execute_vote(result)
        
        return True
    
    def execute_vote(self, result: bool) -> bool:
        """Execute the results of a completed vote"""
        if not self.current_vote or not self.current_vote.executed:
            return False
        
        if result:
            # Vote passed - execute action
            if self.current_vote.type == 'map':
                # Change map
                self._execute_map_change(self.current_vote.subject)
            elif self.current_vote.type == 'kick':
                # Kick player
                self._execute_kick(self.current_vote.subject)
            elif self.current_vote.type == 'option':
                # Execute server option
                self._execute_server_option(self.current_vote.subject)
            
            return True
        else:
            # Vote failed
            return False
    
    def _execute_map_change(self, map_name: str):
        """Execute map change vote"""
        # This would interface with the game server to change maps
        print(f"Vote passed: Changing map to {map_name}")
        # In a real implementation: server.change_map(map_name)
    
    def _execute_kick(self, player_name: str):
        """Execute kick vote"""
        # This would interface with the game server to kick a player
        print(f"Vote passed: Kicking player {player_name}")
        # In a real implementation: server.kick_player(player_name)
    
    def _execute_server_option(self, option: str):
        """Execute server option vote"""
        # This would execute a server configuration change
        print(f"Vote passed: Executing server option {option}")
        # In a real implementation: server.execute_option(option)
    
    def get_vote_status(self) -> Dict:
        """Get current vote status"""
        if not self.current_vote:
            return {'active': False}
        
        total_votes = self.current_vote.votes_yes + self.current_vote.votes_no
        return {
            'active': self.current_vote.active,
            'type': self.current_vote.type,
            'subject': self.current_vote.subject,
            'initiator': self.current_vote.initiator,
            'yes': self.current_vote.votes_yes,
            'no': self.current_vote.votes_no,
            'total': total_votes,
            'time_remaining': self.current_vote.time_remaining(),
            'required': self._get_votes_needed()
        }
    
    def _get_votes_needed(self) -> int:
        """Get number of votes needed to pass"""
        if not self.current_vote:
            return 0
        
        # For now, simple majority
        total_votes = self.current_vote.votes_yes + self.current_vote.votes_no
        return max(self.min_voters, int(total_votes * self.vote_threshold) + 1)
    
    def update(self):
        """Update vote system (call periodically)"""
        if self.current_vote:
            if self.current_vote.is_expired():
                self.current_vote.active = False
                # Execute vote with failure result
                self.execute_vote(False)
    
    def can_start_vote(self, player_name: str) -> bool:
        """Check if a player can start a vote"""
        if not self.voting_enabled:
            return False
        
        # Check cooldown
        if time.time() - self.last_vote_time < self.vote_cooldown:
            return False
        
        # Check if there's already an active vote
        if self.current_vote and self.current_vote.active:
            return False
        
        return True
    
    def get_player_vote_status(self, player_name: str) -> Dict:
        """Get vote status for a specific player"""
        if not self.current_vote:
            return {'can_vote': False, 'voted': False}
        
        # Check if player has voted
        has_voted = player_name in self.current_vote.voters
        
        return {
            'can_vote': self.current_vote.active and not has_voted,
            'voted': has_voted,
            'vote': self.current_vote.voters.get(player_name) if has_voted else None
        }
    
    def cancel_vote(self, reason: str = ""):
        """Cancel the current vote"""
        if self.current_vote:
            self.current_vote.active = False
            self.current_vote = None
            print(f"Vote cancelled: {reason}")


# Global vote manager instance
vote_manager = VoteManager()