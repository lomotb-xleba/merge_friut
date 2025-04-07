import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH = 800
HEIGHT = 600
BASKET_HEIGHT = 100
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BASKET_COLOR = (150, 100, 50)

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
        self.speed = 5
        self.active = True

    def update(self, balls):
        if not self.active:
            return
        
        self.y += self.speed
        
        # Проверка столкновений с другими шариками
        for other in balls:
            if other != self and other.active:
                distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
                if distance < self.radius + other.radius:
                    if self.size_idx == other.size_idx and self.size_idx < len(BALL_SIZES) - 1:
                        self.size_idx += 1
                        self.radius = BALL_SIZES[self.size_idx]
                        self.color = COLORS[self.size_idx]
                        other.active = False
        
        # Остановка при достижении дна корзины
        if self.y + self.radius >= HEIGHT - BASKET_HEIGHT:
            self.y = HEIGHT - BASKET_HEIGHT - self.radius
            self.speed = 0

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def main():
    balls = []
    dropping_ball = None
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and dropping_ball is None:
                x = pygame.mouse.get_pos()[0]
                dropping_ball = Ball(x, 0)  # Создаем новый шарик в месте клика

        # Обновление
        if dropping_ball:
            dropping_ball.update(balls)
            if dropping_ball.speed == 0:  # Шарик достиг дна
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
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()