import src.server as server
import sys
from env import * 

def main():
    server.start(int(PORT))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Application finished (Keyboard Interrupt)")
        sys.exit("Manually Interrupted")
    except Exception as e:
        print(e)
        print("Oh no, something bad happened! Restarting...")
        sys.exit("Manually Interrupted")
