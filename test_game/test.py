from engine.GameInstance import GameInstance
import yaml


if __name__ == "__main__":
    config = {}

    with open('config.yml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    game = GameInstance(config)
    game.run()