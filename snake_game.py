"""
Advanced Snake Game - Premium UI Version 🐍

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
"""

import random
import time
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
START_MOVE_DELAY = 140  # Lower = faster snake

# Colors
BLACK = (10, 10, 18)
DARK_BLUE = (12, 18, 35)
NAVY = (15, 25, 50)
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

PANEL_COLOR = (20, 28, 48)
PANEL_BORDER = (80, 110, 180)
GRID_COLOR = (35, 45, 70)


# ============================================================
# Pygame Setup
# ============================================================

pygame.init()
pygame.display.set_caption("Advanced Snake Game 🐍")

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont("arial", 58, bold=True)
LARGE_FONT = pygame.font.SysFont("arial", 38, bold=True)
MEDIUM_FONT = pygame.font.SysFont("arial", 26, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20)
TINY_FONT = pygame.font.SysFont("arial", 16)


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
    """Convert grid cell position to pixel position."""
    x, y = position
    return x * CELL_SIZE, y * CELL_SIZE


def create_button(surface, text, x, y, width, height, active=True):
    """Draw a clean button-like UI element."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, width, height)

    is_hovered = rect.collidepoint(mouse_x, mouse_y)

    if active and is_hovered:
        button_color = (45, 65, 110)
        border = CYAN
    else:
        button_color = PANEL_COLOR
        border = PANEL_BORDER

    draw_rounded_rect(surface, button_color, rect, 14, border, 2)
    draw_text(surface, text, MEDIUM_FONT, WHITE,
              x + width // 2, y + height // 2)

    return rect


# ============================================================
# Food Class
# ============================================================

class Food:
    """Handles food spawning, animation, and drawing."""

    def __init__(self, snake_body):
        self.position = self.spawn(snake_body)
        self.animation_timer = 0

    def spawn(self, snake_body):
        """Spawn food in a random empty grid cell."""
        while True:
            position = (
                random.randint(1, GRID_WIDTH - 2),
                random.randint(2, GRID_HEIGHT - 2)
            )

            if position not in snake_body:
                return position

    def respawn(self, snake_body):
        """Move food to a new valid location."""
        self.position = self.spawn(snake_body)

    def draw(self, surface):
        """Draw animated food."""
        self.animation_timer += 0.12

        x, y = cell_to_pixel(self.position)

        pulse = abs(pygame.math.Vector2(1, 0).rotate(
            self.animation_timer * 30).x)
        size_offset = int(pulse * 5)

        food_rect = pygame.Rect(
            x + 4 - size_offset // 2,
            y + 4 - size_offset // 2,
            CELL_SIZE - 8 + size_offset,
            CELL_SIZE - 8 + size_offset
        )

        glow_rect = pygame.Rect(
            x + 1,
            y + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )

        pygame.draw.rect(surface, DARK_RED, glow_rect, border_radius=8)
        pygame.draw.rect(surface, RED, food_rect, border_radius=8)

        # Small shine effect
        pygame.draw.circle(surface, WHITE, (x + 10, y + 9), 3)


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
        """Tell snake to grow on next move."""
        self.should_grow = True

    def hits_wall(self):
        """Check if snake hits the window boundary."""
        head_x, head_y = self.body[0]

        return (
            head_x < 0
            or head_x >= GRID_WIDTH
            or head_y < 1
            or head_y >= GRID_HEIGHT
        )

    def hits_self(self):
        """Check if snake head hits its own body."""
        return self.body[0] in self.body[1:]

    def draw(self, surface):
        """Draw snake with better graphics and eyes."""
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
        """Draw eyes on the snake head based on direction."""
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
        self.high_score = 0
        self.reset()

    def reset(self):
        """Reset game state."""
        self.snake = Snake()
        self.food = Food(self.snake.body)

        self.score = 0
        self.level = 1
        self.move_delay = START_MOVE_DELAY
        self.last_move_time = pygame.time.get_ticks()

        self.state = "menu"
        self.game_over_time = 0

    def start_game(self):
        """Start a fresh game."""
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.level = 1
        self.move_delay = START_MOVE_DELAY
        self.last_move_time = pygame.time.get_ticks()
        self.state = "playing"

    def handle_events(self):
        """Handle keyboard and quit events."""
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

                elif self.state == "paused":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"

                elif self.state == "game_over":
                    if event.key == pygame.K_RETURN:
                        self.start_game()

        return True

    def update(self):
        """Update game logic."""
        if self.state != "playing":
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.last_move_time >= self.move_delay:
            self.snake.move()
            self.last_move_time = current_time

            if self.snake.hits_wall() or self.snake.hits_self():
                self.state = "game_over"
                self.game_over_time = time.time()

                if self.score > self.high_score:
                    self.high_score = self.score

                return

            if self.snake.body[0] == self.food.position:
                self.score += 10
                self.snake.grow()
                self.food.respawn(self.snake.body)

                # Increase level every 50 points
                self.level = self.score // 50 + 1

                # Make snake faster but not impossible
                self.move_delay = max(
                    55, START_MOVE_DELAY - (self.level - 1) * 10)

    def draw_top_bar(self):
        """Draw score UI bar."""
        top_bar = pygame.Rect(0, 0, WINDOW_WIDTH, CELL_SIZE)

        pygame.draw.rect(screen, PANEL_COLOR, top_bar)
        pygame.draw.line(screen, PANEL_BORDER, (0, CELL_SIZE),
                         (WINDOW_WIDTH, CELL_SIZE), 2)

        draw_text(screen, f"Score: {self.score}",
                  SMALL_FONT, WHITE, 20, 4, center=False)
        draw_text(screen, f"High Score: {self.high_score}",
                  SMALL_FONT, YELLOW, 170, 4, center=False)
        draw_text(screen, f"Level: {self.level}",
                  SMALL_FONT, CYAN, 390, 4, center=False)
        draw_text(screen, "SPACE: Pause   ESC: Quit",
                  SMALL_FONT, LIGHT_GRAY, 610, 4, center=False)

    def draw_menu(self):
        """Draw main menu screen."""
        draw_gradient_background(screen)

        draw_text(screen, "ADVANCED", TITLE_FONT, CYAN, WINDOW_WIDTH // 2, 150)
        draw_text(screen, "SNAKE GAME", TITLE_FONT,
                  GREEN, WINDOW_WIDTH // 2, 215)

        draw_text(
            screen,
            "A cleaner, smoother version of the classic snake game",
            SMALL_FONT,
            LIGHT_GRAY,
            WINDOW_WIDTH // 2,
            280
        )

        create_button(screen, "PRESS ENTER TO START",
                      WINDOW_WIDTH // 2 - 170, 340, 340, 60)

        draw_text(screen, "Controls", MEDIUM_FONT,
                  WHITE, WINDOW_WIDTH // 2, 440)
        draw_text(screen, "Arrow Keys / WASD  - Move",
                  SMALL_FONT, GRAY, WINDOW_WIDTH // 2, 480)
        draw_text(screen, "SPACE - Pause     ESC - Quit",
                  SMALL_FONT, GRAY, WINDOW_WIDTH // 2, 510)

        draw_text(screen, "Built with Python + Pygame",
                  TINY_FONT, PURPLE, WINDOW_WIDTH // 2, 600)

    def draw_paused_overlay(self):
        """Draw pause overlay."""
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 220,
                            WINDOW_HEIGHT // 2 - 100, 440, 200)
        draw_rounded_rect(screen, PANEL_COLOR, panel, 20, PANEL_BORDER, 3)

        draw_text(screen, "PAUSED", LARGE_FONT, YELLOW,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 35)
        draw_text(screen, "Press SPACE to continue", SMALL_FONT,
                  WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)

    def draw_game_over(self):
        """Draw game over screen."""
        draw_gradient_background(screen)

        panel = pygame.Rect(WINDOW_WIDTH // 2 - 260,
                            WINDOW_HEIGHT // 2 - 180, 520, 360)
        draw_rounded_rect(screen, PANEL_COLOR, panel, 24, RED, 3)

        draw_text(screen, "GAME OVER", TITLE_FONT, RED,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100)

        draw_text(screen, f"Final Score: {self.score}", MEDIUM_FONT,
                  WHITE, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 25)
        draw_text(screen, f"High Score: {self.high_score}", MEDIUM_FONT,
                  YELLOW, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        draw_text(screen, f"Level Reached: {self.level}", MEDIUM_FONT,
                  CYAN, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 65)

        draw_text(screen, "Press ENTER to restart", SMALL_FONT,
                  LIGHT_GRAY, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 125)
        draw_text(screen, "Press ESC to quit", SMALL_FONT, GRAY,
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 155)

    def draw_game(self):
        """Draw active game screen."""
        draw_gradient_background(screen)
        draw_grid(screen)

        self.draw_top_bar()
        self.food.draw(screen)
        self.snake.draw(screen)

    def draw(self):
        """Render current state."""
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
