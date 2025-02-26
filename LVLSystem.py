import random
import pygame
import numpy as np
from enum import Enum

# Constants
TILE_SIZE = 32
ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 10
MIN_ROOMS = 8
MAX_ROOMS = 12
MONSTER_CHANCE = 0.8  # 80% chance of monsters per room
ITEM_CHANCE = 0.3  # 30% chance of items per room

class TileType(Enum):
    """Enum for different tile types"""
    WALL = 0
    FLOOR = 1
    DOOR = 2
    STAIRS_UP = 3
    STAIRS_DOWN = 4
    PLAYER = 5  # Player starting position
    BOSS = 6  # Boss location
    CHEST = 7  # Treasure chest
    TRAP = 8  # Trap
    SPECIAL = 9  # Special encounter

class Room:
    """A rectangular room in the dungeon"""
    def __init__(self, x, y, width, height, room_type="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type  # normal, boss, special, entrance, exit
        self.connected = False
        self.enemies = []
        self.items = []
        self.features = []  # Special features like altars, shrines, etc.
    
    def center(self):
        """Return the center coordinates of the room"""
        center_x = (self.x + self.width // 2)
        center_y = (self.y + self.height // 2)
        return (center_x, center_y)
    
    def intersects(self, other):
        """Check if this room intersects with another room"""
        return (self.x <= other.x + other.width and
                self.x + self.width >= other.x and
                self.y <= other.y + other.height and
                self.y + self.height >= other.y)
    
    def place_enemies(self, dungeon_level, area_index):
        """Place enemies in the room based on difficulty"""
        if self.room_type == "boss":
            # Place a boss
            self.enemies.append({
                "type": "boss",
                "pos": self.center(),
                "level": dungeon_level + 2 + area_index
            })
            return
        
        # Determine number of enemies based on room size and difficulty
        room_area = self.width * self.height
        base_enemies = max(1, room_area // 25)  # 1 enemy per 25 tiles
        difficulty_mod = min(3, max(0, dungeon_level + area_index // 2))
        
        num_enemies = random.randint(
            max(0, base_enemies - 1), 
            base_enemies + difficulty_mod
        )
        
        for _ in range(num_enemies):
            # Place enemy at random position in room
            x = random.randint(self.x + 1, self.x + self.width - 2)
            y = random.randint(self.y + 1, self.y + self.height - 2)
            
            self.enemies.append({
                "type": "normal",
                "pos": (x, y),
                "level": max(1, dungeon_level + random.randint(-1, 1))
            })
    
    def place_items(self, dungeon_level):
        """Place items in the room"""
        # Chance based on room type
        if self.room_type == "boss":
            # Guaranteed item after boss
            item_chance = 1.0
        elif self.room_type == "special":
            # Higher chance in special rooms
            item_chance = 0.6
        else:
            # Normal chance in regular rooms
            item_chance = ITEM_CHANCE
        
        # Determine if room gets an item
        if random.random() < item_chance:
            # Place item at random position in room
            x = random.randint(self.x + 1, self.x + self.width - 2)
            y = random.randint(self.y + 1, self.y + self.height - 2)
            
            # Item type based on rarity roll
            rarity_roll = random.random()
            if rarity_roll < 0.6:  # 60% common
                item_type = "common"
            elif rarity_roll < 0.85:  # 25% uncommon
                item_type = "uncommon"
            elif rarity_roll < 0.95:  # 10% rare
                item_type = "rare"
            elif rarity_roll < 0.99:  # 4% epic
                item_type = "epic"
            else:  # 1% legendary
                item_type = "legendary"
            
            self.items.append({
                "type": item_type,
                "pos": (x, y),
                "level": dungeon_level
            })
    
    def add_special_feature(self, area_index):
        """Add special features to the room"""
        if self.room_type == "special":
            # Only add features to special rooms
            feature_types = [
                "altar",
                "shrine",
                "fountain",
                "statue",
                "library"
            ]
            
            feature_type = random.choice(feature_types)
            
            # Place feature at center of room
            self.features.append({
                "type": feature_type,
                "pos": self.center(),
                "area": area_index
            })


class Dungeon:
    """A dungeon level with multiple rooms"""
    def __init__(self, width, height, player_level=1, area_index=0):
        self.width = width
        self.height = height
        self.player_level = player_level
        self.area_index = area_index
        self.grid = np.zeros((height, width), dtype=int)
        self.rooms = []
        self.entrance = None
        self.exit = None
        self.objects = []  # Interactive objects (doors, chests, etc)
        self.enemies = []  # List of enemies in the dungeon
        self.items = []  # List of items in the dungeon
        
        # Theme/environment based on area index
        self.theme = self._get_theme_for_area(area_index)
    
    def _get_theme_for_area(self, area_index):
        """Get the theme details based on area (hell layer) index"""
        themes = [
            {
                "name": "The Gates of Hell",
                "description": "The entrance to the underworld, a desolate wasteland with fire and brimstone.",
                "primary_color": (139, 0, 0),  # dark red
                "secondary_color": (210, 105, 30),  # chocolate
                "floor_texture": "stone_floor",
                "wall_texture": "hell_wall_1",
                "enemy_types": ["lesser_demon", "imp", "hellhound"]
            },
            {
                "name": "The Burning Plains",
                "description": "Endless plains of fire and suffering.",
                "primary_color": (178, 34, 34),  # firebrick
                "secondary_color": (255, 140, 0),  # dark orange
                "floor_texture": "burning_floor",
                "wall_texture": "hell_wall_2",
                "enemy_types": ["tormentor", "fallen_soul", "abyssal_beast"]
            },
            {
                "name": "The Frozen Depths",
                "description": "A realm of biting cold and frozen souls.",
                "primary_color": (70, 130, 180),  # steel blue
                "secondary_color": (176, 196, 222),  # light steel blue
                "floor_texture": "ice_floor",
                "wall_texture": "ice_wall",
                "enemy_types": ["vengeful_spirit", "corrupted_angel", "flame_demon"]
            },
            {
                "name": "The Abyss of Pain",
                "description": "A cavernous realm where suffering is endless.",
                "primary_color": (128, 0, 128),  # purple
                "secondary_color": (75, 0, 130),  # indigo
                "floor_texture": "flesh_floor",
                "wall_texture": "flesh_wall",
                "enemy_types": ["pain_bringer", "shadow_lurker", "despair_wraith"]
            },
            {
                "name": "The Void of Souls",
                "description": "An empty void where souls drift in eternal darkness.",
                "primary_color": (25, 25, 112),  # midnight blue
                "secondary_color": (0, 0, 139),  # dark blue
                "floor_texture": "void_floor",
                "wall_texture": "void_wall",
                "enemy_types": ["soul_eater", "void_spawn", "infernal_beast"]
            },
            {
                "name": "The Fallen Kingdom",
                "description": "The ruined kingdom of those who once defied the heavens.",
                "primary_color": (72, 61, 139),  # dark slate blue
                "secondary_color": (106, 90, 205),  # slate blue
                "floor_texture": "marble_floor",
                "wall_texture": "ruined_wall",
                "enemy_types": ["archfiend", "dark_seraph", "hell_knight"]
            },
            {
                "name": "Satan's Throne",
                "description": "The final level, home to the ruler of hell.",
                "primary_color": (128, 0, 0),  # maroon
                "secondary_color": (255, 215, 0),  # gold
                "floor_texture": "throne_floor",
                "wall_texture": "throne_wall",
                "enemy_types": ["demon_lord", "fallen_archangel", "apocalypse_beast"]
            }
        ]
        
        return themes[min(area_index, len(themes) - 1)]
    
    def generate(self):
        """Generate a new dungeon level"""
        # Fill the entire grid with walls
        self.grid.fill(TileType.WALL.value)
        
        # Determine number of rooms
        if self.area_index == 6:  # Final area
            # Final area has a fixed layout
            self._generate_final_area()
            return
        
        num_rooms = random.randint(MIN_ROOMS, MAX_ROOMS)
        
        # Place entrance room
        entrance_room = self._add_room(room_type="entrance")
        self.entrance = entrance_room.center()
        
        # Add regular rooms
        for i in range(1, num_rooms - 1):
            room_type = "special" if random.random() < 0.2 else "normal"
            self._add_room(room_type=room_type)
        
        # Place exit room (ensure it's far from entrance)
        exit_room = self._add_room(min_distance=max(self.width, self.height) // 3, room_type="exit")
        self.exit = exit_room.center()
        
        # Connect all rooms
        self._connect_rooms()
        
        # Place stairs
        self.grid[self.entrance[1]][self.entrance[0]] = TileType.STAIRS_UP.value
        self.grid[self.exit[1]][self.exit[0]] = TileType.STAIRS_DOWN.value
        
        # Place objects, enemies, and items
        self._populate_dungeon()
        
        return self
    
    def _generate_final_area(self):
        """Generate the final area with a fixed layout"""
        # Create a more symmetrical, epic layout for the final boss
        
        # Central throne room
        throne_room = Room(self.width // 2 - 5, self.height // 2 - 5, 10, 10, "boss")
        self.rooms.append(throne_room)
        
        # Fill room with floor tiles
        for y in range(throne_room.y, throne_room.y + throne_room.height):
            for x in range(throne_room.x, throne_room.x + throne_room.width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = TileType.FLOOR.value
        
        # Add boss
        throne_room.enemies.append({
            "type": "boss",
            "pos": throne_room.center(),
            "level": self.player_level + 5  # Final boss is much stronger
        })
        
        # Add antechambers/side rooms
        side_rooms = [
            Room(throne_room.x - 8, throne_room.y, 6, 6, "special"),
            Room(throne_room.x + throne_room.width + 2, throne_room.y, 6, 6, "special"),
            Room(throne_room.x, throne_room.y - 8, 6, 6, "entrance")
        ]
        
        for room in side_rooms:
            self.rooms.append(room)
            # Fill room with floor tiles
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.grid[y][x] = TileType.FLOOR.value
            
            # Place enemies and items
            if room.room_type != "entrance":
                room.place_enemies(self.player_level, self.area_index)
                room.place_items(self.player_level)
                room.add_special_feature(self.area_index)
        
        # Connect the rooms with corridors
        for room in side_rooms:
            self._create_corridor(room.center(), throne_room.center())
        
        # Set entrance
        self.entrance = side_rooms[2].center()
        self.grid[self.entrance[1]][self.entrance[0]] = TileType.STAIRS_UP.value
        
        # Collect all enemies and items
        self._populate_dungeon()
    
    def _add_room(self, min_distance=0, room_type="normal"):
        """Add a room to the dungeon, ensuring it's at least min_distance from other rooms"""
        # For entrance/exit rooms, make them slightly larger
        if room_type in ["entrance", "exit"]:
            width = random.randint(ROOM_MIN_SIZE + 1, ROOM_MAX_SIZE + 1)
            height = random.randint(ROOM_MIN_SIZE + 1, ROOM_MAX_SIZE + 1)
        else:
            width = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            height = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        
        for attempt in range(100):  # Limit attempts to prevent infinite loops
            # Place room at random position with 1-tile buffer from edges
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            
            # Create the new room
            new_room = Room(x, y, width, height, room_type)
            
            # Check if it intersects with any existing rooms
            for room in self.rooms:
                if new_room.intersects(room):
                    break
                
                # For entrance/exit, check distance
                if min_distance > 0:
                    center1 = new_room.center()
                    center2 = room.center()
                    distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
                    if distance < min_distance:
                        break
            else:
                # If we got here, there's no intersection
                # Add floor tiles for the room
                for room_y in range(y, y + height):
                    for room_x in range(x, x + width):
                        self.grid[room_y][room_x] = TileType.FLOOR.value
                
                # Add room to the list
                self.rooms.append(new_room)
                
                # Add enemies and items
                if room_type != "entrance":  # Don't place enemies at entrance
                    if random.random() < MONSTER_CHANCE:
                        new_room.place_enemies(self.player_level, self.area_index)
                    
                    new_room.place_items(self.player_level)
                    
                    if room_type == "special":
                        new_room.add_special_feature(self.area_index)
                
                return new_room
        
        # If we couldn't place a room after 100 attempts, create a small room
        # in an available corner as a fallback
        fallback_size = ROOM_MIN_SIZE
        corner_options = [
            (1, 1),  # Top-left
            (1, self.height - fallback_size - 1),  # Bottom-left
            (self.width - fallback_size - 1, 1),  # Top-right
            (self.width - fallback_size - 1, self.height - fallback_size - 1)  # Bottom-right
        ]
        
        for x, y in corner_options:
            new_room = Room(x, y, fallback_size, fallback_size, room_type)
            for room in self.rooms:
                if new_room.intersects(room):
                    break
            else:
                # Add floor tiles
                for room_y in range(y, y + fallback_size):
                    for room_x in range(x, x + fallback_size):
                        self.grid[room_y][room_x] = TileType.FLOOR.value
                
                self.rooms.append(new_room)
                return new_room
        
        # If all else fails, place it in the center
        x = self.width // 2 - fallback_size // 2
        y = self.height // 2 - fallback_size // 2
        new_room = Room(x, y, fallback_size, fallback_size, room_type)
        
        # Add floor tiles
        for room_y in range(y, y + fallback_size):
            for room_x in range(x, x + fallback_size):
                self.grid[room_y][room_x] = TileType.FLOOR.value
        
        self.rooms.append(new_room)
        return new_room
    
    def _connect_rooms(self):
        """Connect all rooms with corridors"""
        # Sort rooms by distance to entrance
        entrance_room = None
        for room in self.rooms:
            if room.room_type == "entrance":
                entrance_room = room
                break
        
        if not entrance_room:
            entrance_room = self.rooms[0]
        
        # Mark entrance room as connected
        entrance_room.connected = True
        
        # Connect all other rooms
        unconnected = [room for room in self.rooms if not room.connected]
        
        while unconnected:
            # Find the closest unconnected room to any connected room
            closest_distance = float('inf')
            closest_pair = (None, None)
            
            for uncon_room in unconnected:
                for con_room in [r for r in self.rooms if r.connected]:
                    center1 = uncon_room.center()
                    center2 = con_room.center()
                    distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
                    
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_pair = (uncon_room, con_room)
            
            # Connect the closest pair
            if closest_pair[0] and closest_pair[1]:
                self._create_corridor(closest_pair[0].center(), closest_pair[1].center())
                closest_pair[0].connected = True
                unconnected.remove(closest_pair[0])
    
    def _create_corridor(self, point1, point2):
        """Create a corridor between two points"""
        x1, y1 = point1
        x2, y2 = point2
        
        # Determine horizontal or vertical first (70% chance horizontal first)
        if random.random() < 0.7:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.grid[y1][x] = TileType.FLOOR.value
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.grid[y][x2] = TileType.FLOOR.value
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.grid[y][x1] = TileType.FLOOR.value
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.grid[y2][x] = TileType.FLOOR.value
        
        # Place doors at room entrances (20% chance)
        if random.random() < 0.2:
            # Find a suitable door location near one of the rooms
            for room in self.rooms:
                if room.x <= x1 <= room.x + room.width and room.y <= y1 <= room.y + room.height:
                    # Point1 is in a room, check bordering tiles
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x1 + dx, y1 + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny][nx] == TileType.FLOOR.value:
                                self.grid[ny][nx] = TileType.DOOR.value
                                self.objects.append({
                                    "type": "door",
                                    "pos": (nx, ny),
                                    "state": "closed"
                                })
                                break
                    break
    
    def _populate_dungeon(self):
        """Collect all enemies and items from rooms"""
        self.enemies = []
        self.items = []
        
        for room in self.rooms:
            for enemy in room.enemies:
                self.enemies.append(enemy)
            
            for item in room.items:
                self.items.append(item)
    
    def add_traps(self):
        """Add traps to the dungeon"""
        # Number of traps based on area index
        num_traps = 2 + self.area_index
        
        for _ in range(num_traps):
            # Find a random floor tile that's not at entrance or exit
            for _ in range(50):  # Limit attempts
                x = random.randint(1, self.width - 2)
                y = random.randint(1, self.height - 2)
                
                # Check if it's a floor tile
                if self.grid[y][x] == TileType.FLOOR.value:
                    # Make sure it's not the entrance or exit
                    if (x, y) != self.entrance and (x, y) != self.exit:
                        # Check it's not on top of an enemy or item
                        for enemy in self.enemies:
                            if enemy["pos"] == (x, y):
                                break
                        else:
                            for item in self.items:
                                if item["pos"] == (x, y):
                                    break
                            else:
                                # Place trap
                                self.grid[y][x] = TileType.TRAP.value
                                break
    
    def get_walkable_neighbors(self, x, y):
        """Get walkable neighboring tiles"""
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.grid[ny][nx] in [TileType.FLOOR.value, TileType.DOOR.value, 
                                        TileType.STAIRS_UP.value, TileType.STAIRS_DOWN.value]:
                    neighbors.append((nx, ny))
        return neighbors
    
    def find_path(self, start, end):
        """Find a path between two points using A* algorithm"""
        # If start or end aren't walkable, return None
        if (start[0] < 0 or start[0] >= self.width or start[1] < 0 or start[1] >= self.height or
            end[0] < 0 or end[0] >= self.width or end[1] < 0 or end[1] >= self.height or
            self.grid[start[1]][start[0]] == TileType.WALL.value or
            self.grid[end[1]][end[0]] == TileType.WALL.value):
            return None
        
        # A* pathfinding
        open_set = [(start, 0)]  # (position, priority)
        came_from = {}
        g_score = {start: 0}
        
        while open_set:
            open_set.sort(key=lambda x: x[1])
            current, _ = open_set.pop(0)
            
            if current == end:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            for neighbor in self.get_walkable_neighbors(*current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + ((neighbor[0] - end[0])**2 + (neighbor[1] - end[1])**2)**0.5
                    open_set.append((neighbor, f_score))
        
        return None  # No path found

    def render(self, surface, viewport, player_pos, tileset=None):
        """Render the dungeon to a pygame surface"""
        viewport_x, viewport_y, viewport_width, viewport_height = viewport
        
        # Calculate which tiles are visible in the viewport
        start_x = max(0, viewport_x // TILE_SIZE)
        end_x = min(self.width, (viewport_x + viewport_width) // TILE_SIZE + 1)
        start_y = max(0, viewport_y // TILE_SIZE)
        end_y = min(self.height, (viewport_y + viewport_height) // TILE_SIZE + 1)
        
        # Default colors for different tile types
        colors = {
            TileType.WALL.value: self.theme["primary_color"],
            TileType.FLOOR.value: self.theme["secondary_color"],
            TileType.DOOR.value: (139, 69, 19),  # brown
            TileType.STAIRS_UP.value: (0, 255, 0),  # green
            TileType.STAIRS_DOWN.value: (255, 0, 0),  # red
            TileType.PLAYER.value: (0, 0, 255),  # blue
            TileType.BOSS.value: (148, 0, 211),  # dark violet
            TileType.CHEST.value: (255, 215, 0),  # gold
            TileType.TRAP.value: (255, 0, 255),  # magenta
            TileType.SPECIAL.value: (0, 255, 255)  # cyan
        }
        
        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.grid[y][x]
                
                # Calculate screen position
                screen_x = x * TILE_SIZE - viewport_x
                screen_y = y * TILE_SIZE - viewport_y
                
                # Draw tile
                if tileset:
                    # If we have a tileset, use it
                    tile_id = tile_type
                    tile_rect = pygame.Rect(
                        (tile_id % tileset.columns) * TILE_SIZE,
                        (tile_id // tileset.columns) * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    surface.blit(tileset.image, (screen_x, screen_y), tile_rect)
                else:
                    # Otherwise use colored rectangles
                    color = colors.get(tile_type, (128, 128, 128))
                    pygame.draw.rect(surface, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                    
                    # Add details for certain tile types
                    if tile_type == TileType.DOOR.value:
                        pygame.draw.rect(surface, (101, 67, 33), 
                                        (screen_x + 5, screen_y + 5, TILE_SIZE - 10, TILE_SIZE - 10))
                    elif tile_type == TileType.STAIRS_UP.value:
                        pygame.draw.polygon(surface, (200, 200, 200),
                                          [(screen_x + 5, screen_y + TILE_SIZE - 5),
                                           (screen_x + TILE_SIZE - 5, screen_y + TILE_SIZE - 5),
                                           (screen_x + TILE_SIZE // 2, screen_y + 5)])
                    elif tile_type == TileType.STAIRS_DOWN.value:
                        pygame.draw.polygon(surface, (200, 200, 200),
                                          [(screen_x + 5, screen_y + 5),
                                           (screen_x + TILE_SIZE - 5, screen_y + 5),
                                           (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE - 5)])
        
        # Render player
        player_screen_x = player_pos[0] * TILE_SIZE - viewport_x
        player_screen_y = player_pos[1] * TILE_SIZE - viewport_y
        pygame.draw.circle(surface, (0, 0, 255), 
                         (player_screen_x + TILE_SIZE // 2, player_screen_y + TILE_SIZE // 2), 
                         TILE_SIZE // 2 - 2)
        
        # Render enemies
        for enemy in self.enemies:
            enemy_x, enemy_y = enemy["pos"]
            enemy_screen_x = enemy_x * TILE_SIZE - viewport_x
            enemy_screen_y = enemy_y * TILE_SIZE - viewport_y
            
            # Only render if in viewport
            if (start_x <= enemy_x < end_x and start_y <= enemy_y < end_y):
                if enemy["type"] == "boss":
                    # Draw boss (larger)
                    pygame.draw.circle(surface, (255, 0, 0), 
                                     (enemy_screen_x + TILE_SIZE // 2, enemy_screen_y + TILE_SIZE // 2), 
                                     TILE_SIZE // 2)
                else:
                    # Draw regular enemy
                    pygame.draw.circle(surface, (200, 0, 0), 
                                     (enemy_screen_x + TILE_SIZE // 2, enemy_screen_y + TILE_SIZE // 2), 
                                     TILE_SIZE // 3)
        
        # Render items
        for item in self.items:
            item_x, item_y = item["pos"]
            item_screen_x = item_x * TILE_SIZE - viewport_x
            item_screen_y = item_y * TILE_SIZE - viewport_y
            
            # Only render if in viewport
            if (start_x <= item_x < end_x and start_y <= item_y < end_y):
                # Color based on rarity
                item_colors = {
                    "common": (200, 200, 200),  # gray
                    "uncommon": (0, 200, 0),    # green
                    "rare": (0, 0, 200),        # blue
                    "epic": (128, 0, 128),      # purple
                    "legendary": (255, 165, 0)  # orange
                }
                color = item_colors.get(item["type"], (255, 255, 255))
                
                # Draw item
                pygame.draw.rect(surface, color, 
                               (item_screen_x + TILE_SIZE // 4, item_screen_y + TILE_SIZE // 4, 
                                TILE_SIZE // 2, TILE_SIZE // 2))


class DungeonManager:
    """Manages the different dungeon levels/areas"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.dungeons = []  # List of generated dungeons
        self.current_area = 0  # Current area index
        self.player_pos = None  # Player position in current dungeon
        self.player_level = 1
        
        # Heat system (difficulty modifiers)
        self.heat_level = 0
        self.active_modifiers = []
    
    def generate_area(self, area_index, player_level):
        """Generate a specific area"""
        dungeon = Dungeon(self.width, self.height, player_level, area_index)
        dungeon.generate()
        
        # Apply heat modifiers
        self._apply_heat_modifiers(dungeon)
        
        return dungeon
    
    def generate_all_areas(self, player_level):
        """Generate all areas (7 layers of hell)"""
        self.dungeons = []
        self.player_level = player_level
        
        for i in range(7):  # 7 layers of hell
            dungeon = self.generate_area(i, player_level)
            self.dungeons.append(dungeon)
        
        # Set initial player position at entrance of first dungeon
        self.current_area = 0
        self.player_pos = self.dungeons[0].entrance
    
    def enter_area(self, area_index):
        """Enter a specific area"""
        if 0 <= area_index < len(self.dungeons):
            self.current_area = area_index
            
            # Place player at entrance or exit depending on if going up or down
            if area_index == 0 or self.player_pos is None:
                # First area or no previous position - start at entrance
                self.player_pos = self.dungeons[area_index].entrance
            else:
                # Check if coming from above or below
                if area_index > self.current_area:
                    # Going down - place at entrance
                    self.player_pos = self.dungeons[area_index].entrance
                else:
                    # Going up - place at exit
                    self.player_pos = self.dungeons[area_index].exit
            
            return True
        return False
    
    def move_player(self, dx, dy):
        """Move player by delta if possible"""
        dungeon = self.dungeons[self.current_area]
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        # Check if move is valid
        if (0 <= new_x < dungeon.width and 0 <= new_y < dungeon.height and
            dungeon.grid[new_y][new_x] != TileType.WALL.value):
            
            # Check special tile interactions
            tile_type = dungeon.grid[new_y][new_x]
            
            if tile_type == TileType.DOOR.value:
                # Check if door is open
                for obj in dungeon.objects:
                    if obj["type"] == "door" and obj["pos"] == (new_x, new_y):
                        if obj["state"] == "closed":
                            # Open the door
                            obj["state"] = "open"
                            dungeon.grid[new_y][new_x] = TileType.FLOOR.value
                        break
            
            elif tile_type == TileType.STAIRS_UP.value:
                # Try to go up a level
                if self.current_area > 0:
                    self.enter_area(self.current_area - 1)
                    return True
            
            elif tile_type == TileType.STAIRS_DOWN.value:
                # Try to go down a level
                if self.current_area < len(self.dungeons) - 1:
                    self.enter_area(self.current_area + 1)
                    return True
            
            # Move player
            self.player_pos = (new_x, new_y)
            
            # Check for items
            for i, item in enumerate(dungeon.items):
                if item["pos"] == (new_x, new_y):
                    # Return item info for pickup
                    picked_item = item
                    dungeon.items.pop(i)
                    return ("item", picked_item)
            
            # Check for enemies
            for i, enemy in enumerate(dungeon.enemies):
                if enemy["pos"] == (new_x, new_y):
                    # Return enemy info for combat
                    encountered_enemy = enemy
                    return ("enemy", encountered_enemy)
            
            # Check for traps
            if tile_type == TileType.TRAP.value:
                # Reset the tile to floor
                dungeon.grid[new_y][new_x] = TileType.FLOOR.value
                return ("trap", None)
            
            return True
        
        return False
    
    def get_current_dungeon(self):
        """Get the current dungeon"""
        return self.dungeons[self.current_area]
    
    def increase_heat(self, amount=1):
        """Increase the heat level and add modifiers"""
        self.heat_level += amount
        
        # Add new modifiers based on heat level
        potential_modifiers = [
            {"name": "More Enemies", "effect": "increase_enemies", "min_heat": 1},
            {"name": "Stronger Enemies", "effect": "stronger_enemies", "min_heat": 2},
            {"name": "Less Health", "effect": "less_health", "min_heat": 3},
            {"name": "More Traps", "effect": "more_traps", "min_heat": 4},
            {"name": "Less Items", "effect": "less_items", "min_heat": 5},
            {"name": "Elite Enemies", "effect": "elite_enemies", "min_heat": 6},
            {"name": "No Healing", "effect": "no_healing", "min_heat": 7},
            {"name": "Time Limit", "effect": "time_limit", "min_heat": 8},
            {"name": "Double Bosses", "effect": "double_bosses", "min_heat": 9},
            {"name": "Extreme Mode", "effect": "extreme_mode", "min_heat": 10}
        ]
        
        # Check for new modifiers to activate
        for modifier in potential_modifiers:
            if (modifier["min_heat"] <= self.heat_level and 
                modifier not in self.active_modifiers):
                self.active_modifiers.append(modifier)
                
                # Regenerate dungeons with new modifiers
                self.generate_all_areas(self.player_level)
                break
    
    def _apply_heat_modifiers(self, dungeon):
        """Apply active heat modifiers to a dungeon"""
        for modifier in self.active_modifiers:
            if modifier["effect"] == "increase_enemies":
                # Add 50% more enemies
                additional_enemies = len(dungeon.enemies) // 2
                for _ in range(additional_enemies):
                    # Find a suitable position
                    for room in dungeon.rooms:
                        if room.room_type != "entrance" and room.room_type != "exit":
                            x = random.randint(room.x + 1, room.x + room.width - 2)
                            y = random.randint(room.y + 1, room.y + room.height - 2)
                            
                            dungeon.enemies.append({
                                "type": "normal",
                                "pos": (x, y),
                                "level": max(1, dungeon.player_level + random.randint(-1, 1))
                            })
                            break
            
            elif modifier["effect"] == "stronger_enemies":
                # Increase enemy levels by 2
                for enemy in dungeon.enemies:
                    enemy["level"] += 2
            
            elif modifier["effect"] == "more_traps":
                # Double the number of traps
                dungeon.add_traps()  # Call twice
                dungeon.add_traps()
            
            elif modifier["effect"] == "less_items":
                # Remove 50% of items
                num_to_remove = len(dungeon.items) // 2
                if num_to_remove > 0:
                    for _ in range(num_to_remove):
                        if dungeon.items:
                            dungeon.items.pop(random.randrange(len(dungeon.items)))
            
            elif modifier["effect"] == "elite_enemies":
                # Convert 25% of enemies to elite (higher level)
                num_to_convert = max(1, len(dungeon.enemies) // 4)
                for _ in range(num_to_convert):
                    if dungeon.enemies:
                        idx = random.randrange(len(dungeon.enemies))
                        if dungeon.enemies[idx]["type"] != "boss":
                            enemy = dungeon.enemies[idx]
                            enemy["type"] = "elite"
                            enemy["level"] += 3
            
            elif modifier["effect"] == "double_bosses":
                # Add a second boss to boss rooms
                for room in dungeon.rooms:
                    if room.room_type == "boss":
                        for enemy in room.enemies:
                            if enemy["type"] == "boss":
                                # Find position for second boss
                                center_x, center_y = room.center()
                                offset_x = random.randint(-2, 2)
                                offset_y = random.randint(-2, 2)
                                pos = (center_x + offset_x, center_y + offset_y)
                                
                                # Add second boss
                                dungeon.enemies.append({
                                    "type": "boss",
                                    "pos": pos,
                                    "level": enemy["level"] - 1  # Slightly weaker than main boss
                                })
                                break
            
            elif modifier["effect"] == "extreme_mode":
                # Combined effects: more traps, stronger enemies, less items
                dungeon.add_traps()
                dungeon.add_traps()
                
                for enemy in dungeon.enemies:
                    enemy["level"] += 3
                
                num_to_remove = len(dungeon.items) * 3 // 4
                if num_to_remove > 0:
                    for _ in range(num_to_remove):
                        if dungeon.items:
                            dungeon.items.pop(random.randrange(len(dungeon.items)))


# Example usage
if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Demonbane - Dungeon Generator Test")
    clock = pygame.time.Clock()
    
    # Create dungeon manager
    dungeon_manager = DungeonManager(50, 50)
    dungeon_manager.generate_all_areas(player_level=1)
    
    # Game loop
    running = True
    viewport_x, viewport_y = 0, 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Movement controls
                if event.key == pygame.K_LEFT:
                    dungeon_manager.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    dungeon_manager.move_player(1, 0)
                elif event.key == pygame.K_UP:
                    dungeon_manager.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    dungeon_manager.move_player(0, 1)
                elif event.key == pygame.K_h:
                    # Test heat system
                    dungeon_manager.increase_heat()
                    print(f"Heat increased to {dungeon_manager.heat_level}")
                    print(f"Active modifiers: {[m['name'] for m in dungeon_manager.active_modifiers]}")
        
        # Center viewport on player
        dungeon = dungeon_manager.get_current_dungeon()
        player_x, player_y = dungeon_manager.player_pos
        viewport_x = max(0, player_x * TILE_SIZE - 400)
        viewport_y = max(0, player_y * TILE_SIZE - 300)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Render current dungeon
        dungeon.render(screen, (viewport_x, viewport_y, 800, 600), dungeon_manager.player_pos)
        
        # Display current level
        font = pygame.font.SysFont("Arial", 24)
        level_text = font.render(f"Level {dungeon_manager.current_area + 1}: {dungeon.theme['name']}", True, (255, 255, 255))
        screen.blit(level_text, (20, 20))
        
        # Display heat level
        heat_text = font.render(f"Heat: {dungeon_manager.heat_level}", True, (255, 255, 255))
        screen.blit(heat_text, (20, 50))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
  
