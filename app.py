import os
import gradio as gr
from env import DungeonEnv
from rl_agent import QLearningAgent

# 1. 환경 및 에이전트 초기화
env = DungeonEnv()
agent = QLearningAgent()


def train_agent(episodes):
    """지정된 에피소드만큼 Q-Learning 에이전트를 학습시킵니다."""
    try:
        episodes = int(episodes)
    except ValueError:
        return "에피소드 수는 숫자여야 합니다.", "학습 실패"

    wins = 0
    losses = 0

    for _ in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = agent.select_action(state)
            next_state, reward, done = env.step(action)
            agent.learn(state, action, reward, next_state, done)
            state = next_state

            if done:
                if reward > 100:
                    wins += 1
                elif reward < -100:
                    losses += 1

    result_text = f"✅ {episodes}번의 학습 완료!\n\n현재 누적 승리(보물): {wins}\n현재 누적 패배(용암): {losses}\n현재 탐험도(Epsilon): {agent.epsilon:.4f}"
    return result_text, "학습 완료. 이제 '데모 실행'을 눌러보세요!"


def run_demo():
    """학습된 에이전트가 한 판을 어떻게 플레이하는지 텍스트 로그로 보여줍니다."""
    state = env.reset()
    done = False
    log = []

    # 시작 상태 기록
    key_idx = state[1]
    key_pos = env.key_spawns[key_idx]
    log.append(f"🏁 게임 시작! 기사 위치: {state[0]}, 목표 열쇠 위치: {key_pos}")

    step_count = 0
    while not done and step_count < 100:  # 무한 루프 방지
        step_count += 1

        # 탐험 없이 최고 가치의 행동만 선택 (데모 모드)
        action = agent.best_action(state)
        action_names = {0: "UP", 1: "DOWN", 2: "LEFT", 3: "RIGHT", 4: "STAY"}

        next_state, reward, done = env.step(action)

        # 상태 기록
        has_key_str = "🔑 (열쇠 보유)" if next_state[2] else "❌ (열쇠 없음)"
        log.append(
            f"Step {step_count}: 행동 [{action_names[action]}] -> 이동: {next_state[0]} | 상태: {has_key_str} | 보상: {reward}")

        state = next_state

        if done:
            if reward > 100:
                log.append("🎉 성공! 보물을 찾았습니다!")
            else:
                log.append("💀 실패! 용암에 빠지거나 턴이 다 되었습니다.")

    return "\n".join(log)


# 2. Gradio 웹 인터페이스 구성
with gr.Blocks(title="RL Dungeon Explorer") as demo:
    gr.Markdown("# 🛡️ 강화학습(Q-Learning) 던전 탐험 봇")
    gr.Markdown("기사가 열쇠를 찾아 보물상자를 여는 훈련을 시켜보세요! (Pygame 코드를 웹용 텍스트 로그로 변환한 버전입니다.)")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 1단계: 에이전트 학습시키기")
            episode_input = gr.Number(value=1000, label="학습할 에피소드 수 (예: 1000)")
            train_btn = gr.Button("🧠 학습 시작", variant="primary")
            train_output = gr.Textbox(label="학습 결과 요약", lines=5)

        with gr.Column():
            gr.Markdown("### 2단계: 데모 플레이 보기")
            demo_btn = gr.Button("▶️ 1판 데모 실행", variant="secondary")
            demo_status = gr.Textbox(label="상태 메시지")
            demo_log = gr.Textbox(label="게임 진행 로그", lines=15)

    # 버튼 클릭 시 함수 연결
    train_btn.click(fn=train_agent, inputs=episode_input, outputs=[train_output, demo_status])
    demo_btn.click(fn=run_demo, inputs=None, outputs=demo_log)


def main():
    # Render 등 클라우드 배포 환경의 포트 설정
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port
    )


if __name__ == "__main__":
    main()