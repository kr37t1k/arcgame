#!/usr/bin/env python3
"""
DDNet Clone launcher script
"""

import sys
import os

def main():
    """Main launcher function"""
    print("DDNet Clone - Version 0.1")
    print("=========================")
    print("To run the game, you need a system with graphics support.")
    print("")
    print("Requirements:")
    print("- Python 3.7 or higher")
    print("- Arcade library")
    print("- Pymunk physics library")
    print("")
    print("To install dependencies:")
    print("pip install -r requirements.txt")
    print("")
    print("To run the game:")
    print("python main.py")
    print("")
    print("Controls:")
    print("- Arrow Keys or WASD: Move left/right and jump")
    print("- Space: Jump")
    print("")
    
    # Try to run the game if possible
    try:
        import main
        print("Attempting to start the game...")
        main.main()
    except Exception as e:
        print(f"Could not start the game: {e}")
        print("This may be because you're running in a headless environment without graphics support.")

if __name__ == "__main__":
    main()