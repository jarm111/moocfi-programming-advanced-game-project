import pygame

class Game:
    def __init__(self, display_width: int, display_height: int) -> None:
        pygame.init()

        self.display_width = display_width
        self.display_height = display_height
        self.display = pygame.display.set_mode(((self.display_width, self.display_height)))

        pygame.display.set_caption("Robo Rush")

        self.clock = pygame.time.Clock()

        self.game_loop()

    def check_events(self) -> None:
        for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()

    def render(self) -> None:
        self.display.fill((0, 0, 0))
        pygame.display.flip()


    def game_loop(self) -> None:
        while True:
           self.check_events()
           self.render()
           self.clock.tick(60)

def main():
    print("Hello from moocfi-programming-advanced-game-project!")
    Game(640, 480)


if __name__ == "__main__":
    main()
