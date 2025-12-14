# ArcGame - Python DDNet Clone

ArcGame is a Python-based clone of the popular 2D platformer/shooter game DDNet (Teeworlds). This project aims to recreate the core gameplay mechanics of DDNet in a lightweight, maintainable Python architecture.

## Features

- **DDNet-compatible physics**: Accurate character movement, jumping, and hook mechanics
- **Multiplayer support**: Client-server architecture with network synchronization
- **Weapon system**: Hammer, gun, shotgun, grenade, and rifle with proper ballistics
- **Game modes**: Deathmatch and Team Deathmatch
- **Tile-based collision**: 32px grid collision system matching DDNet
- **Modular architecture**: Clean separation between engine, game logic, and network

## Architecture

```
arcgame/
├── engine/          # Graphics, input, sound, network
│   ├── graphics.py  # Pygame-based rendering
│   ├── input.py     # Input handling
│   └── network.py   # Networking (asyncio)
├── game/            # Game logic and entities
│   ├── entities/    # Player, projectiles, pickups
│   ├── physics.py   # DDNet physics replication
│   ├── weapons.py   # Weapon system
│   └── gamemodes/   # Game modes (DM, TDM, etc.)
├── base/            # Core utilities
│   ├── vec2.py      # 2D vector math
│   └── collision.py # Collision detection
├── client.py        # Main client
└── server.py        # Dedicated server
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

### Client Only
```bash
python run_game.py
```

### Dedicated Server
```bash
python -m arcgame.server --port 8303 --max-players 16
```

### Client and Server Together
```bash
python run_game.py --client --server
```

## Controls

- **WASD/Arrow Keys**: Move
- **Space**: Jump
- **Left Shift**: Hook
- **1-5**: Switch weapons (Hammer, Gun, Shotgun, Grenade, Rifle)
- **R**: Respawn if dead
- **T**: Toggle team
- **ESC**: Quit

## Development

The project is structured to allow easy expansion:

1. **Physics**: `game/physics.py` contains the core DDNet-compatible physics
2. **Entities**: `game/entities/` contains player and other game objects
3. **Weapons**: `game/weapons.py` implements all weapon mechanics
4. **Game Modes**: `game/gamemodes/` contains different game modes
5. **Rendering**: `engine/graphics.py` handles all graphics rendering

## Technical Details

### Physics System
- Character movement matches DDNet's physics exactly
- Hook mechanics with proper flying and grabbing states
- Tile-based collision with 32px grid
- Gravity, friction, and air control parameters matching DDNet

### Network Architecture
- Client-server model with authoritative server
- Snapshot interpolation for smooth movement
- Client-side prediction with server reconciliation
- Efficient binary protocol (planned)

### Performance Targets
- 60 FPS on integrated graphics
- Support 16-32 players per server
- Low network bandwidth (~10KB/s per client)
- Fast loading times (<2s for maps)

## Roadmap

### Phase 1: MVP
- [x] Basic character movement and physics
- [x] Tilemap loading and rendering
- [x] Local multiplayer
- [x] Basic hook mechanics

### Phase 2: Core Gameplay
- [x] Network multiplayer
- [x] Weapon system
- [x] Collision detection
- [x] Game modes: DM, Team DM

### Phase 3: DDNet Features
- [ ] DDRace elements (freeze, tiles, teleporters)
- [ ] Advanced hook physics
- [ ] Particle effects
- [ ] Sound system

### Phase 4: Polish
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Map editor
- [ ] Mod support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

See the LICENSE file for details.
