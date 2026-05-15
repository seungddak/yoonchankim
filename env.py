# env.py
import random
import pygame
from settings import *
from entities import Knight, Treasure, Lava, Key


class DungeonEnv:
    def __init__(self):
        self.grid_size = GRID_SIZE
        self.walls = self._generate_walls()

        # 기사가 돌아가야 하도록 길목에 용암 배치
        self.lavas = [(3, 2), (7, 2), (5, 5), (2, 7), (7, 7)]

        # 보물상자는 보스방(우측하단 9,9)에 고정
        self.treasure_pos = (9, 9)

        # 🔥 핵심: 열쇠가 나타날 수 있는 3개의 무작위 후보 구역
        self.key_spawns = [(0, 0), (9, 0), (0, 9)]
        self.current_key_idx = 0
        self.key_pos = self.key_spawns[self.current_key_idx]

        self.agent = Knight(0, 0)
        self.treasure = Treasure(*self.treasure_pos)
        self.key_obj = Key(*self.key_pos)
        self.lava_objects = [Lava(x, y) for x, y in self.lavas]

        self.steps = 0
        self.has_key = False
        self.reset()

    def _generate_walls(self):
        # 꼬불꼬불하고 헷갈리게 디자인된 복잡한 미로
        return {
            (2, 0), (2, 1), (2, 2), (2, 3),
            (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
            (6, 0), (6, 1), (6, 2), (6, 3),
            (8, 2), (8, 3), (8, 4),
            (1, 6), (2, 6), (2, 8), (2, 9),
            (6, 6), (7, 6), (8, 6), (6, 8), (7, 8)
        }

    def _random_empty_pos(self):
        # 주인공이 소환될 무작위 빈 공간 찾기
        while True:
            pos = (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))
            if pos not in self.walls and pos not in self.lavas and pos != self.treasure_pos and pos not in self.key_spawns:
                return pos

    def reset(self):
        # 1. 새 게임마다 기사의 위치 무작위 재배정
        self.agent.set_pos(*self._random_empty_pos())

        # 2. 새 게임마다 열쇠의 위치를 3곳 중 무작위 1곳으로 변경
        self.current_key_idx = random.randint(0, len(self.key_spawns) - 1)
        self.key_pos = self.key_spawns[self.current_key_idx]
        self.key_obj.set_pos(*self.key_pos)  # 시각적 오브젝트 위치 업데이트

        self.steps = 0
        self.has_key = False
        return self._get_state()

    def _get_state(self):
        # 🔥 인공지능 상태값에 '이번 판 열쇠 위치 구역(current_key_idx)'을 추가로 알려줌!
        # 이를 통해 매 판 열쇠 위치가 달라도 알아서 파악하고 쫓아갑니다.
        return (self.agent.pos, self.current_key_idx, self.has_key)

    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def step(self, action_idx):
        self.steps += 1
        dx, dy = ACTIONS[action_idx]
        curr_x, curr_y = self.agent.pos
        next_x, next_y = curr_x + dx, curr_y + dy

        reward = -1.0
        done = False

        target = self.treasure_pos if self.has_key else self.key_pos
        old_dist = self._manhattan_distance((curr_x, curr_y), target)

        if not (0 <= next_x < self.grid_size and 0 <= next_y < self.grid_size) or (next_x, next_y) in self.walls:
            reward -= 5.0  # 벽 부딪힘
            next_x, next_y = curr_x, curr_y
        else:
            self.agent.set_pos(next_x, next_y)

        new_dist = self._manhattan_distance((next_x, next_y), target)

        if new_dist < old_dist:
            reward += 2.0
        elif new_dist > old_dist:
            reward -= 2.0

        if not self.has_key and (next_x, next_y) == self.key_pos:
            self.has_key = True
            reward += 50.0

        if (next_x, next_y) == self.treasure_pos:
            if self.has_key:
                reward += 300.0
                done = True
            else:
                reward -= 10.0
                self.agent.set_pos(curr_x, curr_y)

        elif (next_x, next_y) in self.lavas:
            reward -= 100.0
            done = True
        elif self.steps >= MAX_STEPS:
            done = True

        return self._get_state(), reward, done

    def render(self, screen):
        screen.fill(BLACK)

        for x in range(GRID_SIZE + 1):
            pygame.draw.line(screen, DARK_GRAY, (x * CELL_SIZE, 0), (x * CELL_SIZE, BOARD_WIDTH))
        for y in range(GRID_SIZE + 1):
            pygame.draw.line(screen, DARK_GRAY, (0, y * CELL_SIZE), (BOARD_WIDTH, y * CELL_SIZE))

        for wx, wy in self.walls:
            pygame.draw.rect(screen, BROWN, (wx * CELL_SIZE, wy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for lava in self.lava_objects:
            lava.draw(screen)

        if not self.has_key:
            self.key_obj.draw(screen)

        self.treasure.draw(screen, is_unlocked=self.has_key)
        self.agent.draw(screen)