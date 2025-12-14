"""
DDNet Python Implementation
Main entry point for the game
"""

from ursina import *
import sys
import os

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ddnet_game import DDNetGame

def main():
    # Create and run the DDNet game
    app = Ursina(borderless=False, fullscreen=False, title="DDNet Python Implementation")
    game = DDNetGame()
    app.run()

if __name__ == "__main__":
    main()