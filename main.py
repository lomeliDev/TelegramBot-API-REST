import src.server as server


def main():
    server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Application finished (Keyboard Interrupt)")
        sys.exit("Manually Interrupted")
    except Exception:
        print("Oh no, something bad happened! Restarting...")
        sys.exit("Manually Interrupted")
