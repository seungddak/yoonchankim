import os
import time

# 1. [Render 서버용 오류 해결] 모니터/스피커가 없는 서버 환경을 위한 가짜 드라이버 선언
# 반드시 pygame을 import 하기 전에 실행되어야 합니다.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import random
import pygame
import gradio as gr

# Pygame 초기화 (가짜 드라이버 위에서 안전하게 작동)
pygame.init()

class WebDungeonGame:
    def __init__(self):
        # 던전 맵 설정 (0: 빈칸, 1: 벽, 2: 용암, 3: 열쇠, 4: 탈출구)
        self.grid = [
            [0, 0, 1, 0, 4],
            [0, 1, 0, 0, 0],
            [0, 0, 2, 1, 0],
            [1, 0, 0, 2, 0],
            [3, 0, 1, 0, 0]
        ]
        self.rows = 5
        self.cols = 5
        
        # Q-러닝 알고리즘 하이퍼파라미터
        self.actions = [0, 1, 2, 3] # 0:상, 1:하, 2:좌, 3:우
        self.q_table = {}
        self.alpha = 0.1   # 학습률
        self.gamma = 0.9   # 할인율
        self.epsilon = 0.2 # 탐험률
        
        self.total_episodes = 0
        
        # 2. [Render 서버용 오류 해결] 초기 학습 횟수 대폭 축소 (100회 -> 2회)
        # 무료 서버의 사양 한계로 인한 초기 부팅 타임아웃(Port scan timeout)을 방지합니다.
        for _ in range(2):
            self.train_one()

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state, v_epsilon=None):
        if v_epsilon is None:
            v_epsilon = self.epsilon
        if random.random() < v_epsilon:
            return random.choice(self.actions)
        
        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(self.actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def step(self, state, action):
        r, c, has_key = state
        nr, nc = r, c
        
        if action == 0: nr = max(0, r - 1)
        elif action == 1: nr = min(self.rows - 1, r + 1)
        elif action == 2: nc = max(0, c - 1)
        elif action == 3: nc = min(self.cols - 1, c + 1)
        
        # 벽에 부딪힌 경우 제자리
        if self.grid[nr][nc] == 1:
            nr, nc = r, c
            
        next_has_key = has_key
        if self.grid[nr][nc] == 3:
            next_has_key = 1
            
        next_state = (nr, nc, next_has_key)
        
        # 보상 설계
        cell = self.grid[nr][nc]
        if cell == 2:  # 용암
            reward = -100
            done = True
        elif cell == 4:  # 탈출구
            if next_has_key == 1:
                reward = 150
                done = True
            else:
                reward = -10  # 열쇠 없이 탈출구 가면 감점 후 계속 진행
                done = False
        elif cell == 3 and has_key == 0:  # 열쇠 획득
            reward = 50
            done = False
        else:
            reward = -1  # 한 걸음 걸을 때마다 가벼운 패널티
            done = False
            
        return next_state, reward, done

    def train_one(self):
        # 에피소드 시작 상태: (0, 0) 위치, 열쇠 없음(0)
        state = (0, 0, 0)
        done = False
        steps = 0
        
        while not done and steps < 200:
            action = self.choose_action(state)
            next_state, reward, done = self.step(state, action)
            
            # Q-값 업데이트
            max_next_q = max([self.get_q(next_state, a) for a in self.actions])
            old_q = self.get_q(state, action)
            self.q_table[(state, action)] = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)
            
            state = next_state
            steps += 1
            
        self.total_episodes += 1

    def train_multiple(self, amount):
        for _ in range(int(amount)):
            self.train_one()
        return f"현재 학습 판수: {self.total_episodes}판 완료!"

    def draw_dungeon(self, current_state):
        # Pygame을 활용한 가상 화면 렌더링 후 이미지 저장
        cell_size = 80
        width = self.cols * cell_size
        height = self.rows * cell_size
        
        surface = pygame.Surface((width, height))
        surface.fill((240, 240, 240)) # 배경 바탕색
        
        # 격자판 그리기
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                cell_type = self.grid[r][c]
                
                if cell_type == 1: # 벽
                    pygame.draw.rect(surface, (70, 70, 70), rect)
                elif cell_type == 2: # 용암
                    pygame.draw.rect(surface, (230, 50, 50), rect)
                elif cell_type == 3: # 열쇠
                    pygame.draw.rect(surface, (230, 210, 50), rect)
                elif cell_type == 4: # 탈출구
                    pygame.draw.rect(surface, (50, 180, 50), rect)
                    
                pygame.draw.rect(surface, (200, 200, 200), rect, 1)
                
        # 인공지능 에이전트 그리기 (파란색 원)
        ar, ac, a_key = current_state
        agent_center = (ac * cell_size + cell_size // 2, ar * cell_size + cell_size // 2)
        pygame.draw.circle(surface, (50, 100, 230), agent_center, cell_size // 3)
        
        # 열쇠를 소지했다면 에이전트 안에 조그만 노란색 원 추가 표시
        if a_key == 1:
            pygame.draw.circle(surface, (250, 250, 250), agent_center, cell_size // 6)
            
        img_path = "dungeon_state.png"
        pygame.image.save(surface, img_path)
        return img_path

    # 3. [기능 개선] 인공지능의 자율 주행 데모를 사람이 볼 수 있게 천천히 실시간 재생(yield)
    def run_full_demo(self):
        state = (0, 0, 0)
        done = False
        steps = 0
        
        # 첫 시작 화면 전송
        yield self.draw_dungeon(state), f"데모 시작! 현재 위치: {state[:2]} (걸음수: {steps})"
        time.sleep(0.4) # 시작 전 잠깐 대기
        
        while not done and steps < 50:
            # 학습 모드가 아니므로 탐험률(epsilon)을 0으로 만들어 최선의 길 선택
            action = self.choose_action(state, v_epsilon=0.0)
            state, _, done = self.step(state, action)
            steps += 1
            
            # 던전 화면 갱신
            img = self.draw_dungeon(state)
            status_text = f"🤖 AI 탐험 중... 위치: {state[:2]} | 열쇠 소지: {'O' if state[2]==1 else 'X'} (걸음수: {steps})"
            
            if done:
                if self.grid[state[0]][state[1]] == 4 and state[2] == 1:
                    status_text = f"🎉 탈출 성공! 총 {steps}걸음 만에 보물을 찾아 나갔습니다!"
                else:
                    status_text = f"💀 용암에 빠졌습니다! 다음 판엔 더 잘하겠죠? (총 {steps}걸음)"
            
            # Gradio 화면으로 실시간 전송
            yield img, status_text
            
            # ⏱️ 한 걸음 걸을 때마다 0.4초씩 쉬어 가도록 세팅 (더 느리게 보고 싶다면 0.6 등으로 키우세요)
            time.sleep(0.4)

# 글로벌 게임 인스턴스 생성
game = WebDungeonGame()

# 4. Gradio 웹 인터페이스 블록 설계
with gr.Blocks(title="Q-Learning AI Dungeon") as demo:
    gr.Markdown("## 🧠 Q-Learning 인공지능 던전 탐험대 웹 데모")
    gr.Markdown("파란색 인공지능 에이전트가 스스로 최적의 경로를 공부하여 노란색 열쇠를 얻고 초록색 탈출구로 나가는 시뮬레이터입니다.")
    
    with gr.Row():
        with gr.Column(scale=1):
            status_output = gr.Textbox(value=f"현재 학습 판수: {game.total_episodes}판 완료!", label="학습 상태 및 안내")
            train_slider = gr.Slider(minimum=100, maximum=10000, step=100, value=1000, label="추가로 학습시킬 횟수 (판)")
            train_btn = gr.Button("🧠 선택한 만큼 추가 학습 시작", variant="primary")
            demo_btn = gr.Button("🎬 데모 한 판 끝까지 보기 (실시간 재생)", variant="secondary")
            
        with gr.Column(scale=1):
            image_output = gr.Image(value=game.draw_dungeon((0,0,0)), label="던전 실시간 맵 화면", type="filepath")

    # 버튼 이벤트 바인딩
    train_btn.click(
        fn=game.train_multiple,
        inputs=train_slider,
        outputs=status_output
    ).then(
        fn=lambda: game.draw_dungeon((0,0,0)),
        outputs=image_output
    )
    
    demo_btn.click(
        fn=game.run_full_demo,
        outputs=[image_output, status_output]
    )

# 5. [Render 서버용 오류 해결] 포트 포워딩 및 외부 바인딩 완전 차단 우회 설정
if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Render 외부 배포 엔진 가동 - 포트: {server_port}")
    
    demo.queue().launch(
        server_name="0.0.0.0", 
        server_port=server_port,
        share=True
    )
