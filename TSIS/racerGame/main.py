from racer import RacerGame


def main():
    # Main file is only the launcher. All game logic is inside racer.py
    game = RacerGame()
    game.run()


if __name__ == "__main__":
    # This makes sure the game starts only when we run main.py directly
    main()
