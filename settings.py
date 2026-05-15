# settings.py

GRID_SIZE = 10
CELL_SIZE = 60

BOARD_WIDTH = GRID_SIZE * CELL_SIZE
INFO_HEIGHT = 150

WIDTH = BOARD_WIDTH
HEIGHT = BOARD_WIDTH + INFO_HEIGHT

FPS = 30

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)
BLUE = (50, 100, 255)
RED = (255, 60, 60)
GOLD = (255, 215, 0)
BROWN = (139, 69, 19)
SILVER = (200, 200, 210)
PANEL_BG = (230, 235, 240)

# 5가지 행동
ACTIONS = {
    0: (0, -1),   # UP
    1: (0, 1),    # DOWN
    2: (-1, 0),   # LEFT
    3: (1, 0),    # RIGHT
    4: (0, 0),    # STAY
}

ACTION_NAMES = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT", 4: "STAY"}

MAX_STEPS = 150                 # 미로가 복잡해졌으므로 제한 걸음 수 증가
TRAIN_EPISODES_PER_FRAME = 200  # 답답하지 않게 고속 학습 속도 대폭 증가!