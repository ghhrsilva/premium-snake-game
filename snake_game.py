"""
Premium Snake Game - Advanced Edition 🐍✨

Install pygame:
    python3.12 -m venv venv
    source venv/bin/activate
    pip install pygame

Run:
    python snake_game.py

Controls:
    Arrow Keys / WASD  - Move
    SPACE              - Pause / Resume
    ENTER              - Start / Restart
    ESC                - Quit / Back
    M                  - Mute / Unmute
    + / =              - Volume Up
    -                  - Volume Down

Features:
    - Premium neon UI
    - Persistent high score saved to snake_save.json
    - Procedural sound effects
    - Mute / unmute support
    - Volume control
    - Obstacles
    - Power-ups
    - Increasing difficulty
    - Particle effects
    - Main menu, pause screen, game-over screen
"""

import json
import math
import os
import random
import pygame


# ============================================================
# Basic Configuration
# ============================================================

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 680

CELL_SIZE = 24
TOP_BAR_HEIGHT = 64

GRID_COLUMNS = WINDOW_WIDTH // CELL_SIZE
GRID_ROWS = (WINDOW_HEIGHT - TOP_BAR_HEIGHT) // CELL_SIZE

FPS = 60
SAVE_FILE = "snake_save.json"

DIFFICULTIES = {
    "Easy": {
        "move_delay": 155,
        "score_multiplier": 1,
        "start_obstacles": 4,
        "color": (120, 255, 170),
    },
    "Normal": {
        "move_delay": 125,
        "score_multiplier": 2,
        "start_obstacles": 8,
        "color": (100, 210, 255),
    },
    "Hard": {
        "move_delay": 95,
        "score_multiplier": 3,
        "start_obstacles": 12,
        "color": (255, 120, 120),
    },
}

POWER_UP_TYPES = {
    "shield": {
        "name": "Shield",
        "duration": 8_000,
        "color": (90, 180, 255),
        "symbol": "S",
    },
    "slow": {
        "name": "Slow Motion",
        "duration": 7_000,
        "color": (170, 130, 255),
        "symbol": "T",
    },
    "double": {
        "name": "Double Score",
        "duration": 9_000,
        "color": (255, 210, 80),
        "symbol": "2X",
    },
    "bonus": {
        "name": "Bonus Points",
        "duration": 0,
        "color": (255, 120, 190),
        "symbol": "+",
    },
}

# Colors
BLACK = (7, 10, 18)
DARK_NAVY = (9, 15, 31)
PANEL = (17, 27, 54)
PANEL_LIGHT = (28, 44, 86)

WHITE = (245, 248, 255)
MUTED = (150, 163, 190)
SOFT_MUTED = (95, 110, 145)

NEON_GREEN = (85, 255, 150)
GREEN_DARK = (25, 160, 95)
NEON_CYAN = (80, 230, 255)
NEON_BLUE = (95, 150, 255)
NEON_PURPLE = (180, 115, 255)
NEON_PINK = (255, 90, 180)
NEON_RED = (255, 80, 95)
YELLOW = (255, 220, 90)
ORANGE = (255, 155, 70)

GRID_LINE = (27, 41, 75)
OBSTACLE = (115, 122, 145)
OBSTACLE_BORDER = (190, 198, 220)


# ============================================================
# Pygame Setup
# ============================================================

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except pygame.error:
    SOUND_AVAILABLE = False

pygame.display.set_caption("Premium Snake Game 🐍✨")

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("arial", 70, bold=True)
LARGE_FONT = pygame.font.SysFont("arial", 42, bold=True)
MEDIUM_FONT = pygame.font.SysFont("arial", 25, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 18)
TINY_FONT = pygame.font.SysFont("arial", 14)


# ============================================================
# Save System
# ============================================================

def load_save_data():
    """Load high score and audio settings."""
    default_data = {
        "high_score": 0,
        "muted": False,
        "volume": 0.45,
    }

    if not os.path.exists(SAVE_FILE):
        return default_data

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            saved_data = json.load(file)

        default_data.update(saved_data)
        return default_data

    except (json.JSONDecodeError, OSError):
        return default_data


