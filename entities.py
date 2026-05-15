# entities.py
import pygame
import math
from settings import CELL_SIZE, BLUE, GOLD, RED, SILVER


class GameObject:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def pos(self):
        return self._x, self._y

    def set_pos(self, x, y):
        self._x = x
        self._y = y

    def draw(self, surface):
        pass


class Knight(GameObject):
    def draw(self, surface):
        cx = self._x * CELL_SIZE + CELL_SIZE // 2
        cy = self._y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(surface, BLUE, (cx, cy), CELL_SIZE // 2 - 8)
        pygame.draw.rect(surface, (200, 200, 200), (cx - 10, cy - 15, 20, 10))


class Treasure(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tick = 0

    def draw(self, surface, is_unlocked=False):
        self.tick += 1
        px = self._x * CELL_SIZE + 10
        py = self._y * CELL_SIZE + 15

        # 보물 상자 본체
        box_color = GOLD if is_unlocked else (150, 150, 100)
        pygame.draw.rect(surface, box_color, (px, py, CELL_SIZE - 20, CELL_SIZE - 30))

        # 자물쇠 (열쇠가 있으면 초록색, 없으면 빨간색)
        lock_color = (50, 255, 50) if is_unlocked else (255, 50, 50)
        pygame.draw.rect(surface, lock_color, (px + 15, py + 10, 10, 10))

        if is_unlocked and self.tick % 10 < 5:
            pygame.draw.circle(surface, (255, 255, 200), (px + 5, py - 5), 4)


class Lava(GameObject):
    def draw(self, surface):
        px = self._x * CELL_SIZE
        py = self._y * CELL_SIZE
        pygame.draw.rect(surface, RED, (px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4))
        pygame.draw.circle(surface, (255, 120, 0), (px + CELL_SIZE // 3, py + CELL_SIZE // 3), 6)
        pygame.draw.circle(surface, (255, 150, 50), (px + CELL_SIZE * 2 // 3, py + CELL_SIZE * 2 // 3), 4)


class Key(GameObject):
    def draw(self, surface):
        px = self._x * CELL_SIZE + CELL_SIZE // 2
        py = self._y * CELL_SIZE + CELL_SIZE // 2
        # 열쇠 모양 그리기
        pygame.draw.circle(surface, SILVER, (px - 8, py), 6, 3)
        pygame.draw.line(surface, SILVER, (px - 2, py), (px + 12, py), 3)
        pygame.draw.line(surface, SILVER, (px + 6, py), (px + 6, py + 6), 3)
        pygame.draw.line(surface, SILVER, (px + 12, py), (px + 12, py + 6), 3)