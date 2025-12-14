"""Dedicated server for the DDNet clone - handles game logic and networking"""
import asyncio
import json
import time
from .game.entities.player import Player, EntityManager
from .game.physics import PhysicsWorld
from .engine.graphics import MapLoader


class GameServer:
    """Main server class that handles game logic and client connections"""
    def __init__(self, host='localhost', port=8303):
        self.host = host
        self.port = port
        self.running = False
        self.clients = {}  # client_id -> client_info
        self.next_client_id = 1
        
        # Game state
        self.entity_manager = EntityManager()
        self.physics_world = PhysicsWorld()
        self.game_map = None
        self.game_time = 0.0
        self.tick_rate = 50  # Ticks per second (DDNet default)
        self.dt = 1.0 / self.tick_rate
        
        # Server info
        self.server_name = "ArcGame Server"
        self.max_players = 16
        self.game_mode = "DM"  # Deathmatch
        self.map_name = "arcmap"
        
        # Setup initial game state
        self.setup_level()
        
    def setup_level(self):
        """Setup the game level"""
        # Create a test map
        self.game_map = MapLoader.create_test_map(30, 20)
        self.physics_world.add_collision_map(self.game_map)
        
        # Define spawn points
        self.spawn_points = [
            Vec2(100, 300),
            Vec2(200, 300),
            Vec2(300, 300),
            Vec2(400, 300),
            Vec2(500, 300),
            Vec2(600, 300)
        ]
    
    def add_player(self, client_id, name="Player"):
        """Add a player to the game"""
        if len(self.entity_manager.players) >= self.max_players:
            return False, "Server is full"
        
        # Find a spawn point
        spawn_idx = len(self.entity_manager.players) % len(self.spawn_points)
        spawn_pos = self.spawn_points[spawn_idx]
        
        # Create player
        player = Player(client_id, name, pos=spawn_pos)
        self.entity_manager.add_player(player)
        self.physics_world.add_character(player.physics)
        
        # Add to clients
        self.clients[client_id] = {
            'name': name,
            'connected_at': time.time(),
            'last_ping': time.time()
        }
        
        return True, f"Player {name} joined the game"
    
    def remove_player(self, client_id):
        """Remove a player from the game"""
        if client_id in self.entity_manager.players:
            self.entity_manager.remove_player(client_id)
        
        if client_id in self.clients:
            del self.clients[client_id]
    
    def handle_client_input(self, client_id, input_data):
        """Handle input from a client"""
        player = self.entity_manager.get_player(client_id)
        if player:
            # Update player input
            player.set_input(input_data)
    
    def broadcast_state(self):
        """Broadcast game state to all clients"""
        # This would send the current game state to all connected clients
        # For now, we'll just return the state
        state = {
            'time': self.game_time,
            'players': {},
            'projectiles': [],
            'pickups': []
        }
        
        # Add player positions and states
        for pid, player in self.entity_manager.players.items():
            state['players'][pid] = {
                'pos': [player.get_position().x, player.get_position().y],
                'vel': [player.get_velocity().x, player.get_velocity().y],
                'health': player.health,
                'team': player.team,
                'name': player.name,
                'is_alive': player.is_alive,
                'direction': player.direction,
                'hook_state': player.physics.hook_state,
                'hook_pos': [player.physics.hook_pos.x, player.physics.hook_pos.y] if player.physics.hook_state != 'IDLE' else None
            }
        
        return state
    
    async def game_loop(self):
        """Main game loop"""
        while self.running:
            start_time = time.time()
            
            # Update game state
            self.entity_manager.update_all(self.dt)
            self.physics_world.update(self.dt)
            self.game_time += self.dt
            
            # Process client messages (in a real implementation)
            # await self.process_client_messages()
            
            # Broadcast state to clients (in a real implementation)
            # await self.broadcast_to_clients()
            
            # Control tick rate
            elapsed = time.time() - start_time
            sleep_time = max(0, (1.0 / self.tick_rate) - elapsed)
            await asyncio.sleep(sleep_time)
    
    async def start(self):
        """Start the game server"""
        self.running = True
        print(f"Starting ArcGame server on {self.host}:{self.port}")
        print(f"Server: {self.server_name}")
        print(f"Map: {self.map_name}, Mode: {self.game_mode}")
        print(f"Max players: {self.max_players}")
        
        try:
            await self.game_loop()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the game server"""
        self.running = False
        print("Server stopped.")


class NetworkProtocol(asyncio.Protocol):
    """Network protocol for handling client connections"""
    def __init__(self, server):
        self.server = server
        self.transport = None
        self.client_id = None
        self.buffer = b""
    
    def connection_made(self, transport):
        self.transport = transport
        self.client_id = self.server.next_client_id
        self.server.next_client_id += 1
        print(f"Client {self.client_id} connected from {transport.get_extra_info('peername')}")
    
    def data_received(self, data):
        """Handle received data from client"""
        self.buffer += data
        
        # Process complete messages (simplified - in real implementation, use proper message framing)
        try:
            message = json.loads(self.buffer.decode('utf-8'))
            self.buffer = b""
            
            # Handle different message types
            msg_type = message.get('type')
            if msg_type == 'join':
                name = message.get('name', f'Player{self.client_id}')
                success, msg = self.server.add_player(self.client_id, name)
                response = {
                    'type': 'join_response',
                    'success': success,
                    'message': msg,
                    'client_id': self.client_id
                }
                self.send_message(response)
                
            elif msg_type == 'input':
                input_data = message.get('input', {})
                self.server.handle_client_input(self.client_id, input_data)
                
            elif msg_type == 'ping':
                response = {
                    'type': 'pong',
                    'time': time.time()
                }
                self.send_message(response)
                
        except json.JSONDecodeError:
            # Incomplete message, wait for more data
            pass
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def send_message(self, message):
        """Send a message to the client"""
        if self.transport and not self.transport.is_closing():
            try:
                data = json.dumps(message).encode('utf-8')
                self.transport.write(data)
            except Exception as e:
                print(f"Error sending message: {e}")
    
    def connection_lost(self, exc):
        """Handle client disconnection"""
        if self.client_id:
            print(f"Client {self.client_id} disconnected")
            self.server.remove_player(self.client_id)


def main():
    """Main entry point for the server"""
    import argparse
    from .base.vec2 import Vec2  # Import here to avoid circular import issues
    
    parser = argparse.ArgumentParser(description='ArcGame Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8303, help='Port to bind to (default: 8303)')
    parser.add_argument('--name', default='ArcGame Server', help='Server name')
    parser.add_argument('--max-players', type=int, default=16, help='Maximum number of players')
    
    args = parser.parse_args()
    
    print("Starting ArcGame Server...")
    print(f"Configuration: {args.host}:{args.port}")
    print(f"Server name: {args.name}")
    print(f"Max players: {args.max_players}")
    print()
    
    # Create and start server
    server = GameServer(args.host, args.port)
    server.server_name = args.name
    server.max_players = args.max_players
    
    # Setup asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Start network server
        network_server = loop.run_until_complete(
            loop.create_server(lambda: NetworkProtocol(server), args.host, args.port)
        )
        print(f"Listening on {args.host}:{args.port}")
        
        # Start game server
        loop.run_until_complete(server.start())
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        network_server.close()
        loop.run_until_complete(network_server.wait_closed())
        loop.close()
    
    print("Server exited successfully.")


if __name__ == "__main__":
    main()