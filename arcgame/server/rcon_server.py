"""
DDNet RCON Server - Remote console (port 28763)
"""
import socket
import threading
import json
from typing import Dict, Tuple


class RCONServer:
    """Remote console server for server administration"""
    
    def __init__(self, port: int = 28763, password: str = ""):
        self.port = port
        self.password = password
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False
        self.clients: Dict[socket.socket, dict] = {}
        self.server_thread = None
        self.command_handlers = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default command handlers"""
        self.command_handlers = {
            'status': self._handle_status,
            'list': self._handle_list,
            'kick': self._handle_kick,
            'ban': self._handle_ban,
            'map': self._handle_map,
            'reload': self._handle_reload,
            'shutdown': self._handle_shutdown,
            'say': self._handle_say,
            'help': self._handle_help,
        }
    
    def start(self):
        """Start the RCON server"""
        try:
            self.socket.bind(('', self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"RCON server started on port {self.port}")
            
            # Start listening for connections
            self.server_thread = threading.Thread(target=self._accept_connections)
            self.server_thread.daemon = True
            self.server_thread.start()
            
        except Exception as e:
            print(f"Failed to start RCON server: {e}")
    
    def stop(self):
        """Stop the RCON server"""
        self.running = False
        self.socket.close()
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
    
    def _accept_connections(self):
        """Accept incoming RCON connections"""
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                
                # Start a thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except socket.error:
                if self.running:
                    continue
                break
    
    def _handle_client(self, client_socket: socket.socket, addr: Tuple[str, int]):
        """Handle communication with a RCON client"""
        client_info = {
            'addr': addr,
            'authenticated': False,
            'attempts': 0
        }
        self.clients[client_socket] = client_info
        
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    command = data.decode('utf-8').strip()
                    response = self._process_command(command, client_info)
                    
                    client_socket.send(response.encode('utf-8') + b'\n')
                    
                except Exception as e:
                    error_msg = f"Error processing command: {e}\n"
                    client_socket.send(error_msg.encode('utf-8'))
        
        except Exception:
            pass  # Client disconnected
        finally:
            if client_socket in self.clients:
                del self.clients[client_socket]
            try:
                client_socket.close()
            except:
                pass
    
    def _process_command(self, command: str, client_info: dict) -> str:
        """Process a command from an RCON client"""
        if not command.strip():
            return "No command specified"
        
        # Check authentication first
        if not client_info['authenticated']:
            if command.startswith('login '):
                return self._handle_login(command, client_info)
            else:
                return "Not authenticated. Use 'login <password>' first."
        
        # Parse the command
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Handle the command
        if cmd in self.command_handlers:
            try:
                return self.command_handlers[cmd](args, client_info)
            except Exception as e:
                return f"Error executing command: {e}"
        else:
            return f"Unknown command: {cmd}. Type 'help' for available commands."
    
    def _handle_login(self, command: str, client_info: dict) -> str:
        """Handle login command"""
        parts = command.split(' ', 1)
        if len(parts) < 2:
            return "Usage: login <password>"
        
        password = parts[1]
        if password == self.password:
            client_info['authenticated'] = True
            client_info['attempts'] = 0
            return "Login successful."
        else:
            client_info['attempts'] += 1
            if client_info['attempts'] >= 3:  # Max 3 attempts
                return "Too many failed login attempts. Connection closed."
            return "Invalid password."
    
    def _handle_status(self, args: str, client_info: dict) -> str:
        """Handle status command"""
        # This would connect to the main game server to get real status
        # For now, return a placeholder
        status = "DDNet Pygame Server Status:\n"
        status += "  Players: 0/16\n"
        status += "  Map: dm1\n"
        status += "  Gametype: DM\n"
        status += "  Uptime: 0h 0m\n"
        status += f"  RCON clients: {len([c for c in self.clients.values() if c['authenticated']])}"
        return status
    
    def _handle_list(self, args: str, client_info: dict) -> str:
        """Handle list command"""
        # This would connect to the main game server to get player list
        return "No players connected."
    
    def _handle_kick(self, args: str, client_info: dict) -> str:
        """Handle kick command"""
        if not args.strip():
            return "Usage: kick <player_name> [reason]"
        return f"Player '{args.split()[0]}' would be kicked. (Not implemented in this demo)"
    
    def _handle_ban(self, args: str, client_info: dict) -> str:
        """Handle ban command"""
        if not args.strip():
            return "Usage: ban <player_name> [reason]"
        return f"Player '{args.split()[0]}' would be banned. (Not implemented in this demo)"
    
    def _handle_map(self, args: str, client_info: dict) -> str:
        """Handle map command"""
        if not args.strip():
            return "Current map: dm1. Usage: map <map_name>"
        return f"Map would be changed to '{args}'. (Not implemented in this demo)"
    
    def _handle_reload(self, args: str, client_info: dict) -> str:
        """Handle reload command"""
        return "Configuration reloaded. (Not implemented in this demo)"
    
    def _handle_shutdown(self, args: str, client_info: dict) -> str:
        """Handle shutdown command"""
        # This would shut down the main server
        return "Shutdown command received. (Not implemented in this demo)"
    
    def _handle_say(self, args: str, client_info: dict) -> str:
        """Handle say command"""
        if not args.strip():
            return "Usage: say <message>"
        return f"Message '{args}' would be broadcast. (Not implemented in this demo)"
    
    def _handle_help(self, args: str, client_info: dict) -> str:
        """Handle help command"""
        help_text = "Available RCON commands:\n"
        for cmd in sorted(self.command_handlers.keys()):
            help_text += f"  {cmd}\n"
        help_text += "\nUse 'login <password>' to authenticate first."
        return help_text
    
    def execute_command(self, command: str) -> str:
        """Execute a command as if it came from RCON (for internal use)"""
        # Create a dummy client info for internal commands
        dummy_client = {'authenticated': True, 'attempts': 0}
        return self._process_command(command, dummy_client)


# Example usage
if __name__ == "__main__":
    # Create RCON server with default password
    rcon_server = RCONServer(port=28763, password="admin123")
    rcon_server.start()
    
    print("RCON server running. Connect with telnet or netcat:")
    print("  telnet localhost 28763")
    print("Then login with: login admin123")
    
    try:
        while True:
            cmd = input("> ")
            if cmd.lower() == "quit":
                break
            if cmd.strip():
                result = rcon_server.execute_command(cmd)
                print(result)
    except KeyboardInterrupt:
        print("\nShutting down RCON server...")
        rcon_server.stop()