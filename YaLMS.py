import pygame
import random
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
DIFFICULTY_LEVELS = {
    'easy': {'enemy_health': 0.7, 'enemy_speed': 1.0, 'spawn_rate': 1.0, 'damage_multiplier': 0.8},
    'normal': {'enemy_health': 1.0, 'enemy_speed': 1.0, 'spawn_rate': 1.0, 'damage_multiplier': 1.0},
    'hard': {'enemy_health': 1.3, 'enemy_speed': 1.2, 'spawn_rate': 0.8, 'damage_multiplier': 1.2}
}
WIDTH = 1280
HEIGHT = 720
FPS = 60
EXPLOSION_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0)]  # Цвета для взрывов
PARTICLE_COUNT = 15  # Количество частиц при взрыве
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ENEMY_TYPES = ['normal', 'fast', 'strong', 'shooter']
BULLET_SPEED = 7
BONUS_DURATION = 10000  # 10 секунд

# Переменные для анимации
fade_alpha = 0
FADE_SPEED = 5
fade_state = None  # 'fade_out', 'fade_in'

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Warrior")
clock = pygame.time.Clock()

# Загрузка изображений
player_img = pygame.image.load("player.png").convert_alpha()
enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy2_img = pygame.image.load("enemy2.png").convert_alpha()
enemy3_img = pygame.image.load("enemy3.png").convert_alpha()
enemy4_img = pygame.image.load("shooter.png").convert_alpha()
enemy_bullet_img = pygame.image.load("enemy_bullet.png").convert_alpha()
bullet_img = pygame.image.load("bullet.png").convert_alpha()
BONUS_IMAGE = pygame.image.load("bonus.png").convert_alpha()
BACKGROUNDS = [
    pygame.image.load("background.png").convert(),
    pygame.image.load("background2.png").convert(),
    pygame.image.load("background3.png").convert(),
]

current_bg_index = 0
current_bg = BACKGROUNDS[current_bg_index]

