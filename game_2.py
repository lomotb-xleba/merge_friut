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
BOUNCE_FACTOR = 0.7
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
            
        # Проверка столкновения с перевернутой параболой (корзиной)
        # Уравнение перевернутой параболы: y = -a*(x - h)^2 + k
        a = 0.01  # Крутизна параболы
        h = WIDTH // 2  # Центр по x
        k = HEIGHT - 150  # Высота вершины параболы
        parabola_y = -a * (self.x - h)**2 + k
        
        if self.y + self.radius >= parabola_y:
            # Корректируем позицию шарика
            self.y = parabola_y - self.radius
            self.speed_y *= -BOUNCE_FACTOR
            self.speed_x *= FRICTION
            
            # Если скорость очень мала, останавливаем шарик
            if abs(self.speed_y) < 1:
                self.speed_y = 0
                self.on_ground = True
        
        # Проверка столкновений с другими шариками
        for other in balls:
            if other != self and other.active:
                dx = other.x - self.x
                dy = other.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                
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
                        # Физика столкновения - упругое отталкивание
                        angle = math.atan2(dy, dx)
                        overlap = (self.radius + other.radius) - distance
                        
                        # Раздвигаем шарики
                        move_x = math.cos(angle) * overlap * 0.5
                        move_y = math.sin(angle) * overlap * 0.5
                        
                        self.x -= move_x
                        self.y -= move_y
                        other.x += move_x
                        other.y += move_y
                        
                        # Обмен импульсами
                        m1 = self.radius ** 2
                        m2 = other.radius ** 2
                        total_mass = m1 + m2
                        
                        v1x = self.speed_x
                        v1y = self.speed_y
                        v2x = other.speed_x
                        v2y = other.speed_y
                        
                        # Новые скорости после столкновения
                        new_v1x = (v1x*(m1 - m2) + 2*m2*v2x) / total_mass
                        new_v1y = (v1y*(m1 - m2) + 2*m2*v2y) / total_mass
                        new_v2x = (v2x*(m2 - m1) + 2*m1*v1x) / total_mass
                        new_v2y = (v2y*(m2 - m1) + 2*m1*v1y) / total_mass
                        
                        self.speed_x = new_v1x * BOUNCE_FACTOR
                        self.speed_y = new_v1y * BOUNCE_FACTOR
                        other.speed_x = new_v2x * BOUNCE_FACTOR
                        other.speed_y = new_v2y * BOUNCE_FACTOR
                        
                        self.on_ground = False
                        other.on_ground = False
        
        return None

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def draw_trajectory(start_pos, end_pos):
    points = []
    x0, y0 = start_pos
    x1, y1 = end_pos
    
    # Симуляция траектории
    speed_y = 0
    speed_x = (x1 - x0) * 0.1
    y = y0
    x = x0
    points.append((x, y))
    
    for _ in range(100):  # 100 шагов симуляции
        speed_y += GRAVITY
        y += speed_y
        x += speed_x
        speed_x *= FRICTION
        points.append((x, y))
        
        # Проверка столкновения с перевернутой параболой
        a = 0.0015
        h = WIDTH // 2
        k = HEIGHT - 250
        parabola_y = -a * (x - h)**2 + k
        
        if y + 20 >= parabola_y:
            y = parabola_y - 20
            speed_y *= -BOUNCE_FACTOR
            speed_x *= FRICTION
    
    # Рисуем траекторию
    if len(points) > 1:
        pygame.draw.lines(screen, TRAJECTORY_COLOR, False, points, 1)
    
    # Рисуем шарик в конечной позиции
    pygame.draw.circle(screen, TRAJECTORY_COLOR, (int(x), int(y)), 20)

def draw_basket():
    # Рисуем перевернутую параболу (корзину)
    a = 0.01
    h = WIDTH // 2
    k = HEIGHT - 150
    points = []
    for x in range(250, WIDTH-250):
        y = -a * (x - h)**2 + k
        points.append((x, y))
    if len(points) > 1:
        pygame.draw.lines(screen, BASKET_COLOR, False, points, 3)

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