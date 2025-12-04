# ArcGame - Teeworlds/DDNet Analog

ArcGame is a Python-based 2D platformer/shooter game inspired by Teeworlds and DDNet, built using the Ursina engine.

## Features

- 2D platformer gameplay with physics
- Shooting and grappling hook mechanics
- Advanced map editor
- DDNet map loading capability
- Player customization (skin colors)
- Scoreboard system
- Multiplayer-ready architecture

## Controls

- **A/D**: Move left/right
- **Space**: Jump
- **Mouse Left Click**: Shoot
- **Mouse Right Click**: Use hook
- **Tab**: Toggle scoreboard
- **Escape**: Pause menu
- **E**: Open map editor
- **F1**: Toggle camera mode

## Installation

1. Install dependencies: `pip install -r requirements.txt`
2. Run the game: `python -m arcgame.main`

## Project Structure

```
arcgame/
├── core/           # Main game logic
├── entities/       # Game entities (player, world, etc.)
├── ui/            # User interface elements
├── maps/          # Map loading and data
├── settings/      # Configuration and customization
├── editor/        # Map editor
└── main.py       # Entry point
```

## Development

The game is designed to be extensible with:

- Modular architecture
- Configurable settings system
- Customizable player skins
- Advanced map editor
- Support for DDNet maps

## License

MIT License - see LICENSE file for details.
