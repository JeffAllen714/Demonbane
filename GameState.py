import pygame
import sys

# Initialize pygame
pygame.init()

# Game configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FRAME_RATE = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (218, 165, 32)

class GameState:
    """Base class for all game states"""
    def __init__(self, game):
        self.game = game
        self.next_state = None
        self.done = False
        self.quit = False
        self.previous = None

    def startup(self):
        """Called when this state becomes the active state"""
        pass

    def cleanup(self):
        """Called when this state is no longer the active state"""
        pass

    def handle_events(self, events):
        """Handle pygame events"""
        pass

    def update(self, dt):
        """Update game logic"""
        pass

    def draw(self, surface):
        """Draw the state to the screen"""
        pass

class Game:
    """Main game class that manages states"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Demonbane")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state_dict = {}
        self.current_state = None
        self.state_name = None
        self.dt = 0
        self.font = pygame.font.SysFont("Arial", 24)

    def setup_states(self, state_dict, start_state):
        """Set up the game states"""
        self.state_dict = state_dict
        self.state_name = start_state
        self.current_state = self.state_dict[self.state_name]
        self.current_state.startup()

    def change_state(self):
        """Change the current state"""
        if self.current_state.done:
            self.current_state.cleanup()
            self.state_name = self.current_state.next_state
            self.current_state = self.state_dict[self.state_name]
            self.current_state.startup()
            self.current_state.previous = self.state_name

    def handle_events(self):
        """Handle pygame events for the current state"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                
        self.current_state.handle_events(events)

    def update(self):
        """Update the current state"""
        if self.current_state.quit:
            self.running = False
        elif self.current_state.done:
            self.change_state()
        self.current_state.update(self.dt)

    def draw(self):
        """Draw the current state"""
        self.current_state.draw(self.screen)
        
        # Debug info
        fps = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps, (10, 10))
        
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.dt = self.clock.tick(FRAME_RATE) / 1000.0
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()


# Example game states
class TitleState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("Arial", 64)
        self.option_font = pygame.font.SysFont("Arial", 32)
        self.next_state = "MAIN_MENU"
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.done = True
                elif event.key == pygame.K_ESCAPE:
                    self.quit = True
    
    def draw(self, surface):
        surface.fill(BLACK)
        title = self.title_font.render("DEMONBANE", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        surface.blit(title, title_rect)
        
        subtitle = self.option_font.render("Ascend from the Depths", True, GOLD)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        surface.blit(subtitle, subtitle_rect)
        
        prompt = self.game.font.render("Press ENTER to start or ESC to quit", True, WHITE)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.7))
        surface.blit(prompt, prompt_rect)


class MainMenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["New Run", "Settings", "Quit"]
        self.selected = 0
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.title_font = pygame.font.SysFont("Arial", 48)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.selected] == "New Run":
                        self.next_state = "EXPLORATION"
                        self.done = True
                    elif self.options[self.selected] == "Settings":
                        self.next_state = "SETTINGS"
                        self.done = True
                    elif self.options[self.selected] == "Quit":
                        self.quit = True
                        
    def draw(self, surface):
        surface.fill(BLACK)
        
        title = self.title_font.render("Main Menu", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        surface.blit(title, title_rect)
        
        for i, option in enumerate(self.options):
            color = RED if i == self.selected else WHITE
            text = self.menu_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i * 50))
            surface.blit(text, text_rect)


class ExplorationState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.player_pos = [SCREEN_WIDTH//2, SCREEN_HEIGHT//2]
        self.player_speed = 300  # pixels per second
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_state = "MAIN_MENU"
                    self.done = True
                elif event.key == pygame.K_b:
                    self.next_state = "BATTLE"
                    self.done = True
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT]:
            self.player_pos[0] -= self.player_speed * dt
        if keys[pygame.K_RIGHT]:
            self.player_pos[0] += self.player_speed * dt
        if keys[pygame.K_UP]:
            self.player_pos[1] -= self.player_speed * dt
        if keys[pygame.K_DOWN]:
            self.player_pos[1] += self.player_speed * dt
            
        # Boundary checking
        self.player_pos[0] = max(20, min(self.player_pos[0], SCREEN_WIDTH - 20))
        self.player_pos[1] = max(20, min(self.player_pos[1], SCREEN_HEIGHT - 20))
    
    def draw(self, surface):
        surface.fill((50, 10, 10))  # Dark red for hell
        
        # Draw simple player
        pygame.draw.circle(surface, WHITE, (int(self.player_pos[0]), int(self.player_pos[1])), 20)
        
        # Instructions
        instruction = self.game.font.render("Arrow Keys to move | B for battle | ESC for menu", True, WHITE)
        surface.blit(instruction, (20, SCREEN_HEIGHT - 40))
        
        # Level info
        level_text = self.game.font.render("Level 1: The Gates of Hell", True, GOLD)
        surface.blit(level_text, (20, 20))