def save_data(high_score, muted, volume):
    """Save high score and audio settings."""
    data = {
        "high_score": high_score,
        "muted": muted,
        "volume": volume,
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# ============================================================
# Sound System
# ============================================================

def create_tone(frequency, duration, volume):
    """Create a simple generated tone without external audio files."""
    if not SOUND_AVAILABLE:
        return None

    sample_rate = 44100
    sample_count = int(sample_rate * duration)
    buffer = bytearray()

    for sample_index in range(sample_count):
        time_value = sample_index / sample_rate

        wave = math.sin(2 * math.pi * frequency * time_value)
        fade = 1 - (sample_index / sample_count)

        amplitude = int(wave * 32767 * volume * fade)
        buffer += amplitude.to_bytes(2, byteorder="little", signed=True)

    return pygame.mixer.Sound(buffer=bytes(buffer))


class SoundManager:
    """Handles game sound effects, mute, and volume."""

    def __init__(self, muted=False, volume=0.45):
        self.muted = muted
        self.volume = volume

        self.sounds = {
            "click": create_tone(460, 0.06, 0.35),
            "start": create_tone(620, 0.13, 0.40),
            "eat": create_tone(760, 0.08, 0.45),
            "power": create_tone(980, 0.11, 0.45),
            "level": create_tone(520, 0.20, 0.45),
            "hit": create_tone(130, 0.35, 0.50),
            "pause": create_tone(380, 0.08, 0.35),
        }

        self.apply_volume()

    def apply_volume(self):
        """Apply volume to all generated sounds."""
        if not SOUND_AVAILABLE:
            return

        final_volume = 0 if self.muted else self.volume

        for sound in self.sounds.values():
            if sound:
                sound.set_volume(final_volume)

    def play(self, sound_name):
        """Play a sound effect."""
        if self.muted or not SOUND_AVAILABLE:
            return

        sound = self.sounds.get(sound_name)

        if sound:
            sound.play()

    def toggle_mute(self):
        """Mute or unmute game audio."""
        self.muted = not self.muted
        self.apply_volume()

    def volume_up(self):
        """Increase volume."""
        self.volume = min(1.0, self.volume + 0.1)
        self.apply_volume()

    def volume_down(self):
        """Decrease volume."""
        self.volume = max(0.0, self.volume - 0.1)
        self.apply_volume()


# ============================================================
# Drawing Helpers
# ============================================================

def draw_text(surface, text, font, color, x, y, center=True):
    """Draw text."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(rendered, rect)
    return rect


def draw_rounded_rect(surface, color, rect, radius=20, border_color=None, border_width=2):
    """Draw rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

    if border_color:
        pygame.draw.rect(surface, border_color, rect,
                         border_width, border_radius=radius)


def draw_vertical_gradient(surface, top_color, bottom_color):
    """Draw vertical gradient."""
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT

        red = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        green = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        blue = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)

        pygame.draw.line(surface, (red, green, blue),
                         (0, y), (WINDOW_WIDTH, y))


def draw_grid(surface, offset=0):
    """Draw animated grid."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_LINE,
                         (x, TOP_BAR_HEIGHT), (x, WINDOW_HEIGHT), 1)

    for row in range(GRID_ROWS + 1):
        y = TOP_BAR_HEIGHT + row * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE, (0, y), (WINDOW_WIDTH, y), 1)

    scanline_y = TOP_BAR_HEIGHT + \
        int(offset) % (WINDOW_HEIGHT - TOP_BAR_HEIGHT)
    pygame.draw.line(surface, (35, 65, 110), (0, scanline_y),
                     (WINDOW_WIDTH, scanline_y), 2)


def grid_to_pixel(position):
    """Convert grid position to pixel position."""
    column, row = position
    return column * CELL_SIZE, TOP_BAR_HEIGHT + row * CELL_SIZE


def clamp(value, minimum, maximum):
    """Clamp value between minimum and maximum."""
    return max(minimum, min(value, maximum))


def draw_glow_circle(surface, x, y, radius, color, alpha=70):
    """Draw fake glow circle."""
    glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)

    pygame.draw.circle(
        glow_surface,
        (*color, alpha),
        (radius * 2, radius * 2),
        radius * 2
    )

    surface.blit(glow_surface, (x - radius * 2, y - radius * 2))


def draw_glow_rect(surface, rect, color, radius=14):
    """Draw fake glow rectangle."""
    for size in range(4, 0, -1):
        glow_surface = pygame.Surface(
            (rect.width + size * 10, rect.height + size * 10),
            pygame.SRCALPHA
        )

        glow_rect = glow_surface.get_rect()
        glow_rect.center = (
            glow_surface.get_width() // 2,
            glow_surface.get_height() // 2
        )

        pygame.draw.rect(
            glow_surface,
            (*color, 30),
            glow_rect,
            border_radius=radius + size * 4
        )

        surface.blit(glow_surface, (rect.x - size * 5, rect.y - size * 5))

    pygame.draw.rect(surface, color, rect, border_radius=radius)


# ============================================================
# UI Button
# ============================================================

class Button:
    """Clickable UI button."""

    def __init__(self, text, x, y, width, height, accent_color):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.accent_color = accent_color

    def draw(self, surface, selected=False):
        """Draw button."""
        mouse_position = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_position)

        fill = PANEL_LIGHT if hovered else PANEL
        border = self.accent_color if hovered or selected else SOFT_MUTED
        text_color = WHITE if hovered or selected else MUTED

        shadow = self.rect.copy()
        shadow.y += 6
        pygame.draw.rect(surface, (3, 5, 12), shadow, border_radius=18)

        draw_rounded_rect(surface, fill, self.rect, 18, border, 2)
        draw_text(surface, self.text, MEDIUM_FONT, text_color,
                  self.rect.centerx, self.rect.centery)

    def clicked(self, event):
        """Check click."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# ============================================================
