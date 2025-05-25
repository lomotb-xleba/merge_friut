import pygame
import random
import sys
import math

# Инициализация Pygame
pygame.init()

# Константы
BASKET_WIDTH = 600
HEIGHT = 800
FPS = 60
GRAVITY = 0.9
BOUNCE_FACTOR = 0.7
FRICTION = 0.98
BASKET_HEIGHT = 400
BALL_SIZES = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
COLORS = [
    (255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255),
    (0,255,255), (128,0,128), (255,165,0), (75,0,130), (139,69,19)
]

# Настройка экрана
screen = pygame.display.set_mode((BASKET_WIDTH, HEIGHT))
pygame.display.set_caption("Merge Fruit")
clock = pygame.time.Clock()

# Корзина
BASKET_TOP = HEIGHT - BASKET_HEIGHT - 20
BASKET_RECT = pygame.Rect(0, BASKET_TOP, BASKET_WIDTH, BASKET_HEIGHT)
UPPER_LIMIT = BASKET_TOP - 50  # Верхняя граница

# Шрифты
font = pygame.font.SysFont('Arial', 36, bold=True)
small_font = pygame.font.SysFont('Arial', 24)

# Состояние игры
score = 0
game_over = False
countdown_active = False
countdown_start = 0
next_ball_idx = random.randint(0, len(BALL_SIZES)-2)
balls = []

class Ball:
    def __init__(self, x, size_idx):
        self.size_idx = size_idx
        self.radius = BALL_SIZES[size_idx]
        self.color = COLORS[size_idx]
        self.x = x
        self.y = -self.radius
        self.speed_y = 0
        self.speed_x = 0
        self.active = True
        self.on_ground = False
        self.added_to_score = False

    def update(self):
        global score, countdown_active, countdown_start
        
        if not self.active:
            return

        # Физика движения
        if not self.on_ground:
            self.speed_y += GRAVITY
            self.y += self.speed_y
        
        self.x += self.speed_x
        self.speed_x *= FRICTION

        # Коллизии с границами
        if self.x - self.radius < 0:
            self.x = self.radius
            self.speed_x *= -BOUNCE_FACTOR
        elif self.x + self.radius > BASKET_WIDTH:
            self.x = BASKET_WIDTH - self.radius
            self.speed_x *= -BOUNCE_FACTOR

        # Проверка верхней границы
        if self.y + self.radius < UPPER_LIMIT and not countdown_active:
            countdown_active = True
            countdown_start = pygame.time.get_ticks()

        # Коллизия с дном корзины
        if (BASKET_RECT.left <= self.x <= BASKET_RECT.right 
            and self.y + self.radius > BASKET_RECT.bottom):
            self.y = BASKET_RECT.bottom - self.radius
            self.speed_y *= -BOUNCE_FACTOR
            self.speed_x *= FRICTION
            
            if abs(self.speed_y) < 1:
                self.speed_y = 0
                self.on_ground = True
                if not self.added_to_score:
                    score += self.size_idx + 1
                    self.added_to_score = True
        # Улучшенная проверка коллизий с корзиной
        # Проверка левой стенки
        if (self.x - self.radius < BASKET_RECT.left 
            and BASKET_RECT.top <= self.y <= BASKET_RECT.bottom):
            self.x = BASKET_RECT.left + self.radius
            self.speed_x *= -BOUNCE_FACTOR
        
        # Проверка правой стенки
        elif (self.x + self.radius > BASKET_RECT.right 
            and BASKET_RECT.top <= self.y <= BASKET_RECT.bottom):
            self.x = BASKET_RECT.right - self.radius
            self.speed_x *= -BOUNCE_FACTOR
        
        # Проверка нижней стенки
        if (BASKET_RECT.left <= self.x <= BASKET_RECT.right 
            and self.y + self.radius > BASKET_RECT.bottom):
            self.y = BASKET_RECT.bottom - self.radius
            self.speed_y *= -BOUNCE_FACTOR
            self.speed_x *= FRICTION
            
            if abs(self.speed_y) < 1:
                # Усиленная проверка позиции шарика
                in_basket_x = BASKET_RECT.left + self.radius <= self.x <= BASKET_RECT.right - self.radius
                in_basket_y = BASKET_RECT.top + self.radius <= self.y <= BASKET_RECT.bottom - self.radius
                if not (in_basket_x and in_basket_y):
                    return "game_over"
                self.speed_y = 0
                self.on_ground = True
        
        # Улучшенная физика столкновений шариков
        for other in balls:
            if other != self and other.active:
                dx = other.x - self.x
                dy = other.y - self.y
                distance = math.hypot(dx, dy)
                
                if distance < self.radius + other.radius:
                    if self.size_idx == other.size_idx and self.size_idx < len(BALL_SIZES) - 1:
                        # Слияние шариков
                        self.size_idx += 1
                        self.radius = BALL_SIZES[self.size_idx]
                        self.color = COLORS[self.size_idx]
                        other.active = False
                        
                        # Добавляем эффект отталкивания при слиянии
                        angle = math.atan2(dy, dx)
                        force = 5
                        self.speed_x = -math.cos(angle) * force
                        self.speed_y = -math.sin(angle) * force
                        self.on_ground = False
                    else:
                        # Новый расчет физики столкновений
                        norm = math.hypot(dx, dy)
                        nx = dx / norm
                        ny = dy / norm                        
                        p = 2 * (self.speed_x * nx + self.speed_y * ny - other.speed_x * nx - other.speed_y * ny) / (self.radius + other.radius)
                        
                        self.speed_x = (self.speed_x - p * other.radius * nx) * BOUNCE_FACTOR
                        self.speed_y = (self.speed_y - p * other.radius * ny) * BOUNCE_FACTOR
                        other.speed_x = (other.speed_x + p * self.radius * nx) * BOUNCE_FACTOR
                        other.speed_y = (other.speed_y + p * self.radius * ny) * BOUNCE_FACTOR
                        
                        # Корректировка позиций
                        overlap = (self.radius + other.radius) - distance
                        self.x -= overlap * nx * 0.5
                        self.y -= overlap * ny * 0.5
                        other.x += overlap * nx * 0.5
                        other.y += overlap * ny * 0.5
        
        # При остановке в корзине добавляем в счет
        # if self.on_ground and not self.added_to_score:
        #     global score
        #     score += self.size_idx + 1
        #     self.added_to_score = True

        return None

