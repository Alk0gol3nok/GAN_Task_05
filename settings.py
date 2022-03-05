from pygame.math import Vector2 as vec

# НАСТРОЙКИ ЭКРАНА
WIDTH, HEIGHT = 610, 670
FPS = 60
TOP_BOTTOM_BUFFER = 50
MAZE_WIDTH, MAZE_HEIGHT = WIDTH - TOP_BOTTOM_BUFFER, HEIGHT - TOP_BOTTOM_BUFFER

ROWS = 30
COLS = 28

# НАСТРОЙКИ ЦВЕТОВОЙ ПАЛИТРЫ
BLACK = (0, 0, 0)
RED = (208, 22, 22)
GREY = (107, 107, 107)
WHITE = (255, 255, 255)
PLAYER_COLOUR = (190, 194, 15)

# НАСТРОЙКИ ШРИФТОВ
START_TEXT_SIZE = 16
START_FONT = 'arial black'

# НАСТРОЙКИ ИГРОКА
# тут закоментил появление игрока через заданный вектор, чтобы назначать позицию игрока в текстовом файле
# PLAYER_START_POS = vec(2, 2)

# НАСТРОЙКА ВРАГОВ
