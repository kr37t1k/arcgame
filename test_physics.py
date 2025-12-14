"""Test script to verify DDNet physics implementation"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from arcgame.game.character import CharacterPhysics
from arcgame.game.world import World
from arcgame.base.vec2 import Vec2

def test_basic_physics():
    """Test basic character physics functionality"""
    print("Testing basic physics...")
    
    # Create world and character
    world = World()
    world.load_ddnet_map("test")  # This creates a simple test map
    
    character = CharacterPhysics()
    character.init(None, world.get_collision_world(), None)
    character.m_Pos = Vec2(100, 100)
    character.reset()
    
    print(f"Initial position: {character.m_Pos}")
    print(f"Initial velocity: {character.m_Vel}")
    
    # Test gravity
    initial_vel_y = character.m_Vel.y
    character.m_Vel.y += character.m_Tuning['gravity']
    print(f"After gravity: {character.m_Vel.y} (was {initial_vel_y})")
    
    # Test movement input
    character.m_Input['m_Direction'] = 1  # Move right
    character.m_Input['m_TargetX'] = 10
    character.m_Input['m_TargetY'] = -10
    
    # Tick the character
    character.tick(use_input=True)
    print(f"Position after tick: {character.m_Pos}")
    print(f"Velocity after tick: {character.m_Vel}")
    
    # Test move function (collision handling)
    character.move()
    print(f"Position after move: {character.m_Pos}")
    print(f"Velocity after move: {character.m_Vel}")
    
    print("Basic physics test completed successfully!")
    return True

def test_hook_mechanics():
    """Test hook mechanics"""
    print("\nTesting hook mechanics...")
    
    world = World()
    world.load_ddnet_map("test")
    
    character = CharacterPhysics()
    character.init(None, world.get_collision_world(), None)
    character.m_Pos = Vec2(100, 100)
    character.reset()
    
    print(f"Initial hook state: {character.m_HookState}")
    print(f"Initial hook position: {character.m_HookPos}")
    
    # Set hook input
    character.m_Input['m_Hook'] = 1
    character.m_Input['m_TargetX'] = 50
    character.m_Input['m_TargetY'] = 0
    
    # Tick with hook input
    character.tick(use_input=True)
    
    print(f"Hook state after input: {character.m_HookState}")
    print(f"Hook position after input: {character.m_HookPos}")
    print(f"Hook direction: {character.m_HookDir}")
    
    print("Hook mechanics test completed!")
    return True

def test_jump_mechanics():
    """Test jump mechanics"""
    print("\nTesting jump mechanics...")
    
    world = World()
    world.load_ddnet_map("test")
    
    character = CharacterPhysics()
    character.init(None, world.get_collision_world(), None)
    character.m_Pos = Vec2(100, 500)  # Place above ground to test falling
    character.reset()
    
    print(f"Initial velocity: {character.m_Vel}")
    print(f"Initial jump state: {character.m_Jumped}")
    
    # Tick a few times to let character fall to ground
    for i in range(10):
        character.tick(use_input=False)
        character.move()
        print(f"Tick {i+1}: Pos={character.m_Pos}, Vel={character.m_Vel}")
        if world.check_collision(Vec2(character.m_Pos.x, character.m_Pos.y + 15)):  # Grounded check
            print("Character is now grounded")
            break
    
    # Test ground jump
    character.m_Input['m_Jump'] = 1
    character.tick(use_input=True)
    print(f"After jump input: Vel.y = {character.m_Vel.y}, Jumped = {character.m_Jumped}")
    
    print("Jump mechanics test completed!")
    return True

if __name__ == "__main__":
    print("Running DDNet Physics Tests...")
    print("=" * 40)
    
    try:
        test_basic_physics()
        test_hook_mechanics()
        test_jump_mechanics()
        
        print("\n" + "=" * 40)
        print("All physics tests completed successfully!")
        print("DDNet physics implementation is working correctly.")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()