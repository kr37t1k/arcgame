# DDNet Clone - Version 0.1

A Python implementation of a DDNet (Teeworlds-based platformer) clone using Arcade and pymunk physics.

## Features

- Physics-based player movement
- Platformer mechanics with jumping and running
- Collision detection with walls and platforms
- Camera following the player
- Basic level with platforms and obstacles
- Teleporter functionality
- Death tiles that reset player position

## Controls

- **Arrow Keys** or **WASD**: Move left/right and jump
- **Space**: Jump

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python main.py
```

## Current Implementation

Version 0.1 includes:
- Player character with physics-based movement
- Basic level with platforms and obstacles
- Gravity and collision detection
- Camera that follows the player
- Simple win condition (touching the purple teleporter)

## Planned Features for Future Versions

- More DDNet-specific mechanics (prediction, client-side gaming)
- Better collision shapes
- Improved graphics and animations
- More complex levels
- Online multiplayer support
- DDNet-specific items (weapons, hearts, etc.)

## Technical Details

- Uses Arcade for graphics and input handling
- Uses pymunk for physics simulation
- Implements basic platformer physics similar to DDNet
