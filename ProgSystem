import json
import random

class Character:
    """Base class for all characters in the game (player, enemies, NPCs)"""
    def __init__(self, name, level=1):
        self.name = name
        self.level = level
        
        # Base stats
        self.max_health = 0
        self.health = 0
        self.attack = 0
        self.defense = 0
        self.speed = 0
        
        # Additional stats
        self.critical_chance = 5  # Percentage
        self.critical_damage = 150  # Percentage
        self.dodge_chance = 5  # Percentage
        
        # Status effects
        self.status_effects = []
        
    def is_alive(self):
        """Check if character is alive"""
        return self.health > 0
    
    def take_damage(self, amount):
        """Take damage and return the actual damage dealt"""
        # Calculate damage reduction from defense (simple formula)
        damage_reduction = self.defense / (self.defense + 50)  # Caps at ~50% reduction
        actual_damage = int(amount * (1 - damage_reduction))
        actual_damage = max(1, actual_damage)  # Minimum 1 damage
        
        self.health -= actual_damage
        self.health = max(0, self.health)  # Prevent negative health
        
        return actual_damage
    
    def heal(self, amount):
        """Heal character and return amount healed"""
        before = self.health
        self.health += amount
        self.health = min(self.health, self.max_health)  # Cap at max health
        
        return self.health - before
    
    def calculate_attack_damage(self, target):
        """Calculate attack damage against target"""
        # Base damage is attack stat
        damage = self.attack
        
        # Check for critical hit
        is_critical = random.randint(1, 100) <= self.critical_chance
        if is_critical:
            damage = damage * (self.critical_damage / 100)
        
        return int(damage), is_critical
    
    def add_status_effect(self, effect):
        """Add a status effect to the character"""
        self.status_effects.append(effect)
    
    def update_status_effects(self):
        """Update all status effects and remove expired ones"""
        active_effects = []
        for effect in self.status_effects:
            effect.update()
            if effect.duration > 0:
                active_effects.append(effect)
        
        self.status_effects = active_effects


