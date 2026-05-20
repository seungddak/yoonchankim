다른 부분은 전혀 건드리지 않고, 오직 **'▶️ 데모 한 판 끝까지 보기'** 버튼을 눌렀을 때만 한 걸음씩 실시간으로 화면이 갱신되면서 천천히 움직이도록 수정했습니다.

이를 위해 코드 최상단에 시간 지연을 위한 `import time`을 추가하고, `do_episode` 함수를 Gradio의 실시간 애니메이션 기능(`yield`)에 맞춰 변형했습니다.

아래의 전체 코드를 복사해서 기존 `app.py`에 그대로 덮어쓰기 해주시면 됩니다!

```python
import os
import time  # ⏱️ 천천히 보여주기 위해 time 모듈 추가

# 🛠️ [중요] Render 서버(화면/스피커 없음)를 위한 가짜 드라이버 설정
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import random
import pygame
import gradio as gr
from PIL import Image

# 기존에 작성하신 파일들 임포트 (수정 없이 그대로 사용!)
from env import DungeonEnv
from rl_agent import QLearningAgent
from settings import *

# Pygame 초기화 (화면은 안 뜨지만 내부적으로 엔진이 돌아감)
pygame.init()


class WebDungeonGame:
    def __init__(self):
        self.env = DungeonEnv()
        self.agent = QLearningAgent()
        self.episode = 0
        self.wins = 0
        self.losses = 0
        self.recent_results = []
        self.demo_done = False
        self.last_result = "READY"
        self.last_action = 4
        self.step_count = 0

        # 서버 시작 시 기본 학습 100번 진행 (친구 코드 아이디어)
        for _ in range(100):
            self.train_one()
        self.start_new_demo()

    def train_one(self):
        state = self.env._get_state() if hasattr(self.env, '_get_state') else self.env.reset()
        # 혹시 기존 env.reset()이 상태를 반환하지 않는 경우를 대비해 안전하게 처리
        init_state = self.env.reset()
        state = init_state if init_state is not None else self.env._get_state()
        
        done = False
        result_type = "unknown"

        while not done:
            action = self.agent.select_action(state)
            next_state, reward, done = self.env.step(action)
            self.agent.learn(state, action, reward, next_state, done)
            state = next_state

            if done:
                if reward > 100:
                    self.wins += 1
                    self.recent_results.append(1)
                    result_type = "escaped"
                else:
                    self.losses += 1
                    self.recent_results.append(0)
                    result_type = "died"

        self.episode += 1
        if self.agent.epsilon > self.agent.epsilon_min:
            self.agent.epsilon *= self.agent.epsilon_decay

        if len(self.recent_results) > 100:
            self.recent_results.pop(0)

    def train_many(self, n):
        for _ in range(int(n)):
            self.train_one()

    def start_new_demo(self):
        self.env.reset()
        self.demo_done = False
        self.last_result = "RUNNING"
        self.last_action = 4
        self.step_count = 0

    def run_demo_step(self):
        if self.demo_done:
            return

        state = self.env._get_state()
        # 데모 모드에서는 탐험(랜덤) 없이 최고 가치의 행동만 수행
        self.last_action = self.agent.best_action(state)

        _, reward, done = self.env.step(self.last_action)
        self.demo_done = done
        self.step_count += 1

        if done:
            if reward > 100:
                self.last_result = "SUCCESS 🏆 (보물 획득)"
            else:
                self.last_result = "FAILED 💀 (용암/시간초과)"

    def run_demo_episode(self):
        if self.demo_done:
            self.start_new_demo()
        while not self.demo_done:
            self.run_demo_step()

    def render_pygame_to_pil(self):
        # 1. 화면 대신 메모리에 Pygame 도화지(Surface) 생성
        surface = pygame.Surface((BOARD_WIDTH, BOARD_WIDTH))

        # 2. 여러분이 짠 기존 Pygame 그리기 함수를 그대로 호출!
        self.env.render(surface)

        # 3. Pygame 도화지를 웹에서 볼 수 있는 이미지로 찰칵! 캡처
        string_image = pygame.image.tostring(surface, "RGB")
        img = Image.frombytes("RGB", (BOARD_WIDTH, BOARD_WIDTH), string_image)
        return img

    def get_markdown_info(self):
        total = max(self.wins + self.losses, 1)
        recent_win_rate = (sum(self.recent_results) / max(len(self.recent_results), 1)) * 100
        total_win_rate = (self.wins / total) * 100

        return (
            f"### 📊 기사 훈련 상태\n"
            f"- **학습 에피소드:** {self.episode:,} 판\n"
            f"- **보물 획득(승) / 용암 빠짐(패):** {self.wins:,} / {self.losses:,}\n"
            f"- **전체 성공률:** {total_win_rate:.1f}% | **최근 100판 성공률:** {recent_win_rate:.1f}%\n"
            f"---\n"
            f"### 🎮 현재 데모 상황\n"
            f"- **진행 상태:** {self.last_result}\n"
            f"- **이동 스텝 수:** {self.step_count} / {MAX_STEPS}\n"
            f"- **열쇠 보유 여부:** {'🔑 있음' if self.env.has_key else '❌ 없음'}\n"
            f"- **에이전트 Epsilon (탐험률):** {self.agent.epsilon:.4f}"
        )


# Gradio 인터페이스 함수들
def output(game):
    return game, game.render_pygame_to_pil(), game.get_markdown_info()


def init_game():
    return output(WebDungeonGame())


def train_agent(game, episodes):
    if game is None: game = WebDungeonGame()
    game.train_many(episodes)
    return output(game)


def do_step(game):
    if game is None: game = WebDungeonGame()
    if game.demo_done:
        game.start_new_demo()
    else:
        game.run_demo_step()
    return output(game)


# 🛠️ [수정 부분] 데모 한 판 보기 버튼을 누를 때만 화면을 실시간으로 천천히 업데이트
def do_episode(game):
    if game is None: game = WebDungeonGame()
    
    # 이미 끝난 상태라면 새 데모를 시작하고 첫 화면을 바로 보여줌
    if game.demo_done:
        game.start_new_demo()
        yield output(game)
        time.sleep(0.25)
    
    # 게임이 끝날 때까지 한 걸음 걸을 때마다 웹 화면으로 전송(yield)하고 대기(sleep)
    while not game.demo_done:
        game.run_demo_step()
        yield output(game)
        time.sleep(0.25)  # ⏱️ 0.25초마다 움직입니다. 속도를 더 늦추려면 이 숫자를 키우세요!


def do_reset(game):
    if game is None: game = WebDungeonGame()
    game.start_new_demo()
    return output(game)


# 웹 페이지 화면 구성
with gr.Blocks(title="Pygame RL Dungeon") as demo:
    gr.Markdown("# 🛡️ Q-Learning 던전 탐험 (Pygame 원본 유지 버전!)")

    state = gr.State(None)

    with gr.Row():
        # Pygame 화면이 렌더링될 자리
        game_screen = gr.Image(label="Pygame Screen", type="pil", height=600)
        info_panel = gr.Markdown()

    with gr.Row():
        episodes_slider = gr.Slider(10, 1000, value=100, step=10, label="추가 학습 에피소드 수")
        train_btn = gr.Button("🧠 선택한 만큼 학습", variant="primary")

    with gr.Row():
        step_btn = gr.Button("👣 데모 한 스텝씩 보기")
        episode_btn = gr.Button("▶️ 데모 한 판 끝까지 보기")
        reset_btn = gr.Button("🔄 새 데모 시작")

    demo.load(init_game, inputs=None, outputs=[state, game_screen, info_panel])
    train_btn.click(train_agent, inputs=[state, episodes_slider], outputs=[state, game_screen, info_panel])
    step_btn.click(do_step, inputs=state, outputs=[state, game_screen, info_panel])
    episode_btn.click(do_episode, inputs=state, outputs=[state, game_screen, info_panel])
    reset_btn.click(do_reset, inputs=state, outputs=[state, game_screen, info_panel])

# 🛠️ Render 서버용 맞춤 실행부 설정
if __name__ == "__main__":
    # Render가 주는 PORT 값을 안전하게 숫자로 가져옵니다. (기본값 10000)
    server_port = int(os.environ.get("PORT", 10000))
    
    print(f"🚀 Render 배포 시작 - 포트 번호: {server_port}")
    
    # 대기열(queue)을 활성화한 후 외부 접속(0.0.0.0)이 가능하도록 문을 열어줍니다.
    demo.queue().launch(
        server_name="0.0.0.0", 
        server_port=server_port,
        share=True
    )

```
