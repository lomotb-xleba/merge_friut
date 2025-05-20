import pygame
import random
import sys
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH = 800
HEIGHT = 600
FPS = 60
GRAVITY = 0.9
BOUNCE_FACTOR = 0.8
FRICTION = 0.98

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BASKET_COLOR = (150, 100, 50)
TRAJECTORY_COLOR = (200, 200, 200, 150)
RED = (255, 0, 0)
GAME_OVER_COLOR = (200, 50, 50, 200)

# Размеры шариков (от маленького к большому)
BALL_SIZES = [20, 30, 40, 50, 60]
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Merge Fruit")
clock = pygame.time.Clock()

BASKET_WIDTH = 300
BASKET_HEIGHT = 200
BASKET_TOP = HEIGHT - BASKET_HEIGHT - 50
BASKET_RECT = pygame.Rect((WIDTH//2 - BASKET_WIDTH//2, BASKET_TOP), 
                        (BASKET_WIDTH, BASKET_HEIGHT))
# Шрифты
font = pygame.font.SysFont('Arial', 36)

class Ball:
    def __init__(self, x, size_idx):
        self.x = x
        self.y = -BALL_SIZES[size_idx]
        self.size_idx = size_idx
        self.radius = BALL_SIZES[size_idx]
        self.color = COLORS[size_idx]
        self.speed_y = 0
        self.speed_x = 0
        self.active = True
        self.on_ground = False

    def update(self, balls):
        if not self.active:
            return
        
        # Применяем гравитацию, если шарик не на земле
        if not self.on_ground:
            self.speed_y += GRAVITY
            self.y += self.speed_y
        
        # Применяем горизонтальное движение
        self.x += self.speed_x
        self.speed_x *= FRICTION
        
        # Проверка столкновений с границами экрана
        if self.x - self.radius < 0:
            self.x = self.radius
            self.speed_x *= -BOUNCE_FACTOR
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x *= -BOUNCE_FACTOR
            
        # Проверка столкновения с нижней границей (игра заканчивается)
        if self.y + self.radius >= HEIGHT:
            return "game_over"

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
                # Проверяем, находится ли шарик внутри корзины
                in_basket_x = BASKET_RECT.left <= self.x <= BASKET_RECT.right
                in_basket_y = BASKET_RECT.top <= self.y <= BASKET_RECT.bottom
                if in_basket_x and in_basket_y:
                    self.speed_y = 0
                    self.on_ground = True
                else:
                    return "game_over"  # Шарик остановился вне корзины
        
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
        
        return None

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def draw_trajectory(start_pos, end_pos):
    points = []
    x0, y0 = start_pos
    x1, y1 = end_pos
    
    speed_y = 0
    speed_x = (x1 - x0) * 0.1
    y = y0
    x = x0
    points.append((x, y))
    
    for _ in range(100):
        speed_y += GRAVITY
        y += speed_y
        x += speed_x
        speed_x *= FRICTION
        
        # Проверка коллизий с корзиной для траектории
        radius = 20  # Размер шарика в предсказании
        
        # Левая стенка
        if x - radius < BASKET_RECT.left and BASKET_RECT.top <= y <= BASKET_RECT.bottom:
            x = BASKET_RECT.left + radius
            speed_x *= -BOUNCE_FACTOR
        
        # Правая стенка
        elif x + radius > BASKET_RECT.right and BASKET_RECT.top <= y <= BASKET_RECT.bottom:
            x = BASKET_RECT.right - radius
            speed_x *= -BOUNCE_FACTOR
        
        # Нижняя стенка
        if BASKET_RECT.left <= x <= BASKET_RECT.right and y + radius > BASKET_RECT.bottom:
            y = BASKET_RECT.bottom - radius
            speed_y *= -BOUNCE_FACTOR
            speed_x *= FRICTION
        
        points.append((x, y))
    
    if len(points) > 1:
        pygame.draw.lines(screen, TRAJECTORY_COLOR, False, points, 1)
    
    pygame.draw.circle(screen, TRAJECTORY_COLOR, (int(x), int(y)), 20)

def draw_basket():
    # Рисуем корзину в виде перевернутой П
    # Боковые стенки
    pygame.draw.line(screen, BASKET_COLOR, 
                    (BASKET_RECT.left, BASKET_RECT.top),
                    (BASKET_RECT.left, BASKET_RECT.bottom), 3)
    pygame.draw.line(screen, BASKET_COLOR,
                    (BASKET_RECT.right, BASKET_RECT.top),
                    (BASKET_RECT.right, BASKET_RECT.bottom), 3)
    
    # Нижняя стенка
    pygame.draw.line(screen, BASKET_COLOR,
                    (BASKET_RECT.left, BASKET_RECT.bottom),
                    (BASKET_RECT.right, BASKET_RECT.bottom), 3)
    
    # Пунктирная верхняя граница
    dash_length = 10
    for x in range(BASKET_RECT.left, BASKET_RECT.right, dash_length*2):
        pygame.draw.line(screen, BASKET_COLOR, (x, BASKET_RECT.top),
                        (x + dash_length, BASKET_RECT.top), 2)

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(GAME_OVER_COLOR)
    screen.blit(overlay, (0, 0))
    
    text = font.render("Game Over", True, WHITE)
    restart_text = font.render("Press R to Restart", True, WHITE)
    quit_text = font.render("Press Q to Quit", True, WHITE)
    
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 60))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 60))

def main():
    balls = []
    dropping_ball = None
    mouse_pressed = False
    start_pos = None
    game_over = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and dropping_ball is None:
                    mouse_pressed = True
                    start_pos = pygame.mouse.get_pos()
                
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_pressed and dropping_ball is None:
                    mouse_pressed = False
                    end_pos = pygame.mouse.get_pos()
                    dropping_ball = Ball(start_pos[0], 0)
                    # Добавляем горизонтальную скорость в зависимости от движения мыши
                    dropping_ball.speed_x = (end_pos[0] - start_pos[0]) * 0.1
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Рестарт игры
                        balls = []
                        dropping_ball = None
                        mouse_pressed = False
                        start_pos = None
                        game_over = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

        # Обновление
        if not game_over:
            if dropping_ball:
                result = dropping_ball.update(balls)
                if result == "game_over":
                    game_over = True
                elif dropping_ball.on_ground:  # Шарик остановился
                    balls.append(dropping_ball)
                    dropping_ball = None
            
            for ball in balls[:]:
                result = ball.update(balls)
                if result == "game_over":
                    game_over = True
                if not ball.active:
                    balls.remove(ball)

        # Отрисовка
        screen.fill(WHITE)
        
        # Рисуем корзину (перевернутую параболу)
        draw_basket()
        
        # Рисуем шарики
        for ball in balls:
            ball.draw()
        if dropping_ball:
            dropping_ball.draw()
        
        # Рисуем траекторию при зажатой ЛКМ
        if mouse_pressed and start_pos and dropping_ball is None and not game_over:
            current_pos = pygame.mouse.get_pos()
            draw_trajectory(start_pos, current_pos)
        
        # Рисуем экран окончания игры
        if game_over:
            draw_game_over()
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()