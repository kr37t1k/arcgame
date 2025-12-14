"""
DDNet Anticheat System - Basic cheat detection
"""
from typing import Dict, List, Tuple
import time
from ..game.character import CharacterPhysics


class AnticheatSystem:
    """Basic cheat detection for the server"""
    
    def __init__(self):
        self.player_stats: Dict[int, dict] = {}
        self.suspicious_events: List[dict] = []
        self.cheat_thresholds = {
            'speed_hack': 1.5,  # Movement speed multiplier threshold
            'aimbot_angle': 10.0,  # Degrees threshold for aim assistance detection
            'kill_spree_warning': 10,  # Kills before warning
            'connection_flood': 5,  # Max connections per minute from same IP
        }
        self.last_positions: Dict[int, Tuple[float, float]] = {}
        self.position_times: Dict[int, float] = {}
    
    def register_player(self, client_id: int):
        """Register a new player with the anticheat system"""
        self.player_stats[client_id] = {
            'kills': 0,
            'deaths': 0,
            'kill_streak': 0,
            'last_kill_time': 0,
            'connections': [],
            'speed_violations': 0,
            'teleport_violations': 0,
            'last_pos': None,
            'last_pos_time': 0,
        }
    
    def unregister_player(self, client_id: int):
        """Remove a player from the anticheat system"""
        if client_id in self.player_stats:
            del self.player_stats[client_id]
        if client_id in self.last_positions:
            del self.last_positions[client_id]
        if client_id in self.position_times:
            del self.position_times[client_id]
    
    def check_movement(self, client_id: int, new_pos: Tuple[float, float], 
                      character: CharacterPhysics) -> bool:
        """Check for movement-related cheats (speed hack, teleport)"""
        if client_id not in self.player_stats:
            self.register_player(client_id)
        
        current_time = time.time()
        old_pos = self.player_stats[client_id].get('last_pos')
        old_time = self.player_stats[client_id].get('last_pos_time', 0)
        
        if old_pos and old_time:
            # Calculate distance traveled
            dx = new_pos[0] - old_pos[0]
            dy = new_pos[1] - old_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            # Calculate time elapsed
            time_elapsed = current_time - old_time
            
            if time_elapsed > 0:
                # Calculate speed
                speed = distance / time_elapsed
                
                # Get max expected speed from character physics
                # This is a simplified check - real implementation would be more complex
                max_speed = 100.0  # This should come from character physics
                
                if speed > max_speed * self.cheat_thresholds['speed_hack']:
                    self.player_stats[client_id]['speed_violations'] += 1
                    self._log_suspicious_event(client_id, 'speed_hack', {
                        'speed': speed,
                        'max_allowed': max_speed * self.cheat_thresholds['speed_hack'],
                        'position': new_pos
                    })
                    return False  # Movement flagged as suspicious
        
        # Update position tracking
        self.player_stats[client_id]['last_pos'] = new_pos
        self.player_stats[client_id]['last_pos_time'] = current_time
        
        return True
    
    def check_kill(self, client_id: int, victim_id: int) -> bool:
        """Check for kill-related cheats"""
        if client_id not in self.player_stats:
            self.register_player(client_id)
        
        current_time = time.time()
        stats = self.player_stats[client_id]
        
        # Update kill statistics
        stats['kills'] += 1
        
        # Check kill streak
        if current_time - stats.get('last_kill_time', 0) < 5:  # 5 second window
            stats['kill_streak'] += 1
        else:
            stats['kill_streak'] = 1
        
        stats['last_kill_time'] = current_time
        
        # Check for excessive kill streak
        if stats['kill_streak'] >= self.cheat_thresholds['kill_spree_warning']:
            self._log_suspicious_event(client_id, 'kill_spree', {
                'kill_streak': stats['kill_streak'],
                'victim_id': victim_id
            })
            # Reset streak after warning
            stats['kill_streak'] = 0
        
        return True
    
    def check_input(self, client_id: int, input_data: dict) -> bool:
        """Check for input-related cheats"""
        if client_id not in self.player_stats:
            self.register_player(client_id)
        
        # Check for impossible input combinations
        # (e.g., moving left and right at the same time)
        left = input_data.get('left', False)
        right = input_data.get('right', False)
        
        if left and right:
            self._log_suspicious_event(client_id, 'impossible_input', {
                'input': input_data
            })
            return False
        
        return True
    
    def check_connection_flood(self, ip_address: str) -> bool:
        """Check for connection flooding from the same IP"""
        current_time = time.time()
        
        # Clean old connection records (older than 1 minute)
        recent_connections = [
            conn_time for conn_time in self.get_recent_connections(ip_address)
            if current_time - conn_time < 60
        ]
        
        # Update connections list
        self.set_recent_connections(ip_address, recent_connections)
        
        # Check if too many connections in the time window
        if len(recent_connections) >= self.cheat_thresholds['connection_flood']:
            self._log_suspicious_event(-1, 'connection_flood', {
                'ip': ip_address,
                'connections': len(recent_connections)
            })
            return False
        
        # Add current connection
        recent_connections.append(current_time)
        self.set_recent_connections(ip_address, recent_connections)
        
        return True
    
    def get_recent_connections(self, ip_address: str) -> List[float]:
        """Get recent connection times for an IP"""
        # This would be implemented with a proper data structure in a real system
        # For now, we'll use a simple approach
        return []
    
    def set_recent_connections(self, ip_address: str, connections: List[float]):
        """Set recent connection times for an IP"""
        # This would be implemented with a proper data structure in a real system
        pass
    
    def _log_suspicious_event(self, client_id: int, event_type: str, details: dict):
        """Log a suspicious event"""
        event = {
            'timestamp': time.time(),
            'client_id': client_id,
            'type': event_type,
            'details': details
        }
        self.suspicious_events.append(event)
        
        # Keep only recent events (last hour)
        current_time = time.time()
        self.suspicious_events = [
            e for e in self.suspicious_events
            if current_time - e['timestamp'] < 3600
        ]
        
        print(f"Anticheat warning: {event_type} detected for client {client_id}")
    
    def get_player_violations(self, client_id: int) -> int:
        """Get number of violations for a player"""
        if client_id in self.player_stats:
            return (self.player_stats[client_id].get('speed_violations', 0) + 
                   self.player_stats[client_id].get('teleport_violations', 0))
        return 0
    
    def should_kick_player(self, client_id: int) -> bool:
        """Check if a player should be kicked for cheating"""
        violations = self.get_player_violations(client_id)
        # For now, kick after 5 violations - this would be configurable in a real system
        return violations >= 5
    
    def reset_player_stats(self, client_id: int):
        """Reset statistics for a player"""
        if client_id in self.player_stats:
            self.player_stats[client_id] = {
                'kills': 0,
                'deaths': 0,
                'kill_streak': 0,
                'last_kill_time': 0,
                'connections': [],
                'speed_violations': 0,
                'teleport_violations': 0,
                'last_pos': None,
                'last_pos_time': 0,
            }