"""Main game loop for DDNet Pygame implementation"""
import pygame
import sys
from game.world import World
from game.character import CharacterPhysics
from engine.pygame_renderer import PygameRenderer
from engine.input_handler import InputHandler
from base.vec2 import Vec2


class DDNetGame:
    def __init__(self):
        self.running = True
        self.renderer = PygameRenderer(1024, 768)
        self.world = World()
        
        # Create test characters
        self.characters = []
        self.create_test_characters()
        
        # Input handler
        self.input_handler = InputHandler()
        
        # Fixed timestep variables
        self.physics_accumulator = 0.0
        self.physics_dt = 1/50.0  # 50Hz like DDNet
        self.clock = pygame.time.Clock()
        
        # Create world
        self.world.load_ddnet_map("maps/dm7.map")  # This will use the default simple map
        
    def create_test_characters(self):
        """Create test characters"""
        # Create player character
        player = CharacterPhysics()
        player.init(None, self.world.get_collision_world(), None)
        player.m_Pos = Vec2(100, 100)  # Start position
        player.reset()
        
        # Add to world characters list (simplified)
        if not hasattr(self.world, 'm_apCharacters'):
            self.world.m_apCharacters = [None] * 64  # MAX_CLIENTS
        self.world.m_apCharacters[0] = player
        
        self.characters.append(player)
    
    def handle_input(self, event):
        """Handle pygame input events"""
        if event.type == pygame.QUIT:
            self.running = False
        
        # Let the input handler process the event
        self.input_handler.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
    
    def update_input(self):
        """Update character input based on current key states"""
        if not self.characters:
            return
            
        player = self.characters[0]
        
        # Use input handler to update character input
        self.input_handler.update_character_input(player, self.renderer.screen_to_world)
    
    def update_physics(self, dt):
        """Update physics at fixed timestep"""
        for character in self.characters:
            # Update character physics
            character.tick(use_input=True)
            character.move()
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                self.handle_input(event)
            
            # Clear just pressed/released sets
            self.input_handler.clear_just_pressed()
            
            # Update input
            self.update_input()
            
            # Fixed timestep physics
            frame_time = self.clock.tick(60) / 1000.0  # Convert to seconds
            self.physics_accumulator += frame_time
            
            while self.physics_accumulator >= self.physics_dt:
                self.update_physics(self.physics_dt)
                self.physics_accumulator -= self.physics_dt
            
            # Render
            self.renderer.render(self.world, self.characters, frame_time)
        
        # Cleanup
        self.renderer.cleanup()


def main():
    """Entry point"""
    game = DDNetGame()
    game.run()


if __name__ == "__main__":
    main()