import pygame
import random
import sys
import json

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Sound setup
try:
    pop_sound = pygame.mixer.Sound('pop.mp3')
    shoot_sound = pygame.mixer.Sound('shoot.wav')
except:
    pop_sound = None
    shoot_sound = None
    print("Warning: Could not load sound file")

# High Score file
HIGH_SCORE_FILE = 'high_scores.json'


class HighScoreManager:
    @staticmethod
    def load_high_scores():
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def save_high_score(score, level):
        scores = HighScoreManager.load_high_scores()
        scores.append({'score': score, 'level': level})
        scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:10]
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(scores, f)


class GameSettings:
    def __init__(self):
        self.fish_speed = 7
        self.level = 1
        self.score = 0
        self.lives = 3
        self.bubbles_popped = 0
        self.level_up_alert_timer = 0


class Bubble:
    def __init__(self, level, special=False):
        self.special = special
        if self.special:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (15, 15), 15)
        else:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, WHITE, (15, 15), 15)
        self.rect = self.image.get_rect(center=(WIDTH, random.randint(0, HEIGHT)))
        self.speed = -(1.5 + (level - 1) * 0.5)

    def move(self):
        self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.speed = 10

    def move(self):
        self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)


def draw_fish(screen, fish_rect):
    pygame.draw.ellipse(screen, ORANGE, fish_rect)  # Body
    tail_points = [
        (fish_rect.left, fish_rect.centery),
        (fish_rect.left - 20, fish_rect.centery - 15),
        (fish_rect.left - 20, fish_rect.centery + 15)
    ]
    pygame.draw.polygon(screen, ORANGE, tail_points)  # Tail
    eye_pos = (fish_rect.right - 15, fish_rect.centery - 5)
    pygame.draw.circle(screen, WHITE, eye_pos, 5)  # Eye
    pygame.draw.circle(screen, (0, 0, 0), eye_pos, 2)  # Pupil


def draw_game_over_screen(screen, score, level):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont(None, 64)
    small_font = pygame.font.SysFont(None, 36)

    game_over_text = font.render("GAME OVER", True, WHITE)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))

    score_text = small_font.render(f"Total Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    level_text = small_font.render(f"Level Reached: {level}", True, WHITE)
    level_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

    restart_text = small_font.render("Press R to Restart", True, WHITE)
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(level_text, level_rect)
    screen.blit(restart_text, restart_rect)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fish Bubble Shooter")
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    game_settings = GameSettings()
    game_over = False

    fish_rect = pygame.Rect(WIDTH // 10, HEIGHT // 2 - 15, 60, 30)
    bubbles = []
    bullets = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_settings = GameSettings()
                    fish_rect = pygame.Rect(WIDTH // 10, HEIGHT // 2 - 15, 60, 30)
                    bubbles.clear()
                    bullets.clear()
                    game_over = False

            if not game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bullets.append(Bullet(fish_rect.right, fish_rect.centery))
                if shoot_sound:
                    shoot_sound.play()

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and fish_rect.top > 0:
                fish_rect.y -= game_settings.fish_speed
            if keys[pygame.K_DOWN] and fish_rect.bottom < HEIGHT:
                fish_rect.y += game_settings.fish_speed

            if random.randint(0, 25) == 0:
                bubbles.append(Bubble(game_settings.level))
            if random.randint(0, 200) == 0:  # Special bubble appears very rarely
                bubbles.append(Bubble(game_settings.level, special=True))

            for bubble in bubbles[:]:
                bubble.move()
                if bubble.rect.right < 0:  # Bubble crosses the screen
                    game_settings.lives -= 1
                    bubbles.remove(bubble)
                    if game_settings.lives <= 0:
                        game_over = True
                        HighScoreManager.save_high_score(game_settings.score, game_settings.level)

            for bullet in bullets[:]:
                bullet.move()
                for bubble in bubbles[:]:
                    if bullet.rect.colliderect(bubble.rect):
                        bubbles.remove(bubble)
                        bullets.remove(bullet)
                        game_settings.score += 10  # Standard scoring for all bubbles
                        game_settings.bubbles_popped += 1
                        if game_settings.bubbles_popped >= game_settings.level * 10:
                            game_settings.level += 1
                            game_settings.level_up_alert_timer = 90
                        break

            if game_settings.level_up_alert_timer > 0:
                game_settings.level_up_alert_timer -= 1

        screen.fill((0, 0, 150))

        draw_fish(screen, fish_rect)

        for bubble in bubbles:
            bubble.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        if not game_over:
            score_text = font.render(f"Score: {game_settings.score}", True, WHITE)
            level_text = font.render(f"Level: {game_settings.level}", True, WHITE)
            lives_text = font.render(f"Lives: {game_settings.lives}", True, WHITE)

            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (10, 50))
            screen.blit(lives_text, (10, 90))

            if game_settings.level_up_alert_timer > 0:
                alert_text = font.render(f"Level {game_settings.level}!", True, YELLOW)
                screen.blit(alert_text, (WIDTH // 2 - alert_text.get_width() // 2, HEIGHT // 2))
        else:
            draw_game_over_screen(screen, game_settings.score, game_settings.level)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