# Particle System
# ============================================================

class Particle:
    """Visual particle."""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.radius = random.randint(3, 7)
        self.life = random.randint(25, 45)

        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 4.5)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self):
        """Update particle."""
        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.94
        self.vy *= 0.94

        self.life -= 1
        self.radius = max(0, self.radius - 0.08)

    def draw(self, surface):
        """Draw particle."""
        if self.life <= 0:
            return

        alpha = clamp(self.life * 6, 0, 255)
        particle_surface = pygame.Surface((30, 30), pygame.SRCALPHA)

        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha),
            (15, 15),
            int(self.radius)
        )

        surface.blit(particle_surface, (self.x - 15, self.y - 15))


class ParticleSystem:
    """Manages particles."""

    def __init__(self):
        self.particles = []

    def burst(self, x, y, color, amount=24):
        """Create particles."""
        for _ in range(amount):
            self.particles.append(Particle(x, y, color))

    def update(self):
        """Update particles."""
        for particle in self.particles:
            particle.update()

        self.particles = [
            particle for particle in self.particles
            if particle.life > 0
        ]

    def draw(self, surface):
        """Draw particles."""
        for particle in self.particles:
            particle.draw(surface)


# ============================================================
# Snake
# ============================================================

class Snake:
    """Snake movement and rendering."""

    def __init__(self):
        start_column = GRID_COLUMNS // 2
        start_row = GRID_ROWS // 2

        self.body = [
            (start_column, start_row),
            (start_column - 1, start_row),
            (start_column - 2, start_row),
        ]

        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_next = False

    def set_direction(self, direction):
        """Change direction without instant reverse."""
        current_x, current_y = self.direction
        new_x, new_y = direction

        if current_x + new_x == 0 and current_y + new_y == 0:
            return

        self.next_direction = direction

    def move(self):
        """Move snake."""
        self.direction = self.next_direction

        head_column, head_row = self.body[0]
        direction_column, direction_row = self.direction

        new_head = (
            head_column + direction_column,
            head_row + direction_row
        )

        self.body.insert(0, new_head)

        if self.grow_next:
            self.grow_next = False
        else:
            self.body.pop()

    def grow(self):
        """Grow snake."""
        self.grow_next = True

    def hit_wall(self):
        """Check wall collision."""
        head_column, head_row = self.body[0]

        return (
            head_column < 0
            or head_column >= GRID_COLUMNS
            or head_row < 0
            or head_row >= GRID_ROWS
        )

    def hit_self(self):
        """Check self collision."""
        return self.body[0] in self.body[1:]

    def draw(self, surface, shield_active=False):
        """Draw snake."""
        for index, segment in enumerate(self.body):
            x, y = grid_to_pixel(segment)

            shrink = min(index, 8)
            rect = pygame.Rect(
                x + 3 + shrink // 3,
                y + 3 + shrink // 3,
                CELL_SIZE - 6 - shrink // 2,
                CELL_SIZE - 6 - shrink // 2
            )

            if index == 0:
                head_color = NEON_BLUE if shield_active else NEON_GREEN
                draw_glow_rect(surface, rect, head_color, radius=10)
                pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
            else:
                ratio = index / max(1, len(self.body))
                green_value = int(255 - ratio * 100)
                color = (40, green_value, 120)
                pygame.draw.rect(surface, color, rect, border_radius=9)

        self.draw_eyes(surface)

    def draw_eyes(self, surface):
        """Draw snake eyes."""
        head_x, head_y = grid_to_pixel(self.body[0])
        direction_x, direction_y = self.direction

        center_x = head_x + CELL_SIZE // 2
        center_y = head_y + CELL_SIZE // 2

        if direction_x == 1:
            eyes = [(center_x + 5, center_y - 5), (center_x + 5, center_y + 5)]
        elif direction_x == -1:
            eyes = [(center_x - 5, center_y - 5), (center_x - 5, center_y + 5)]
        elif direction_y == -1:
            eyes = [(center_x - 5, center_y - 5), (center_x + 5, center_y - 5)]
        else:
            eyes = [(center_x - 5, center_y + 5), (center_x + 5, center_y + 5)]

        for eye in eyes:
            pygame.draw.circle(surface, BLACK, eye, 4)
            pygame.draw.circle(surface, WHITE, (eye[0] - 1, eye[1] - 1), 1)