# Загрузка звуков
UPGRADE_SOUND = pygame.mixer.Sound("upgrade.wav")
shoot_sound = pygame.mixer.Sound("laser.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
bonus_sound = pygame.mixer.Sound("archivo.wav")
pygame.mixer.music.load("background.ogg")

class Player(pygame.sprite.Sprite):
    def __init__(self, ship_type):
        super().__init__()
        self.ship_level = 1
        self.double_bullet = False
        self.bonus_timer = 0
        self.ship_type = ship_type

        # Параметры в зависимости от типа корабля
        if ship_type == "sniper":
            self.base_max_health = 50
            self.base_shoot_delay = 550
            self.base_bullet_damage = 400
        elif ship_type == "shotguner":
            self.base_max_health = 150
            self.base_shoot_delay = 500
            self.base_bullet_damage = 30
        else:  # Стандартный
            self.base_max_health = 100
            self.base_shoot_delay = 250
            self.base_bullet_damage = 90

        self.max_health = self.base_max_health
        self.health = self.max_health
        self.shoot_delay = self.base_shoot_delay
        self.bullet_damage = self.base_bullet_damage

        self.image = pygame.transform.scale(player_img, (50, 38))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT-50)
        self.speed = 8
        self.last_shot = pygame.time.get_ticks()
        self.shooting = False

    def level_up(self):
        self.ship_level += 1
        self.max_health = self.base_max_health + 25 * (self.ship_level - 1)
        self.health = min(self.health + 25, self.max_health)
        self.shoot_delay = max(self.base_shoot_delay - 15 * (self.ship_level - 1), 50)
        self.base_bullet_damage += 20
        self.bullet_damage = self.base_bullet_damage

    def activate_bonus(self):
        self.health = min(self.health + 20, self.max_health)
        if self.ship_type == "shotguner":
            self.bullet_damage = self.base_bullet_damage * 2
        else:
            self.double_bullet = True
        self.bonus_timer = pygame.time.get_ticks() + BONUS_DURATION

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        self.rect.clamp_ip(screen.get_rect())

        if self.shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot()

        now = pygame.time.get_ticks()
        if now > self.bonus_timer:
            if self.ship_type == "shotguner":
                self.bullet_damage = self.base_bullet_damage
            else:
                self.double_bullet = False
                
    def apply_upgrade(self, upgrade_type, value):
        if upgrade_type == "shoot_delay":
            self.base_shoot_delay = int(self.base_shoot_delay * value)
            self.shoot_delay = self.base_shoot_delay
        elif upgrade_type == "health":
            self.base_max_health += value
            self.max_health = self.base_max_health
            self.health = min(self.health + value, self.max_health)
        elif upgrade_type == "damage":
            self.base_bullet_damage = int(self.base_bullet_damage * value)
            self.bullet_damage = self.base_bullet_damage

    def shoot(self):
        if self.ship_type == "shotguner":
            angles = [-5, -2.5, 0, 2.5, 5]
            if self.double_bullet:
                angles = [a*1.5 for a in angles]
            for angle in angles:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_damage, max_distance=250)
                bullet.speed_y = -10
                bullet.speed_x = angle
                all_sprites.add(bullet)
                bullets.add(bullet)
        else:
            bullet = Bullet(self.rect.centerx, self.rect.top, self.bullet_damage)
            all_sprites.add(bullet)
            bullets.add(bullet)
            if self.double_bullet:
                bullet2 = Bullet(self.rect.centerx + 10, self.rect.top, self.bullet_damage)
                all_sprites.add(bullet2)
                bullets.add(bullet2)
        shoot_sound.play()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, difficulty):
        super().__init__()
        self.difficulty = difficulty
        self.enemy_type = enemy_type
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 2000

        # Инициализация базовых значений в зависимости от типа
        if enemy_type == 'normal':
            self.image = pygame.transform.scale(enemy_img, (40, 30))
            self.speed_y = 2
            self.speed_x = random.randrange(-2, 2)
            self.max_health = 180
            self.score_value = 10

        elif enemy_type == 'fast':
            self.image = pygame.transform.scale(enemy2_img, (30, 20))
            self.speed_y = 5
            self.speed_x = random.randrange(-4, 4)
            self.max_health = 90
            self.score_value = 15

        elif enemy_type == 'strong':
            self.image = pygame.transform.scale(enemy3_img, (60, 45))
            self.speed_y = 1
            self.speed_x = random.randrange(-1, 1)
            self.max_health = 360
            self.score_value = 30

        elif enemy_type == 'shooter':
            self.image = pygame.transform.scale(enemy4_img, (35, 25))
            self.speed_y = 2
            self.speed_x = 0
            self.max_health = 180
            self.score_value = 25
            self.shoot_delay = 1500

        # Применяем модификаторы сложности ПОСЛЕ инициализации базовых значений
        diff = DIFFICULTY_LEVELS[difficulty]
        self.max_health = int(self.max_health * diff['enemy_health'])
        self.speed_y *= diff['enemy_speed']
        self.speed_x *= diff['enemy_speed']
        self.score_value = int(self.score_value * (2 - diff['enemy_health']))
        
        self.health = self.max_health
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40)

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        if self.enemy_type == 'shooter':
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot()
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.kill()

    def shoot(self):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx = dx / distance
            dy = dy / distance

        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, dx*BULLET_SPEED, dy*BULLET_SPEED)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)
        shoot_sound.play()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.image = pygame.transform.scale(enemy_bullet_img, (8, 8))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = dx
        self.speed_y = dy

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=1, max_distance=None):
        super().__init__()
        self.image = pygame.transform.scale(bullet_img, (5, 10))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10
        self.speed_x = 0
        self.damage = damage
        self.max_distance = max_distance
        self.distance_traveled = 0

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        self.distance_traveled += abs(self.speed_y)
        if self.rect.bottom < 0 or (self.max_distance and self.distance_traveled >= self.max_distance):
            self.kill()

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 2000
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.timer:
            self.explode()
            self.kill()

    def explode(self):
        explosion_rect = pygame.Rect(self.rect.x - 75, self.rect.y - 75, 150, 150)
        if explosion_rect.colliderect(player.rect):
            player.health -= 50
            if player.health <= 0:
                player.health = 0
                global game_over
                game_over = True

        explosion = Explosion(self.rect.centerx, self.rect.centery)
        all_sprites.add(explosion)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((150, 150), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (75, 75), 75)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 200
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > self.timer:
            self.kill()

class Bonus(pygame.sprite.Sprite):
    def __init__(self, difficulty):
        super().__init__()
        self.difficulty = difficulty
        self.speed = 3 * DIFFICULTY_LEVELS[difficulty]['spawn_rate']
        self.image = pygame.transform.scale(BONUS_IMAGE, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WIDTH-50)
        self.rect.y = -50
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)  # Время жизни в кадрах
        self.age = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()

class EnemyExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.frame = 0
        self.images = []
        self.enemy_type = enemy_type
        
        # Создаем анимацию взрыва программно
        for i in range(10, 50, 5):
            surf = pygame.Surface((i*2, i*2), pygame.SRCALPHA)
            color = random.choice(EXPLOSION_COLORS)
            pygame.draw.circle(surf, color, (i, i), i, width=4)
            self.images.append(pygame.transform.scale(surf, (i*2, i*2)))
        
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))  # Центрируем взрыв на точке смерти врага
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame < len(self.images):
                self.image = self.images[self.frame]
            else:
                self.kill()
                
