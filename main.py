# ============================================================
# file: main.py
# 프로그램 진입점 – 실행 시 CLI + GUI 동시 가동
# ============================================================

import threading

def _run_cli():
    """텍스트 기반(TUI) 인터페이스를 별도 스레드에서 실행"""
    from ui import UserInterface
    UserInterface().run()                 # 블로킹 루프

def _run_gui():
    """Tkinter GUI는 메인 스레드에서 실행 (Tk 제약 만족)"""
    from gui import GUIInterface
    GUIInterface()                        # 내부에서 mainloop() 호출

if __name__ == "__main__":
    # 1) CLI(TUI) 스레드 시작 ─ 데몬으로 두어 GUI 창이 닫히면 함께 종료
    cli_thread = threading.Thread(
        target=_run_cli,
        name="CLIThread",
        daemon=True     # 메인(=GUI) 종료 시 자동 정리
    )
    cli_thread.start()

    # 2) 메인 스레드에서 GUI 실행
    _run_gui()

    # GUI 창을 닫고 나면 여기 도달 → 데몬 스레드도 함께 종료됨
