import pygame
from settings import *
from database import *

vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app  # передаём так сказать шаблон ("местность") где будем распологать игрока
        self.starting_pos = [pos.x, pos.y]  # стартовая позиция (координата списка клеток)
        self.grid_pos = pos  # позиция относительно вспомогательной сектки
        self.pix_pos = self.get_pix_pos()  # позиция относителньо карте, каждой клетки в пикселях
        self.direction = vec(1, 0)  # плавное передвижение (векторное)
        self.stored_direction = None  # второстепенная перменная, которая отвечает за "прошлое" положение на карте
        self.able_to_move = True  # можем ли мы идти в том или инном направлении относительно нашей координаты
        self.current_score = 0  # наш счетчик очков
        self.high_score = 0
        self.speed = 2  # скорость игрока
        self.lives = 3  # наш счетчик жизней

    # функция, которая отвечает за любой апдейт игроком - например, подбор монеты или смена позиции
    def update(self):
        if self.able_to_move:
            self.pix_pos += self.direction * self.speed
        # выполняем следующее, если мы движемся в данный момент
        if self.time_to_move():
            # если следующее положение будет не текущим, то проход разрешен
            if self.stored_direction is not None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()
        # Настройки на смещение с начальной точки относительно координатной сетки (вспомогательной)
        self.grid_pos[0] = (self.pix_pos[0] - TOP_BOTTOM_BUFFER +
                            self.app.cell_width // 2) // self.app.cell_width + 1
        self.grid_pos[1] = (self.pix_pos[1] - TOP_BOTTOM_BUFFER +
                            self.app.cell_height // 2) // self.app.cell_height + 1
        # если мы на точке монеты - то "съедаем" её, вызываем функцию удаления данной монеты с позиции игрока
        if self.on_coin():
            self.eat_coin()

    # функция, которая рисует игрока
    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOUR,
                           (int(self.pix_pos.x), int(self.pix_pos.y)), self.app.cell_width // 2 - 2)

        # Рисуем жизни игрока
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (30 + 20 * x, HEIGHT - 15), 7)

        # Закоментил это дело, тут создаётся прямоугольник, который следует за нами, и отслеживает наше место положение
        # по желанию можно раскоментить, чтобы наглядно посмотреть отслеживание ( или же переделать карту )

        # pygame.draw.rect(self.app.screen, RED, (self.grid_pos[0]*self.app.cell_width+TOP_BOTTOM_BUFFER//2,
        # self.grid_pos[1]*self.app.cell_height+TOP_BOTTOM_BUFFER//2, self.app.cell_width, self.app.cell_height), 1)

    # обычная функция, проверяющая стоим мы на монете или нет
    def on_coin(self):
        if self.grid_pos in self.app.coins:
            # небольшая првоерка на то, находимся ли мы в центре - в момент съедения монеты
            # эта проверка нужна для того, чтобы монета не исчезала слишком рано, при соприкосновении с её границей
            # тут у нас проверка по центру x
            if int(self.pix_pos.x + TOP_BOTTOM_BUFFER // 2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            # тут у нас проверка по центру y
            if int(self.pix_pos.y + TOP_BOTTOM_BUFFER // 2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    # функция, начисляющая очки за съеденные монеты (удаление монеты, засчитывание очков)
    def eat_coin(self):
        self.app.coins.remove(self.grid_pos)
        self.current_score += 1

    # функция которая передаёт перемещение игрока относительно последней его позиции(координаты)
    def move(self, direction):
        self.stored_direction = direction

    # функция, которая вернет позицию относительно клетки карты
    def get_pix_pos(self):
        return vec((self.grid_pos[0] * self.app.cell_width) + TOP_BOTTOM_BUFFER // 2 + self.app.cell_width // 2,
                   (self.grid_pos[1] * self.app.cell_height) +
                   TOP_BOTTOM_BUFFER // 2 + self.app.cell_height // 2)
        print(self.grid_pos, self.pix_pos)

    # функция, отвечающая за действия, если мы движемся в данный момент, а не стоим на месте (x, y)
    def time_to_move(self):
        # x:
        if int(self.pix_pos.x + TOP_BOTTOM_BUFFER // 2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        # y:
        if int(self.pix_pos.y + TOP_BOTTOM_BUFFER // 2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    # функция, определяющая можем ли мы двигаться дальше (если следующая координата не является стеной)
    def can_move(self):
        for wall in self.app.walls:
            if vec(self.grid_pos + self.direction) == wall:
                return False
        return True
