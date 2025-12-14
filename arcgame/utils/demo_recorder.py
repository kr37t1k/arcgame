"""
DDNet Demo Recorder - Record/play .demo files
"""
import struct
import time
from typing import Dict, List, Any, Optional


class DemoRecorder:
    """Record and playback DDNet demo files"""
    
    def __init__(self):
        self.recording = False
        self.playing = False
        self.demo_data = []
        self.current_tick = 0
        self.start_time = 0
        self.filename = ""
        
        # Demo header info
        self.demo_version = 3  # DDNet demo version
        self.map_name = ""
        self.game_type = "DM"
        self.tick_rate = 50  # 50Hz like DDNet
    
    def start_recording(self, filename: str, map_name: str, game_type: str = "DM"):
        """Start recording a demo"""
        self.filename = filename
        self.map_name = map_name
        self.game_type = game_type
        self.recording = True
        self.demo_data = []
        self.start_time = time.time()
        self.current_tick = 0
        
        # Add initial demo header info
        self.demo_data.append({
            'tick': 0,
            'type': 'header',
            'map_name': map_name,
            'game_type': game_type,
            'tick_rate': self.tick_rate
        })
        
        print(f"Started recording demo: {filename}")
    
    def stop_recording(self):
        """Stop recording a demo"""
        if self.recording:
            self.recording = False
            self._write_demo_file()
            print(f"Demo recording stopped. Saved to: {self.filename}")
    
    def record_frame(self, game_state: Dict[str, Any]):
        """Record a frame of game state"""
        if self.recording:
            self.current_tick += 1
            frame_data = {
                'tick': self.current_tick,
                'type': 'frame',
                'timestamp': time.time() - self.start_time,
                'game_state': game_state.copy()
            }
            self.demo_data.append(frame_data)
    
    def record_event(self, event_type: str, event_data: Dict[str, Any]):
        """Record a specific event"""
        if self.recording:
            self.current_tick += 1
            event_record = {
                'tick': self.current_tick,
                'type': 'event',
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': time.time() - self.start_time
            }
            self.demo_data.append(event_record)
    
    def _write_demo_file(self):
        """Write demo data to file in DDNet format"""
        with open(self.filename, 'wb') as f:
            # Write header
            f.write(b'DEMO')  # Magic number
            f.write(struct.pack('<I', self.demo_version))  # Version
            f.write(struct.pack('<I', self.tick_rate))     # Tick rate
            f.write(self.map_name.encode('utf-8') + b'\x00')  # Null-terminated map name
            
            # Write frame count
            frame_count = sum(1 for d in self.demo_data if d['type'] == 'frame')
            f.write(struct.pack('<I', frame_count))
            
            # Write all frames
            for data in self.demo_data:
                if data['type'] == 'frame':
                    # Write tick number
                    f.write(struct.pack('<I', data['tick']))
                    
                    # Write frame data (simplified - in real implementation this would be more complex)
                    frame_bytes = str(data['game_state']).encode('utf-8')
                    f.write(struct.pack('<I', len(frame_bytes)))
                    f.write(frame_bytes)
    
    def load_demo(self, filename: str):
        """Load a demo file for playback"""
        try:
            with open(filename, 'rb') as f:
                # Read header
                magic = f.read(4)
                if magic != b'DEMO':
                    raise ValueError("Invalid demo file format")
                
                version = struct.unpack('<I', f.read(4))[0]
                tick_rate = struct.unpack('<I', f.read(4))[0]
                
                # Read map name
                map_name_bytes = b''
                while True:
                    byte = f.read(1)
                    if byte == b'\x00' or not byte:
                        break
                    map_name_bytes += byte
                map_name = map_name_bytes.decode('utf-8')
                
                # Read frame count
                frame_count = struct.unpack('<I', f.read(4))[0]
                
                # Read all frames
                self.demo_data = []
                for _ in range(frame_count):
                    tick = struct.unpack('<I', f.read(4))[0]
                    data_len = struct.unpack('<I', f.read(4))[0]
                    frame_data = f.read(data_len)
                    
                    self.demo_data.append({
                        'tick': tick,
                        'type': 'frame',
                        'game_state': eval(frame_data.decode('utf-8'))  # Simplified
                    })
                
                self.filename = filename
                self.map_name = map_name
                self.tick_rate = tick_rate
                self.current_tick = 0
                
                print(f"Loaded demo: {filename}, {frame_count} frames")
                return True
                
        except Exception as e:
            print(f"Error loading demo: {e}")
            return False
    
    def start_playback(self):
        """Start playing the loaded demo"""
        if self.demo_data:
            self.playing = True
            self.current_tick = 0
            print("Started demo playback")
    
    def stop_playback(self):
        """Stop demo playback"""
        self.playing = False
        print("Stopped demo playback")
    
    def get_next_frame(self) -> Optional[Dict[str, Any]]:
        """Get the next frame in the demo"""
        if self.playing and self.current_tick < len(self.demo_data):
            frame = self.demo_data[self.current_tick]
            self.current_tick += 1
            return frame
        return None
    
    def seek_to_tick(self, tick: int):
        """Seek to a specific tick in the demo"""
        for i, data in enumerate(self.demo_data):
            if data['type'] == 'frame' and data['tick'] >= tick:
                self.current_tick = i
                break
    
    def get_demo_info(self) -> Dict[str, Any]:
        """Get information about the loaded demo"""
        if self.demo_data:
            total_ticks = max((d['tick'] for d in self.demo_data if d['type'] == 'frame'), default=0)
            duration = total_ticks / self.tick_rate if self.tick_rate > 0 else 0
            
            return {
                'filename': self.filename,
                'map_name': self.map_name,
                'game_type': self.game_type,
                'tick_rate': self.tick_rate,
                'total_ticks': total_ticks,
                'duration': duration,
                'frame_count': len([d for d in self.demo_data if d['type'] == 'frame'])
            }
        return {}


