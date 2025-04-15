import pygame
import random
import sys
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH = 800
HEIGHT = 600
BASKET_HEIGHT = 100
FPS = 60
GRAVITY = 0.9
BOUNCE_FACTOR = 0.4
FRICTION = 0.99

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BASKET_COLOR = (150, 100, 50)
TRAJECTORY_COLOR = (200, 200, 200, 150)

# Размеры шариков (от маленького к большому)
BALL_SIZES = [20, 30, 40, 50, 60]
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Merge Fruit")
clock = pygame.time.Clock()

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
            
        # Остановка при достижении дна корзины
        if self.y + self.radius >= HEIGHT - BASKET_HEIGHT:
            self.y = HEIGHT - BASKET_HEIGHT - self.radius
            self.speed_y *= -BOUNCE_FACTOR
            self.speed_x *= FRICTION
            
            # Если скорость очень мала, останавливаем шарик
            if abs(self.speed_y) < 1:
                self.speed_y = 0
                self.on_ground = True
        
        # Проверка столкновений с другими шариками
        for other in balls:
            if other != self and other.active:
                distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
                if distance < self.radius + other.radius:
                    if self.size_idx == other.size_idx and self.size_idx < len(BALL_SIZES) - 1:
                        # Слияние шариков
                        self.size_idx += 1
                        self.radius = BALL_SIZES[self.size_idx]
                        self.color = COLORS[self.size_idx]
                        other.active = False
                        
                        # Добавляем эффект отталкивания при слиянии
                        angle = math.atan2(self.y - other.y, self.x - other.x)
                        force = 5
                        self.speed_x = math.cos(angle) * force
                        self.speed_y = math.sin(angle) * force
                        self.on_ground = False
                    else:
                        # Физика столкновения
                        angle = math.atan2(self.y - other.y, self.x - other.x)
                        overlap = (self.radius + other.radius) - distance
                        
                        # Раздвигаем шарики
                        self.x += math.cos(angle) * overlap * 0.5
                        self.y += math.sin(angle) * overlap * 0.5
                        other.x -= math.cos(angle) * overlap * 0.5
                        other.y -= math.sin(angle) * overlap * 0.5
                        
                        # Обмен импульсами
                        total_mass = self.radius + other.radius
                        new_speed_x1 = (self.speed_x * (self.radius - other.radius) + 2 * other.radius * other.speed_x) / total_mass
                        new_speed_y1 = (self.speed_y * (self.radius - other.radius) + 2 * other.radius * other.speed_y) / total_mass
                        new_speed_x2 = (other.speed_x * (other.radius - self.radius) + 2 * self.radius * self.speed_x) / total_mass
                        new_speed_y2 = (other.speed_y * (other.radius - self.radius) + 2 * self.radius * self.speed_y) / total_mass
                        
                        self.speed_x, self.speed_y = new_speed_x1 * BOUNCE_FACTOR, new_speed_y1 * BOUNCE_FACTOR
                        other.speed_x, other.speed_y = new_speed_x2 * BOUNCE_FACTOR, new_speed_y2 * BOUNCE_FACTOR
                        
                        self.on_ground = False
                        other.on_ground = False

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def draw_trajectory(start_pos, end_pos):
    points = []
    x0, y0 = start_pos
    x1, y1 = end_pos
    
    # Симуляция траектории
    speed_y = 0
    y = y0
    x = x0
    points.append((x, y))
    
    for _ in range(50):  # 50 шагов симуляции
        speed_y += GRAVITY
        y += speed_y
        points.append((x, y))
        
        if y + 20 >= HEIGHT - BASKET_HEIGHT:
            y = HEIGHT - BASKET_HEIGHT - 20
            speed_y *= -BOUNCE_FACTOR
    
    # Рисуем траекторию
    if len(points) > 1:
        pygame.draw.lines(screen, TRAJECTORY_COLOR, False, points, 1)
    
    # Рисуем шарик в конечной позиции
    pygame.draw.circle(screen, TRAJECTORY_COLOR, (int(x), int(y)), 20)

def main():
    balls = []
    dropping_ball = None
    mouse_pressed = False
    start_pos = None
    
    # Создаем поверхность для прозрачной траектории
    trajectory_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and dropping_ball is None:
                mouse_pressed = True
                start_pos = pygame.mouse.get_pos()
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_pressed and dropping_ball is None:
                mouse_pressed = False
                end_pos = pygame.mouse.get_pos()
                dropping_ball = Ball(start_pos[0], 0)
                # Добавляем горизонтальную скорость в зависимости от движения мыши
                dropping_ball.speed_x = (end_pos[0] - start_pos[0]) * 0.1

        # Обновление
        if dropping_ball:
            dropping_ball.update(balls)
            if dropping_ball.on_ground:  # Шарик остановился
                balls.append(dropping_ball)
                dropping_ball = None
        
        for ball in balls[:]:
            ball.update(balls)
            if not ball.active:
                balls.remove(ball)

        # Отрисовка
        screen.fill(WHITE)
        
        # Рисуем корзину
        pygame.draw.rect(screen, BASKET_COLOR, (0, HEIGHT - BASKET_HEIGHT, WIDTH, BASKET_HEIGHT))
        
        # Рисуем шарики
        for ball in balls:
            ball.draw()
        if dropping_ball:
            dropping_ball.draw()
        
        # Рисуем траекторию при зажатой ЛКМ
        if mouse_pressed and start_pos and dropping_ball is None:
            current_pos = pygame.mouse.get_pos()
            draw_trajectory(start_pos, current_pos)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()