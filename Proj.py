import pygame
import random
import math
 
# Инициализация Pygame
pygame.init()
 
# Размеры окна
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space Warrior")
 
# Цвета
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
 
# Загрузка изображений
player_img = pygame.image.load("player.png")  
enemy_img = pygame.image.load("enemy.webp")
bullet_img = pygame.image.load("bullet.png")  
 
# Масштабирование изображений
player_img = pygame.transform.scale(player_img, (50, 50))
enemy_img = pygame.transform.scale(enemy_img, (40, 40))
bullet_img = pygame.transform.scale(bullet_img, (10, 20))
 
 
# Класс для игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.width = 50
        self.height = 50
        self.img = player_img
        self.rect = self.img.get_rect(center=(self.x, self.y))
 
    def move(self, dx):
       self.x += dx*self.speed
       if self.x < self.width //2:
           self.x = self.width//2
       if self.x > width - self.width//2:
           self.x = width - self.width // 2
       self.rect = self.img.get_rect(center=(self.x, self.y))
 
    def draw(self, screen):
        screen.blit(self.img,self.rect)
 
# Класс для врага
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.width = 40
        self.height = 40
        self.img = enemy_img
        self.rect = self.img.get_rect(center=(self.x, self.y))
 
    def move(self):
        self.y += self.speed
        self.rect = self.img.get_rect(center=(self.x, self.y))
    def draw(self, screen):
        screen.blit(self.img, self.rect)
 
 
# Класс для пули
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.width = 10
        self.height = 20
        self.img = bullet_img
        self.rect = self.img.get_rect(center=(self.x, self.y))
 
    def move(self):
        self.y -= self.speed
        self.rect = self.img.get_rect(center=(self.x, self.y))
    def draw(self, screen):
        screen.blit(self.img, self.rect)
 
# Создание объектов
player = Player(width // 2, height - 70)
enemies = []
bullets = []
last_enemy_spawn = pygame.time.get_ticks()
spawn_interval = 1500
 
# Основной цикл игры
running = True
clock = pygame.time.Clock()
score = 0
font = pygame.font.Font(None, 36)
 
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
              bullets.append(Bullet(player.x, player.y-player.height//2))
 
    # Управление игроком
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx = -1
    if keys[pygame.K_RIGHT]:
        dx = 1
    player.move(dx)
 
    # Спаун врагов
    now = pygame.time.get_ticks()
    if now - last_enemy_spawn >= spawn_interval:
       x = random.randint(50, width - 50)
       y = 0
       enemies.append(Enemy(x,y))
       last_enemy_spawn = now
 
    # Движение пуль и врагов
    for bullet in bullets:
        bullet.move()
        if bullet.y < 0:
             bullets.remove(bullet)
    for enemy in enemies:
        enemy.move()
        if enemy.y > height:
             enemies.remove(enemy)
 
    # Проверка столкновений
    for bullet in bullets:
        for enemy in enemies:
            if bullet.rect.colliderect(enemy.rect):
              bullets.remove(bullet)
              enemies.remove(enemy)
              score += 1
 
    # Отрисовка
    screen.fill(black)
    player.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)
 
    # Отрисовка счета
    text_surface = font.render(f"Score: {score}", True, white)
    screen.blit(text_surface, (10, 10))
 
    pygame.display.flip()
 
pygame.quit()
