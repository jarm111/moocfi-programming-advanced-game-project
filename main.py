import pygame

class Player:
    def __init__(self, image: pygame.Surface, speed: int, starting_pos: tuple[int, int]) -> None:
        self.image = image
        self.x = starting_pos[0]
        self.y = starting_pos[1]
        self.width = image.get_width()
        self.height = image.get_height()
        self.speed = speed

    def move(self, pos: tuple[int, int], edges: tuple[int, int]) -> None:
        edgex, edgey = edges
        x, y = pos
        x = x - self.width / 2
        y = y - self.height / 2
        if self.x > x and self.x > 0:
            self.x -= self.speed
        if self.x < x and self.x < edgex - self.width:
            self.x += self.speed
        if self.y > y and self.y > 0:
            self.y -= self.speed
        if self.y < y and self.y < edgey - self.height:
            self.y += self.speed


class Game:
    def __init__(self, display_width: int, display_height: int) -> None:
        pygame.init()

        self.display_width = display_width
        self.display_height = display_height
        self.display = pygame.display.set_mode(((self.display_width, self.display_height)))

        pygame.display.set_caption("Robo Rush")

        self.clock = pygame.time.Clock()

        self.images = self.load_images()

        self.player = Player(self.images["robot"], 3, (0, 0))

        self.mouse_pos = (0, 0)

        self.game_loop()


    def check_events(self) -> None:
        for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()
                if tapahtuma.type == pygame.MOUSEMOTION:
                    self.mouse_pos = tapahtuma.pos

    def render(self) -> None:
        self.display.fill((0, 0, 0))
        self.display.blit(self.player.image, (self.player.x, self.player.y))
        pygame.display.flip()

    def game_loop(self) -> None:
        while True:
           self.check_events()
           self.player.move(self.mouse_pos, (self.display_width, self.display_height))
           self.render()
           self.clock.tick(60)

    def load_images(self) -> dict[str, pygame.Surface]:
        return {
            "robot": pygame.image.load("robo.png"),
            "door": pygame.image.load("ovi.png"),
            "coin": pygame.image.load("kolikko.png"),
            "foe": pygame.image.load("hirvio.png")
        }

def main():
    Game(640, 480)


if __name__ == "__main__":
    main()
