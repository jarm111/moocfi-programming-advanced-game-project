import pygame

class Renderable:
    def __init__(self, image: pygame.Surface, starting_pos: tuple[int, int]) -> None:
        self.image = image
        self.x = starting_pos[0]
        self.y = starting_pos[1]
        self.width = image.get_width()
        self.height = image.get_height()

class Player(Renderable):
    def __init__(self, image: pygame.Surface, starting_pos: tuple[int, int], speed: int, ) -> None:
        super().__init__(image, starting_pos)
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

class Foe(Renderable):
    def __init__(self, image: pygame.Surface, starting_pos: tuple[int, int], speed: int) -> None:
        super().__init__(image, starting_pos)
        self.speed = speed
        self.direction = "se"

    def move(self, edges: tuple[int, int]) -> None:
        if self.__is_edge(edges):
            self.__change_direction()
        if self.direction == "ne":
            self.x += self.speed
            self.y -= self.speed
        if self.direction == "se":
            self.x += self.speed
            self.y += self.speed
        if self.direction == "sw":
            self.x -= self.speed
            self.y += self.speed
        if self.direction == "nw":
            self.x -= self.speed
            self.y -= self.speed

    def __change_direction(self):
        if self.direction == "ne":
            self.direction = "se"
        elif self.direction == "se":
            self.direction = "sw"
        elif self.direction == "sw":
            self.direction = "nw"
        else:
            self.direction = "ne"

    def __is_edge(self, edges: tuple[int, int]):
        x, y, width, height = self.x, self.y, self.width, self.height
        edgex, edgey = edges
        return x < 0 or y < 0 or y + height >= edgey or x + width >= edgex

class Game:
    def __init__(self, display_width: int, display_height: int) -> None:
        pygame.init()

        self.display_width = display_width
        self.display_height = display_height
        self.display = pygame.display.set_mode(((self.display_width, self.display_height)))

        pygame.display.set_caption("Robo Rush")

        self.clock = pygame.time.Clock()

        self.images = self.load_images()

        self.player = Player(self.images["robot"], (0, 0), 3)

        self.foe = Foe(self.images["foe"], (300, 200), 1)

        self.coin = Renderable(self.images["coin"], (400, 100))

        self.door = Renderable(self.images["door"], (320, 240))

        self.mouse_pos = (0, 0)

        self.game_loop()

    def check_events(self) -> None:
        for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()
                if tapahtuma.type == pygame.MOUSEMOTION:
                    self.mouse_pos = tapahtuma.pos

    def render(self) -> None:
        self.display.fill((100, 100, 200))
        for item in [self.player, self.foe, self.coin, self.door]:
            image, pos = item.image, (item.x, item.y)
            self.display.blit(image, pos)
        pygame.display.flip()

    def game_loop(self) -> None:
        edges = (self.display_width, self.display_height)
        while True:
           self.check_events()
           self.player.move(self.mouse_pos, edges)
           self.foe.move(edges)
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
