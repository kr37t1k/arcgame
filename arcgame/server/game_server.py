"""
DDNet Game Server - Main server class
Based on ddnet-19.5/src/engine/server/server.cpp logic
"""
import socket
import threading
import time
import json
import sqlite3
from typing import Dict, List, Optional
from ..config.server_config import server_config
from ..game.world import World
from ..map.map_manager import MapManager


class Player:
    """Player information for the server"""
    def __init__(self, client_id: int, address: tuple):
        self.client_id = client_id
        self.address = address
        self.name = f"Player{client_id}"
        self.score = 0
        self.team = 0  # 0 = spectator, 1 = team1, 2 = team2
        self.is_authenticated = False
        self.connection_time = time.time()
        self.last_activity = time.time()
        self.ping = 0
        self.is_admin = False
        self.is_muted = False


class GameServer:
    """Main game server class"""
    
    def __init__(self):
        self.config = server_config
        self.port = self.config.get("sv_port", 8303)
        self.max_clients = self.config.get("sv_max_clients", 16)
        self.game_type = self.config.get("sv_gametype", "DM")
        self.current_map = self.config.get("sv_map", "dm1")
        
        # Networking
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.clients: Dict[int, Player] = {}
        self.client_counter = 0
        
        # Game state
        self.world = World()
        self.map_manager = MapManager()
        self.tick_rate = 50  # 50Hz like DDNet
        self.tick_counter = 0
        self.start_time = 0
        
        # Threading
        self.server_thread = None
        self.game_loop_thread = None
        
        # Database for player stats
        self.db_connection = sqlite3.connect("arcgame/server/players.db", check_same_thread=False)
        self._init_database()
    
    def _init_database(self):
        """Initialize the player database"""
        cursor = self.db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_playtime INTEGER DEFAULT 0,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                flags_captured INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0
            )
        ''')
        self.db_connection.commit()
    
    def start(self):
        """Start the game server"""
        try:
            self.socket.bind(('', self.port))
            self.running = True
            self.start_time = time.time()
            
            # Load the current map
            self.load_map(self.current_map)
            
            # Start server thread to handle network
            self.server_thread = threading.Thread(target=self._network_loop)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Start game loop thread
            self.game_loop_thread = threading.Thread(target=self._game_loop)
            self.game_loop_thread.daemon = True
            self.game_loop_thread.start()
            
            print(f"DDNet Pygame server started on port {self.port}")
            print(f"Server name: {self.config.get('sv_name', 'DDNet Server')}")
            print(f"Current map: {self.current_map}")
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            self.running = False
    
    def stop(self):
        """Stop the game server"""
        self.running = False
        if self.socket:
            self.socket.close()
        
        # Close database connection
        if self.db_connection:
            self.db_connection.close()
    
    def _network_loop(self):
        """Handle network communication"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                
                # Parse the network packet
                if data:
                    self._handle_packet(data, addr)
                    
            except socket.error:
                if self.running:  # Only print error if we're supposed to be running
                    time.sleep(0.001)  # Prevent busy waiting
            except Exception:
                pass  # Continue running even if there's an error
    
    def _game_loop(self):
        """Main game logic loop running at 50Hz"""
        target_time = 1.0 / self.tick_rate
        while self.running:
            start_time = time.time()
            
            # Update game state
            self._update_game_state()
            
            # Send snapshots to clients
            self._send_snapshots()
            
            # Control the tick rate
            elapsed = time.time() - start_time
            sleep_time = target_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            self.tick_counter += 1
    
    def _update_game_state(self):
        """Update the game world state"""
        # Update world physics
        self.world.update(1.0 / self.tick_rate)
        
        # Update player states, handle timeouts, etc.
        current_time = time.time()
        for client_id, player in list(self.clients.items()):
            # Check for timeouts
            if current_time - player.last_activity > 300:  # 5 minutes
                self._disconnect_client(client_id, "Timeout")
    
    def _send_snapshots(self):
        """Send game state snapshots to clients"""
        # In a real implementation, this would serialize the game state
        # and send it to each connected client
        pass
    
    def _handle_packet(self, data: bytes, addr: tuple):
        """Handle incoming network packets"""
        try:
            # For now, assume JSON packets (in a real implementation, use DDNet protocol)
            packet = json.loads(data.decode('utf-8'))
            packet_type = packet.get('type')
            
            if packet_type == 'connect':
                self._handle_connect(packet, addr)
            elif packet_type == 'input':
                self._handle_input(packet, addr)
            elif packet_type == 'chat':
                self._handle_chat(packet, addr)
            elif packet_type == 'rcon':
                self._handle_rcon(packet, addr)
                
        except (json.JSONDecodeError, KeyError):
            # Invalid packet, ignore
            pass
    
    def _handle_connect(self, packet: dict, addr: tuple):
        """Handle client connection"""
        if len(self.clients) >= self.max_clients:
            # Send server full message
            response = {'type': 'error', 'message': 'Server is full'}
            self.socket.sendto(json.dumps(response).encode(), addr)
            return
        
        # Create new client
        self.client_counter += 1
        client_id = self.client_counter
        
        player = Player(client_id, addr)
        player.name = packet.get('name', f'Player{client_id}')
        
        self.clients[client_id] = player
        
        # Send welcome message
        response = {
            'type': 'welcome',
            'client_id': client_id,
            'map': self.current_map,
            'game_type': self.game_type
        }
        self.socket.sendto(json.dumps(response).encode(), addr)
        
        print(f"Player {player.name} connected from {addr}")
    
    def _handle_input(self, packet: dict, addr: tuple):
        """Handle player input"""
        client_id = packet.get('client_id')
        if client_id in self.clients:
            player = self.clients[client_id]
            player.last_activity = time.time()
            
            # Process input (movement, actions, etc.)
            # This would update the player's state in the world
            input_data = packet.get('input', {})
            # Process the input in the game world
            self.world.process_player_input(client_id, input_data)
    
    def _handle_chat(self, packet: dict, addr: tuple):
        """Handle chat messages"""
        client_id = packet.get('client_id')
        if client_id in self.clients:
            player = self.clients[client_id]
            message = packet.get('message', '')
            
            # Check if player is muted
            if player.is_muted:
                response = {'type': 'chat', 'message': 'You are muted'}
                self.socket.sendto(json.dumps(response).encode(), addr)
                return
            
            # Broadcast chat message to all clients
            chat_packet = {
                'type': 'chat',
                'sender': player.name,
                'message': message,
                'team_only': packet.get('team_only', False)
            }
            
            # Send to all connected clients
            for other_id, other_player in self.clients.items():
                self.socket.sendto(json.dumps(chat_packet).encode(), other_player.address)
    
    def _handle_rcon(self, packet: dict, addr: tuple):
        """Handle remote console commands"""
        password = packet.get('password', '')
        command = packet.get('command', '')
        
        # Check if this is from an admin or has correct password
        is_admin = False
        for client_id, player in self.clients.items():
            if player.address == addr and player.is_admin:
                is_admin = True
                break
        
        correct_password = self.config.get('sv_rcon_password', '')
        if is_admin or password == correct_password:
            response = self._execute_rcon_command(command)
        else:
            response = {'type': 'rcon', 'output': 'Access denied'}
        
        self.socket.sendto(json.dumps(response).encode(), addr)
    
    def _execute_rcon_command(self, command: str) -> dict:
        """Execute a remote console command"""
        parts = command.split()
        if not parts:
            return {'type': 'rcon', 'output': 'No command specified'}
        
        cmd = parts[0].lower()
        
        if cmd == 'status':
            output = f"Server: {self.config.get('sv_name')}\n"
            output += f"Map: {self.current_map}\n"
            output += f"Players: {len(self.clients)}/{self.max_clients}\n"
            output += f"Game Type: {self.game_type}\n"
            output += f"Uptime: {int(time.time() - self.start_time)}s"
            return {'type': 'rcon', 'output': output}
        
        elif cmd == 'kick':
            if len(parts) < 2:
                return {'type': 'rcon', 'output': 'Usage: kick <player_name>'}
            
            player_name = parts[1]
            for client_id, player in self.clients.items():
                if player.name.lower() == player_name.lower():
                    self._disconnect_client(client_id, f'Kicked by RCON: {" ".join(parts[2:])}')
                    return {'type': 'rcon', 'output': f'Kicked {player.name}'}
            
            return {'type': 'rcon', 'output': f'Player {player_name} not found'}
        
        elif cmd == 'map':
            if len(parts) < 2:
                return {'type': 'rcon', 'output': f'Current map: {self.current_map}'}
            
            new_map = parts[1]
            if self.map_manager.has_map(new_map):
                self.load_map(new_map)
                return {'type': 'rcon', 'output': f'Map changed to {new_map}'}
            else:
                return {'type': 'rcon', 'output': f'Map {new_map} not found'}
        
        elif cmd == 'list':
            player_list = [f"{player.name} (ID: {client_id})" for client_id, player in self.clients.items()]
            output = "Connected players:\n" + "\n".join(player_list) if player_list else "No players connected"
            return {'type': 'rcon', 'output': output}
        
        else:
            return {'type': 'rcon', 'output': f'Unknown command: {cmd}'}
    
    def _disconnect_client(self, client_id: int, reason: str = ""):
        """Disconnect a client"""
        if client_id in self.clients:
            player = self.clients[client_id]
            print(f"Player {player.name} disconnected: {reason}")
            
            # Save player stats to database
            self._save_player_stats(player)
            
            del self.clients[client_id]
    
    def _save_player_stats(self, player: Player):
        """Save player statistics to database"""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO players (name, last_seen, total_playtime, kills, deaths, score, points)
                VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
            ''', (player.name, int(time.time() - player.connection_time), 
                  player.kills, player.deaths, player.score, player.score))
            self.db_connection.commit()
        except sqlite3.Error:
            pass  # Continue even if stats saving fails
    
    def load_map(self, map_name: str):
        """Load a map on the server"""
        if self.map_manager.has_map(map_name):
            map_path = self.map_manager.load_map(map_name)
            if map_path:
                self.world.load_from_map(map_path)
                self.current_map = map_name
                self.config.set('sv_map', map_name)
                print(f"Map loaded: {map_name}")
                return True
        
        print(f"Failed to load map: {map_name}")
        return False
    
    def broadcast_message(self, message: str):
        """Send a message to all connected clients"""
        packet = {'type': 'broadcast', 'message': message}
        for client_id, player in self.clients.items():
            try:
                self.socket.sendto(json.dumps(packet).encode(), player.address)
            except:
                # Client might have disconnected
                pass