def draw_basket():
    # Боковые стенки
    pygame.draw.line(screen, (150, 100, 50), (0, BASKET_TOP), (0, HEIGHT), 5)
    pygame.draw.line(screen, (150, 100, 50), (BASKET_WIDTH, BASKET_TOP), (BASKET_WIDTH, HEIGHT), 5)
    
    # Верхняя пунктирная граница
    dash_length = 15
    for x in range(0, BASKET_WIDTH, dash_length*2):
        pygame.draw.line(screen, (150, 100, 50), 
                        (x, UPPER_LIMIT), 
                        (x + dash_length, UPPER_LIMIT), 3)

def draw_game_over():
    # Затемнение
    overlay = pygame.Surface((BASKET_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Текст
    text = font.render("Game Over", True, (255, 255, 255))
    screen.blit(text, (BASKET_WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
    
    # Кнопки
    restart_btn = pygame.Rect(BASKET_WIDTH//2 - 90, HEIGHT//2, 180, 50)
    quit_btn = pygame.Rect(BASKET_WIDTH//2 - 90, HEIGHT//2 + 70, 180, 50)
    
    pygame.draw.rect(screen, (0, 200, 0), restart_btn)
    pygame.draw.rect(screen, (200, 0, 0), quit_btn)
    
    # Текст кнопок
    screen.blit(font.render("Restart", True, (0,0,0)), 
               (restart_btn.x + 40, restart_btn.y + 10))
    screen.blit(font.render("Quit", True, (0,0,0)), 
               (quit_btn.x + 60, quit_btn.y + 10))
    
    # Обработка кликов
    mouse_pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        if restart_btn.collidepoint(mouse_pos):
            reset_game()
        elif quit_btn.collidepoint(mouse_pos):
            pygame.quit()
            sys.exit()

def reset_game():
    global score, game_over, countdown_active, countdown_start, balls, next_ball_idx
    score = 0
    game_over = False
    countdown_active = False
    countdown_start = 0
    balls = []
    next_ball_idx = random.randint(0, len(BALL_SIZES)-2)

def draw_hud():
    global game_over
    # Следующий шарик
    pygame.draw.circle(screen, COLORS[next_ball_idx], (BASKET_WIDTH - 50, 50), 30)
    
    # Счет
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))
    
    # Таймер
    if countdown_active and not game_over:
        elapsed = pygame.time.get_ticks() - countdown_start
        if elapsed >= 3000:
            game_over = True
        else:
            timer = 3 - elapsed // 1000
            timer_text = font.render(str(timer), True, (255, 0, 0))
            screen.blit(timer_text, (BASKET_WIDTH//2 - 15, 100))

# Основной цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONUP and not game_over:
            x, y = event.pos
            balls.append(Ball(x, next_ball_idx))
            next_ball_idx = random.randint(0, len(BALL_SIZES)-2)

    # Обновление
    if not game_over:
        for ball in balls:
            ball.update()
        
        # Проверка высоты шариков
        for ball in balls:
            if ball.y + ball.radius < UPPER_LIMIT:
                break
        else:
            countdown_active = False

    # Отрисовка
    screen.fill((255, 255, 255))
    draw_basket()
    
    for ball in balls:
        if ball.active:
            pygame.draw.circle(screen, ball.color, 
                              (int(ball.x), int(ball.y)), ball.radius)
    
    draw_hud()
    
    if game_over:
        draw_game_over()

    pygame.display.flip()
    clock.tick(FPS)