import pygame
import random
from settings import *

vec = pygame.math.Vector2


# аналогичный класс игроку
class Enemy:
    def __init__(self, app, pos, number):
        self.app = app  # передаём так сказать шаблон ("местность") где будем распологать врага
        self.grid_pos = pos  # позиция относительно вспомогательной сектки
        self.starting_pos = [pos.x, pos.y]  # стартовая позиция (координата списка клеток)
        self.pix_pos = self.get_pix_pos()  # позиция относителньо карте, каждой клетки в пикселях
        self.radius = int(self.app.cell_width//2.3) # ставим радиус, чтобы они имели фиксированный размер == игрока
        self.number = number  # номер врага
        self.colour = self.set_colour()  # цвет врага
        self.direction = vec(0, 0)  # плавное передвижение (векторное)
        self.personality = self.set_personality()  # заданный персональный "алгоритм поведения"
        self.target = None  # будет ли таргет на игроке
        self.speed = self.set_speed()  # заданная скорость

    # функция вхаимодействия с позицией игрока и врага
    def update(self):
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            # если пошел цикл старта, начинаем движение всех врагов
            if self.time_to_move():
                self.move()

        # Настройки на смещение с начальной точки относительно координатной сетки (вспомогательной)\
        # аналогично апдейту персонажа
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.app.cell_height//2)//self.app.cell_height+1

    # функция рисования каждого врага (кругом)
    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour,
                           (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    # функция дял задания скорости соответствующему типу
    def set_speed(self):
        if self.personality in ["speedy", "scared"]:
            speed = 2
        else:
            speed = 1
        return speed

    # функция установка цели на игрока
    def set_target(self):
        # проверка на "личность" врага
        if self.personality == "speedy" or self.personality == "slow":
            return self.app.player.grid_pos
        # если он "scared" - то будет убегать от игрока в противоположный угол
        else:
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)
            if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)
            else:
                return vec(COLS-2, ROWS-2)

    # такая же функция движения, как и у игрока, обход по веторному, пиксельному и координатному положению
    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    # Фугкция, отвечающая за определение способа движения
    # тут мы отталкивается от способа "поведения" врага
    def move(self):
        if self.personality == "random":
            self.direction = self.get_random_direction()
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)

    # функция движения к игроку
    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)  # записываем в путь следующую клетку до игрока
        xdir = next_cell[0] - self.grid_pos[0]  # поиск по x
        ydir = next_cell[1] - self.grid_pos[1]  # поиск по y
        return vec(xdir, ydir)  # вовзращаем векторное направление до игрока

    # функция нахождения нового пути до игрока
    def find_next_cell_in_path(self, target):
        # путь будет состоять из: точки старта игрока, точка старта врага
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
                        int(target[0]), int(target[1])])
        return path[1]  # возвращаем начальную клетку до игрока и строим путь по каждой клетке

    # функция = алгоритм поиска в ширину (генерация пути до игрока)
    def BFS(self, start, target):
        # создаём опять вспомогательную сетку, для упрощенного поиска
        grid = [[0 for x in range(28)] for x in range(30)]
        # начинаем обход (просмотр) по списку стен
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                # начинаем отрисовку "псевдостен" на сгенерированной сетке
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]  # начало нашей очереди (проложения пути)
        path = []  # наш проложенный путь, записанный в список для таргета
        visited = []  # список, уже посвещенных клеток
        while queue:  # начало цикла (проход по каждой не посещенной клетке)
            current = queue[0]  # текущая клетка
            queue.remove(queue[0])  # как только посетили клетку - удаляем из очереди
            visited.append(current)  # добавляем посещенную клетку в список "посещенных клеток"
            if current == target:  # проверяем, если текущая клетка - является позицией игрока, то строим путь до него
                break  # естественно выходим из цикла, путь построен, обход по остальным клеткам не нужен
            else:  # если не обнаружили по поиску в ширину, начинаем поиск в глубину
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]  # даёт координаты соседних клеток
                for neighbour in neighbours:  # начинаем обход
                    # проверяем не уперлись ли мы в ширину нашей карты (ось "x")
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        # проверяем не уперлись ли мы в длину нашей карты (ось "y")
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            # присваиваем следующей клетке полученную координату, благодаря обходу в ширину и высоту
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            # опять же как и в ширину, проверяем не посещена ли она уже с прошлого обхода
                            if next_cell not in visited:
                                #  проверяем не стена ли это, т.к в самом начале цикла 1 = добавленной стенке
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)  # если всё в порядке добавляем в очередь - как путь
                                    # добавляем весь путь в словарь для двух координат:
                                    # первая координата - там где мы заспавнились
                                    # вторая координата - там где нас нашли путем прохода в глубь и ширь
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]  # помечаем, как самый короткий найденный путь до игрока
        while target != start:  # цикл, работающий пока мы не вернулись к началу очереди (новый поиск пути)
            for step in path:  # проходим по значениям ячеек найденного пути
                if step["Next"] == target:  # если в одной из этих ячеек - игрок находится в данный момент
                    target = step["Current"]  # то нашей следующей посещенной клеткой будет место игрока (цель)
                    shortest.insert(0, step["Current"])  # вставляем в короткий путь - самую близкую клетку к игроку
        return shortest  # возвращаем для врага этот самый короткий путь

    # отдельная функция под рандомное движение врага (отдельный вид поведения)
    def get_random_direction(self):
        while True:
            # если использовать векторную координату - то он будет ходить лесенкой
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            # нам нужно создать переменную следующей позиции, для проверки на стены
            # без этой переменной враг будет ходить как ему угодно, не определяя стен
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    # функция получения позиции врага (пиксели)
    def get_pix_pos(self):
        return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2 +
                   self.app.cell_height//2)

    # функция выдачи цветов для каждого врага
    def set_colour(self):
        if self.number == 0:
            return (43, 78, 203)
        if self.number == 1:
            return (197, 200, 27)
        if self.number == 2:
            return (189, 29, 29)
        if self.number == 3:
            return (215, 159, 33)

    # функция выдачи "поведения" для каждого врага
    def set_personality(self):
        if self.number == 0:
            return "speedy"
        elif self.number == 1:
            return "slow"
        elif self.number == 2:
            return "random"
        else:
            return "scared"