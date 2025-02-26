import pygame
import sys
import os
import random
from GameState import GameState, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GOLD, BLACK
from ProgSystem import Player, generate_enemy, generate_weapon, generate_artifact

class EnhancedMainMenuState(GameState):
    """Enhanced main menu with character creation and save/load options"""
    def __init__(self, game):
        super().__init__(game)
        self.options = ["New Game", "Continue", "Settings", "Quit"]
        self.selected = 0
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.title_font = pygame.font.SysFont("Arial", 64)
        self.info_font = pygame.font.SysFont("Arial", 18)
        
        # Background flame effect
        self.particles = []
        self.max_particles = 100
        self._initialize_particles()
        
        # Character creation submenu
        self.show_character_creation = False
        self.char_options = ["Crusader", "Prophet", "Templar"]
        self.char_selected = 0
        self.char_descriptions = {
            "Crusader": "A balanced warrior with good offense and defense. Wields holy weapons to smite demons.",
            "Prophet": "A magic-focused class with powerful abilities but lower health. Can heal and cast divine spells.",
            "Templar": "A defensive tank with high health and armor. Specializes in protecting from demonic influence."
        }
        
        # Continue submenu
        self.show_continue_menu = False
        self.continue_selected = 0
        self.save_slots = [1, 2, 3]
        self.save_info = [None, None, None]
    
    def startup(self):
        """Called when state becomes active"""
        # Get saved game info
        for i, slot in enumerate(self.save_slots):
            self.save_info[i] = self.game.save_system.get_save_info(slot)
    
    def _initialize_particles(self):
        """Initialize flame particles for background effect"""
        self.particles = []
        for _ in range(self.max_particles):
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(SCREEN_HEIGHT, SCREEN_HEIGHT + 100),
                'size': random.randint(2, 8),
                'speed': random.uniform(1.0, 3.0),
                'color': (
                    random.randint(200, 255),  # Red
                    random.randint(0, 100),    # Green
                    0                         # Blue
                ),
                'alpha': random.randint(100, 200)
            })
    
    def handle_events(self, events):
        """Handle pygame events"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.show_character_creation:
                    self._handle_character_creation(event)
                elif self.show_continue_menu:
                    self._handle_continue_menu(event)
                else:
                    self._handle_main_menu(event)
    
    def _handle_main_menu(self, event):
        """Handle main menu inputs"""
        if event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_RETURN:
            if self.options[self.selected] == "New Game":
                self.show_character_creation = True
                self.char_selected = 0
            elif self.options[self.selected] == "Continue":
                # Check if there are any saves
                has_saves = any(info is not None for info in self.save_info)
                if has_saves:
                    self.show_continue_menu = True
                    self.continue_selected = 0
                else:
                    self.game.messages.append("No saved games found!")
            elif self.options[self.selected] == "Settings":
                self.next_state = "SETTINGS"
                self.done = True
            elif self.options[self.selected] == "Quit":
                self.quit = True
    
    def _handle_character_creation(self, event):
        """Handle character creation menu inputs"""
        if event.key == pygame.K_ESCAPE:
            self.show_character_creation = False
        elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
            self.char_selected = (self.char_selected + 1) % len(self.char_options)
        elif event.key == pygame.K_UP or event.key == pygame.K_LEFT:
            self.char_selected = (self.char_selected - 1) % len(self.char_options)
        elif event.key == pygame.K_RETURN:
            # Create character and start game
            selected_class = self.char_options[self.char_selected]
            self.game.player = Player("Player", selected_class)
            
            # Reset dungeon manager and generate new dungeons
            self.game.dungeon_manager.heat_level = 0
            self.game.dungeon_manager.active_modifiers = []
            self.game.dungeon_manager.generate_all_areas(self.game.player.level)
            
            # Set flag to recreate dungeon in exploration state
            self.game.new_game = True
            
            # Clear messages
            self.game.messages = []
            
            # Go to exploration
            self.next_state = "EXPLORATION"
            self.done = True
    
    def _handle_continue_menu(self, event):
        """Handle continue menu inputs"""
        if event.key == pygame.K_ESCAPE:
            self.show_continue_menu = False
        elif event.key == pygame.K_DOWN:
            self.continue_selected = (self.continue_selected + 1) % len(self.save_slots)
        elif event.key == pygame.K_UP:
            self.continue_selected = (self.continue_selected - 1) % len(self.save_slots)
        elif event.key == pygame.K_RETURN:
            slot = self.save_slots[self.continue_selected]
            
            # Only try to load if slot has a save
            if self.save_info[self.continue_selected]:
                loaded_data = self.game.save_system.load_game(slot)
                
                if loaded_data:
                    player, dungeon_info = loaded_data
                    
                    # Update game state with loaded data
                    self.game.player = player
                    self.game.dungeon_manager.current_area = dungeon_info["current_area"]
                    self.game.dungeon_manager.player_pos = dungeon_info["player_pos"]
                    self.game.dungeon_manager.heat_level = dungeon_info["heat_level"]
                    
                    # Regenerate dungeons with loaded heat level
                    self.game.dungeon_manager.generate_all_areas(player.level)
                    
                    # Update heat modifiers if possible
                    if "active_modifiers" in dungeon_info:
                        for mod_name in dungeon_info["active_modifiers"]:
                            for mod in self.game.dungeon_manager.potential_modifiers:
                                if mod["name"] == mod_name and mod not in self.game.dungeon_manager.active_modifiers:
                                    self.game.dungeon_manager.active_modifiers.append(mod)
                    
                    # Apply modifiers to all dungeons
                    for dungeon in self.game.dungeon_manager.dungeons:
                        self.game.dungeon_manager._apply_heat_modifiers(dungeon)
                    
                    self.game.messages.append(f"Game loaded from slot {slot}")
                    
                    # Go to exploration state
                    self.next_state = "EXPLORATION"
                    self.done = True
                else:
                    self.game.messages.append(f"Failed to load from slot {slot}")
    
    def update(self, dt):
        """Update menu animations"""
        # Update flame particles
        for particle in self.particles:
            particle['y'] -= particle['speed']
            
            # Reset particles that go off screen
            if particle['y'] < -10:
                particle['y'] = SCREEN_HEIGHT + random.randint(0, 50)
                particle['x'] = random.randint(0, SCREEN_WIDTH)
                particle['alpha'] = random.randint(100, 200)
    
    def draw(self, surface):
        """Draw menu state"""
        # Fill background with dark color
        surface.fill((20, 10, 10))
        
        # Draw flame particles
        for particle in self.particles:
            # Create a surface for the particle with alpha
            particle_surface = pygame.Surface((particle['size'], particle['size'] * 2))
            particle_surface.fill((0, 0, 0))
            particle_surface.set_colorkey((0, 0, 0))
            
            # Draw fire shape
            pygame.draw.ellipse(
                particle_surface,
                particle['color'],
                (0, 0, particle['size'], particle['size'] * 2)
            )
            
            # Set alpha and blit
            particle_surface.set_alpha(particle['alpha'])
            surface.blit(particle_surface, (particle['x'], particle['y']))
        
        # Draw title
        title = self.title_font.render("DEMONBANE", True, RED)
        shadow = self.title_font.render("DEMONBANE", True, (100, 0, 0))
        
        # Add pulsing effect to title
        pulse = (pygame.time.get_ticks() % 1000) / 1000  # 0 to 1 over 1 second
        pulse_offset = int(pulse * 3)  # 0 to 3 pixels
        
        # Draw shadow slightly offset
        surface.blit(shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 
                            SCREEN_HEIGHT//4 - title.get_height()//2 + 3))
        
        # Draw main title with pulse
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2 - pulse_offset, 
                           SCREEN_HEIGHT//4 - title.get_height()//2 - pulse_offset))
        
        # Draw subtitle
        subtitle = self.menu_font.render("Ascend from the Depths", True, GOLD)
        surface.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 
                              SCREEN_HEIGHT//4 + title.get_height()//2 + 10))
        
        if self.show_character_creation:
            self._draw_character_creation(surface)
        elif self.show_continue_menu:
            self._draw_continue_menu(surface)
        else:
            self._draw_main_menu(surface)
        
        # Draw messages
        if hasattr(self.game, 'messages') and self.game.messages:
            last_message = self.game.messages[-1]
            message = self.info_font.render(last_message, True, WHITE)
            surface.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT - 30))
    
    def _draw_main_menu(self, surface):
        """Draw main menu options"""
        for i, option in enumerate(self.options):
            color = RED if i == self.selected else WHITE
            text = self.menu_font.render(option, True, color)
            
            # Add subtle vertical motion to selected option
            y_offset = 0
            if i == self.selected:
                pulse = (pygame.time.get_ticks() % 1000) / 1000  # 0 to 1 over 1 second
                y_offset = int(pulse * 4) - 2  # -2 to 2 pixels
            
            surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 
                              SCREEN_HEIGHT//2 + i * 50 + y_offset))
    
    def _draw_character_creation(self, surface):
        """Draw character creation interface"""
        # Draw semi-transparent background panel
        panel = pygame.Surface((600, 400))
        panel.set_alpha(200)
        panel.fill((30, 20, 20))
        surface.blit(panel, (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150))
        
        # Draw title
        title = self.menu_font.render("Choose Your Class", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 130))
        
        # Draw class options
        x_positions = [SCREEN_WIDTH//4, SCREEN_WIDTH//2, 3*SCREEN_WIDTH//4]
        
        for i, char_class in enumerate(self.char_options):
            color = RED if i == self.char_selected else WHITE
            text = self.menu_font.render(char_class, True, color)
            
            # Position at the three points
            x_pos = x_positions[i] - text.get_width()//2
            y_pos = SCREEN_HEIGHT//2 - 50
            surface.blit(text, (x_pos, y_pos))
            
            # Draw selection indicator (box around selected)
            if i == self.char_selected:
                pygame.draw.rect(surface, RED, 
                               (x_pos - 10, y_pos - 5, 
                                text.get_width() + 20, text.get_height() + 10), 
                               2)
                
                # Draw class description
                desc = self.char_descriptions[char_class]
                desc_wrapped = self._wrap_text(desc, self.info_font, 500)
                
                for j, line in enumerate(desc_wrapped):
                    desc_text = self.info_font.render(line, True, WHITE)
                    surface.blit(desc_text, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 50 + j * 25))
        
        # Draw class stats visualization
        stats = {
            "Crusader": {"HP": 70, "ATK": 70, "DEF": 60, "SPD": 50},
            "Prophet": {"HP": 50, "ATK": 80, "DEF": 40, "SPD": 70},
            "Templar": {"HP": 90, "ATK": 50, "DEF": 80, "SPD": 30}
        }
        
        selected_stats = stats[self.char_options[self.char_selected]]
        stat_y = SCREEN_HEIGHT//2 + 150
        
        for i, (stat, value) in enumerate(selected_stats.items()):
            # Stat name
            stat_text = self.info_font.render(stat, True, WHITE)
            surface.blit(stat_text, (SCREEN_WIDTH//2 - 200 + i * 100, stat_y))
            
            # Stat bar
            bar_y = stat_y + 25
            pygame.draw.rect(surface, (50, 50, 50), 
                           (SCREEN_WIDTH//2 - 200 + i * 100, bar_y, 20, 100))
            pygame.draw.rect(surface, self._get_stat_color(stat), 
                           (SCREEN_WIDTH//2 - 200 + i * 100, bar_y + (100 - value), 20, value))
        
        # Draw instructions
        inst_text = self.info_font.render("Use LEFT/RIGHT to select, ENTER to confirm, ESC to cancel", True, WHITE)
        surface.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, SCREEN_HEIGHT//2 + 280))
    
    def _draw_continue_menu(self, surface):
        """Draw continue game menu"""
        # Draw semi-transparent background panel
        panel = pygame.Surface((600, 400))
        panel.set_alpha(200)
        panel.fill((30, 20, 20))
        surface.blit(panel, (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150))
        
        # Draw title
        title = self.menu_font.render("Load Game", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 130))
        
        # Draw save slots
        for i, slot in enumerate(self.save_slots):
            color = RED if i == self.continue_selected else WHITE
            
            # Show slot info if save exists
            if self.save_info[i]:
                info = self.save_info[i]
                text = self.menu_font.render(f"Slot {slot}: {info['player_name']} (Level {info['player_level']})", True, color)
            else:
                text = self.menu_font.render(f"Slot {slot}: Empty", True, color)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50 + i * 80))
            surface.blit(text, text_rect)
            
            # Show additional info if save exists
            if self.save_info[i]:
                info = self.save_info[i]
                
                info_text = self.info_font.render(
                    f"Class: {info['player_class']} | Area: {info['area']}", 
                    True, color
                )
                info_rect = info_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20 + i * 80))
                surface.blit(info_text, info_rect)
        
        # Draw instructions
        inst_text = self.info_font.render("Press ENTER to load, ESC to cancel", True, WHITE)
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 200))
        surface.blit(inst_text, inst_rect)
    
    def _get_stat_color(self, stat):
        """Get color for stat visualization"""
        colors = {
            "HP": (255, 50, 50),   # Red
            "ATK": (255, 155, 0),  # Orange
            "DEF": (50, 100, 255), # Blue
            "SPD": (50, 255, 50)   # Green
        }
        return colors.get(stat, (255, 255, 255))
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within a certain width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Try adding this word to the current line
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Line is full, start a new one
                lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
      