class UpgradeSystem:
    def __init__(self):
        self.available_upgrades = [
            {"name": "Rapid Fire", "description": "+10% fire rate", 
             "type": "shoot_delay", "value": 0.90, "color": (0,255,255)},
            {"name": "Armor Plating", "description": "+35 max health", 
             "type": "health", "value": 35, "color": (0,255,0)},
            {"name": "Damage Boost", "description": "+10% damage", 
             "type": "damage", "value": 1.1, "color": (255,0,0)},
            {"name": "Speed Boost", "description": "+15% speed", 
             "type": "speed", "value": 1.10, "color": (255,255,0)}
        ]

    def get_random_upgrades(self, count=3):
        return random.sample(self.available_upgrades, count)
    
upgrade_system = UpgradeSystem()

def draw_xp_bar(surf, x, y, current_xp, xp_needed, current_level):
    BAR_WIDTH = 300
    BAR_HEIGHT = 20
    fill = (current_xp / xp_needed) * BAR_WIDTH
    outline_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, (255, 255, 0), fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)
    font = pygame.font.Font(None, 24)
    text = font.render(f"Ship Level {current_level} → {current_level+1}", True, WHITE)
    surf.blit(text, (x + BAR_WIDTH + 10, y-3))

def show_game_over_screen(score, level):
    screen.blit(BACKGROUNDS[0], (0, 0))
    
    # Заголовок
    draw_text(screen, "GAME OVER", 72, WIDTH/2, HEIGHT/4)
    
    # Статистика
    draw_text(screen, f"Final Score: {score}", 36, WIDTH/2, HEIGHT/2 - 60)
    draw_text(screen, f"Reached Level: {level}", 36, WIDTH/2, HEIGHT/2 - 20)
    
    # Инструкции
    draw_text(screen, "Press SPACE to play again", 28, WIDTH/2, HEIGHT - 200)
    draw_text(screen, "Press ESC to quit", 28, WIDTH/2, HEIGHT - 150)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    return True

def show_upgrade_screen(player):
    player.shooting = False
    screen.blit(current_bg, (0, 0))
    all_sprites.draw(screen)
    
    # Создаем полупрозрачный фон
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 200), overlay.get_rect())
    screen.blit(overlay, (0, 0))
    
    draw_text(screen, "LEVEL UP!", 72, WIDTH/2, HEIGHT/4)
    draw_text(screen, "Choose an upgrade:", 36, WIDTH/2, HEIGHT/3)
    
    upgrades = upgrade_system.get_random_upgrades(3)
    
    # Рисуем карточки улучшений
    card_width = 400
    card_height = 250
    padding = 50
    
    for i, upgrade in enumerate(upgrades):
        x = WIDTH/2 - (card_width + padding) + i*(card_width + padding)
        y = HEIGHT/2 - card_height/2
        
        # Рамка карточки
        pygame.draw.rect(screen, upgrade['color'], (x, y, card_width, card_height), 3)
        pygame.draw.rect(screen, (30, 30, 30), (x+3, y+3, card_width-6, card_height-6))
        
        # Текст
        draw_text(screen, upgrade['name'], 32, x + card_width/2, y + 30)
        draw_text(screen, upgrade['description'], 24, x + card_width/2, y + 80)
        draw_text(screen, f"Press {i+1}", 28, x + card_width/2, y + card_height - 50)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.apply_upgrade(upgrades[0]['type'], upgrades[0]['value'])
                    waiting = False
                elif event.key == pygame.K_2:
                    player.apply_upgrade(upgrades[1]['type'], upgrades[1]['value'])
                    waiting = False
                elif event.key == pygame.K_3:
                    player.apply_upgrade(upgrades[2]['type'], upgrades[2]['value'])
                    waiting = False
                    
