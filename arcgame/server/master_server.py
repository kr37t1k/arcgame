"""
DDNet Master Server - Server listing/registration
"""
import socket
import threading
import json
import time
from typing import Dict, List, Optional


class ServerInfo:
    """Information about a registered server"""
    def __init__(self, address: str, port: int, name: str = "", 
                 game_type: str = "", map_name: str = "", 
                 players: int = 0, max_players: int = 0):
        self.address = address
        self.port = port
        self.name = name
        self.game_type = game_type
        self.map_name = map_name
        self.players = players
        self.max_players = max_players
        self.last_update = time.time()
        self.version = "0.1"  # DDNet Pygame version


class MasterServer:
    """Master server for server listing and registration"""
    
    def __init__(self, port: int = 8300):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.servers: Dict[str, ServerInfo] = {}  # key: "ip:port"
        self.server_thread = None
        self.cleanup_interval = 300  # 5 minutes
        self.server_timeout = 600  # 10 minutes without update = remove
        
    def start(self):
        """Start the master server"""
        try:
            self.socket.bind(('', self.port))
            self.running = True
            
            print(f"Master server started on port {self.port}")
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Start cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_loop)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
        except Exception as e:
            print(f"Failed to start master server: {e}")
    
    def stop(self):
        """Stop the master server"""
        self.running = False
        if self.socket:
            self.socket.close()
    
    def _server_loop(self):
        """Main server loop for handling registration requests"""
        while self.running:
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    self._handle_packet(data, addr)
            except socket.error:
                if self.running:
                    time.sleep(0.001)
            except Exception:
                pass
    
    def _cleanup_loop(self):
        """Clean up old server entries"""
        while self.running:
            time.sleep(self.cleanup_interval)
            self._cleanup_old_servers()
    
    def _handle_packet(self, data: bytes, addr: tuple):
        """Handle incoming packets"""
        try:
            packet = json.loads(data.decode('utf-8'))
            packet_type = packet.get('type')
            
            if packet_type == 'register':
                self._handle_register(packet, addr)
            elif packet_type == 'query':
                self._handle_query(addr)
            elif packet_type == 'heartbeat':
                self._handle_heartbeat(packet, addr)
                
        except (json.JSONDecodeError, KeyError):
            pass  # Invalid packet
    
    def _handle_register(self, packet: dict, addr: tuple):
        """Handle server registration"""
        server_addr, server_port = addr
        
        # Create server info
        server_info = ServerInfo(
            address=server_addr,
            port=packet.get('port', server_port),
            name=packet.get('name', f'Server at {server_addr}:{server_port}'),
            game_type=packet.get('gametype', 'DM'),
            map_name=packet.get('map', 'unknown'),
            players=packet.get('players', 0),
            max_players=packet.get('max_players', 16)
        )
        
        # Register the server
        key = f"{server_addr}:{server_port}"
        self.servers[key] = server_info
        
        print(f"Server registered: {server_info.name} at {server_addr}:{server_port}")
        
        # Send confirmation
        response = {'type': 'registered', 'success': True}
        self.socket.sendto(json.dumps(response).encode(), addr)
    
    def _handle_query(self, addr: tuple):
        """Handle server list query"""
        # Return list of active servers
        active_servers = []
        current_time = time.time()
        
        for key, server in self.servers.items():
            if current_time - server.last_update < self.server_timeout:
                active_servers.append({
                    'address': server.address,
                    'port': server.port,
                    'name': server.name,
                    'gametype': server.game_type,
                    'map': server.map_name,
                    'players': server.players,
                    'max_players': server.max_players
                })
        
        response = {
            'type': 'server_list',
            'servers': active_servers,
            'count': len(active_servers)
        }
        self.socket.sendto(json.dumps(response).encode(), addr)
    
    def _handle_heartbeat(self, packet: dict, addr: tuple):
        """Handle server heartbeat (keepalive)"""
        server_addr, server_port = addr
        key = f"{server_addr}:{server_port}"
        
        if key in self.servers:
            # Update server info with new data
            server = self.servers[key]
            server.last_update = time.time()
            
            # Update server info if provided
            if 'name' in packet:
                server.name = packet['name']
            if 'gametype' in packet:
                server.game_type = packet['gametype']
            if 'map' in packet:
                server.map_name = packet['map']
            if 'players' in packet:
                server.players = packet['players']
            if 'max_players' in packet:
                server.max_players = packet['max_players']
    
    def _cleanup_old_servers(self):
        """Remove servers that haven't updated in a while"""
        current_time = time.time()
        old_servers = [
            key for key, server in self.servers.items()
            if current_time - server.last_update > self.server_timeout
        ]
        
        for key in old_servers:
            server = self.servers[key]
            print(f"Removed inactive server: {server.name} at {key}")
            del self.servers[key]
    
    def get_server_list(self) -> List[ServerInfo]:
        """Get list of currently active servers"""
        current_time = time.time()
        return [
            server for server in self.servers.values()
            if current_time - server.last_update < self.server_timeout
        ]
    
    def get_server_count(self) -> int:
        """Get number of currently active servers"""
        return len(self.get_server_list())


class MasterClient:
    """Client for querying master server"""
    
    def __init__(self, master_host: str = "localhost", master_port: int = 8300):
        self.master_host = master_host
        self.master_port = master_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5)  # 5 second timeout
    
    def query_servers(self) -> List[Dict]:
        """Query the master server for active servers"""
        try:
            # Send query packet
            query_packet = {'type': 'query'}
            self.socket.sendto(json.dumps(query_packet).encode(), 
                              (self.master_host, self.master_port))
            
            # Receive response
            data, addr = self.socket.recvfrom(4096)
            response = json.loads(data.decode('utf-8'))
            
            if response.get('type') == 'server_list':
                return response.get('servers', [])
            else:
                return []
                
        except (socket.timeout, json.JSONDecodeError, ConnectionRefusedError):
            return []  # Return empty list if query fails
    
    def register_server(self, server_info: Dict) -> bool:
        """Register a server with the master server"""
        try:
            # Add registration packet type
            server_info['type'] = 'register'
            
            self.socket.sendto(json.dumps(server_info).encode(),
                              (self.master_host, self.master_port))
            
            # Wait for confirmation
            data, addr = self.socket.recvfrom(1024)
            response = json.loads(data.decode('utf-8'))
            
            return response.get('success', False)
            
        except (socket.timeout, json.JSONDecodeError, ConnectionRefusedError):
            return False
    
    def send_heartbeat(self, server_info: Dict):
        """Send heartbeat to keep server registered"""
        try:
            server_info['type'] = 'heartbeat'
            self.socket.sendto(json.dumps(server_info).encode(),
                              (self.master_host, self.master_port))
        except:
            pass  # Ignore errors for heartbeats


# Example usage
if __name__ == "__main__":
    # Run as master server
    master = MasterServer()
    master.start()
    
    print("Master server running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down master server...")
        master.stop()