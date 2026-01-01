import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Music
pygame.mixer.music.load('lovely.mp3')
pygame.mixer.music.play(-1)


# Screen settings
WIDTH, HEIGHT = 1366, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - by Sanzu")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("comicsansms", 30)
BIG_FONT = pygame.font.SysFont("comicsansms", 60)

# Colors
BG_COLOR = (10, 10, 40)
WHITE = (255, 255, 255)
CYAN = (0, 255, 150)
ORANGE_RED = (255, 100, 0)
YELLOW = (255, 255, 100)

# Global high score (persists across restarts)
high_score = 0

class Player:
    def __init__(self):
        self.x = WIDTH // 2 - 20
        self.y = HEIGHT - 60
        self.width = 40
        self.height = 45
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.shoot_cooldown = 0
        self.speed = 7

    def update(self, keys):
        # Movement
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.rect.topleft = (self.x, self.y)
        
        # Cooldown decrement
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def draw(self, screen):
        # Ship polygon (pointing up)
        points = [
            (self.x + 20, self.y),          # Top point
            (self.x + 5, self.y + 40),      # Bottom left
            (self.x + 35, self.y + 40)      # Bottom right
        ]
        pygame.draw.polygon(screen, CYAN, points)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 12
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 11

    def update(self):
        self.y -= self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)

class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 40)
        self.y = -50
        self.width = 40
        self.height = 45
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, speed):
        self.y += speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        # Enemy polygon (pointing down)
        points = [
            (self.x + 5, self.y),           # Top left
            (self.x + 35, self.y),          # Top right
            (self.x + 20, self.y + 40)      # Bottom point
        ]
        pygame.draw.polygon(screen, ORANGE_RED, points)

def main():
    global high_score
    
    # Reset for new game
    score = 0
    enemy_speed = 2.0
    spawn_timer = 0
    spawn_delay = 120
    
    player = Player()
    bullets = []
    enemies = []
    stars = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(150)]
    
    game_over = False

    while True:
        clock.tick(60)
        screen.fill(BG_COLOR)

        # Update and draw stars (always, for parallax effect)
        for i in range(len(stars)):
            sx, sy = stars[i]
            pygame.draw.circle(screen, WHITE, (sx, sy), 1)
            stars[i] = (sx, sy + 1)
            if stars[i][1] > HEIGHT:
                stars[i] = (random.randint(0, WIDTH - 1), random.randint(-20, 0))

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # RESTART GAME
                        score = 0
                        enemy_speed = 2.0
                        spawn_delay = 120
                        player = Player()
                        bullets = []
                        enemies = []
                        stars = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(150)]
                        game_over = False
                    # else: shoot handled below with get_pressed() for auto-fire

        if not game_over:
            # Auto-fire on hold SPACE
            if keys[pygame.K_SPACE] and player.shoot_cooldown == 0:
                bullets.append(Bullet(player.x + player.width // 2 - 2, player.y))
                player.shoot_cooldown = 8

            # Spawn enemies
            spawn_timer += 1
            if spawn_timer > spawn_delay:
                enemies.append(Enemy())
                spawn_timer = 0
                spawn_delay = max(25, spawn_delay - 0.8)  # Increase spawn rate

            # Update player
            player.update(keys)

            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.y < -20:
                    bullets.remove(bullet)

            # Update enemies
            for enemy in enemies[:]:
                enemy.update(enemy_speed)
                if enemy.y > HEIGHT + 20:
                    enemies.remove(enemy)
                # Player collision
                if player.rect.colliderect(enemy.rect):
                    game_over = True

            # Bullet-enemy collisions
            for bullet in bullets[:]:
                hit = False
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 10
                        hit = True
                        break
                if hit:
                    break

            # Increase difficulty
            enemy_speed = 2.0 + (score / 800.0)

            # Update high score
            if score > high_score:
                high_score = score

        # Draw everything
        player.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        # UI
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        hi_text = FONT.render(f"High: {high_score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        screen.blit(hi_text, (20, 60))

        # Controls hint
        hint_text = pygame.font.SysFont("comicsansms", 20).render("A/D or Arrows: Move | Hold SPACE: Shoot", True, (150, 150, 255))
        screen.blit(hint_text, (20, HEIGHT - 30))

        if game_over:
            over_text = BIG_FONT.render("GAME OVER", True, (255, 50, 50))
            restart_text = FONT.render("Press SPACE to restart", True, WHITE)
            screen.blit(over_text, (WIDTH // 2 - 180, HEIGHT // 2 - 60))
            screen.blit(restart_text, (WIDTH // 2 - 140, HEIGHT // 2 + 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()