# ============================================================
# Food
# ============================================================

class Food:
    """Food object."""

    def __init__(self, blocked_cells):
        self.position = self.spawn(blocked_cells)
        self.timer = random.uniform(0, 10)

    def spawn(self, blocked_cells):
        """Spawn food away from blocked cells."""
        while True:
            position = (
                random.randint(1, GRID_COLUMNS - 2),
                random.randint(1, GRID_ROWS - 2)
            )

            if position not in blocked_cells:
                return position

    def respawn(self, blocked_cells):
        """Respawn food."""
        self.position = self.spawn(blocked_cells)

    def draw(self, surface):
        """Draw animated food."""
        self.timer += 0.08

        x, y = grid_to_pixel(self.position)
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2

        floating = math.sin(self.timer) * 3
        pulse = (math.sin(self.timer * 2) + 1) / 2

        draw_glow_circle(surface, center_x, int(
            center_y + floating), int(12 + pulse * 5), NEON_RED, 55)

        pygame.draw.circle(
            surface,
            NEON_RED,
            (center_x, int(center_y + floating)),
            int(8 + pulse * 2)
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (center_x - 3, int(center_y - 3 + floating)),
            3
        )


# ============================================================
# Obstacles
# ============================================================

class ObstacleManager:
    """Creates and draws obstacles."""

    def __init__(self):
        self.obstacles = []

    def generate(self, snake_body, amount):
        """Generate obstacles."""
        self.obstacles = []

        while len(self.obstacles) < amount:
            position = self.random_position()

            if self.is_valid_position(position, snake_body, None):
                self.obstacles.append(position)

    def random_position(self):
        """Return random grid position."""
        return (
            random.randint(1, GRID_COLUMNS - 2),
            random.randint(1, GRID_ROWS - 2)
        )

    def is_valid_position(self, position, snake_body, food_position):
        """Check whether obstacle position is safe."""
        snake_head = snake_body[0]
        distance = abs(position[0] - snake_head[0]) + \
            abs(position[1] - snake_head[1])

        return (
            position not in snake_body
            and position not in self.obstacles
            and position != food_position
            and distance > 6
        )

    def add_obstacles(self, snake_body, food_position, amount):
        """Add more obstacles as level increases."""
        added = 0
        tries = 0

        while added < amount and tries < 500:
            tries += 1
            position = self.random_position()

            if self.is_valid_position(position, snake_body, food_position):
                self.obstacles.append(position)
                added += 1

    def remove_obstacle(self, position):
        """Remove one obstacle."""
        if position in self.obstacles:
            self.obstacles.remove(position)

    def draw(self, surface):
        """Draw obstacles."""
        for obstacle in self.obstacles:
            x, y = grid_to_pixel(obstacle)

            rect = pygame.Rect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
            shine = pygame.Rect(x + 7, y + 7, CELL_SIZE - 14, 5)

            pygame.draw.rect(surface, OBSTACLE, rect, border_radius=7)
            pygame.draw.rect(surface, OBSTACLE_BORDER,
                             rect, 2, border_radius=7)
            pygame.draw.rect(surface, WHITE, shine, border_radius=4)


# ============================================================
# Power-Up
# ============================================================

