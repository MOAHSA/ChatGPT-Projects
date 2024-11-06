import pygame
import math
import random
import os

# Game settings dictionary
GAME_SETTINGS = {
    'window': {'width': 1400, 'height':800},
    'player': {
        'speed': 6,
        'max_speed': 15,
        'health': 100,
        'max_health': 100,
        'size': 20,

    },
    'gun':{
        'cooldown': 500,
        'size': 30,
        'min_cooldown': 100,  # Minimum cooldown
        'max_cooldown': 1000,  # Maximum cooldown
    },
    'bullet': {
        'speed': 6,
        'lifetime': 2000,  # milliseconds
        'max_count': 5,
        'max_speed': 12,
        'collision_margin': 40,
        'attack_damage':25,
        'size': 8,
        'spacing': 20,  # Adjust this value for more or less spacing
        'min_attack_damage': 5,  # Minimum attack damage
        'max_attack_damage': 100,  # Maximum attack damage
        'max_bullet_count' : 6,
        'temp_bullet_count':0,
        'bullet_count': 1,


    },
    'enemy': {
        'speed_min': 1,
        'speed_max': 5,
        'collision_margin': 40,
        'size': 20,
        'attack_damage':5
    },
    'wave': {
        'increase_rate': 2,
        'delay_min': 1000,  # 1 second
        'delay_max': 2000  # 2 seconds
    },
    'item': {
        'lifetime_min': 2000,  # 1 second
        'lifetime_max': 3500,  # 3.5 seconds
        'effect_duration': 5000,  # 5 seconds
        'size': 20,
        'effect_text_duration': 1000,  # 1 second1
    },
    'fps': 60,
    'font': {
        'default_size': 20,
        'ui_size': 36,
        'title_size': 48,  # Added title font size
        'effect_text_size': 24  # Added effect text font size
    }
}

# Color Dictionary with descriptive names
COLORS = {
    'player_color': (185, 255, 148),  
    'bullet_color': (211, 242, 222),  
    'enemy_color': (255, 150, 148),   
    'good_item_color': (0, 170, 0), 
    'bad_item_color': (170, 0, 0),   
    'ui_text_color': (200, 200, 200), 
    'background_color': (27, 27, 27),     
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((GAME_SETTINGS['window']['width'], GAME_SETTINGS['window']['height']))
pygame.display.set_caption("2D Shooting Game")
clock = pygame.time.Clock()

# Effect values dictionary
EFFECT_VALUES = {
    'increase_health': 10,
    'decrease_health': 10,
    'increase_bullet_speed': 2,
    'decrease_bullet_speed': 2,
    'increase_player_speed': 1,
    'decrease_player_speed': 1,
    'add_bullet': 1,
    'remove_bullet': 1,
    'increase_attack_damage': 5,  # New effect for increasing attack damage
    'decrease_attack_damage': 5,  # New effect for decreasing attack damage
    'increase_cooldown': 100,      # New effect for increasing cooldown
    'decrease_cooldown': 100,      # New effect for decreasing cooldown
    'untouchable': 1                # New effect for untouchable status
}

# Define colors for each effect
EFFECT_COLORS = {
    'increase_health': (0, 255, 0),  # Green
    'decrease_health': (255, 0, 0),  # Red
    'increase_bullet_speed': (0, 0, 255),  # Blue
    'decrease_bullet_speed': (255, 165, 0),  # Orange
    'increase_player_speed': (255, 255, 0),  # Yellow
    'decrease_player_speed': (128, 0, 128),  # Purple
    'add_bullet': (0, 255, 255),  # Cyan
    'remove_bullet': (255, 192, 203),  # Pink
    'increase_attack_damage': (255, 20, 147),  # Deep Pink
    'decrease_attack_damage': (255, 140, 0),  # Dark Orange
    'increase_cooldown': (128, 128, 128),  # Gray
    'decrease_cooldown': (0, 128, 0),  # Dark Green
    'untouchable': (75, 0, 130),  # Indigo
}

# Define the base path for audio files
BASE_PATH = os.path.dirname(__file__)  # Get the directory of the current file

# Load sound effects
shoot_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'audio/shoot.wav'))
explosion_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'audio/explosion.wav'))
impact_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'audio/impact.ogg'))

# Set the volume to 50%
shoot_sound.set_volume(0.5)  # Set shoot sound volume to 50%
explosion_sound.set_volume(0.5)  # Set explosion sound volume to 50%
impact_sound.set_volume(0.5)  # Set impact sound volume to 50%

