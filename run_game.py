#!/usr/bin/env python3
"""
ArcGame launcher script
"""

import sys
import os

def main():
    """Main launcher function"""
    print("ArcGame - Teeworlds/DDNet Analog")
    print("===============================")
    print("A Python-based 2D platformer/shooter game inspired by Teeworlds and DDNet.")
    print("")
    print("Requirements:")
    print("- Python 3.7 or higher")
    print("- Ursina engine")
    print("- Panda3D")
    print("")
    print("To install dependencies:")
    print("pip install -r requirements.txt")
    print("")
    print("To run the game:")
    print("python -m arcgame.main")
    print("")
    print("Controls:")
    print("- A/D: Move left/right")
    print("- Space: Jump")
    print("- Mouse Left Click: Shoot")
    print("- Mouse Right Click: Use hook")
    print("- Tab: Toggle scoreboard")
    print("- Escape: Pause menu")
    print("- E: Open map editor")
    print("- F1: Toggle camera mode")
    print("")
    
    # Try to run the game if possible
    try:
        sys.path.insert(0, '/workspace')
        from arcgame.client import main as game_main
        print("Attempting to start the game...")
        game_main()
    except ImportError as e:
        print(f"Could not import the game: {e}")
        print("Make sure you're in the correct directory and have installed dependencies.")
        print("To install dependencies:")
        print("pip install pygame")
    except Exception as e:
        print(f"Could not start the game: {e}")
        print("This may be because you're running in a headless environment without graphics support.")

if __name__ == "__main__":
    main()