class PowerUp:
    """Power-up object."""

    def __init__(self, blocked_cells):
        self.kind = random.choice(list(POWER_UP_TYPES.keys()))
        self.position = self.spawn(blocked_cells)
        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 10_000
        self.timer = random.uniform(0, 10)

    def spawn(self, blocked_cells):
        """Spawn power-up away from blocked cells."""
        while True:
            position = (
                random.randint(1, GRID_COLUMNS - 2),
                random.randint(1, GRID_ROWS - 2)
            )

            if position not in blocked_cells:
                return position

    def expired(self):
        """Check whether power-up expired."""
        return pygame.time.get_ticks() - self.spawn_time > self.life_time

    def draw(self, surface):
        """Draw power-up."""
        self.timer += 0.1

        config = POWER_UP_TYPES[self.kind]
        color = config["color"]
        symbol = config["symbol"]

        x, y = grid_to_pixel(self.position)
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2

        floating = math.sin(self.timer) * 4
        radius = int(10 + math.sin(self.timer * 2) * 2)

        draw_glow_circle(surface, center_x, int(
            center_y + floating), 15, color, 60)

        pygame.draw.circle(
            surface, color, (center_x, int(center_y + floating)), radius)
        pygame.draw.circle(
            surface, WHITE, (center_x, int(center_y + floating)), radius, 2)

        draw_text(
            surface,
            symbol,
            TINY_FONT,
            BLACK,
            center_x,
            int(center_y + floating)
        )


# ============================================================
# Main Game
# ============================================================

