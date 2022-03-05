import pygame
import sys
import copy
from player_class import *
from settings import *
from enemy_class import *
from database import *

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
vec = pygame.math.Vector2  # установка нашей позиции и скорости
pygame.mixer.music.load('sounds/menu.mp3')
live_sound = pygame.mixer.Sound('sounds/playing.ogg')
dead_sound = pygame.mixer.Sound('sounds/dead_menu.ogg')


# ******************************************ОСНОВНОЕ ТЕЛО ПРИЛОЖЕНИЯ*********************************************
class App:
    def __init__(self):
        pygame.mixer.music.play(0)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))  # ширина и высота экрана
        self.clock = pygame.time.Clock()  # контроль количества кадров
        self.running = True  # отслеживание запуска приложения
        self.state = 'start'  # начальное состояние (стартовый экран)
        self.cell_width = MAZE_WIDTH // COLS  # определение ширины
        self.cell_height = MAZE_HEIGHT // ROWS  # определение высоты
        self.walls = []  # наш список стен
        self.coins = []  # наш список монет
        self.enemies = []  # наш список врагов
        self.e_pos = []  # позиции врагов (у нас их несколько, поэтому список)
        self.p_pos = None  # позиция игрока (начальная)
        self.load()  # функция для загрузки элементов
        self.player = Player(self, vec(self.p_pos))  # векторное перемещение игрока
        self.make_enemies()  # функция создания врагов

    def run(self):  # главная функция приложения
        while self.running:
            if self.state == 'start':  # состояние приложения при старте
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':  # состояние приложения во время цикла
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':  # состояние приложения после окончания игры или прерывания
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)  # частота обновления действий игрока вместе с циклом 60=60
        pygame.quit()  # после завершения цикла игры - выходим из приложения
        sys.exit()

    # ***************************************ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ****************************************
    # отрисовка текста
    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0] - text_size[0] // 2
            pos[1] = pos[1] - text_size[1] // 2
        screen.blit(text, pos)

    # загрузка фоновой карты
    def load(self):
        self.background = pygame.image.load('maze.png')
        self.background = pygame.transform.scale(self.background, (MAZE_WIDTH, MAZE_HEIGHT))
        # Открываем нашу карту
        with open("walls.txt", 'r') as file:
            # проходим по y ( берем enumerate, чтобы  получить помимо индекса ещё и голую нумерацию клетки
            # всё это нужно, чтобы определить не только координату игрока, но и конкретного объекта
            for yidx, line in enumerate(file):
                # проходим по x
                for xidx, char in enumerate(line):
                    # дальше идёт опредление, чем является данный элемент массива (стена, монета, игрок, враг, ворота)
                    if char == "1":
                        self.walls.append(vec(xidx, yidx))
                    elif char == "C":
                        self.coins.append(vec(xidx, yidx))
                    elif char == "P":
                        self.p_pos = [xidx, yidx]
                    elif char in ["2", "3", "4", "5"]:
                        self.e_pos.append([xidx, yidx])
                    elif char == "B":
                        pygame.draw.rect(self.background, BLACK, (xidx * self.cell_width, yidx * self.cell_height,
                                                                  self.cell_width, self.cell_height))

    # функция по созданию врагов
    def make_enemies(self):
        for idx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def draw_grid(self):  # рисует вспомогательную сетку
        for x in range(WIDTH // self.cell_width):  # проходим по ширине всей карты
            pygame.draw.line(self.background, GREY, (x * self.cell_width, 0),
                             (x * self.cell_width, HEIGHT))
        for x in range(HEIGHT // self.cell_height):  # проходим по высоте всей карты
            pygame.draw.line(self.background, GREY, (0, x * self.cell_height),
                             (WIDTH, x * self.cell_height))
        # ВСПОМОГАТЕЛЬНАЯ ОТРИСОВКА НА НАЧАЛЬНОМ УРОВНЕ (БОЛЬШЕ НЕ ИСПОЛЬЗУЕТСЯ)
        # 1)тут рисую визуализацию стены, чтобы проще было работать с ней, во время установки объектов
        # for wall in self.walls:
            # pygame.draw.rect(self.background, (112, 55, 163),
            # (wall.x * self.cell_width, wall.y * self.cell_height, self.cell_width))
        # 2)тут рисую монетки, чтобы проще было определить позиции, где они быть не должны
        # for coin in self.coins:
        #     pygame.draw.rect(self.background, (167, 179, 34), (coin.x*self.cell_width,
        #  coin.y*self.cell_height, self.cell_width, self.cell_height))

    def reset(self):
        dead_sound.stop()
        live_sound.play()
        for value in cur.execute("SELECT max(score) FROM SCORES"):
            new = value
            self.player.high_score = new[0]
        db.commit()
        print(self.player.high_score)
        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.coins = []
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == 'C':
                        self.coins.append(vec(xidx, yidx))
        self.state = "playing"

    # ****************************************СТАРТОВЫЕ ФУНКЦИИ************************************************
    def start_events(self):  # переход к карте ( по пробелу )
        for event in pygame.event.get():  # доступ к главному экрану
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'playing'  # переход в игровое состояние
                pygame.mixer.music.stop()
                live_sound.play()
                live_sound.set_volume(1)

    def start_update(self):
        pass

    def start_draw(self):  # отрисовка начального экрана
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACE BAR', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 50], START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [
            WIDTH // 2, HEIGHT // 2], START_TEXT_SIZE, (44, 167, 198), START_FONT, centered=True)
        self.draw_text('2022  GRIGOREV Corporation', self.screen, [WIDTH // 2, HEIGHT // 2 + 100],
                       START_TEXT_SIZE, (128, 0, 255), START_FONT, centered=True)
        self.draw_text('ИП-19-7к G.A.N', self.screen, [WIDTH // 2, HEIGHT // 2 + 50],
                       START_TEXT_SIZE, (255, 203, 219), START_FONT, centered=True)
        self.draw_text('HIGH SCORE', self.screen, [4, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        pygame.display.update()

    # **************************************** АКТИВНЫЕ(ИГРОВЫЕ)ФУНКЦИИ******************************************
    # функция отвечающая за движения героя
    def playing_events(self):
        for event in pygame.event.get():  # проверка на игровое состояние, в случае чего завершить игровой процесс
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:  # добавляем движегния персонажа
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))

    # функция на взаимодействие игрока с врагом
    def playing_update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update()
        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                self.remove_life()

    # функция для рисования на дисплее
    def playing_draw(self):
        self.screen.fill(BLACK)  # заливка главного экрана
        self.screen.blit(self.background, (TOP_BOTTOM_BUFFER // 2, TOP_BOTTOM_BUFFER // 2))  # заливка игрового экрана
        self.draw_coins()  # рисуем монеты
        # self.draw_grid()  # вспомогательная сетка для рисования
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),  # обозначаем текст текущих очков
                       self.screen, [60, 0], 18, WHITE, START_FONT)
        self.draw_text('HIGH SCORE: {}'.format(self.player.high_score), self.screen, [WIDTH // 2 + 60, 0], 18, WHITE, START_FONT)  # аналогично рекорд
        self.player.draw()  # рисуем игрока
        # отрисовка позиции врагов
        for enemy in self.enemies:
            enemy.draw()
        pygame.display.update()  # обычный апдейт экрана (применить все изменения рисовки, координат и тд)

    # функция - удаление жизни при столкновении
    def remove_life(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
            live_sound.stop()
            dead_sound.play()
        else:
            self.player.grid_pos = vec(self.player.starting_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.grid_pos = vec(enemy.starting_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0

    # функция рисующая монеты поверх экрана, а не картинки!
    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (124, 123, 7),
                               (int(coin.x*self.cell_width)+self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(coin.y*self.cell_height)+self.cell_height//2+TOP_BOTTOM_BUFFER//2), 5)

    #  ******************************************ФУНКЦИИ ОКОНЧАНИЯ ИГРЫ*******************************************

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        self.draw_text("GAME OVER", self.screen, [WIDTH//2, 100],  52, RED, "arial", centered=True)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  36, (190, 190, 190), "arial", centered=True)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  36, (190, 190, 190), "arial", centered=True)
        pygame.display.update()
