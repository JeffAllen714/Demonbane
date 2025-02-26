import pygame
import sys
import os
import json
from GameState import Game, TitleState, ExplorationState, BattleState, SCREEN_WIDTH, SCREEN_HEIGHT
from LVLSystem import DungeonManager, TileType, TILE_SIZE
from ProgSystem import Player, Enemy, StatusEffect, generate_enemy, generate_weapon, generate_artifact
from SettingsState import SettingsState
from MainMenuState import EnhancedMainMenuState

# Initialize pygame
pygame.init()

# Asset management constants
ASSET_DIR = "assets"
IMAGE_DIR = os.path.join(ASSET_DIR, "images")
SOUND_DIR = os.path.join(ASSET_DIR, "sounds")
SAVE_DIR = os.path.join(ASSET_DIR, "saves")

# Make sure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(SOUND_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)

# Create placeholder images if they don't exist
def create_placeholder_images():
    # Player placeholder
    player_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    player_img.fill((0, 0, 255))  # Blue
    pygame.draw.circle(player_img, (200, 200, 255), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
    
    # Enemy placeholder
    enemy_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    enemy_img.fill((255, 0, 0))  # Red
    pygame.draw.circle(enemy_img, (255, 200, 200), (TILE_SIZE//2, TILE_SIZE//2), TILE_SIZE//2)
    
    # Boss placeholder
    boss_img = pygame.Surface((TILE_SIZE*2, TILE_SIZE*2))
    boss_img.fill((150, 0, 0))  # Dark red
    pygame.draw.circle(boss_img, (200, 0, 0), (TILE_SIZE, TILE_SIZE), TILE_SIZE)
    
    # Tile placeholders
    floor_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    floor_img.fill((210, 105, 30))  # Brown
    
    wall_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall_img.fill((139, 0, 0))  # Dark red
    
    door_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    door_img.fill((101, 67, 33))  # Dark brown
    pygame.draw.rect(door_img, (210, 105, 30), (TILE_SIZE//4, TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))
    
    stairs_up_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    stairs_up_img.fill((0, 255, 0))  # Green
    pygame.draw.polygon(stairs_up_img, (200, 200, 200), [(TILE_SIZE//2, 0), (0, TILE_SIZE), (TILE_SIZE, TILE_SIZE)])
    
    stairs_down_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    stairs_down_img.fill((255, 0, 0))  # Red
    pygame.draw.polygon(stairs_down_img, (200, 200, 200), [(0, 0), (TILE_SIZE, 0), (TILE_SIZE//2, TILE_SIZE)])
    
    # Save images to disk
    images = {
        "player.png": player_img,
        "enemy.png": enemy_img,
        "boss.png": boss_img,
        "floor.png": floor_img,
        "wall.png": wall_img,
        "door.png": door_img,
        "stairs_up.png": stairs_up_img,
        "stairs_down.png": stairs_down_img
    }
    
    for name, img in images.items():
        path = os.path.join(IMAGE_DIR, name)
        if not os.path.exists(path):
            pygame.image.save(img, path)
            print(f"Created placeholder image: {path}")

# Asset loader class
class AssetLoader:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        
    def load_images(self):
        """Load all images from the image directory"""
        for filename in os.listdir(IMAGE_DIR):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                path = os.path.join(IMAGE_DIR, filename)
                self.images[filename] = pygame.image.load(path).convert_alpha()
                print(f"Loaded image: {filename}")
        
        # Create tileset from images
        self.tileset = {
            TileType.WALL.value: self.images.get("wall.png"),
            TileType.FLOOR.value: self.images.get("floor.png"),
            TileType.DOOR.value: self.images.get("door.png"),
            TileType.STAIRS_UP.value: self.images.get("stairs_up.png"),
            TileType.STAIRS_DOWN.value: self.images.get("stairs_down.png")
        }
    
    def load_sounds(self):
        """Load all sounds from the sound directory"""
        for filename in os.listdir(SOUND_DIR):
            if filename.endswith(".wav") or filename.endswith(".ogg"):
                path = os.path.join(SOUND_DIR, filename)
                self.sounds[filename] = pygame.mixer.Sound(path)
                print(f"Loaded sound: {filename}")

# Enhanced Exploration State that uses DungeonManager
class EnhancedExplorationState(ExplorationState):
    def __init__(self, game, dungeon_manager, player):
        super().__init__(game)
        self.dungeon_manager = dungeon_manager
        self.player_character = player
        
        # Camera/viewport 
        self.viewport_width = SCREEN_WIDTH
        self.viewport_height = SCREEN_HEIGHT
        self.viewport_x = 0
        self.viewport_y = 0
    
    def startup(self):
        """Additional setup when state becomes active"""
        # If starting a new game or coming from different state
        if hasattr(self.game, 'new_game') and self.game.new_game:
            # Generate new dungeons
            self.dungeon_manager.generate_all_areas(self.player_character.level)
            self.game.new_game = False
    
    def handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_state = "MAIN_MENU"
                    self.done = True
                elif event.key == pygame.K_h:
                    # Increase heat level (difficulty)
                    self.dungeon_manager.increase_heat()
    
    def update(self, dt):
        """Update game logic"""
        keys = pygame.key.get_pressed()
        
        # Movement with collision detection
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        
        # Only try to move if a direction key is pressed
        if dx != 0 or dy != 0:
            result = self.dungeon_manager.move_player(dx, dy)
            
            # Handle the result of the movement
            if isinstance(result, tuple):
                interaction_type, data = result
                
                if interaction_type == "enemy":
                    # Start battle with the encountered enemy
                    self.game.battle_state.setup_battle(self.player_character, data)
                    self.next_state = "BATTLE"
                    self.done = True
                
                elif interaction_type == "item":
                    # Pick up item
                    if data["type"] in ["common", "uncommon", "rare", "epic", "legendary"]:
                        # Generate a weapon or artifact
                        if random.random() < 0.7:  # 70% chance of weapon
                            weapon = generate_weapon(self.player_character.level, data["type"])
                            self.player_character.add_weapon(weapon)
                            self.game.messages.append(f"Found {weapon.name} ({weapon.rarity})!")
                        else:
                            artifact = generate_artifact(self.player_character.level, data["type"])
                            self.player_character.add_artifact(artifact)
                            self.game.messages.append(f"Found {artifact.name} ({artifact.rarity})!")
                
                elif interaction_type == "trap":
                    # Spring a trap
                    damage = max(5, self.player_character.level * 2)
                    self.player_character.take_damage(damage)
                    self.game.messages.append(f"Triggered a trap! Took {damage} damage.")
                    
                    if not self.player_character.is_alive():
                        self.game.messages.append("You have died!")
                        self.next_state = "GAME_OVER"
                        self.done = True
        
        # Update camera to follow player
        dungeon = self.dungeon_manager.get_current_dungeon()
        player_x, player_y = self.dungeon_manager.player_pos
        
        # Center camera on player
        self.viewport_x = max(0, (player_x * TILE_SIZE) - (self.viewport_width // 2))
        self.viewport_y = max(0, (player_y * TILE_SIZE) - (self.viewport_height // 2))
        
        # Clamp camera to dungeon boundaries
        max_viewport_x = (dungeon.width * TILE_SIZE) - self.viewport_width
        max_viewport_y = (dungeon.height * TILE_SIZE) - self.viewport_height
        self.viewport_x = min(max_viewport_x, max(0, self.viewport_x))
        self.viewport_y = min(max_viewport_y, max(0, self.viewport_y))
    
    def draw(self, surface):
        """Draw the state to the screen"""
        # Get current dungeon and render it
        dungeon = self.dungeon_manager.get_current_dungeon()
        dungeon.render(surface, 
                     (self.viewport_x, self.viewport_y, self.viewport_width, self.viewport_height), 
                     self.dungeon_manager.player_pos)
        
        # Draw HUD overlay
        self._draw_hud(surface)
        
        # Draw messages
        if hasattr(self.game, 'messages') and self.game.messages:
            font = pygame.font.SysFont("Arial", 18)
            for i, message in enumerate(self.game.messages[-3:]):  # Show last 3 messages
                text = font.render(message, True, (255, 255, 255))
                surface.blit(text, (10, SCREEN_HEIGHT - 80 + i * 20))
    
    def _draw_hud(self, surface):
        """Draw HUD elements"""
        # Player info
        font = pygame.font.SysFont("Arial", 16)
        
        # Background for HUD
        hud_bg = pygame.Surface((200, 80))
        hud_bg.set_alpha(150)
        hud_bg.fill((0, 0, 0))
        surface.blit(hud_bg, (10, 10))
        
        # Player name and level
        name_text = font.render(f"{self.player_character.name} - Level {self.player_character.level}", True, (255, 255, 255))
        surface.blit(name_text, (20, 15))
        
        # Health bar
        hp_text = font.render(f"HP: {self.player_character.health}/{self.player_character.max_health}", True, (255, 255, 255))
        surface.blit(hp_text, (20, 35))
        pygame.draw.rect(surface, (255, 0, 0), (80, 35, 100, 15))
        hp_percent = self.player_character.health / self.player_character.max_health
        pygame.draw.rect(surface, (0, 255, 0), (80, 35, 100 * hp_percent, 15))
        
        # Area info
        area_index = self.dungeon_manager.current_area
        area_name = dungeon.theme["name"]
        area_text = font.render(f"Area {area_index + 1}: {area_name}", True, (255, 255, 255))
        surface.blit(area_text, (20, 55))
        
        # Heat level
        heat_text = font.render(f"Heat: {self.dungeon_manager.heat_level}", True, (255, 255, 255))
        surface.blit(heat_text, (20, 75))

# Enhanced Battle State that uses Character classes
class EnhancedBattleState(BattleState):
    def __init__(self, game):
        super().__init__(game)
        self.player_character = None
        self.enemy_character = None
        self.battle_bg = None
    
    def setup_battle(self, player, enemy_data):
        """Set up a new battle with player and enemy"""
        self.player_character = player
        
        # Create an Enemy object from the enemy data
        if isinstance(enemy_data, dict):
            # Create from data
            enemy_level = enemy_data.get("level", 1)
            enemy_type = enemy_data.get("type", "normal")
            
            if enemy_type == "boss":
                # Get appropriate boss name based on area
                area_index = self.game.dungeon_manager.current_area
                boss_names = [
                    "Gateway Guardian",
                    "Flame Overlord",
                    "Frozen Monarch",
                    "Pain Master",
                    "Soul Harvester",
                    "Fallen King",
                    "Dark Prince"
                ]
                boss_name = boss_names[min(area_index, len(boss_names) - 1)]
                self.enemy_character = Enemy(boss_name, enemy_level, "boss")
            else:
                # Generate normal enemy
                self.enemy_character = generate_enemy(enemy_level, self.game.dungeon_manager.current_area)
        else:
            # Already an Enemy object
            self.enemy_character = enemy_data
        
        # Reset battle state
        self.battle_phase = "SELECT"
        self.selected_action = 0
        self.battle_log = []
        self.animation_timer = 0
        
        # Set up actions based on player abilities
        self.actions = ["Attack", "Defend"]
        if self.player_character.abilities:
            for ability in self.player_character.abilities:
                self.actions.append(f"Ability: {ability.name}")
        self.actions.append("Item")
        
        # Create a background for this battle
        area_index = self.game.dungeon_manager.current_area
        bg_color = self.game.dungeon_manager.get_current_dungeon().theme["primary_color"]
        
        self.battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.battle_bg.fill(bg_color)
        
        # Add some simple decorations
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            radius = random.randint(5, 15)
            color = self.game.dungeon_manager.get_current_dungeon().theme["secondary_color"]
            pygame.draw.circle(self.battle_bg, color, (x, y), radius)
    
    def handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.battle_phase == "SELECT":
                    if event.key == pygame.K_UP:
                        self.selected_action = (self.selected_action - 1) % len(self.actions)
                    elif event.key == pygame.K_DOWN:
                        self.selected_action = (self.selected_action + 1) % len(self.actions)
                    elif event.key == pygame.K_RETURN:
                        action = self.actions[self.selected_action]
                        
                        if action == "Attack":
                            # Basic attack
                            damage, is_crit = self.player_character.calculate_attack_damage(self.enemy_character)
                            actual_damage = self.enemy_character.take_damage(damage)
                            
                            crit_text = " (Critical hit!)" if is_crit else ""
                            self.battle_log.append(f"You attack for {actual_damage} damage{crit_text}!")
                            
                            self.battle_phase = "ENEMY_TURN"
                            self.animation_timer = 0.5  # half second for enemy turn
                        
                        elif action == "Defend":
                            # Defensive stance - reduce damage next turn
                            defense_buff = StatusEffect("DefendStance", 1, {"defense": int(self.player_character.defense * 0.5)})
                            self.player_character.add_status_effect(defense_buff)
                            
                            self.battle_log.append("You take a defensive stance!")
                            self.battle_phase = "ENEMY_TURN"
                            self.animation_timer = 0.5
                        
                        elif action.startswith("Ability:"):
                            # Use a special ability
                            ability_name = action[9:]  # Remove "Ability: " prefix
                            ability_index = None
                            
                            # Find the ability
                            for i, ability in enumerate(self.player_character.abilities):
                                if ability.name == ability_name:
                                    ability_index = i
                                    break
                            
                            if ability_index is not None:
                                result, message = self.player_character.use_ability(ability_index, self.enemy_character)
                                
                                if result:
                                    target, value, text = message
                                    self.battle_log.append(text)
                                else:
                                    self.battle_log.append(message)
                                
                                self.battle_phase = "ENEMY_TURN"
                                self.animation_timer = 0.5
                            else:
                                self.battle_log.append("Ability not found!")
                        
                        elif action == "Item":
                            # TODO: Implement item usage
                            self.battle_log.append("No items to use!")
                
                elif event.key == pygame.K_ESCAPE:
                    # Allow escaping from battle (for debugging)
                    if self.game.debug_mode:
                        self.next_state = "EXPLORATION"
                        self.done = True
    
    def update(self, dt):
        """Update battle logic"""
        # Update status effects
        self.player_character.update_status_effects()
        self.enemy_character.update_status_effects()
        
        if self.battle_phase == "ENEMY_TURN":
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                if self.enemy_character.is_alive():
                    # Enemy AI makes a decision
                    action, param = self.enemy_character.choose_action(self.player_character)
                    
                    if action == "attack":
                        # Basic attack
                        damage, is_crit = self.enemy_character.calculate_attack_damage(self.player_character)
                        actual_damage = self.player_character.take_damage(damage)
                        
                        crit_text = " (Critical hit!)" if is_crit else ""
                        self.battle_log.append(f"{self.enemy_character.name} attacks for {actual_damage} damage{crit_text}!")
                    
                    elif action == "ability":
                        # Use enemy ability
                        result, message = self.enemy_character.use_ability(param, self.player_character)
                        
                        if result:
                            target, value, text = message
                            self.battle_log.append(text)
                    
                    # Check for player defeat
                    if not self.player_character.is_alive():
                        self.battle_log.append("You have been defeated!")
                        self.animation_timer = 2.0  # 2 second delay before returning to menu
                        self.battle_phase = "RESULTS"
                    else:
                        self.battle_phase = "SELECT"
                else:
                    # Enemy defeated
                    self.battle_log.append(f"You defeated the {self.enemy_character.name}!")
                    
                    # Gain experience
                    xp = self.enemy_character.experience_reward
                    level_ups = self.player_character.gain_experience(xp)
                    
                    self.battle_log.append(f"Gained {xp} experience!")
                    
                    if level_ups > 0:
                        self.battle_log.append(f"Level up! You are now level {self.player_character.level}!")
                    
                    # Get loot
                    drops, gold = self.enemy_character.get_loot()
                    if drops:
                        for item_name, rarity in drops:
                            self.battle_log.append(f"Found {item_name} ({rarity})!")
                            
                            # TODO: Add items to inventory
                    
                    self.animation_timer = 2.0  # 2 second delay before returning
                    self.battle_phase = "RESULTS"
        
        elif self.battle_phase == "RESULTS":
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                if not self.player_character.is_alive():
                    # Player died - return to main menu
                    self.game.messages.append("You have fallen...")
                    self.next_state = "GAME_OVER"
                else:
                    # Return to exploration
                    for message in self.battle_log[-3:]:
                        self.game.messages.append(message)
                    self.next_state = "EXPLORATION"
                
                self.done = True
    
    def draw(self, surface):
        """Draw the battle screen"""
        # Draw battle background
        if self.battle_bg:
            surface.blit(self.battle_bg, (0, 0))
        else:
            # Fallback background
            surface.fill((0, 0, 0))
        
        # Draw battle UI
        self._draw_battle_interface(surface)
        
        # Draw battle log
        self._draw_battle_log(surface)
    
    def _draw_battle_interface(self, surface):
        """Draw the battle interface"""
        font = pygame.font.SysFont("Arial", 24)
        
        # Enemy section
        enemy_hp_percent = self.enemy_character.health / self.enemy_character.max_health
        pygame.draw.rect(surface, (255, 0, 0), (500, 100, 200, 30))
        pygame.draw.rect(surface, (0, 255, 0), (500, 100, 200 * enemy_hp_percent, 30))
        
        enemy_name = font.render(f"{self.enemy_character.name} Lv.{self.enemy_character.level}", True, (255, 255, 255))
        surface.blit(enemy_name, (500, 70))
        enemy_hp = font.render(f"HP: {self.enemy_character.health}/{self.enemy_character.max_health}", True, (255, 255, 255))
        surface.blit(enemy_hp, (500, 140))
        
        # Draw enemy sprite placeholder
        enemy_rect = pygame.Rect(550, 180, 100, 100)
        pygame.draw.rect(surface, (200, 0, 0), enemy_rect)
        pygame.draw.circle(surface, (255, 100, 100), enemy_rect.center, 40)
        
        # Player section
        player_hp_percent = self.player_character.health / self.player_character.max_health
        pygame.draw.rect(surface, (255, 0, 0), (100, 400, 200, 30))
        pygame.draw.rect(surface, (0, 255, 0), (100, 400, 200 * player_hp_percent, 30))
        
        player_name = font.render(f"{self.player_character.name} Lv.{self.player_character.level}", True, (255, 255, 255))
        surface.blit(player_name, (100, 370))
        player_hp = font.render(f"HP: {self.player_character.health}/{self.player_character.max_health}", True, (255, 255, 255))
        surface.blit(player_hp, (100, 440))
        
        # Draw player sprite placeholder
        player_rect = pygame.Rect(150, 300, 100, 100)
        pygame.draw.rect(surface, (0, 0, 200), player_rect)
        pygame.draw.circle(surface, (100, 100, 255), player_rect.center, 40)
        
        # Action menu
        if self.battle_phase == "SELECT":
            menu_bg = pygame.Surface((200, len(self.actions) * 40 + 20))
            menu_bg.set_alpha(200)
            menu_bg.fill((50, 50, 50))
            surface.blit(menu_bg, (500, 350))
            
            for i, action in enumerate(self.actions):
                color = (255, 255, 0) if i == self.selected_action else (255, 255, 255)
                text = font.render(action, True, color)
                surface.blit(text, (520, 360 + i * 40))
        
        # Status effects
        self._draw_status_effects(surface, self.player_character, (100, 470))
        self._draw_status_effects(surface, self.enemy_character, (500, 160))
    
    def _draw_status_effects(self, surface, character, position):
        """Draw status effect icons for a character"""
        font = pygame.font.SysFont("Arial", 16)
        
        for i, effect in enumerate(character.status_effects):
            effect_rect = pygame.Rect(position[0] + i * 60, position[1], 50, 30)
            
            # Choose color based on effect type
            if effect.name.endswith("Up"):
                color = (0, 255, 0)  # Green for buffs
            elif effect.name.endswith("Down"):
                color = (255, 0, 0)  # Red for debuffs
            else:
                color = (255, 255, 0)  # Yellow for other effects
            
            pygame.draw.rect(surface, color, effect_rect)
            effect_text = font.render(f"{effect.name[:4]}:{effect.duration}", True, (0, 0, 0))
            surface.blit(effect_text, effect_rect.move(5, 5).topleft)
    
    def _draw_battle_log(self, surface):
        """Draw the battle log"""
        font = pygame.font.SysFont("Arial", 18)
        
        log_bg = pygame.Surface((780, 100))
        log_bg.set_alpha(150)
        log_bg.fill((0, 0, 0))
        surface.blit(log_bg, (10, 10))
        
        # Show the last few log entries
        log_entries = self.battle_log[-5:] if len(self.battle_log) > 5 else self.battle_log
        for i, entry in enumerate(log_entries):
            log_text = font.render(entry, True, (255, 255, 255))
            surface.blit(log_text, (20, 20 + i * 20))

# Game Over state
class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("Arial", 64)
        self.option_font = pygame.font.SysFont("Arial", 32)
        self.next_state = "TITLE"
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE]:
                    self.done = True
    
    def draw(self, surface):
        surface.fill((0, 0, 0))
        
        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        surface.blit(title, title_rect)
        
        # Show death message
        if hasattr(self.game, 'messages') and self.game.messages:
            last_message = self.game.messages[-1]
            message = self.option_font.render(last_message, True, (255, 255, 255))
            message_rect = message.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(message, message_rect)
        
        # Show stats
        if hasattr(self.game, 'player'):
            stats_font = pygame.font.SysFont("Arial", 24)
            level_text = stats_font.render(f"Final Level: {self.game.player.level}", True, (255, 255, 255))
            surface.blit(level_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
            
            # TODO: Add more stats (enemies defeated, areas explored, etc.)
        
        prompt = self.game.font.render("Press any key to return to title screen", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.8))
        surface.blit(prompt, prompt_rect)

# Save/Load system
class SaveSystem:
    def __init__(self, save_dir):
        self.save_dir = save_dir
    
    def save_game(self, player, dungeon_manager, slot=1):
        """Save the game to a slot"""
        save_data = {
            "player": player.save_to_dict(),
            "dungeon": {
                "current_area": dungeon_manager.current_area,
                "player_pos": dungeon_manager.player_pos,
                "heat_level": dungeon_manager.heat_level,
                "active_modifiers": [mod["name"] for mod in dungeon_manager.active_modifiers]
            },
            "timestamp": pygame.time.get_ticks()
        }
        
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"Game saved to {save_path}")
        return True
    
    def load_game(self, slot=1):
        """Load the game from a slot"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            print(f"No save file found at {save_path}")
            return None
        
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            # Create player from save data
            player = Player.load_from_dict(save_data["player"])
            
            # Dungeon info to return
            dungeon_info = save_data["dungeon"]
            
            print(f"Game loaded from {save_path}")
            return player, dungeon_info
        
        except Exception as e:
            print(f"Error loading save file: {e}")
            return None
    
    def save_exists(self, slot=1):
        """Check if a save exists in the given slot"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        return os.path.exists(save_path)
    
    def get_save_info(self, slot=1):
        """Get basic info about a save without loading the full data"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            return {
                "player_name": save_data["player"]["name"],
                "player_class": save_data["player"]["class_type"],
                "player_level": save_data["player"]["level"],
                "area": save_data["dungeon"]["current_area"] + 1,
                "timestamp": save_data["timestamp"]
            }
        except:
            return None

# Main execution
def main():
    # Create placeholder assets
    create_placeholder_images()
    
    # Set up asset loader
    assets = AssetLoader()
    assets.load_images()
    
    # Set up save system
    save_system = SaveSystem(SAVE_DIR)
    
    # Create the game
    game = Game()
    
    # Set up debugging
    game.debug_mode = True
    
    # Create a message log
    game.messages = []
    
    # Create player character (will be replaced during character creation)
    game.player = Player("Player", "Crusader")
    
    # Create dungeon manager
    game.dungeon_manager = DungeonManager(50, 50)
    
    # Set up save system
    game.save_system = SaveSystem(SAVE_DIR)
    
    # Flag for new game
    game.new_game = True
    
    # Create enhanced game states
    states = {
        "TITLE": TitleState(game),
        "MAIN_MENU": EnhancedMainMenuState(game),
        "EXPLORATION": EnhancedExplorationState(game, game.dungeon_manager, game.player),
        "BATTLE": EnhancedBattleState(game),
        "GAME_OVER": GameOverState(game),
        "SETTINGS": SettingsState(game)
    }
    
    # Set up the game state machine
    game.setup_states(states, "TITLE")
    
    # Store battle state for easy access
    game.battle_state = states["BATTLE"]
    
    # Start the game loop
    game.run()

if __name__ == "__main__":
    main()
  