class PremiumSnakeGame:
    """Main game controller."""

    def __init__(self):
        save = load_save_data()

        self.high_score = save["high_score"]
        self.selected_difficulty = "Normal"

        self.sound_manager = SoundManager(
            muted=save["muted"],
            volume=save["volume"]
        )

        self.menu_timer = 0
        self.transition_alpha = 0

        self.start_button = Button(
            "START GAME",
            WINDOW_WIDTH // 2 - 155,
            360,
            310,
            58,
            NEON_GREEN
        )

        self.easy_button = Button(
            "EASY",
            WINDOW_WIDTH // 2 - 260,
            450,
            150,
            52,
            DIFFICULTIES["Easy"]["color"]
        )

        self.normal_button = Button(
            "NORMAL",
            WINDOW_WIDTH // 2 - 75,
            450,
            150,
            52,
            DIFFICULTIES["Normal"]["color"]
        )

        self.hard_button = Button(
            "HARD",
            WINDOW_WIDTH // 2 + 110,
            450,
            150,
            52,
            DIFFICULTIES["Hard"]["color"]
        )

        self.mute_button = Button(
            "MUTE",
            WINDOW_WIDTH - 145,
            14,
            120,
            38,
            NEON_CYAN
        )

        self.reset_game_objects()
        self.state = "menu"

    def reset_game_objects(self):
        """Reset game objects."""
        self.snake = Snake()
        self.particles = ParticleSystem()

        # IMPORTANT:
        # Create power_up before calling get_blocked_cells().
        # Otherwise get_blocked_cells() tries to read self.power_up
        # before it exists, and Python throws an AttributeError.
        self.power_up = None

        difficulty = DIFFICULTIES[self.selected_difficulty]

        self.obstacle_manager = ObstacleManager()
        self.obstacle_manager.generate(
            self.snake.body,
            difficulty["start_obstacles"]
        )

        blocked_cells = self.get_blocked_cells()
        self.food = Food(blocked_cells)

        self.next_power_spawn_time = pygame.time.get_ticks() + random.randint(6_000, 10_000)

        self.score = 0
        self.level = 1
        self.previous_level = 1

        self.active_effects = {
            "shield": 0,
            "slow": 0,
            "double": 0,
        }

        self.move_delay = difficulty["move_delay"]
        self.last_move_time = pygame.time.get_ticks()

    def get_blocked_cells(self):
        """Return cells occupied by snake, obstacles, and food if available."""
        blocked = set(self.snake.body)
        blocked.update(self.obstacle_manager.obstacles)

        if hasattr(self, "food"):
            blocked.add(self.food.position)

        if self.power_up:
            blocked.add(self.power_up.position)

        return blocked

    def start_game(self):
        """Start new game."""
        self.reset_game_objects()
        self.state = "playing"
        self.transition_alpha = 180
        self.sound_manager.play("start")

    def save_current_settings(self):
        """Save high score and audio settings."""
        save_data(
            self.high_score,
            self.sound_manager.muted,
            self.sound_manager.volume
        )

    def toggle_mute(self):
        """Toggle mute."""
        self.sound_manager.toggle_mute()
        self.save_current_settings()

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_current_settings()
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.toggle_mute()

                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    self.sound_manager.volume_up()
                    self.save_current_settings()

                elif event.key == pygame.K_MINUS:
                    self.sound_manager.volume_down()
                    self.save_current_settings()

                elif event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                        self.sound_manager.play("pause")
                    elif self.state == "paused":
                        self.state = "playing"
                        self.sound_manager.play("pause")
                    else:
                        self.save_current_settings()
                        return False

                elif self.state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.start_game()

                elif self.state == "playing":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.snake.set_direction((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.snake.set_direction((0, 1))
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.snake.set_direction((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.snake.set_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        self.state = "paused"
                        self.sound_manager.play("pause")

                elif self.state == "paused":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.sound_manager.play("pause")

                elif self.state == "game_over":
                    if event.key == pygame.K_RETURN:
                        self.start_game()

            if self.mute_button.clicked(event):
                self.toggle_mute()

            if self.state == "menu":
                if self.start_button.clicked(event):
                    self.start_game()

                elif self.easy_button.clicked(event):
                    self.selected_difficulty = "Easy"
                    self.sound_manager.play("click")

                elif self.normal_button.clicked(event):
                    self.selected_difficulty = "Normal"
                    self.sound_manager.play("click")

                elif self.hard_button.clicked(event):
                    self.selected_difficulty = "Hard"
                    self.sound_manager.play("click")

            elif self.state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.start_game()

        return True

    def effect_active(self, effect_name):
        """Check active power-up effect."""
        return pygame.time.get_ticks() < self.active_effects[effect_name]

    def update_difficulty(self):
        """Make the game harder as level increases."""
        difficulty = DIFFICULTIES[self.selected_difficulty]
        base_delay = difficulty["move_delay"]

        delay_reduction = (self.level - 1) * 7

        if self.effect_active("slow"):
            self.move_delay = max(75, base_delay - delay_reduction + 45)
        else:
            self.move_delay = max(42, base_delay - delay_reduction)

        if self.level > self.previous_level:
            obstacles_to_add = 2

            if self.level >= 5:
                obstacles_to_add = 3

            if self.level >= 10:
                obstacles_to_add = 4

            self.obstacle_manager.add_obstacles(
                self.snake.body,
                self.food.position,
                obstacles_to_add
            )

            self.previous_level = self.level
            self.sound_manager.play("level")

    def maybe_spawn_power_up(self):
        """Spawn power-up sometimes."""
        current_time = pygame.time.get_ticks()

        if self.power_up and self.power_up.expired():
            self.power_up = None
            self.next_power_spawn_time = current_time + \
                random.randint(6_000, 11_000)

        if self.power_up is None and current_time >= self.next_power_spawn_time:
            blocked = self.get_blocked_cells()
            self.power_up = PowerUp(blocked)

    def apply_power_up(self, kind):
        """Apply collected power-up."""
        current_time = pygame.time.get_ticks()
        config = POWER_UP_TYPES[kind]

        if kind == "bonus":
            self.score += 50
            self.particles.burst(
                *self.get_cell_center(self.snake.body[0]),
                config["color"],
                amount=36
            )
        else:
            self.active_effects[kind] = current_time + config["duration"]

        self.sound_manager.play("power")

    def get_cell_center(self, position):
        """Get pixel center of a grid cell."""
        x, y = grid_to_pixel(position)
        return x + CELL_SIZE // 2, y + CELL_SIZE // 2

    def handle_collision(self):
        """Handle collisions."""
        head = self.snake.body[0]

        hit_wall = self.snake.hit_wall()
        hit_self = self.snake.hit_self()
        hit_obstacle = head in self.obstacle_manager.obstacles

        if hit_obstacle and self.effect_active("shield"):
            self.obstacle_manager.remove_obstacle(head)
            self.particles.burst(
                *self.get_cell_center(head),
                POWER_UP_TYPES["shield"]["color"],
                amount=34
            )
            self.sound_manager.play("power")
            return False

        if hit_wall or hit_self or hit_obstacle:
            self.state = "game_over"
            self.sound_manager.play("hit")

            if self.score > self.high_score:
                self.high_score = self.score
                self.save_current_settings()

            return True

        return False

    def update(self):
        """Update game."""
        self.menu_timer += 0.025

        if self.transition_alpha > 0:
            self.transition_alpha -= 8

        self.particles.update()

        if self.state != "playing":
            return

        self.maybe_spawn_power_up()
        self.update_difficulty()

        current_time = pygame.time.get_ticks()

        if current_time - self.last_move_time < self.move_delay:
            return

        self.snake.move()
        self.last_move_time = current_time

        if self.handle_collision():
            return

        head = self.snake.body[0]

        if head == self.food.position:
            multiplier = DIFFICULTIES[self.selected_difficulty]["score_multiplier"]

            if self.effect_active("double"):
                multiplier *= 2

            self.score += 10 * multiplier
            self.level = self.score // 90 + 1

            self.snake.grow()
            self.sound_manager.play("eat")

            self.particles.burst(
                *self.get_cell_center(self.food.position),
                DIFFICULTIES[self.selected_difficulty]["color"],
                amount=28
            )

            self.food.respawn(self.get_blocked_cells())

        if self.power_up and head == self.power_up.position:
            self.apply_power_up(self.power_up.kind)
            self.power_up = None
            self.next_power_spawn_time = current_time + \
                random.randint(7_000, 12_000)

    def draw_background(self):
        """Draw premium background."""
        draw_vertical_gradient(screen, DARK_NAVY, BLACK)

        colors = [NEON_CYAN, NEON_PURPLE, NEON_GREEN, NEON_PINK, NEON_BLUE]

        for index in range(5):
            x = int((index * 220 + math.sin(self.menu_timer + index) * 40) %
                    WINDOW_WIDTH)
            y = int(110 + index * 115 + math.cos(self.menu_timer + index) * 24)

            glow_surface = pygame.Surface((190, 190), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface, (*colors[index], 22), (95, 95), 78)
            screen.blit(glow_surface, (x - 95, y - 95))

    def draw_audio_button(self):
        """Draw mute/unmute button."""
        text = "UNMUTE" if self.sound_manager.muted else "MUTE"
        self.mute_button.text = text
        self.mute_button.draw(screen)

    def draw_menu(self):
        """Draw menu."""
        self.draw_background()

        title_y = 145 + math.sin(self.menu_timer * 1.6) * 8

        draw_text(screen, "PREMIUM", TITLE_FONT,
                  NEON_CYAN, WINDOW_WIDTH // 2, title_y)
        draw_text(screen, "SNAKE", TITLE_FONT, NEON_GREEN,
                  WINDOW_WIDTH // 2, title_y + 72)

        draw_text(
            screen,
            "Obstacles • Power-ups • Sound • Saved high score • Chaos, but make it aesthetic",
            SMALL_FONT,
            MUTED,
            WINDOW_WIDTH // 2,
            268
        )

        cards = [
            ("Obstacles", ORANGE),
            ("Power-ups", NEON_PINK),
            ("Hard Levels", NEON_RED),
        ]

        card_width = 190
        start_x = WINDOW_WIDTH // 2 - ((card_width * 3 + 24 * 2) // 2)

        for index, (text, color) in enumerate(cards):
            rect = pygame.Rect(start_x + index *
                               (card_width + 24), 298, card_width, 66)
            draw_rounded_rect(screen, PANEL, rect, 18, color, 2)
            draw_text(screen, text, SMALL_FONT, WHITE,
                      rect.centerx, rect.centery)

        self.start_button.draw(screen)

        draw_text(screen, "Select Difficulty", SMALL_FONT,
                  MUTED, WINDOW_WIDTH // 2, 432)

        self.easy_button.draw(screen, self.selected_difficulty == "Easy")
        self.normal_button.draw(screen, self.selected_difficulty == "Normal")
        self.hard_button.draw(screen, self.selected_difficulty == "Hard")

        selected_color = DIFFICULTIES[self.selected_difficulty]["color"]

        draw_text(
            screen,
            f"Selected: {self.selected_difficulty}",
            MEDIUM_FONT,
            selected_color,
            WINDOW_WIDTH // 2,
            535
        )

        volume_percent = int(self.sound_manager.volume * 100)

        audio_text = "Muted" if self.sound_manager.muted else f"Volume: {volume_percent}%"

        draw_text(
            screen,
            f"High Score: {self.high_score}   •   Audio: {audio_text}",
            SMALL_FONT,
            YELLOW,
            WINDOW_WIDTH // 2,
            580
        )

        draw_text(
            screen,
            "ENTER Start • M Mute • + / - Volume • ESC Quit",
            TINY_FONT,
            SOFT_MUTED,
            WINDOW_WIDTH // 2,
            625
        )

        self.draw_audio_button()

    def draw_top_bar(self):
        """Draw HUD."""
        top_rect = pygame.Rect(0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT)

        pygame.draw.rect(screen, PANEL, top_rect)
        pygame.draw.line(screen, PANEL_LIGHT, (0, TOP_BAR_HEIGHT),
                         (WINDOW_WIDTH, TOP_BAR_HEIGHT), 2)

        difficulty_color = DIFFICULTIES[self.selected_difficulty]["color"]

        draw_text(screen, "SNAKE", MEDIUM_FONT,
                  NEON_GREEN, 24, 18, center=False)
        draw_text(screen, f"Score: {self.score}",
                  SMALL_FONT, WHITE, 145, 22, center=False)
        draw_text(screen, f"High: {self.high_score}",
                  SMALL_FONT, YELLOW, 270, 22, center=False)
        draw_text(screen, f"Level: {self.level}",
                  SMALL_FONT, NEON_CYAN, 390, 22, center=False)
        draw_text(screen, f"Mode: {self.selected_difficulty}",
                  SMALL_FONT, difficulty_color, 500, 22, center=False)
        draw_text(screen, f"Obstacles: {len(self.obstacle_manager.obstacles)}",
                  SMALL_FONT, ORANGE, 640, 22, center=False)

        self.draw_audio_button()

    def draw_active_effects(self):
        """Draw active power-up effects."""
        current_time = pygame.time.get_ticks()
        x = 18
        y = WINDOW_HEIGHT - 42

        for effect, end_time in self.active_effects.items():
            if current_time < end_time:
                config = POWER_UP_TYPES[effect]
                seconds_left = max(0, (end_time - current_time) // 1000)

                rect = pygame.Rect(x, y, 165, 30)
                draw_rounded_rect(screen, PANEL, rect, 14, config["color"], 2)

                draw_text(
                    screen,
                    f"{config['name']}: {seconds_left}s",
                    TINY_FONT,
                    WHITE,
                    rect.centerx,
                    rect.centery
                )

                x += 175

    def draw_game(self):
        """Draw gameplay."""
        self.draw_background()
        draw_grid(screen, offset=pygame.time.get_ticks() / 12)

        self.draw_top_bar()
        self.obstacle_manager.draw(screen)
        self.food.draw(screen)

        if self.power_up:
            self.power_up.draw(screen)

        self.snake.draw(screen, shield_active=self.effect_active("shield"))
        self.particles.draw(screen)
        self.draw_active_effects()

    def draw_pause_overlay(self):
        """Draw pause screen."""
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 280,
                            WINDOW_HEIGHT // 2 - 145, 560, 290)
        draw_rounded_rect(screen, PANEL, panel, 28, NEON_CYAN, 3)

        draw_text(screen, "PAUSED", LARGE_FONT, YELLOW,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 70)
        draw_text(screen, "SPACE to continue", SMALL_FONT, WHITE,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 15)
        draw_text(screen, "M mute • + / - volume • ESC resume",
                  SMALL_FONT, MUTED, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25)

    def draw_game_over(self):
        """Draw game over screen."""
        self.draw_background()

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 315,
                            WINDOW_HEIGHT // 2 - 230, 630, 460)
        draw_rounded_rect(screen, PANEL, panel, 30, NEON_RED, 3)

        draw_text(screen, "GAME OVER", TITLE_FONT, NEON_RED,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 155)

        draw_text(screen, f"Final Score: {self.score}", MEDIUM_FONT,
                  WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 70)
        draw_text(screen, f"High Score: {self.high_score}", MEDIUM_FONT,
                  YELLOW, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)
        draw_text(screen, f"Level Reached: {self.level}", MEDIUM_FONT,
                  NEON_CYAN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10)
        draw_text(screen, f"Difficulty: {self.selected_difficulty}", MEDIUM_FONT,
                  DIFFICULTIES[self.selected_difficulty]["color"], WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        draw_text(screen, f"Obstacles Survived: {len(self.obstacle_manager.obstacles)}",
                  MEDIUM_FONT, ORANGE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90)

        restart = pygame.Rect(WINDOW_WIDTH // 2 - 170,
                              WINDOW_HEIGHT // 2 + 140, 340, 58)
        draw_rounded_rect(screen, PANEL_LIGHT, restart, 18, NEON_GREEN, 2)

        draw_text(screen, "ENTER / CLICK TO RESTART", SMALL_FONT,
                  WHITE, restart.centerx, restart.centery)
        draw_text(screen, "ESC to quit", TINY_FONT, MUTED,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 210)

    def draw_transition(self):
        """Draw fade transition."""
        if self.transition_alpha <= 0:
            return

        transition = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        transition.fill((255, 255, 255, self.transition_alpha))
        screen.blit(transition, (0, 0))

    def draw(self):
        """Draw current state."""
        if self.state == "menu":
            self.draw_menu()

        elif self.state == "playing":
            self.draw_game()

        elif self.state == "paused":
            self.draw_game()
            self.draw_pause_overlay()

        elif self.state == "game_over":
            self.draw_game_over()

        self.draw_transition()
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

        self.save_current_settings()
        pygame.quit()


# ============================================================
# Run Game
# ============================================================

if __name__ == "__main__":
    game = PremiumSnakeGame()
    game.run()
