from racer import RacerGame


def main():
    #main file is only the launcher. All game logic is inside racer.py
    game = RacerGame()
    game.run()


if __name__ == "__main__":
    #this makes sure the game starts only when we run main.py directly
    main()
