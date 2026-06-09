from .worker import run_bridge_loop

if __name__ == "__main__":
    try:
        run_bridge_loop()
    except KeyboardInterrupt:
        print("\n[Playwright] Stopped.")
