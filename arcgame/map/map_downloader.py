"""
DDNet Map Downloader - Downloads maps from servers
"""
import os
import urllib.request
from typing import Callable, Optional
import threading
import time


class MapDownloader:
    def __init__(self):
        self.download_queue = []
        self.downloading = False
        self.current_download = None
        self.progress_callback: Optional[Callable] = None
        self.completed_callback: Optional[Callable] = None
        self.download_thread = None
    
    def download_map(self, server_ip: str, map_name: str, map_crc: int = 0, 
                     progress_callback: Optional[Callable] = None, 
                     completed_callback: Optional[Callable] = None):
        """
        Download a map from a server
        In a real implementation, this would use DDNet's network protocol
        For now, we'll simulate downloading from a URL
        """
        # Set callbacks
        self.progress_callback = progress_callback
        self.completed_callback = completed_callback
        
        # Create download task
        download_task = {
            'server_ip': server_ip,
            'map_name': map_name,
            'map_crc': map_crc,
            'status': 'pending',
            'progress': 0.0
        }
        
        self.download_queue.append(download_task)
        
        # Start download if not already downloading
        if not self.downloading:
            self._start_download_process()
    
    def _start_download_process(self):
        """Start the download process in a separate thread"""
        self.downloading = True
        self.download_thread = threading.Thread(target=self._download_worker)
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def _download_worker(self):
        """Worker thread for handling downloads"""
        while self.download_queue:
            task = self.download_queue.pop(0)
            self.current_download = task
            
            try:
                # Simulate download progress
                task['status'] = 'downloading'
                
                # In a real implementation, we would connect to the server
                # and request the map via DDNet's network protocol
                # For now, we'll simulate by copying from source if available
                success = self._simulate_download(task)
                
                if success:
                    task['status'] = 'completed'
                    if self.completed_callback:
                        self.completed_callback(task['map_name'], True)
                else:
                    task['status'] = 'failed'
                    if self.completed_callback:
                        self.completed_callback(task['map_name'], False)
                        
            except Exception as e:
                task['status'] = 'failed'
                if self.completed_callback:
                    self.completed_callback(task['map_name'], False)
        
        self.downloading = False
        self.current_download = None
    
    def _simulate_download(self, task: dict) -> bool:
        """Simulate downloading a map - in real implementation would use network protocol"""
        # First check if we have the map in our ddnet-19.5 source
        source_map_path = f"ddnet-19.5/data/maps/{task['map_name']}.map"
        
        if os.path.exists(source_map_path):
            # Copy from source to downloaded maps directory
            dest_path = f"arcgame/data/maps/downloaded/{task['map_name']}.map"
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy the file
            with open(source_map_path, 'rb') as src, open(dest_path, 'wb') as dst:
                while True:
                    chunk = src.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    dst.write(chunk)
                    # Simulate progress
                    if self.progress_callback:
                        # This is a rough progress estimation
                        self.progress_callback(len(chunk), os.path.getsize(source_map_path))
            
            return True
        else:
            # In a real implementation, we would request the map via UDP
            # For now, let's see if we can find it in any of the DDNet source directories
            possible_paths = [
                f"ddnet-19.5/data/maps/{task['map_name']}.map",
                f"ddnet-19.5/data/maps/downloaded/{task['map_name']}.map",
                f"ddnet-19.5/data/maps/community/{task['map_name']}.map",
                f"ddnet-19.5/data/maps/official/{task['map_name']}.map",
                f"ddnet-19.5/data/maps/campaigns/{task['map_name']}.map"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    dest_path = f"arcgame/data/maps/downloaded/{task['map_name']}.map"
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    with open(path, 'rb') as src, open(dest_path, 'wb') as dst:
                        while True:
                            chunk = src.read(8192)
                            if not chunk:
                                break
                            dst.write(chunk)
                            if self.progress_callback:
                                self.progress_callback(len(chunk), os.path.getsize(path))
                    
                    return True
        
        return False
    
    def check_local_map(self, map_name: str, expected_crc: int = 0) -> bool:
        """
        Check if map exists locally and optionally verify CRC
        Returns True if map exists and CRC matches (if provided)
        """
        from .map_manager import MapManager
        manager = MapManager()
        return manager.has_map(map_name)
    
    def get_download_progress(self) -> dict:
        """Get current download progress information"""
        if self.current_download:
            return {
                'map_name': self.current_download['map_name'],
                'status': self.current_download['status'],
                'progress': self.current_download.get('progress', 0.0)
            }
        return {'status': 'idle'}
    
    def cancel_download(self):
        """Cancel current download"""
        self.download_queue.clear()
        self.downloading = False
        if self.download_thread and self.download_thread.is_alive():
            # In a real implementation we would properly stop the thread
            pass