class Player(Character):
    """Player character class with progression"""
    def __init__(self, name, class_type="Crusader"):
        super().__init__(name)
        self.class_type = class_type
        self.experience = 0
        self.experience_to_level = 100
        self.skill_points = 0
        self.weapons = []
        self.artifacts = []
        self.active_weapon = None
        self.inventory = []
        
        # Initialize stats based on class
        self._initialize_class_stats()
        
        # Special abilities
        self.abilities = []
        self._initialize_class_abilities()
        
        # Equip starting weapon
        self._equip_starting_weapon()
    
    def _initialize_class_stats(self):
        """Initialize stats based on chosen class"""
        if self.class_type == "Crusader":
            self.max_health = 100
            self.health = 100
            self.attack = 15
            self.defense = 10
            self.speed = 8
        elif self.class_type == "Prophet":
            self.max_health = 80
            self.health = 80
            self.attack = 10
            self.defense = 5
            self.speed = 10
        elif self.class_type == "Templar":
            self.max_health = 120
            self.health = 120
            self.attack = 12
            self.defense = 15
            self.speed = 6
    
    def _initialize_class_abilities(self):
        """Initialize abilities based on chosen class"""
        if self.class_type == "Crusader":
            self.abilities = [
                Ability("Divine Strike", 10, target_type="enemy", effect="damage", power=20),
                Ability("Holy Shield", 15, target_type="self", effect="defense_up", power=50, duration=3)
            ]
        elif self.class_type == "Prophet":
            self.abilities = [
                Ability("Smite", 8, target_type="enemy", effect="damage", power=15),
                Ability("Healing Prayer", 12, target_type="self", effect="heal", power=30)
            ]
        elif self.class_type == "Templar":
            self.abilities = [
                Ability("Judgment", 12, target_type="enemy", effect="damage", power=18),
                Ability("Righteous Fury", 20, target_type="self", effect="attack_up", power=40, duration=2)
            ]
    
    def _equip_starting_weapon(self):
        """Equip the starting weapon based on class"""
        if self.class_type == "Crusader":
            weapon = Weapon("Sword of Faith", weapon_type="sword", attack_bonus=5)
        elif self.class_type == "Prophet":
            weapon = Weapon("Staff of Light", weapon_type="staff", attack_bonus=3)
        elif self.class_type == "Templar":
            weapon = Weapon("Holy Mace", weapon_type="mace", attack_bonus=4)
        
        self.weapons.append(weapon)
        self.equip_weapon(weapon)
    
    def gain_experience(self, amount):
        """Gain experience and level up if necessary"""
        self.experience += amount
        
        # Level up if enough experience
        level_ups = 0
        while self.experience >= self.experience_to_level:
            self.experience -= self.experience_to_level
            self.level_up()
            level_ups += 1
            # Increase experience required for next level
            self.experience_to_level = int(self.experience_to_level * 1.5)
        
        return level_ups
    
    def level_up(self):
        """Level up the character"""
        self.level += 1
        self.skill_points += 3
        
        # Stat increases
        self.max_health += int(self.max_health * 0.1)  # 10% increase
        self.health = self.max_health
        self.attack += 2
        self.defense += 1
        self.speed += 1
    
    def equip_weapon(self, weapon):
        """Equip a weapon"""
        if weapon in self.weapons:
            self.active_weapon = weapon
    
    def use_ability(self, ability_index, target=None):
        """Use an ability"""
        if ability_index < 0 or ability_index >= len(self.abilities):
            return False, "Invalid ability index"
        
        ability = self.abilities[ability_index]
        
        # Check if ability can be used
        if ability.cooldown_remaining > 0:
            return False, f"{ability.name} is on cooldown for {ability.cooldown_remaining} turns"
        
        # Start cooldown
        ability.start_cooldown()
        
        # Apply ability effects
        if ability.effect == "damage":
            if target and ability.target_type == "enemy":
                damage = int(ability.power + (self.attack * 0.5))
                return True, (target, damage, f"{self.name} used {ability.name}!")
        
        elif ability.effect == "heal":
            if ability.target_type == "self":
                heal_amount = int(ability.power + (self.level * 2))
                self.heal(heal_amount)
                return True, (self, heal_amount, f"{self.name} used {ability.name} and healed for {heal_amount} HP!")
        
        elif ability.effect == "defense_up":
            if ability.target_type == "self":
                effect = StatusEffect("DefenseUp", duration=ability.duration, 
                                     stats_bonus={"defense": int(self.defense * ability.power / 100)})
                self.add_status_effect(effect)
                return True, (self, ability.power, f"{self.name} used {ability.name} and increased defense!")
        
        elif ability.effect == "attack_up":
            if ability.target_type == "self":
                effect = StatusEffect("AttackUp", duration=ability.duration,
                                     stats_bonus={"attack": int(self.attack * ability.power / 100)})
                self.add_status_effect(effect)
                return True, (self, ability.power, f"{self.name} used {ability.name} and increased attack!")
        
        return False, "Ability couldn't be used"
    
    def spend_skill_points(self, stat, amount=1):
        """Spend skill points to improve a stat"""
        if self.skill_points < amount:
            return False, "Not enough skill points"
        
        if stat == "health":
            self.max_health += 10 * amount
            self.health = self.max_health
        elif stat == "attack":
            self.attack += 2 * amount
        elif stat == "defense":
            self.defense += 2 * amount
        elif stat == "speed":
            self.speed += 1 * amount
        else:
            return False, "Invalid stat"
        
        self.skill_points -= amount
        return True, f"Increased {stat} by spending {amount} skill points"
    
    def add_weapon(self, weapon):
        """Add a weapon to inventory"""
        self.weapons.append(weapon)
    
    def add_artifact(self, artifact):
        """Add an artifact to inventory"""
        self.artifacts.append(artifact)
        # Apply artifact bonuses
        for stat, bonus in artifact.stat_bonuses.items():
            if stat == "max_health":
                self.max_health += bonus
            elif stat == "attack":
                self.attack += bonus
            elif stat == "defense":
                self.defense += bonus
            elif stat == "speed":
                self.speed += bonus
    
    def get_total_stats(self):
        """Get the total stats including equipment and status effects"""
        # Start with base stats
        total_stats = {
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "critical_chance": self.critical_chance,
            "critical_damage": self.critical_damage,
            "dodge_chance": self.dodge_chance
        }
        
        # Add weapon bonuses
        if self.active_weapon:
            total_stats["attack"] += self.active_weapon.attack_bonus
            
            # Add weapon special effects
            for stat, bonus in self.active_weapon.stat_bonuses.items():
                if stat in total_stats:
                    total_stats[stat] += bonus
        
        # Add status effect bonuses
        for effect in self.status_effects:
            for stat, bonus in effect.stats_bonus.items():
                if stat in total_stats:
                    total_stats[stat] += bonus
        
        return total_stats
    
    def save_to_dict(self):
        """Convert player data to dictionary for saving"""
        data = {
            "name": self.name,
            "class_type": self.class_type,
            "level": self.level,
            "experience": self.experience,
            "experience_to_level": self.experience_to_level,
            "skill_points": self.skill_points,
            "max_health": self.max_health,
            "health": self.health,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "critical_chance": self.critical_chance,
            "critical_damage": self.critical_damage,
            "dodge_chance": self.dodge_chance,
            "weapons": [weapon.to_dict() for weapon in self.weapons],
            "active_weapon": self.weapons.index(self.active_weapon) if self.active_weapon else -1,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "abilities": [ability.to_dict() for ability in self.abilities]
        }
        return data
    
    @classmethod
    def load_from_dict(cls, data):
        """Create a player from saved data"""
        player = cls(data["name"], data["class_type"])
        player.level = data["level"]
        player.experience = data["experience"]
        player.experience_to_level = data["experience_to_level"]
        player.skill_points = data["skill_points"]
        player.max_health = data["max_health"]
        player.health = data["health"]
        player.attack = data["attack"]
        player.defense = data["defense"]
        player.speed = data["speed"]
        player.critical_chance = data["critical_chance"]
        player.critical_damage = data["critical_damage"]
        player.dodge_chance = data["dodge_chance"]
        
        # Load weapons
        player.weapons = [Weapon.from_dict(weapon_data) for weapon_data in data["weapons"]]
        if data["active_weapon"] >= 0:
            player.active_weapon = player.weapons[data["active_weapon"]]
        
        # Load artifacts
        player.artifacts = [Artifact.from_dict(artifact_data) for artifact_data in data["artifacts"]]
        
        # Load abilities
        player.abilities = [Ability.from_dict(ability_data) for ability_data in data["abilities"]]
        
        return player


