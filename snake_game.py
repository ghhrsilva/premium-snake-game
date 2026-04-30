"""
Advanced Snake Game - Obstacles + Sound + Persistent High Score 🐍

How to install pygame:
    python3.12 -m venv venv
    source venv/bin/activate
    pip install pygame

How to run:
    python snake_game.py

Controls:
    Arrow Keys / WASD  - Move
    SPACE              - Pause / Resume
    ENTER              - Start / Restart
    ESC                - Quit

Features:
    - Modern UI
    - Animated food
    - Snake eyes
    - Obstacles
    - Sound effects
    - Persistent high score saved to high_score.txt
    - Score, level, speed scaling
"""

import os
import random
import math
import pygame


# ============================================================
# Game Configuration
# ============================================================

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650

CELL_SIZE = 25
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

FPS = 60
START_MOVE_DELAY = 140
HIGH_SCORE_FILE = "high_score.txt"

# Colors
BLACK = (10, 10, 18)
DARK_BLUE = (12, 18, 35)
WHITE = (240, 240, 245)
GRAY = (140, 150, 165)
LIGHT_GRAY = (190, 200, 215)

GREEN = (40, 220, 120)
DARK_GREEN = (20, 150, 85)
LIME = (120, 255, 140)

RED = (245, 70, 80)
DARK_RED = (160, 30, 40)

YELLOW = (255, 220, 80)
CYAN = (80, 220, 255)
PURPLE = (170, 100, 255)
ORANGE = (255, 145, 60)

PANEL_COLOR = (20, 28, 48)
PANEL_BORDER = (80, 110, 180)
GRID_COLOR = (35, 45, 70)
OBSTACLE_COLOR = (110, 115, 135)
OBSTACLE_BORDER = (180, 185, 205)


# ============================================================
# Pygame Setup
# ============================================================

pygame.init()
pygame.mixer.init()

pygame.display.set_caption("Advanced Snake Game 🐍")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("arial", 58, bold=True)
LARGE_FONT = pygame.font.SysFont("arial", 38, bold=True)
MEDIUM_FONT = pygame.font.SysFont("arial", 26, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20)
TINY_FONT = pygame.font.SysFont("arial", 16)


# ============================================================
# Sound System
# ============================================================

def create_tone(frequency=440, duration=0.12, volume=0.25):
    """
    Create a simple beep sound using pygame's array system.

    This avoids needing external .wav files.
    Because apparently even a snake game needs audio engineering now.
    """
    sample_rate = 44100
    sample_count = int(sample_rate * duration)

    buffer = bytearray()

    for sample_index in range(sample_count):
        time_value = sample_index / sample_rate
        wave = math.sin(2 * math.pi * frequency * time_value)
        amplitude = int(wave * 32767 * volume)

        buffer += amplitude.to_bytes(2, byteorder="little", signed=True)

    return pygame.mixer.Sound(buffer=bytes(buffer))


class SoundManager:
    """Handles all game sound effects."""

    def __init__(self):
        self.eat_sound = create_tone(720, 0.08, 0.25)
        self.game_over_sound = create_tone(160, 0.35, 0.35)
        self.pause_sound = create_tone(420, 0.08, 0.18)
        self.start_sound = create_tone(540, 0.12, 0.22)

    def play_eat(self):
        self.eat_sound.play()

    def play_game_over(self):
        self.game_over_sound.play()

    def play_pause(self):
        self.pause_sound.play()

    def play_start(self):
        self.start_sound.play()


# ============================================================
# High Score System
# ============================================================

def load_high_score():
    """Load high score from file."""
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read().strip())
    except ValueError:
        return 0


def save_high_score(score):
    """Save high score to file."""
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
        file.write(str(score))


# ============================================================
# Helper Functions
# ============================================================

def draw_text(surface, text, font, color, x, y, center=True):
    """Draw text on the screen."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    surface.blit(text_surface, text_rect)


def draw_rounded_rect(surface, color, rect, radius=15, border_color=None, border_width=2):
    """Draw a rounded rectangle with optional border."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

    if border_color:
        pygame.draw.rect(surface, border_color, rect,
                         border_width, border_radius=radius)


def draw_gradient_background(surface):
    """Draw a vertical gradient background."""
    for y in range(WINDOW_HEIGHT):
        ratio = y / WINDOW_HEIGHT

        red = int(DARK_BLUE[0] * (1 - ratio) + BLACK[0] * ratio)
        green = int(DARK_BLUE[1] * (1 - ratio) + BLACK[1] * ratio)
        blue = int(DARK_BLUE[2] * (1 - ratio) + BLACK[2] * ratio)

        pygame.draw.line(surface, (red, green, blue),
                         (0, y), (WINDOW_WIDTH, y))