class DemoPlayer:
    """Demo player UI component"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.recorder = DemoRecorder()
        
        # Playback state
        self.playing = False
        self.paused = False
        self.current_time = 0
        self.total_time = 0
        
        # UI state
        self.font = None  # Will be initialized when needed
        self.play_button_rect = None
        self.pause_button_rect = None
        self.stop_button_rect = None
        self.seek_bar_rect = None
    
    def load_demo_file(self, filename: str) -> bool:
        """Load a demo file"""
        return self.recorder.load_demo(filename)
    
    def toggle_play_pause(self):
        """Toggle play/pause state"""
        if not self.recorder.demo_data:
            return
        
        if not self.playing:
            self.recorder.start_playback()
            self.playing = True
            self.paused = False
        else:
            self.paused = not self.paused
    
    def stop_playback(self):
        """Stop playback"""
        self.recorder.stop_playback()
        self.playing = False
        self.paused = False
        self.current_time = 0
    
    def update(self, dt: float):
        """Update demo player"""
        if self.playing and not self.paused:
            # In a real implementation, we would get the next frame and update the game state
            next_frame = self.recorder.get_next_frame()
            if next_frame is None:
                # End of demo
                self.stop_playback()
            else:
                self.current_time = next_frame['tick'] / self.recorder.tick_rate
    
    def draw_ui(self, screen):
        """Draw demo player UI"""
        if not self.font:
            import pygame
            self.font = pygame.font.Font(None, 24)
        
        # Draw playback controls
        button_width = 60
        button_height = 30
        button_y = self.screen_height - 50
        
        # Play button
        play_rect = pygame.Rect(50, button_y, button_width, button_height)
        pygame.draw.rect(screen, (0, 150, 0) if not self.playing else (0, 200, 0), play_rect)
        pygame.draw.rect(screen, (255, 255, 255), play_rect, 2)
        play_text = self.font.render("Play" if not self.playing else ("Pause" if not self.paused else "Resume"), True, (255, 255, 255))
        text_rect = play_text.get_rect(center=play_rect.center)
        screen.blit(play_text, text_rect)
        self.play_button_rect = play_rect
        
        # Stop button
        stop_rect = pygame.Rect(120, button_y, button_width, button_height)
        pygame.draw.rect(screen, (150, 0, 0), stop_rect)
        pygame.draw.rect(screen, (255, 255, 255), stop_rect, 2)
        stop_text = self.font.render("Stop", True, (255, 255, 255))
        text_rect = stop_text.get_rect(center=stop_rect.center)
        screen.blit(stop_text, text_rect)
        self.stop_button_rect = stop_rect
        
        # Draw time info
        if self.recorder.demo_data:
            demo_info = self.recorder.get_demo_info()
            time_text = self.font.render(
                f"Time: {self.current_time:.1f}s / {demo_info['duration']:.1f}s", 
                True, (255, 255, 255)
            )
            screen.blit(time_text, (200, button_y + 5))
    
    def handle_click(self, pos):
        """Handle UI clicks"""
        x, y = pos
        
        # Check play/pause button
        if self.play_button_rect and self.play_button_rect.collidepoint(x, y):
            self.toggle_play_pause()
        
        # Check stop button
        if self.stop_button_rect and self.stop_button_rect.collidepoint(x, y):
            self.stop_playback()


# Example usage
if __name__ == "__main__":
    # Example of how to use the demo recorder
    recorder = DemoRecorder()
    
    # Start recording
    recorder.start_recording("test_demo.demo", "dm1")
    
    # Simulate recording some frames
    for i in range(100):  # Record 100 frames
        game_state = {
            'players': [
                {'id': 0, 'x': i * 2, 'y': 100, 'alive': True},
                {'id': 1, 'x': 200 - i, 'y': 150, 'alive': True}
            ],
            'projectiles': [],
            'game_tick': i
        }
        recorder.record_frame(game_state)
    
    # Stop recording
    recorder.stop_recording()
    
    print("Demo recording example completed")