class Enemy(Character):
    """Enemy character class"""
    def __init__(self, name, level=1, enemy_type="demon"):
        super().__init__(name, level)
        self.enemy_type = enemy_type
        self.experience_reward = 20 * level
        self.gold_reward = 10 * level
        
        # Initialize stats based on type and level
        self._initialize_enemy_stats()
        
        # Special abilities
        self.abilities = []
        self._initialize_abilities()
        
        # Loot table
        self.loot_table = self._initialize_loot_table()
    
    def _initialize_enemy_stats(self):
        """Initialize stats based on enemy type and level"""
        # Base stats by type
        if self.enemy_type == "demon":
            base_health = 40
            base_attack = 12
            base_defense = 5
            base_speed = 7
        elif self.enemy_type == "fallen":
            base_health = 30
            base_attack = 15
            base_defense = 3
            base_speed = 10
        elif self.enemy_type == "beast":
            base_health = 60
            base_attack = 10
            base_defense = 8
            base_speed = 5
        else:  # Default
            base_health = 40
            base_attack = 10
            base_defense = 5
            base_speed = 6
        
        # Scale by level
        level_multiplier = 1 + (self.level - 1) * 0.2
        self.max_health = int(base_health * level_multiplier)
        self.health = self.max_health
        self.attack = int(base_attack * level_multiplier)
        self.defense = int(base_defense * level_multiplier)
        self.speed = int(base_speed * level_multiplier)
    
    def _initialize_abilities(self):
        """Initialize abilities based on enemy type"""
        if self.enemy_type == "demon":
            self.abilities = [
                Ability("Demonic Slash", 3, target_type="enemy", effect="damage", power=15),
                Ability("Hellfire", 5, target_type="enemy", effect="damage", power=20)
            ]
        elif self.enemy_type == "fallen":
            self.abilities = [
                Ability("Corrupt Strike", 3, target_type="enemy", effect="damage", power=12),
                Ability("Wither", 4, target_type="enemy", effect="defense_down", power=20, duration=2)
            ]
        elif self.enemy_type == "beast":
            self.abilities = [
                Ability("Savage Bite", 3, target_type="enemy", effect="damage", power=14),
                Ability("Roar", 5, target_type="self", effect="attack_up", power=30, duration=2)
            ]
    
    def _initialize_loot_table(self):
        """Initialize potential drops based on enemy type"""
        loot_table = {
            "common": [],
            "uncommon": [],
            "rare": []
        }
        
        if self.enemy_type == "demon":
            loot_table["common"].append(("Demon Essence", 0.5))
            loot_table["uncommon"].append(("Hellfire Fragment", 0.2))
            loot_table["rare"].append(("Demon's Heart", 0.05))
        elif self.enemy_type == "fallen":
            loot_table["common"].append(("Tarnished Halo", 0.5))
            loot_table["uncommon"].append(("Broken Wing", 0.2))
            loot_table["rare"].append(("Fallen Grace", 0.05))
        elif self.enemy_type == "beast":
            loot_table["common"].append(("Beast Hide", 0.5))
            loot_table["uncommon"].append(("Sharp Fang", 0.2))
            loot_table["rare"].append(("Beast's Core", 0.05))
        
        return loot_table
    
    def choose_action(self, player):
        """AI decision making for enemy turn"""
        # Simple AI: Use abilities when available, otherwise normal attack
        
        # Check if any ability is off cooldown
        available_abilities = [i for i, ability in enumerate(self.abilities) 
                              if ability.cooldown_remaining == 0]
        
        # 70% chance to use ability if available
        if available_abilities and random.random() < 0.7:
            ability_index = random.choice(available_abilities)
            return ("ability", ability_index)
        else:
            return ("attack", None)
    
    def use_ability(self, ability_index, target=None):
        """Use an ability"""
        if ability_index < 0 or ability_index >= len(self.abilities):
            return False, "Invalid ability index"
        
        ability = self.abilities[ability_index]
        
        # Check if ability can be used
        if ability.cooldown_remaining > 0:
            return False, "Ability on cooldown"
        
        # Start cooldown
        ability.start_cooldown()
        
        # Apply ability effects
        if ability.effect == "damage":
            if target and ability.target_type == "enemy":
                damage = int(ability.power + (self.attack * 0.3))
                return True, (target, damage, f"{self.name} used {ability.name}!")
        
        elif ability.effect == "defense_down":
            if target and ability.target_type == "enemy":
                effect = StatusEffect("DefenseDown", duration=ability.duration, 
                                     stats_bonus={"defense": -int(target.defense * ability.power / 100)})
                target.add_status_effect(effect)
                return True, (target, ability.power, f"{self.name} used {ability.name} and decreased {target.name}'s defense!")
        
        elif ability.effect == "attack_up":
            if ability.target_type == "self":
                effect = StatusEffect("AttackUp", duration=ability.duration,
                                     stats_bonus={"attack": int(self.attack * ability.power / 100)})
                self.add_status_effect(effect)
                return True, (self, ability.power, f"{self.name} used {ability.name} and increased attack!")
        
        return False, "Ability couldn't be used"
    
    def get_loot(self):
        """Generate loot drops based on loot table"""
        drops = []
        
        # Check each rarity tier
        for rarity, items in self.loot_table.items():
            for item_name, drop_chance in items:
                if random.random() < drop_chance:
                    drops.append((item_name, rarity))
        
        # Always drop some gold
        gold = self.gold_reward + random.randint(-5, 5)
        gold = max(1, gold)  # Minimum 1 gold
        
        return drops, gold


