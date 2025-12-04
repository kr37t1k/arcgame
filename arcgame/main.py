"""
ArcGame - A Teeworlds/DDNet Analog Game
Main entry point for the game
"""

from ursina import *
import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game import ArcGame
from settings.config import GameConfig

def main():
    # Initialize the game configuration
    config = GameConfig()
    
    # Create and run the game
    app = Ursina(borderless=False, fullscreen=False, title="ArcGame")
    game = ArcGame(config)
    app.run()

if __name__ == "__main__":
    main()