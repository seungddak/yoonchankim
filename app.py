import os
import gradio as gr  # Gradio를 사용 중이라고 가정했습니다.


def greet(name):
    return "Hello " + name + "!"


def main():
    # 복잡한 Container 대신 아주 단순한 앱 구조로 테스트합니다.
    app = gr.Interface(fn=greet, inputs="text", outputs="text")

    port = int(os.environ.get("PORT", 7860))
    app.launch(
        server_name="0.0.0.0",
        server_port=port
    )


if __name__ == "__main__":
    main()