def draw_health_bar(surf, x, y, current, max_hp):
    if current < 0:
        current = 0
    BAR_LENGTH = max_hp * 2
    BAR_HEIGHT = 15
    fill = (current / max_hp) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 3)

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def select_difficulty():
    screen.blit(BACKGROUNDS[0], (0, 0))
    draw_text(screen, "Select difficulty:", 48, WIDTH/2, HEIGHT/4)
    
    # Опции сложности
    difficulties = [
        ("1. Easy", "Enemies are weaker and slower", (WIDTH/2 - 200, HEIGHT/2)),
        ("2. Normal", "Standard game balance", (WIDTH/2, HEIGHT/2)),
        ("3. Hard", "Challenge for veterans", (WIDTH/2 + 200, HEIGHT/2))
    ]
    
    for i, (title, desc, pos) in enumerate(difficulties):
        draw_text(screen, title, 32, pos[0], pos[1] - 30)
        draw_text(screen, desc, 22, pos[0], pos[1] + 20)
    
    pygame.display.flip()
    
    waiting = True
    selected = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected = 'easy'
                    waiting = False
                elif event.key == pygame.K_2:
                    selected = 'normal'
                    waiting = False
                elif event.key == pygame.K_3:
                    selected = 'hard'
                    waiting = False
    return selected