class Ability:
    """Special abilities that characters can use"""
    def __init__(self, name, cooldown, target_type="enemy", effect="damage", power=10, duration=1):
        self.name = name
        self.cooldown = cooldown
        self.cooldown_remaining = 0
        self.target_type = target_type  # "enemy", "self", "ally", "all_enemies"
        self.effect = effect  # "damage", "heal", "buff", "debuff", etc.
        self.power = power  # Base power/effectiveness
        self.duration = duration  # For effects with duration
    
    def start_cooldown(self):
        """Start the cooldown for this ability"""
        self.cooldown_remaining = self.cooldown
    
    def update(self):
        """Update cooldown, called each turn"""
        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1
    
    def to_dict(self):
        """Convert ability to dictionary for saving"""
        return {
            "name": self.name,
            "cooldown": self.cooldown,
            "cooldown_remaining": self.cooldown_remaining,
            "target_type": self.target_type,
            "effect": self.effect,
            "power": self.power,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create ability from dictionary"""
        ability = cls(
            data["name"], 
            data["cooldown"],
            data["target_type"],
            data["effect"],
            data["power"],
            data["duration"]
        )
        ability.cooldown_remaining = data["cooldown_remaining"]
        return ability


class StatusEffect:
    """Status effects that can be applied to characters"""
    def __init__(self, name, duration=1, stats_bonus=None):
        self.name = name
        self.duration = duration
        self.stats_bonus = stats_bonus or {}  # Dictionary of stat bonuses
    
    def update(self):
        """Update the effect duration"""
        self.duration -= 1


class Weapon:
    """Weapons that can be equipped by the player"""
    def __init__(self, name, weapon_type="sword", attack_bonus=5, level=1, rarity="common"):
        self.name = name
        self.weapon_type = weapon_type  # sword, staff, bow, etc.
        self.attack_bonus = attack_bonus
        self.level = level
        self.rarity = rarity  # common, uncommon, rare, epic, legendary
        self.stat_bonuses = {}  # Additional stat bonuses
        self.upgrade_level = 0
        self.max_upgrade_level = 5
        
        # Initialize stat bonuses based on rarity
        self._initialize_stat_bonuses()
    
    def _initialize_stat_bonuses(self):
        """Initialize stat bonuses based on weapon type and rarity"""
        # Rarity multiplier
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 1.2,
            "rare": 1.5,
            "epic": 2.0,
            "legendary": 3.0
        }
        
        multiplier = rarity_multipliers.get(self.rarity, 1.0)
        
        # Weapon type specific bonuses
        if self.weapon_type == "sword":
            self.stat_bonuses["critical_chance"] = int(5 * multiplier)
        elif self.weapon_type == "staff":
            self.stat_bonuses["attack"] = int(3 * multiplier)
        elif self.weapon_type == "bow":
            self.stat_bonuses["speed"] = int(2 * multiplier)
        elif self.weapon_type == "mace":
            self.stat_bonuses["defense"] = int(3 * multiplier)
    
    def upgrade(self):
        """Upgrade the weapon"""
        if self.upgrade_level < self.max_upgrade_level:
            self.upgrade_level += 1
            self.attack_bonus += int(self.attack_bonus * 0.2)  # 20% increase
            
            # Upgrade stat bonuses
            for stat in self.stat_bonuses:
                self.stat_bonuses[stat] += int(self.stat_bonuses[stat] * 0.2)
            
            return True
        return False
    
    def to_dict(self):
        """Convert weapon to dictionary for saving"""
        return {
            "name": self.name,
            "weapon_type": self.weapon_type,
            "attack_bonus": self.attack_bonus,
            "level": self.level,
            "rarity": self.rarity,
            "stat_bonuses": self.stat_bonuses,
            "upgrade_level": self.upgrade_level,
            "max_upgrade_level": self.max_upgrade_level
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create weapon from dictionary"""
        weapon = cls(
            data["name"],
            data["weapon_type"],
            data["attack_bonus"],
            data["level"],
            data["rarity"]
        )
        weapon.stat_bonuses = data["stat_bonuses"]
        weapon.upgrade_level = data["upgrade_level"]
        weapon.max_upgrade_level = data["max_upgrade_level"]
        return weapon


class Artifact:
    """Special items that provide passive bonuses"""
    def __init__(self, name, description, rarity="common"):
        self.name = name
        self.description = description
        self.rarity = rarity
        self.stat_bonuses = {}
        
        # Generate bonuses based on rarity
        self._generate_bonuses()
    
    def _generate_bonuses(self):
        """Generate stat bonuses based on rarity"""
        # Rarity power levels
        power_levels = {
            "common": 5,
            "uncommon": 10,
            "rare": 15,
            "epic": 25,
            "legendary": 40
        }
        
        base_power = power_levels.get(self.rarity, 5)
        
        # Possible stats to buff
        stats = ["max_health", "attack", "defense", "speed", "critical_chance"]
        
        # Choose 1-3 stats based on rarity
        num_stats = min(3, max(1, {"common": 1, "uncommon": 1, "rare": 2, "epic": 2, "legendary": 3}.get(self.rarity, 1)))
        
        chosen_stats = random.sample(stats, num_stats)
        
        # Assign bonuses
        for stat in chosen_stats:
            if stat == "critical_chance":
                # Critical chance has lower values
                self.stat_bonuses[stat] = random.randint(1, max(1, base_power // 3))
            elif stat == "max_health":
                # Health has higher values
                self.stat_bonuses[stat] = random.randint(base_power, base_power * 3)
            else:
                self.stat_bonuses[stat] = random.randint(1, base_power)
    
    def to_dict(self):
        """Convert artifact to dictionary for saving"""
        return {
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "stat_bonuses": self.stat_bonuses
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create artifact from dictionary"""
        artifact = cls(data["name"], data["description"], data["rarity"])
        artifact.stat_bonuses = data["stat_bonuses"]
        return artifact


# Helper functions for generating enemies and items
def generate_enemy(level, area_index):
    """Generate an enemy appropriate for level and area"""
    # Types of enemies by area
    area_enemies = {
        0: ["Lesser Demon", "Imp", "Hellhound"],
        1: ["Tormentor", "Fallen Soul", "Abyssal Beast"],
        2: ["Vengeful Spirit", "Corrupted Angel", "Flame Demon"],
        3: ["Pain Bringer", "Shadow Lurker", "Despair Wraith"],
        4: ["Soul Eater", "Void Spawn", "Infernal Beast"],
        5: ["Archfiend", "Dark Seraph", "Hell Knight"],
        6: ["Demon Lord", "Fallen Archangel", "Apocalypse Beast"]
    }
    
    enemy_types = ["demon", "fallen", "beast"]
    
    # Choose name and type
    chosen_index = random.randint(0, 2)
    enemy_name = area_enemies[min(area_index, 6)][chosen_index]
    enemy_type = enemy_types[chosen_index]
    
    # Create enemy with appropriate level (player level + area difficulty)
    enemy_level = max(1, level + random.randint(-1, 1) + area_index // 2)
    
    return Enemy(enemy_name, enemy_level, enemy_type)

def generate_weapon(level, rarity=None):
    """Generate a random weapon"""
    weapon_types = ["sword", "staff", "bow", "mace"]
    weapon_names = {
        "sword": ["Blade of Faith", "Righteous Edge", "Holy Slicer", "Divine Cutter"],
        "staff": ["Staff of Light", "Holy Rod", "Divine Focus", "Blessed Branch"],
        "bow": ["Angel's Arc", "Divine Bow", "Heavenly Launcher", "Sacred Shot"],
        "mace": ["Holy Hammer", "Righteous Mace", "Sacred Crusher", "Divine Smiter"]
    }
    
    # Determine rarity if not specified
    if not rarity:
        rarity_chances = {
            "common": 0.6,
            "uncommon": 0.25,
            "rare": 0.1,
            "epic": 0.04,
            "legendary": 0.01
        }
        
        roll = random.random()
        cumulative = 0
        for r, chance in rarity_chances.items():
            cumulative += chance
            if roll <= cumulative:
                rarity = r
                break
    
    # Choose weapon type and name
    weapon_type = random.choice(weapon_types)
    weapon_name = random.choice(weapon_names[weapon_type])
    
    # Calculate attack bonus based on level and rarity
    base_attack = 5 + (level * 2)
    rarity_multipliers = {
        "common": 1.0,
        "uncommon": 1.3,
        "rare": 1.6,
        "epic": 2.0,
        "legendary": 3.0
    }
    
    attack_bonus = int(base_attack * rarity_multipliers.get(rarity, 1.0))
    
    return Weapon(weapon_name, weapon_type, attack_bonus, level, rarity)

def generate_artifact(level, rarity=None):
    """Generate a random artifact"""
    artifact_prefixes = ["Holy", "Divine", "Blessed", "Sacred", "Angelic", "Righteous"]
    artifact_types = ["Relic", "Emblem", "Icon", "Symbol", "Charm", "Talisman"]
    
    # Determine rarity if not specified
    if not rarity:
        rarity_chances = {
            "common": 0.5,
            "uncommon": 0.3,
            "rare": 0.15,
            "epic": 0.04,
            "legendary": 0.01
        }
        
        roll = random.random()
        cumulative = 0
        for r, chance in rarity_chances.items():
            cumulative += chance
            if roll <= cumulative:
                rarity = r
                break
    
    # Generate name
    prefix = random.choice(artifact_prefixes)
    artifact_type = random.choice(artifact_types)
    name = f"{prefix} {artifact_type}"
    
    # Generate description
    descriptions = {
        "common": "A modest relic with faint divine energy.",
        "uncommon": "A blessed object with noticeable holy power.",
        "rare": "A sacred artifact humming with divine energy.",
        "epic": "A powerful holy relic radiating intense divine aura.",
        "legendary": "An extraordinary artifact of legend, overflowing with celestial power."
    }
    
    description = descriptions.get(rarity, "A divine artifact.")
    
    return Artifact(name, description, rarity)


# Example usage
if __name__ == "__main__":
    # Create a player
    player = Player("Crusader", "Templar")
    print(f"Created {player.class_type} named {player.name}")
    print(f"Stats: HP {player.health}/{player.max_health}, ATK {player.attack}, DEF {player.defense}")
    
    # Generate an enemy
    enemy = generate_enemy(player.level, 0)
    print(f"\nEncountered {enemy.name} (Level {enemy.level})")
    print(f"Stats: HP {enemy.health}/{enemy.max_health}, ATK {enemy.attack}, DEF {enemy.defense}")
    
    # Simulate a battle
    print("\nBattle simulation:")
    
    # Player attacks enemy
    damage, is_crit = player.calculate_attack_damage(enemy)
    actual_damage = enemy.take_damage(damage)
    crit_text = " (Critical hit!)" if is_crit else ""
    print(f"{player.name} attacks for {actual_damage} damage{crit_text}!")
    print(f"{enemy.name} has {enemy.health}/{enemy.max_health} HP remaining")
    
    # Enemy attacks player
    if enemy.is_alive():
        damage, is_crit = enemy.calculate_attack_damage(player)
        actual_damage = player.take_damage(damage)
        crit_text = " (Critical hit!)" if is_crit else ""
        print(f"{enemy.name} attacks for {actual_damage} damage{crit_text}!")
        print(f"{player.name} has {player.health}/{player.max_health} HP remaining")
    
    # Player uses an ability
    if player.abilities:
        print("\nUsing ability:")
        result, message = player.use_ability(0, enemy)
        if result:
            target, value, text = message
            print(text)
            if isinstance(target, Enemy):
                print(f"{enemy.name} has {enemy.health}/{enemy.max_health} HP remaining")
    
    # Give player experience
    if not enemy.is_alive():
        xp = enemy.experience_reward
        level_ups = player.gain_experience(xp)
        print(f"\n{enemy.name} defeated! Gained {xp} experience.")
        if level_ups > 0:
            print(f"Level up! {player.name} is now level {player.level}")
            print(f"New stats: HP {player.health}/{player.max_health}, ATK {player.attack}, DEF {player.defense}")
    
    # Find a weapon
    weapon = generate_weapon(player.level)
    print(f"\nFound {weapon.name} ({weapon.rarity})!")
    print(f"Attack bonus: +{weapon.attack_bonus}")
    
    # Find an artifact
    artifact = generate_artifact(player.level)
    print(f"\nFound {artifact.name} ({artifact.rarity})!")
    print(f"Description: {artifact.description}")
    print("Stat bonuses:")
    for stat, bonus in artifact.stat_bonuses.items():
        print(f"  {stat}: +{bonus}")