def draw_grid(surface):
    """Draw a subtle grid background."""
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)

    for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)


def cell_to_pixel(position):
    """Convert grid coordinates to pixel coordinates."""
    x, y = position
    return x * CELL_SIZE, y * CELL_SIZE


def create_button(surface, text, x, y, width, height):
    """Draw a button-like UI element."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)
    is_hovered = rect.collidepoint(mouse_x, mouse_y)

    if is_hovered:
        button_color = (45, 65, 110)
        border_color = CYAN
    else:
        button_color = PANEL_COLOR
        border_color = PANEL_BORDER

    draw_rounded_rect(surface, button_color, rect, 14, border_color, 2)
    draw_text(surface, text, MEDIUM_FONT, WHITE,
              x + width // 2, y + height // 2)

    return rect


# ============================================================
# Food Class
# ============================================================

class Food:
    """Handles food spawning, animation, and drawing."""

    def __init__(self, snake_body, obstacles):
        self.position = self.spawn(snake_body, obstacles)
        self.animation_timer = 0

    def spawn(self, snake_body, obstacles):
        """Spawn food in a random empty grid cell."""
        while True:
            position = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(2, GRID_HEIGHT - 2)
            )

            if position not in snake_body and position not in obstacles:
                return position

    def respawn(self, snake_body, obstacles):
        """Move food to a new valid location."""
        self.position = self.spawn(snake_body, obstacles)

    def draw(self, surface):
        """Draw animated food."""
        self.animation_timer += 0.12

        x, y = cell_to_pixel(self.position)

        pulse = abs(math.sin(self.animation_timer))
        size_offset = int(pulse * 5)

        food_rect = pygame.Rect(
            x + 4 - size_offset // 2,
            y + 4 - size_offset // 2,
            CELL_SIZE - 8 + size_offset,
            CELL_SIZE - 8 + size_offset
        )

        glow_rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

        pygame.draw.rect(surface, DARK_RED, glow_rect, border_radius=8)
        pygame.draw.rect(surface, RED, food_rect, border_radius=8)
        pygame.draw.circle(surface, WHITE, (x + 10, y + 9), 3)


# ============================================================
# Obstacle Manager
# ============================================================

class ObstacleManager:
    """Creates, stores, and draws obstacles."""

    def __init__(self):
        self.obstacles = []

    def generate(self, snake_body, amount):
        """Generate obstacles without overlapping snake."""
        self.obstacles = []

        while len(self.obstacles) < amount:
            position = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(3, GRID_HEIGHT - 2)
            )

            too_close_to_snake_head = self.is_too_close(
                position, snake_body[0], min_distance=5)

            if (
                position not in snake_body
                and position not in self.obstacles
                and not too_close_to_snake_head
            ):
                self.obstacles.append(position)

    def is_too_close(self, position_1, position_2, min_distance):
        """Avoid spawning obstacles too close to the snake head."""
        x1, y1 = position_1
        x2, y2 = position_2

        distance = abs(x1 - x2) + abs(y1 - y2)
        return distance < min_distance

    def add_more_obstacles(self, snake_body, food_position, amount):
        """Add extra obstacles as the level increases."""
        added = 0

        while added < amount:
            position = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(3, GRID_HEIGHT - 2)
            )

            if (
                position not in snake_body
                and position not in self.obstacles
                and position != food_position
            ):
                self.obstacles.append(position)
                added += 1

    def draw(self, surface):
        """Draw obstacles with a metallic block style."""
        for obstacle in self.obstacles:
            x, y = cell_to_pixel(obstacle)

            rect = pygame.Rect(x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
            shine = pygame.Rect(x + 7, y + 7, CELL_SIZE - 14, 5)

            pygame.draw.rect(surface, OBSTACLE_COLOR, rect, border_radius=6)
            pygame.draw.rect(surface, OBSTACLE_BORDER,
                             rect, 2, border_radius=6)
            pygame.draw.rect(surface, LIGHT_GRAY, shine, border_radius=4)


# ============================================================
# Snake Class
# ============================================================

class Snake:
    """Snake movement, drawing, growth, and collision logic."""

    def __init__(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2

        self.body = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y)
        ]

        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.should_grow = False

    def set_direction(self, new_direction):
        """Set direction while preventing instant reverse movement."""
        current_x, current_y = self.direction
        new_x, new_y = new_direction

        if (current_x + new_x, current_y + new_y) != (0, 0):
            self.next_direction = new_direction

    def move(self):
        """Move snake by one grid cell."""
        self.direction = self.next_direction

        head_x, head_y = self.body[0]
        move_x, move_y = self.direction

        new_head = (head_x + move_x, head_y + move_y)

        self.body.insert(0, new_head)

        if self.should_grow:
            self.should_grow = False
        else:
            self.body.pop()

    def grow(self):
        """Grow snake on the next move."""
        self.should_grow = True

    def hits_wall(self):
        """Check wall collision."""
        head_x, head_y = self.body[0]

        return (
            head_x < 0
            or head_x >= GRID_WIDTH
            or head_y < 1
            or head_y >= GRID_HEIGHT
        )

    def hits_self(self):
        """Check self collision."""
        return self.body[0] in self.body[1:]

    def hits_obstacle(self, obstacles):
        """Check obstacle collision."""
        return self.body[0] in obstacles

    def draw(self, surface):
        """Draw the snake."""
        for index, segment in enumerate(self.body):
            x, y = cell_to_pixel(segment)
            rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)

            if index == 0:
                color = LIME
                border_color = WHITE
            else:
                color = GREEN if index % 2 == 0 else DARK_GREEN
                border_color = None

            pygame.draw.rect(surface, color, rect, border_radius=8)

            if border_color:
                pygame.draw.rect(surface, border_color,
                                 rect, 2, border_radius=8)

        self.draw_eyes(surface)

    def draw_eyes(self, surface):
        """Draw snake eyes based on direction."""
        head_x, head_y = cell_to_pixel(self.body[0])
        direction_x, direction_y = self.direction

        center_x = head_x + CELL_SIZE // 2
        center_y = head_y + CELL_SIZE // 2

        if direction_x == 1:
            eye_1 = (center_x + 5, center_y - 5)
            eye_2 = (center_x + 5, center_y + 5)
        elif direction_x == -1:
            eye_1 = (center_x - 5, center_y - 5)
            eye_2 = (center_x - 5, center_y + 5)
        elif direction_y == -1:
            eye_1 = (center_x - 5, center_y - 5)
            eye_2 = (center_x + 5, center_y - 5)
        else:
            eye_1 = (center_x - 5, center_y + 5)
            eye_2 = (center_x + 5, center_y + 5)

        pygame.draw.circle(surface, BLACK, eye_1, 3)
        pygame.draw.circle(surface, BLACK, eye_2, 3)


# ============================================================
# Game Class
# ============================================================

class SnakeGame:
    """Main game controller."""

    def __init__(self):
        self.sound_manager = SoundManager()
        self.high_score = load_high_score()
        self.reset()

    def reset(self):
        """Reset game objects and state."""
        self.snake = Snake()

        self.obstacle_manager = ObstacleManager()
        self.obstacle_manager.generate(self.snake.body, amount=8)

        self.food = Food(self.snake.body, self.obstacle_manager.obstacles)

        self.score = 0
        self.level = 1
        self.move_delay = START_MOVE_DELAY
        self.last_move_time = pygame.time.get_ticks()

        self.state = "menu"
        self.previous_level = 1

    def start_game(self):
        """Start a new game."""
        self.snake = Snake()

        self.obstacle_manager = ObstacleManager()
        self.obstacle_manager.generate(self.snake.body, amount=8)

        self.food = Food(self.snake.body, self.obstacle_manager.obstacles)

        self.score = 0
        self.level = 1
        self.previous_level = 1
        self.move_delay = START_MOVE_DELAY
        self.last_move_time = pygame.time.get_ticks()

        self.state = "playing"
        self.sound_manager.play_start()

    def trigger_game_over(self):
        """Handle game over logic."""
        self.state = "game_over"
        self.sound_manager.play_game_over()

        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def handle_events(self):
        """Handle keyboard input and window close."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state == "menu":
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
                        self.sound_manager.play_pause()

                elif self.state == "paused":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.sound_manager.play_pause()

                elif self.state == "game_over":
                    if event.key == pygame.K_RETURN:
                        self.start_game()

        return True

    def update(self):
        """Update game state."""
        if self.state != "playing":
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.last_move_time >= self.move_delay:
            self.snake.move()
            self.last_move_time = current_time

            if (
                self.snake.hits_wall()
                or self.snake.hits_self()
                or self.snake.hits_obstacle(self.obstacle_manager.obstacles)
            ):
                self.trigger_game_over()
                return

            if self.snake.body[0] == self.food.position:
                self.score += 10
                self.snake.grow()
                self.sound_manager.play_eat()

                self.food.respawn(
                    self.snake.body, self.obstacle_manager.obstacles)

                self.level = self.score // 50 + 1
                self.move_delay = max(
                    55, START_MOVE_DELAY - (self.level - 1) * 10)

                if self.level > self.previous_level:
                    self.obstacle_manager.add_more_obstacles(
                        self.snake.body,
                        self.food.position,
                        amount=2
                    )
                    self.previous_level = self.level

    def draw_top_bar(self):
        """Draw the top score/status bar."""
        top_bar = pygame.Rect(0, 0, WINDOW_WIDTH, CELL_SIZE)

        pygame.draw.rect(screen, PANEL_COLOR, top_bar)
        pygame.draw.line(screen, PANEL_BORDER, (0, CELL_SIZE),
                         (WINDOW_WIDTH, CELL_SIZE), 2)

        draw_text(screen, f"Score: {self.score}",
                  SMALL_FONT, WHITE, 20, 4, center=False)
        draw_text(screen, f"High Score: {self.high_score}",
                  SMALL_FONT, YELLOW, 160, 4, center=False)
        draw_text(screen, f"Level: {self.level}",
                  SMALL_FONT, CYAN, 390, 4, center=False)
        draw_text(screen, f"Obstacles: {len(self.obstacle_manager.obstacles)}",
                  SMALL_FONT, ORANGE, 510, 4, center=False)
        draw_text(screen, "SPACE: Pause   ESC: Quit",
                  SMALL_FONT, LIGHT_GRAY, 685, 4, center=False)

    def draw_menu(self):
        """Draw the main menu."""
        draw_gradient_background(screen)

        draw_text(screen, "ADVANCED", TITLE_FONT, CYAN, WINDOW_WIDTH // 2, 130)
        draw_text(screen, "SNAKE GAME", TITLE_FONT,
                  GREEN, WINDOW_WIDTH // 2, 195)

        draw_text(
            screen,
            "Now with obstacles, sounds, and saved high scores",
            SMALL_FONT,
            LIGHT_GRAY,
            WINDOW_WIDTH // 2,
            260
        )

        create_button(screen, "PRESS ENTER TO START",
                      WINDOW_WIDTH // 2 - 180, 330, 360, 65)

        draw_text(screen, "Controls", MEDIUM_FONT,
                  WHITE, WINDOW_WIDTH // 2, 450)
        draw_text(screen, "Arrow Keys / WASD  - Move",
                  SMALL_FONT, GRAY, WINDOW_WIDTH // 2, 490)
        draw_text(screen, "SPACE - Pause     ESC - Quit",
                  SMALL_FONT, GRAY, WINDOW_WIDTH // 2, 520)
        draw_text(screen, f"Saved High Score: {self.high_score}",
                  SMALL_FONT, YELLOW, WINDOW_WIDTH // 2, 560)

        draw_text(screen, "Built with Python + Pygame",
                  TINY_FONT, PURPLE, WINDOW_WIDTH // 2, 610)

    def draw_paused_overlay(self):
        """Draw pause overlay."""
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 230,
                            WINDOW_HEIGHT // 2 - 105, 460, 210)
        draw_rounded_rect(screen, PANEL_COLOR, panel, 22, PANEL_BORDER, 3)

        draw_text(screen, "PAUSED", LARGE_FONT, YELLOW,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 35)
        draw_text(screen, "Press SPACE to continue", SMALL_FONT,
                  WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25)

    def draw_game_over(self):
        """Draw game over screen."""
        draw_gradient_background(screen)

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 280,
                            WINDOW_HEIGHT // 2 - 190, 560, 380)
        draw_rounded_rect(screen, PANEL_COLOR, panel, 24, RED, 3)

        draw_text(screen, "GAME OVER", TITLE_FONT, RED,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 115)

        draw_text(screen, f"Final Score: {self.score}", MEDIUM_FONT,
                  WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40)
        draw_text(screen, f"High Score: {self.high_score}", MEDIUM_FONT,
                  YELLOW, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 5)
        draw_text(screen, f"Level Reached: {self.level}", MEDIUM_FONT,
                  CYAN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)
        draw_text(screen, f"Obstacles Survived: {len(self.obstacle_manager.obstacles)}",
                  MEDIUM_FONT, ORANGE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 95)

        draw_text(screen, "Press ENTER to restart", SMALL_FONT,
                  LIGHT_GRAY, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 145)
        draw_text(screen, "Press ESC to quit", SMALL_FONT, GRAY,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 175)

    def draw_game(self):
        """Draw active gameplay."""
        draw_gradient_background(screen)
        draw_grid(screen)

        self.draw_top_bar()
        self.obstacle_manager.draw(screen)
        self.food.draw(screen)
        self.snake.draw(screen)

    def draw(self):
        """Draw current screen based on state."""
        if self.state == "menu":
            self.draw_menu()

        elif self.state == "playing":
            self.draw_game()

        elif self.state == "paused":
            self.draw_game()
            self.draw_paused_overlay()

        elif self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

        pygame.quit()


# ============================================================
# Start Game
# ============================================================

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
