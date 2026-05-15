# main.py
import sys
import pygame

from env import DungeonEnv
from rl_agent import QLearningAgent
from settings import *


class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RL Dungeon Explorer: Key Edition")
        self.clock = pygame.time.Clock()

        self.font_b = pygame.font.SysFont("malgungothic", 18, bold=True)
        self.font_m = pygame.font.SysFont("malgungothic", 16)

        self.env = DungeonEnv()
        self.agent = QLearningAgent()

        self.training = False
        self.auto_play = False

        self.episode = 0
        self.wins = 0
        self.losses = 0

        self.demo_done = False
        self.step_delay = 200
        self.last_step_t = 0
        self.current_state = self.env.reset()

    def _train_one(self):
        state = self.env.reset()
        done = False
        while not done:
            action = self.agent.select_action(state)
            next_state, reward, done = self.env.step(action)
            self.agent.learn(state, action, reward, next_state, done)
            state = next_state

            if done:
                if reward > 100:
                    self.wins += 1
                elif reward < -100:
                    self.losses += 1

        self.episode += 1
        if self.agent.epsilon > self.agent.epsilon_min:
            self.agent.epsilon *= self.agent.epsilon_decay

    def start_new_demo(self):
        self.current_state = self.env.reset()
        self.demo_done = False

    def run_demo_step(self):
        if self.demo_done: return
        action = self.agent.best_action(self.current_state)
        next_state, reward, done = self.env.step(action)
        self.current_state = next_state
        if done: self.demo_done = True

    def draw_panel(self):
        panel = pygame.Surface((WIDTH, INFO_HEIGHT))
        panel.fill(PANEL_BG)
        pygame.draw.line(panel, DARK_GRAY, (0, 0), (WIDTH, 0), 3)

        mode_str = "모드: 고속 학습중 (T를 눌러 중지)" if self.training else "모드: 데모 (A: 자동, D: 새 게임)"
        key_str = "보유" if self.env.has_key else "미보유 (먼저 은빛 열쇠를 찾으세요!)"

        texts = [
            mode_str,
            f"에피소드: {self.episode} | 열쇠 상태: {key_str}",
            f"성공(보물 획득): {self.wins} | 실패(용암): {self.losses}",
            "단축키 - [T] 학습 On/Off  [A] 데모 On/Off  [D] 재시작"
        ]

        for i, txt in enumerate(texts):
            rendered = self.font_b.render(txt, True, BLACK) if i == 0 else self.font_m.render(txt, True, DARK_GRAY)
            panel.blit(rendered, (15, 15 + i * 30))

        self.screen.blit(panel, (0, BOARD_WIDTH))

    def run(self):
        while True:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.training = not self.training
                    elif event.key == pygame.K_a:
                        self.auto_play = not self.auto_play
                    elif event.key == pygame.K_d:
                        self.start_new_demo()

            if self.training:
                for _ in range(TRAIN_EPISODES_PER_FRAME):
                    self._train_one()
                if now - self.last_step_t > self.step_delay:
                    if self.demo_done:
                        self.start_new_demo()
                    else:
                        self.run_demo_step()
                    self.last_step_t = now
            else:
                if self.auto_play and now - self.last_step_t > self.step_delay:
                    if self.demo_done:
                        self.start_new_demo()
                    else:
                        self.run_demo_step()
                    self.last_step_t = now

            self.env.render(self.screen)
            self.draw_panel()
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    GameApp().run()