def show_ship_selection():
    screen.blit(BACKGROUNDS[0], (0, 0))
    draw_text(screen, "Select your ship:", 48, WIDTH/2, HEIGHT/4)

    # Загрузка изображений кораблей
    sniper_img = pygame.transform.scale(player_img, (100, 76))
    shotguner_img = pygame.transform.scale(player_img, (100, 76))
    standard_img = pygame.transform.scale(player_img, (100, 76))

    # Позиции для изображений кораблей
    sniper_rect = sniper_img.get_rect(center=(WIDTH/2 - 200, HEIGHT/2))
    shotguner_rect = shotguner_img.get_rect(center=(WIDTH/2, HEIGHT/2))
    standard_rect = standard_img.get_rect(center=(WIDTH/2 + 200, HEIGHT/2))

    # Отображение изображений кораблей
    screen.blit(sniper_img, sniper_rect)
    screen.blit(shotguner_img, shotguner_rect)
    screen.blit(standard_img, standard_rect)

    # Текстовые описания кораблей
    draw_text(screen, "Sniper", 22, WIDTH/2 - 200, HEIGHT/2 + 60)
    draw_text(screen, "Shotguner", 22, WIDTH/2, HEIGHT/2 + 60)
    draw_text(screen, "Standard", 22, WIDTH/2 + 200, HEIGHT/2 + 60)

    draw_text(screen, "Press 1, 2 or 3 to choose", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.flip()

    waiting = True
    selected_ship = None
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_ship = 'sniper'
                    waiting = False
                elif event.key == pygame.K_2:
                    selected_ship = 'shotguner'
                    waiting = False
                elif event.key == pygame.K_3:
                    selected_ship = 'standard'
                    waiting = False

        # Подсветка выбранного корабля
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            pygame.draw.rect(screen, GREEN, sniper_rect, 3)
        elif keys[pygame.K_2]:
            pygame.draw.rect(screen, GREEN, shotguner_rect, 3)
        elif keys[pygame.K_3]:
            pygame.draw.rect(screen, GREEN, standard_rect, 3)
        pygame.display.flip()

    return selected_ship

def show_start_screen():
    screen.blit(BACKGROUNDS[0], (0, 0))
    draw_text(screen, "SPACE WARRIOR", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "Arrow keys to move, Space to fire", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "Press any key to begin", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

# Группы спрайтов
bombs = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bonuses = pygame.sprite.Group()

def create_bonus(difficulty):
    bonus = Bonus(difficulty)
    all_sprites.add(bonus)
    bonuses.add(bonus)

def create_enemies(num, difficulty):
    diff = DIFFICULTY_LEVELS[difficulty]['spawn_rate']
    num = int(num * diff)
    for _ in range(num):
        if level < 3:
            types = ['normal', 'fast']
        elif level < 5:
            types = ['normal', 'fast', 'strong']
        else:
            types = ENEMY_TYPES

        enemy_type = random.choice(types)
        enemy = Enemy(enemy_type, difficulty)
        all_sprites.add(enemy)
        enemies.add(enemy)

# Игровой цикл
pygame.mixer.music.play(loops=-1)
game_over = True
running = True
score = 0
level = 1
current_xp = 0
xp_needed = 450
next_bonus_score = 350
color_1 = (0, 0, 0)

while running:
    if game_over:
        pygame.mixer.music.stop()
        screen.fill(color_1)
        difficulty = select_difficulty()
        # Показать экран Game Over
        restart = show_game_over_screen(score, level)
        if not difficulty:
            running = False
            continue
        if not restart:
            running = False
            continue
            
        # Перезапуск игры
        pygame.mixer.music.play(loops=-1)
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        bombs = pygame.sprite.Group()

        ship_type = show_ship_selection()
        if not ship_type:
            running = False
            continue

        player = Player(ship_type)
        all_sprites.add(player)
        score = 0
        level = 1
        current_xp = 0
        create_enemies(8, difficulty)
        game_over = False
        

    clock.tick(FPS)

    # Обработка анимации смены фона
    if fade_state == 'fade_out':
        fade_alpha += FADE_SPEED
        if fade_alpha >= 255:
            fade_alpha = 255
            current_bg_index = (current_bg_index + 1) % len(BACKGROUNDS)
            current_bg = BACKGROUNDS[current_bg_index]
            fade_state = 'fade_in'
    elif fade_state == 'fade_in':
        fade_alpha -= FADE_SPEED
        if fade_alpha <= 0:
            fade_alpha = 0
            fade_state = None

    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullet_list in hits.items():
        for bullet in bullet_list:
            enemy.health -= bullet.damage
        if enemy.health <= 0:
            score += enemy.score_value
            current_xp += enemy.score_value
            explosion_sound.play()
    
            # Создаем эффекты
            explosion = EnemyExplosion(enemy.rect.centerx, enemy.rect.centery, enemy.enemy_type)
            all_sprites.add(explosion)
    
            # Создаем частицы
            for _ in range(PARTICLE_COUNT):
                color = random.choice(EXPLOSION_COLORS)
                particle = Particle(enemy.rect.centerx, enemy.rect.centery, color)
                all_sprites.add(particle)
                
            # Эффект для strong врагов
            if enemy.enemy_type == 'strong':
                for _ in range(PARTICLE_COUNT * 2):
                    color = (255, 0, 0)
                    particle = Particle(enemy.rect.centerx, enemy.rect.centery, color)
                    particle.speed_x *= 1.5
                    particle.speed_y *= 1.5
                    all_sprites.add(particle)
    
            # Создаем бомбу для strong врагов
            if enemy.enemy_type == 'strong':
                bomb = Bomb(enemy.rect.centerx, enemy.rect.centery)
                all_sprites.add(bomb)
                bombs.add(bomb)
    
            enemy.kill()
            if random.random() < 0.1 * (1.5 if difficulty == 'hard' else 1.0):
                create_bonus(difficulty)

    xp_needed_current = 450 * player.ship_level
    if current_xp >= xp_needed_current:
        levels_gained = current_xp // xp_needed_current
        UPGRADE_SOUND.play()  # Звук играет один раз при любом количестве уровней
        for _ in range(levels_gained):
            player.level_up()
            player.shooting = False  # Сбрасываем состояние стрельбы
            show_upgrade_screen(player)
        current_xp %= xp_needed_current


    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shooting = True
            elif event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                player.shooting = False

    # Обновление
    all_sprites.update()

    # Проверка столкновений игрока с бонусами
    hits = pygame.sprite.spritecollide(player, bonuses, True)
    for hit in hits:
        player.activate_bonus()
        bonus_sound.play()

    # Проверка столкновений игрока с врагами и пулями
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        damage = 20 * DIFFICULTY_LEVELS[difficulty]['damage_multiplier']
        player.health -= damage
        if player.health <= 0:
            pygame.mixer.music.stop()
            game_over = True

    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in hits:
        damage = 20 * DIFFICULTY_LEVELS[difficulty]['damage_multiplier']
        player.health -= damage
        if player.health <= 0:
            pygame.mixer.music.stop()
            game_over = True

    # Создание новых врагов при необходимости
    if len(enemies) == 0:
        level += 1
        if level % 5 == 0:
            fade_state = 'fade_out'
        create_enemies(8 + level * 2 + random.randint(0, level * 3), difficulty)

    # Рендеринг
    screen.blit(current_bg, (0, 0))
    all_sprites.draw(screen)
    xp_needed_current = 450 * player.ship_level
    draw_xp_bar(screen, WIDTH//2 - 150, 40, current_xp, xp_needed_current, player.ship_level)
    draw_health_bar(screen, 5, 5, player.health, player.max_health)
    draw_text(screen, f"Score: {score}", 18, WIDTH // 2, 10)
    draw_text(screen, f"Level: {level}", 18, WIDTH - 60, 10)
    if fade_state is not None:
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
    if player.bonus_timer > pygame.time.get_ticks():
        time_left = (player.bonus_timer - pygame.time.get_ticks()) // 1000 + 1
        if player.ship_type == "shotguner":
            draw_text(screen, f"DOUBLE DAMAGE: {time_left}s", 22, WIDTH//2, 70)  # Y=70
        elif player.double_bullet:
            draw_text(screen, f"DOUBLE BULLET: {time_left}s", 22, WIDTH//2, 70)
    pygame.display.flip()

pygame.quit()