class BattleState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.battle_phase = "SELECT"  # SELECT, ACTION, ENEMY_TURN, RESULTS
        self.actions = ["Attack", "Defend", "Special", "Item"]
        self.selected_action = 0
        self.battle_log = []
        self.enemy = {"name": "Lesser Demon", "hp": 50, "max_hp": 50, "attack": 12}
        self.player = {"name": "Crusader", "hp": 100, "max_hp": 100, "attack": 15, "defense": 5}
        self.animation_timer = 0
        self.battle_font = pygame.font.SysFont("Arial", 24)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.battle_phase == "SELECT":
                    if event.key == pygame.K_UP:
                        self.selected_action = (self.selected_action - 1) % len(self.actions)
                    elif event.key == pygame.K_DOWN:
                        self.selected_action = (self.selected_action + 1) % len(self.actions)
                    elif event.key == pygame.K_RETURN:
                        if self.actions[self.selected_action] == "Attack":
                            damage = self.player["attack"]
                            self.enemy["hp"] = max(0, self.enemy["hp"] - damage)
                            self.battle_log.append(f"You deal {damage} damage to {self.enemy['name']}!")
                            self.battle_phase = "ENEMY_TURN"
                            self.animation_timer = 0.5  # half second for enemy turn
                elif event.key == pygame.K_ESCAPE:
                    self.next_state = "EXPLORATION"
                    self.done = True
                    
    def update(self, dt):
        if self.battle_phase == "ENEMY_TURN":
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                if self.enemy["hp"] > 0:
                    damage = max(1, self.enemy["attack"] - self.player["defense"])
                    self.player["hp"] = max(0, self.player["hp"] - damage)
                    self.battle_log.append(f"{self.enemy['name']} deals {damage} damage to you!")
                    
                    # Check for defeat
                    if self.player["hp"] <= 0:
                        self.battle_log.append("You have been defeated!")
                        self.animation_timer = 2.0  # 2 second delay before returning to menu
                        self.battle_phase = "RESULTS"
                    else:
                        self.battle_phase = "SELECT"
                else:
                    self.battle_log.append(f"You defeated the {self.enemy['name']}!")
                    self.animation_timer = 2.0  # 2 second delay before returning
                    self.battle_phase = "RESULTS"
                    
        elif self.battle_phase == "RESULTS":
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                # Reset for next battle
                self.enemy["hp"] = self.enemy["max_hp"]
                self.next_state = "EXPLORATION"
                self.done = True
    
    def draw(self, surface):
        surface.fill(BLACK)
        
        # Draw battle UI
        # Enemy section
        enemy_hp_percent = self.enemy["hp"] / self.enemy["max_hp"]
        pygame.draw.rect(surface, RED, (500, 100, 200, 30))
        pygame.draw.rect(surface, GOLD, (500, 100, 200 * enemy_hp_percent, 30))
        enemy_name = self.battle_font.render(f"{self.enemy['name']}", True, WHITE)
        surface.blit(enemy_name, (500, 70))
        
        # Player section
        player_hp_percent = self.player["hp"] / self.player["max_hp"]
        pygame.draw.rect(surface, RED, (100, 400, 200, 30))
        pygame.draw.rect(surface, GOLD, (100, 400, 200 * player_hp_percent, 30))
        player_name = self.battle_font.render(f"{self.player['name']}", True, WHITE)
        surface.blit(player_name, (100, 370))
        
        # Action menu
        if self.battle_phase == "SELECT":
            pygame.draw.rect(surface, (50, 50, 50), (500, 350, 200, 200))
            for i, action in enumerate(self.actions):
                color = RED if i == self.selected_action else WHITE
                text = self.battle_font.render(action, True, color)
                surface.blit(text, (550, 380 + i * 40))
                
        # Battle log (last 3 messages)
        log_entries = self.battle_log[-3:] if self.battle_log else []
        for i, entry in enumerate(log_entries):
            log_text = self.game.font.render(entry, True, WHITE)
            surface.blit(log_text, (20, 20 + i * 30))


# Main execution
def main():
    game = Game()
    
    # Create all the game states
    states = {
        "TITLE": TitleState(game),
        "MAIN_MENU": MainMenuState(game),
        "EXPLORATION": ExplorationState(game),
        "BATTLE": BattleState(game)
    }
    
    # Set up the game state machine
    game.setup_states(states, "TITLE")
    
    # Start the game loop
    game.run()

if __name__ == "__main__":
    main()
  