class Player:
    def __init__(self):
        self.position = pygame.Vector2(GAME_SETTINGS['window']['width'] // 2, GAME_SETTINGS['window']['height'] // 2)
        self.speed = GAME_SETTINGS['player']['speed']
        self.health = GAME_SETTINGS['player']['health']
        self.cooldown = GAME_SETTINGS['gun']['cooldown']
        self.last_shot_time = 0
        self.bullet_speed = GAME_SETTINGS['bullet']['speed']
        self.temp_speed_boost = 0
        self.temp_bullet_count = 1  # This can be increased by effects
        self.attack_damage = GAME_SETTINGS['bullet']['attack_damage']  # Initialize attack damage
        self.untouchable = False  # Initialize untouchable status
        self.untouchable_duration = 0  # Duration for untouchable effect
        self.active_effects = {}  # Dictionary to track active effects and their durations
        self.effect_start_time = {}  # Dictionary to track when each effect started

    def get_rect(self):
        return pygame.Rect(self.position.x - 15, self.position.y - 15, GAME_SETTINGS['player']['size'], GAME_SETTINGS['player']['size'])

    def movement(self):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: direction.y -= 1
        if keys[pygame.K_s]: direction.y += 1
        if keys[pygame.K_a]: direction.x -= 1
        if keys[pygame.K_d]: direction.x += 1
        if direction.length() > 0:
            direction = direction.normalize() * min(self.speed + self.temp_speed_boost, GAME_SETTINGS['player']['max_speed'])
        self.position += direction
        self.position.x = max(0, min(self.position.x, GAME_SETTINGS['window']['width']))
        self.position.y = max(0, min(self.position.y, GAME_SETTINGS['window']['height']))

    def fire_bullet(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.cooldown:
            bullets = []
            mouse_x, mouse_y = pygame.mouse.get_pos()
            angle = math.atan2(mouse_y - self.position.y, mouse_x - self.position.x)

            # Ensure at least one bullet is shot
            num_bullets_to_shoot = max(1, self.temp_bullet_count)

            # Define spacing between bullets
            spacing = GAME_SETTINGS['bullet']['spacing']  # Adjust this value for more or less spacing

            # Fire bullets based on the current bullet count
            for i in range(num_bullets_to_shoot):
                bullet_position = self.position.copy()
                # Apply spacing based on the index
                bullet_position.x += (i - (num_bullets_to_shoot - 1) / 2) * spacing
                bullet = Bullet(bullet_position, angle, self.bullet_speed)
                bullets.append(bullet)

            self.last_shot_time = current_time
            shoot_sound.play()  # Play shoot sound
            return bullets
        return []

    def get_gun_position(self):
        """Calculate the position of the gun (triangle) based on the mouse position."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.position.y, mouse_x - self.position.x)
        # Position the gun at the edge of the player circle (15 pixels radius + gun length)
        gun_length = 15  # Length of the gun
        gun_x = self.position.x + math.cos(angle) * (15 + gun_length)
        gun_y = self.position.y + math.sin(angle) * (15 + gun_length)
        return (gun_x, gun_y), angle  # Return the position and angle for drawing

    def collect_item(self, item):
        item.display_effect_text(screen)  # Display the item's effect text

        # Update to use EFFECT_VALUES dictionary
        effect_value = EFFECT_VALUES[item.effect]  # Get the effect value from the dictionary
        if item.effect == 'increase_health':
            self.health = min(self.health + effect_value, GAME_SETTINGS['player']['max_health'])  # Increase health reasonably
        elif item.effect == 'decrease_health':
            self.health = max(self.health - effect_value, 0)  # Decrease health reasonably
        elif item.effect == 'increase_bullet_speed':
            self.bullet_speed = min(self.bullet_speed + effect_value, GAME_SETTINGS['bullet']['max_speed'])  # Increase bullet speed reasonably
        elif item.effect == 'decrease_bullet_speed':
            self.bullet_speed = max(self.bullet_speed - effect_value, 1)  # Decrease bullet speed reasonably
        elif item.effect == 'increase_player_speed':
            self.temp_speed_boost = min(self.temp_speed_boost + effect_value, GAME_SETTINGS['player']['max_speed'])   # Increase player speed reasonably
            pygame.time.set_timer(pygame.USEREVENT, GAME_SETTINGS['item']['effect_duration'])  # Set a timer for the effect duration
        elif item.effect == 'decrease_player_speed':
            self.temp_speed_boost = max(self.temp_speed_boost - effect_value, 0)  # Decrease player speed reasonably
        elif item.effect == 'add_bullet': 
            self.temp_bullet_count = min(self.temp_bullet_count + effect_value, GAME_SETTINGS['bullet']['max_bullet_count'])   # Add bullets Ensure it does not exceed max_bullet_count
            pygame.time.set_timer(pygame.USEREVENT, GAME_SETTINGS['item']['effect_duration'])  # Set a timer for the effect duration
        elif item.effect == 'remove_bullet':
            self.temp_bullet_count = max(self.temp_bullet_count - effect_value, 1)  # Ensure at least 1 bullet remains
        elif item.effect == 'increase_attack_damage':
            self.attack_damage = min(self.attack_damage + effect_value, GAME_SETTINGS['bullet']['max_attack_damage'])  # Increase attack damage
        elif item.effect == 'decrease_attack_damage':
            self.attack_damage = max(self.attack_damage - effect_value, GAME_SETTINGS['bullet']['min_attack_damage'])  # Decrease attack damage
        elif item.effect == 'increase_cooldown':
            self.cooldown = min(self.cooldown + effect_value, GAME_SETTINGS['gun']['max_cooldown'])  # Increase cooldown
        elif item.effect == 'decrease_cooldown':
            self.cooldown = max(self.cooldown - effect_value, GAME_SETTINGS['gun']['min_cooldown'])  # Decrease cooldown
        elif item.effect == 'untouchable':
            self.untouchable = True  # Set untouchable status
            self.untouchable_duration = pygame.time.get_ticks() + GAME_SETTINGS['item']['effect_duration']  # Set duration for untouchable

        if item.effect in self.active_effects:
            self.active_effects[item.effect] += EFFECT_VALUES[item.effect]  # Extend duration if already active
        else:
            self.active_effects[item.effect] = EFFECT_VALUES[item.effect]  # Set new effect duration
            self.effect_start_time[item.effect] = pygame.time.get_ticks()  # Record start time

        # Print the player's state after collecting the item
        #print(f"Player State after collecting item: Health: {self.health}, PlayerSpeed: {self.temp_speed_boost}, Bullet Speed: {self.bullet_speed}, Bullet Count: {self.temp_bullet_count}, Attack Damage: {self.attack_damage}, Untouchable: {self.untouchable}, Active Effects: {self.active_effects}")

class Bullet:
    def __init__(self, position, angle, speed):
        self.position = position
        self.angle = angle
        self.speed = speed
        self.lifetime = pygame.time.get_ticks() + GAME_SETTINGS['bullet']['lifetime']  # Set the bullet's lifetime

    def update(self):
        # Check if the bullet is still alive
        if pygame.time.get_ticks() < self.lifetime:
            # Update bullet position based on speed and angle
            self.position.x += self.speed * math.cos(self.angle)
            self.position.y += self.speed * math.sin(self.angle)
            return True  # Bullet is still alive
        return False  # Bullet has expired

class Enemy:
    def __init__(self, position):
        self.position = position
        self.health = 50
        self.speed = random.randint(GAME_SETTINGS['enemy']['speed_min'], GAME_SETTINGS['enemy']['speed_max'])  # Use GAME_SETTINGS
        self.vector = pygame.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
        self.target_position = None  # Target position to move towards
        self.path = []  # List to store path points
        self.path_index = 0  # Current index in the path

    def move_towards_player(self, player_position, enemies):
        # If no target position, set it to the player's position
        if self.target_position is None:
            self.target_position = player_position
            self.calculate_path(player_position)  # Calculate initial path

        # Check for potential collisions with other enemies
        if self.check_for_collisions(enemies):
            self.avoid_collision(enemies)

        # Move along the path
        if self.path:
            self.follow_path()
        else:
            self.target_position = player_position  # Update target if path is empty
            self.calculate_path(player_position)  # Recalculate path

    def calculate_path(self, target):
        # Implement a pathfinding algorithm (e.g., A* or Dijkstra's)
        # For simplicity, we will use a placeholder for path calculation
        self.path = [self.position.copy(), target]  # Direct path for now
        self.path_index = 0  # Reset path index

    def follow_path(self):
        if self.path_index < len(self.path):
            direction = self.path[self.path_index] - self.position
            if direction.length() > 0:
                direction = direction.normalize() * self.speed
                self.position += direction

            # Check if reached the next path point
            if self.position.distance_to(self.path[self.path_index]) < 5:  # Threshold for reaching the point
                self.path_index += 1  # Move to the next point in the path

    def check_for_collisions(self, enemies):
        # Check if this enemy is too close to others
        for enemy in enemies:
            if enemy != self and self.position.distance_to(enemy.position) < GAME_SETTINGS['enemy']['collision_margin']:  # Collision radius
                return True
        return False

    def avoid_collision(self, enemies):
        # Implement separation behavior to avoid overcrowding
        for enemy in enemies:
            if enemy != self:
                direction = self.position - enemy.position
                if direction.length() < 30:  # If too close
                    if direction.length() > 0:
                        self.position += direction.normalize() * 2  # Move away slightly

class Item:
    def __init__(self, position, item_type):
        self.position = position
        self.item_type = item_type  # 'good' or 'bad'
        self.effect = self.random_effect()  # Randomly choose an effect
        self.lifetime = pygame.time.get_ticks() + random.randint(GAME_SETTINGS['item']['lifetime_min'], GAME_SETTINGS['item']['lifetime_max'])
        self.effect_text_surface = None  # Surface for displaying effect text
        self.effect_text_timer = None  # Timer for effect text display
        self.rect = pygame.Rect(self.position.x, self.position.y, GAME_SETTINGS['item']['size'], GAME_SETTINGS['item']['size'])  # Define the rect for collision
        self.effect_display_duration = GAME_SETTINGS['item']['effect_text_duration']  # Duration to display effect text in milliseconds
        self.effect_display_start_time = None  # Start time for displaying effect text

    def random_effect(self):
        if self.item_type == 'good':
            return random.choice([
                'increase_health', 
                'increase_bullet_speed', 
                'increase_player_speed', 
                'add_bullet', 
                'increase_attack_damage',  # New effect for increasing attack damage
                'decrease_cooldown',        # New effect for decreasing cooldown
                'untouchable'               # New effect for untouchable status
            ])
        else:
            return random.choice([
                'decrease_health', 
                'decrease_bullet_speed', 
                'decrease_player_speed', 
                'remove_bullet', 
                'decrease_attack_damage',  # New effect for decreasing attack damage
                'increase_cooldown'        # New effect for increasing cooldown
            ])

    def update(self):
        if pygame.time.get_ticks() < self.lifetime:
            return True
        else:
            self.effect_display_start_time = None  # Reset the display timer when the item expires
        return False

    def display_effect_text(self, screen):
        if self.effect_display_start_time is None:  # Only set the start time if it's not already set
            effect_text = self.effect.replace('_', ' ').upper()
            color = EFFECT_COLORS[self.effect] if self.effect in EFFECT_COLORS else COLORS['good_item_color']
            font = pygame.font.Font(None, GAME_SETTINGS['font']['effect_text_size'])  # Use a larger font size for better visibility
            self.effect_text_surface = font.render(effect_text, True, color)
            self.effect_display_start_time = pygame.time.get_ticks()  # Start the timer

        # Draw the effect text if the duration has not expired
        if pygame.time.get_ticks() - self.effect_display_start_time < self.effect_display_duration:
            text_rect = self.effect_text_surface.get_rect(center=(self.position.x, self.position.y - 20))  # Position above the item
            screen.blit(self.effect_text_surface, text_rect)

    def get_rect(self):
        # Update the rect position based on the current position
        self.rect.topleft = (self.position.x, self.position.y)
        return self.rect

class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.items = []
        self.wave = 1
        self.wave_delay = random.randint(GAME_SETTINGS['wave']['delay_min'], GAME_SETTINGS['wave']['delay_max'])  # Random delay for the next wave
        self.last_wave_time = pygame.time.get_ticks()  # Track the last wave time
        self.spawn_enemies()
        self.scores = self.load_scores()  # Load scores from file
        self.username = ""  # Initialize username
        self.paused = False  # Initialize paused state

    def load_scores(self):
        """Load scores from a file."""
        scores_file_path = os.path.join(os.path.dirname(__file__), "high_scores.txt")  # Updated path
        if not os.path.exists(scores_file_path):
            return []
        scores = []
        with open(scores_file_path, "r") as file:
            for line in file:
                try:
                    username, score = line.strip().split(",")  # Expecting "username,score"
                    scores.append((username, int(score)))  # Convert score to int
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")  # Log the invalid line
        return scores

    def save_score(self):
        """Save the current wave to the scores file in descending order."""
        scores_file_path = os.path.join(os.path.dirname(__file__), "high_scores.txt")  # Updated path
        self.scores.append((self.username, self.wave))  # Add the current wave and username to the scores
        self.scores.sort(key=lambda x: x[1], reverse=True)  # Sort scores from max to min
        with open(scores_file_path, "w") as file:
            for username, score in self.scores:
                file.write(f"{username},{score}\n")  # Save username and score

    def reset_game(self):
        """Reset the game state for a new game."""
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.items = []
        self.wave = 1
        self.wave_delay = random.randint(GAME_SETTINGS['wave']['delay_min'], GAME_SETTINGS['wave']['delay_max'])
        self.last_wave_time = pygame.time.get_ticks()
        self.spawn_enemies()

    def main_menu(self):
        """Display the main menu and handle user input."""
        self.username = self.get_username()  # Get username from the user
        while True:
            screen.fill(COLORS['background_color'])
            title_font = pygame.font.Font(None, GAME_SETTINGS['font']['title_size'])
            title_text = title_font.render("2D Shooting Game", True, COLORS['ui_text_color'])
            font = pygame.font.Font(None, GAME_SETTINGS['font']['ui_size'])
            start_text = font.render("Press ENTER to Start", True, COLORS['ui_text_color'])
            exit_text = font.render("Press ESC to Exit", True, COLORS['ui_text_color'])
            score_title_text = title_font.render("High Scores", True, COLORS['ui_text_color'])

            # Display scores on the left side
            score_texts = [font.render(f"{username}: {score} Waves", True, COLORS['ui_text_color']) for username, score in self.scores]
            for i, score_text in enumerate(score_texts):
                screen.blit(score_text, (50, 150 + i * 30))  # Adjust position as needed

            screen.blit(title_text, (GAME_SETTINGS['window']['width'] // 2 - title_text.get_width() // 2, 50))
            screen.blit(score_title_text, (50, 100))  # Position for the score title
            screen.blit(start_text, (GAME_SETTINGS['window']['width'] // 2 - start_text.get_width() // 2, 250))
            screen.blit(exit_text, (GAME_SETTINGS['window']['width'] // 2 - exit_text.get_width() // 2, 300))
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()  # Force exit on quit event
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Start the game
                        return
                    if event.key == pygame.K_ESCAPE:  # Exit the game
                        pygame.quit()
                        exit()  # Force exit on escape key

    def get_username(self):
        """Prompt the user to enter their username."""
        input_box = pygame.Rect(50, 200, 140, 32)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        font = pygame.font.Font(None, 32)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()  # Force exit on quit event
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            return text  # Return the entered username
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            screen.fill(COLORS['background_color'])

            # Display "Enter Name" above the input box
            enter_name_text = font.render("Enter Name", True, COLORS['ui_text_color'])
            screen.blit(enter_name_text, (50, 150))  # Position for the "Enter Name" text
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width()+10)
            input_box.w = width
            screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
            pygame.draw.rect(screen, color, input_box, 2)
            
            pygame.display.flip()

    def spawn_enemies(self):
        for _ in range(self.wave * GAME_SETTINGS['wave']['increase_rate']):
            # Spawn enemies outside the window
            if random.choice([True, False]):
                enemy_position = pygame.Vector2(random.randint(-50, GAME_SETTINGS['window']['width'] + 50), random.randint(-50, -10))
            else:
                enemy_position = pygame.Vector2(random.randint(-50, GAME_SETTINGS['window']['width'] + 50), random.randint(GAME_SETTINGS['window']['height'] + 10, GAME_SETTINGS['window']['height'] + 50))
            self.enemies.append(Enemy(enemy_position))

    def game_over(self):
        """Display the game over screen and return to the main menu."""
        self.save_score()  # Save the score when game is over
        font = pygame.font.Font(None, GAME_SETTINGS['font']['ui_size'])
        title_font = pygame.font.Font(None, GAME_SETTINGS['font']['title_size'])
        
        score_title_text = title_font.render("High Scores", True, COLORS['ui_text_color'])

        while True:
            screen.fill(COLORS['background_color'])
            
            # Display scores on the left side
            score_texts = [font.render(f"{username}: {score} Waves", True, COLORS['ui_text_color']) for username, score in self.scores]
            for i, score_text in enumerate(score_texts):
                screen.blit(score_text, (50, 150 + i * 30))  # Adjust position as needed

            screen.blit(score_title_text, (50, 100))  # Position for the score title
            
            font = pygame.font.Font(None, GAME_SETTINGS['font']['ui_size'])
            game_over_text = font.render("Game Over", True, COLORS['ui_text_color'])
            wave_text = font.render(f"Last Wave: {self.wave}", True, COLORS['ui_text_color'])
            restart_text = font.render("Press ENTER to Restart", True, COLORS['ui_text_color'])
            exit_text = font.render("Press ESC to Exit", True, COLORS['ui_text_color'])

            screen.blit(game_over_text, (GAME_SETTINGS['window']['width'] // 2 - game_over_text.get_width() // 2, 100))
            screen.blit(wave_text, (GAME_SETTINGS['window']['width'] // 2 - wave_text.get_width() // 2, 150))
            screen.blit(restart_text, (GAME_SETTINGS['window']['width'] // 2 - restart_text.get_width() // 2, 200))
            screen.blit(exit_text, (GAME_SETTINGS['window']['width'] // 2 - exit_text.get_width() // 2, 250))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Restart the game
                        self.reset_game()
                        return
                    if event.key == pygame.K_ESCAPE:  # Exit the game
                        pygame.quit()
                        exit()

    def check_collisions(self):
        # Check bullet collisions with enemies
        for bullet in self.bullets[:]:  # Iterate over a copy of the list
            for enemy in self.enemies[:]:
                if bullet.position.distance_to(enemy.position) < (GAME_SETTINGS['bullet']['size'] + GAME_SETTINGS['enemy']['size']):  # Collision radius (bullet + enemy)
                    enemy.health -= self.player.attack_damage
                    self.bullets.remove(bullet)  # Remove bullet on collision
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.drop_item(enemy.position)  # Drop item when enemy is defeated
                    explosion_sound.play()  # Play explosion sound
                    break  # Exit inner loop after collision

        # Check player collisions with enemies
        for enemy in self.enemies[:]:
            if enemy.position.distance_to(self.player.position) < (GAME_SETTINGS['player']['size'] + GAME_SETTINGS['enemy']['size']):  # Collision radius (player + enemy)
                if not self.player.untouchable:  # Only take damage if not untouchable
                    self.player.health -= GAME_SETTINGS['enemy']['attack_damage']
                    self.enemies.remove(enemy)
                    impact_sound.play()  # Play impact sound
                
        if self.player.health <= 0:
            self.game_over()

        # Check item collisions with player using rect
        for item in self.items[:]:
            if self.player.get_rect().colliderect(item.get_rect()):  # Use rect for collision detection
                self.items.remove(item)
                self.player.collect_item(item)  # Call collect_item on the player instance

        # Check for enemy collisions
        for i in range(len(self.enemies)):
            for j in range(i + 1, len(self.enemies)):
                if self.enemies[i].position.distance_to(self.enemies[j].position) < GAME_SETTINGS['enemy']['size'] + GAME_SETTINGS['enemy']['size']:  # Collision radius
                    self.enemies[i].health = 0  # Remove enemy on collision

    def drop_item(self, position):
        if random.random() < 0.4:  # 60% chance to drop an item
            item_type = 'bad' if random.random() < 0.3 else 'good'  # 30% chance for bad item
            item = Item(position, item_type)
            self.items.append(item)

    def check_wave_progression(self):
        if not self.enemies:  # If there are no enemies left
            current_time = pygame.time.get_ticks()
            if current_time - self.last_wave_time >= self.wave_delay:  # Check if the delay has passed
                self.wave += 1  # Increase wave number
                self.wave_delay = random.randint(GAME_SETTINGS['wave']['delay_min'], GAME_SETTINGS['wave']['delay_max'])  # Set random delay for the next wave
                
                # Increase enemy speed every 5 waves
                if self.wave % 5 == 0:
                    GAME_SETTINGS['enemy']['speed_min'] += 1  # Increase minimum enemy speed
                    GAME_SETTINGS['enemy']['speed_max'] += 1  # Increase maximum enemy speed
                
                self.last_wave_time = current_time  # Update the last wave time
                self.spawn_enemies()  # Spawn new enemies for the next wave

    def draw_ui(self):
        font = pygame.font.Font(None, GAME_SETTINGS['font']['ui_size'])
        health_text = font.render(f'Health: {self.player.health}', True, COLORS['ui_text_color'])
        wave_text = font.render(f'Wave: {self.wave}', True, COLORS['ui_text_color'])
        screen.blit(health_text, (10, 10))
        screen.blit(wave_text, (10, 40))

    def pause_menu(self):
        """Display the pause menu and handle user input."""
        while self.paused:
            screen.fill(COLORS['background_color'])
            font = pygame.font.Font(None, GAME_SETTINGS['font']['ui_size'])
            pause_text = font.render("Game Paused", True, COLORS['ui_text_color'])
            resume_text = font.render("Press R to Resume", True, COLORS['ui_text_color'])
            restart_text = font.render("Press ENTER to Restart", True, COLORS['ui_text_color'])
            exit_text = font.render("Press ESC to Exit", True, COLORS['ui_text_color'])

            screen.blit(pause_text, (GAME_SETTINGS['window']['width'] // 2 - pause_text.get_width() // 2, 100))
            screen.blit(resume_text, (GAME_SETTINGS['window']['width'] // 2 - resume_text.get_width() // 2, 150))
            screen.blit(restart_text, (GAME_SETTINGS['window']['width'] // 2 - restart_text.get_width() // 2, 200))
            screen.blit(exit_text, (GAME_SETTINGS['window']['width'] // 2 - exit_text.get_width() // 2, 250))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()  # Force exit on quit event
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Resume the game
                        self.paused = False
                    if event.key == pygame.K_RETURN:  # Restart the game
                        self.reset_game()
                        self.paused = False
                        return
                    if event.key == pygame.K_ESCAPE:  # Exit the game
                        pygame.quit()
                        exit()  # Force exit on escape key



    def spawn_good_item(self, item_type):
        # Define the position where the item will spawn (for testing, we can spawn it at the player's position)
        item_position = self.player.position.copy()
        item = Item(item_position, item_type)
        self.items.append(item)

    def draw_gun(self, screen):
        gun_position, angle = self.player.get_gun_position()
        # Define the points of the triangle (gun)
        triangle_points = [
            (gun_position[0], gun_position[1]),  # Tip of the gun
            (gun_position[0] - 10, gun_position[1] + 5),  # Bottom left
            (gun_position[0] - 10, gun_position[1] - 5)   # Bottom right
        ]
        # Draw the triangle
        pygame.draw.polygon(screen, (255, 0, 0), triangle_points)  # Red triangle

        # Draw cooldown timer around the gun
        self.draw_cooldown_timer(gun_position)

    def draw_cooldown_timer(self, gun_position):
        """Draw a circular timer for the gun cooldown."""
        current_time = pygame.time.get_ticks()
        cooldown_duration = self.player.cooldown  # Get the cooldown duration
        elapsed_time = current_time - self.player.last_shot_time  # Time since the last shot
        remaining_time = max(0, cooldown_duration - elapsed_time)  # Calculate remaining time

        # Calculate the angle for the remaining time
        angle = (remaining_time / cooldown_duration) * 360
        effect_radius = 20  # Radius of the cooldown timer circle

        # Draw the cooldown arc
        pygame.draw.arc(screen, (0, 255, 0), (gun_position[0] - effect_radius, gun_position[1] - effect_radius, effect_radius * 2, effect_radius * 2), -90 * (math.pi / 180), (angle - 90) * (math.pi / 180), 5)

    def draw_effect_timers(self):
        """Draw circular timers for active effects in the top right corner."""
        current_time = pygame.time.get_ticks()
        effect_radius = 30  # Radius of the timer circle
        effect_positions = {
            'increase_health': (GAME_SETTINGS['window']['width'] - 50, 50),
            'decrease_health': (GAME_SETTINGS['window']['width'] - 50, 100),
            'increase_bullet_speed': (GAME_SETTINGS['window']['width'] - 50, 150),
            'decrease_bullet_speed': (GAME_SETTINGS['window']['width'] - 50, 200),
            'increase_player_speed': (GAME_SETTINGS['window']['width'] - 50, 250),
            'decrease_player_speed': (GAME_SETTINGS['window']['width'] - 50, 300),
            'add_bullet': (GAME_SETTINGS['window']['width'] - 50, 350),
            'remove_bullet': (GAME_SETTINGS['window']['width'] - 50, 400),
            'increase_attack_damage': (GAME_SETTINGS['window']['width'] - 50, 450),
            'decrease_attack_damage': (GAME_SETTINGS['window']['width'] - 50, 500),
            'increase_cooldown': (GAME_SETTINGS['window']['width'] - 50, 550),
            'decrease_cooldown': (GAME_SETTINGS['window']['width'] - 50, 600),
            'untouchable': (GAME_SETTINGS['window']['width'] - 50, 650),
        }

        for effect, position in effect_positions.items():
            if effect in self.player.active_effects:
                duration = GAME_SETTINGS['item']['effect_duration']
                elapsed_time = current_time - self.player.effect_start_time[effect]
                remaining_time = max(0, duration - elapsed_time)

                # Calculate the angle for the remaining time
                angle = (remaining_time / duration) * 360
                # Determine the color based on the effect type
                if effect in ['decrease_health', 'decrease_bullet_speed', 'decrease_player_speed', 'remove_bullet', 'decrease_attack_damage', 'increase_cooldown']:
                    color = (255, 0, 0)  # Red for bad effects
                else:
                    color = EFFECT_COLORS[effect]  # Use the predefined color for good effects
                # Draw the circular timer with the effect's color
                pygame.draw.arc(screen, color, (position[0] - effect_radius, position[1] - effect_radius, effect_radius * 2, effect_radius * 2), -90 * (math.pi / 180), (angle - 90) * (math.pi / 180), 5)

    def run(self):
        running = True
        self.main_menu()  # Call the main menu at the start
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:  # Handle temporary effect expiration
                    self.player.temp_speed_boost = 0  # Reset speed boost
                    self.player.temp_bullet_count = 1  # Reset bullet count
                    self.player.untouchable = False  # Reset untouchable status
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Press 'P' to pause the game
                        self.paused = True
                        self.pause_menu()  # Call the pause menu
                    if event.key == pygame.K_m:
                        self.main_menu()  # Call the main menu
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        bullets = self.player.fire_bullet()  # Fire bullets
                        if bullets:
                            self.bullets.extend(bullets)

            # Check for key presses to spawn items
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:  # Press 1 to add a bullet
                self.player.temp_bullet_count += 1  # Increase the temporary bullet count
            if keys[pygame.K_2]:  # Press 2 to increase health
                self.player.health = min(self.player.health + 10, 100)  # Increase health
            if keys[pygame.K_3]:  # Press 3 to increase bullet speed
                self.player.bullet_speed = min(self.player.bullet_speed + 2, GAME_SETTINGS['bullet']['max_speed'])  # Increase bullet speed
            if keys[pygame.K_4]:  # Press 4 to increase player speed
                self.player.temp_speed_boost += 1  # Increase speed boost
            if keys[pygame.K_5]:  # Press 5 to decrease health
                self.player.health = max(self.player.health - 10, 0)  # Decrease health
            if keys[pygame.K_6]:  # Press 6 to decrease bullet speed
                self.player.bullet_speed = max(self.player.bullet_speed - 2, 1)  # Decrease bullet speed
            if keys[pygame.K_7]:  # Press 7 to decrease player speed
                self.player.temp_speed_boost = max(self.player.temp_speed_boost - 1, 0)  # Decrease speed boost
            if keys[pygame.K_8]:  # Press 8 to remove a bullet
                self.player.temp_bullet_count = max(self.player.temp_bullet_count - 1, 1)  # Ensure at least 1 bullet can be shot

            self.player.movement()  # Update player movement

            # Update bullets
            self.bullets = [bullet for bullet in self.bullets if bullet.update()]  # Keep only alive bullets

            # Update enemies
            for enemy in self.enemies:
                enemy.move_towards_player(self.player.position, self.enemies)

            # Update items
            self.items = [item for item in self.items if item.update()]

            self.check_collisions()
            self.check_wave_progression()  # Check if we need to progress to the next wave

            # Draw everything
            screen.fill(COLORS['background_color'])  # Clear screen
            for bullet in self.bullets:
                pygame.draw.circle(screen, COLORS['bullet_color'], (int(bullet.position.x), int(bullet.position.y)), GAME_SETTINGS['bullet']['size'])
            for item in self.items:
                color = COLORS['good_item_color'] if item.item_type == 'good' else COLORS['bad_item_color']
                pygame.draw.rect(screen, color, (item.position.x, item.position.y, GAME_SETTINGS['item']['size'], GAME_SETTINGS['item']['size']))  # Draw item as a rectangle
                item.display_effect_text(screen)  # Display the item's effect text
            pygame.draw.circle(screen, COLORS['player_color'], (int(self.player.position.x), int(self.player.position.y)), GAME_SETTINGS['player']['size'])
            self.draw_gun(screen)  # Draw the gun triangle
            for enemy in self.enemies:
                pygame.draw.circle(screen, COLORS['enemy_color'], (int(enemy.position.x), int(enemy.position.y)), GAME_SETTINGS['enemy']['size'])

            self.draw_ui()
            self.draw_effect_timers()  # Draw the effect timers
            pygame.display.flip()
            clock.tick(GAME_SETTINGS['fps'])

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
