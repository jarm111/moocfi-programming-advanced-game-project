import pygame

# CONSTANTS
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60
GAME_TITLE = "Hot Coins"
BACKGROUND_COLOR = (100, 100, 200)
PLAYER_SPEED = 3
FOE_SPEED = 1
IMAGES = {
            "robot": "robo.png",
            "door": "ovi.png",
            "coin": "kolikko.png",
            "foe": "hirvio.png"
        }


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    
    def tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

class Renderable:
    def __init__(self, image: pygame.Surface, starting_pos: Point) -> None:
        self.image = image
        self.position = starting_pos
        self.width = image.get_width()
        self.height = image.get_height()

    @property
    def x(self):
        return self.position.x
    
    @property
    def y(self):
        return self.position.y
    
    @x.setter
    def x(self, value):
        self.position = Point(value, self.position.y)

    @y.setter
    def y(self, value):
        self.position = Point(self.position.x, value)

class Player(Renderable):
    def __init__(self, image: pygame.Surface, starting_pos: Point, speed: int, ) -> None:
        super().__init__(image, starting_pos)
        self.speed = speed

    def move(self, pos: Point, edges: Point) -> None:
        edgex, edgey = edges.tuple()
        x, y = pos.tuple()
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
    def __init__(self, image: pygame.Surface, starting_pos: Point, speed: int) -> None:
        super().__init__(image, starting_pos)
        self.speed = speed
        self.direction = "se"

    def move(self, edges: Point) -> None:
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

    def __is_edge(self, edges: Point):
        x, y, width, height = self.x, self.y, self.width, self.height
        edgex, edgey = edges.tuple()
        return x < 0 or y < 0 or y + height >= edgey or x + width >= edgex

class Game:
    def __init__(self, display_width: int, display_height: int) -> None:
        pygame.init()

        self.display_width = display_width
        self.display_height = display_height
        self.display = pygame.display.set_mode(((self.display_width, self.display_height)))

        pygame.display.set_caption(GAME_TITLE)

        self.clock = pygame.time.Clock()

        self.images = self.load_images()

        self.player = Player(self.images["robot"], Point(0, 0), 3)

        self.foe = Foe(self.images["foe"], Point(300, 200), 1)

        self.coin = Renderable(self.images["coin"], Point(400, 100))

        self.door = Renderable(self.images["door"], Point(320, 240))

        self.mouse_pos = Point(0, 0)

        self.game_loop()

    def check_events(self) -> None:
        for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()
                if tapahtuma.type == pygame.MOUSEMOTION:
                    self.mouse_pos = Point(*tapahtuma.pos)

    def render(self) -> None:
        self.display.fill(BACKGROUND_COLOR)
        for item in [self.player, self.foe, self.coin, self.door]:
            image, pos = item.image, (item.x, item.y)
            self.display.blit(image, pos)
        pygame.display.flip()

    def game_loop(self) -> None:
        edges = Point(self.display_width, self.display_height)
        while True:
           self.check_events()
           self.player.move(self.mouse_pos, edges)
           self.foe.move(edges)
           self.render()
           self.clock.tick(FPS)

    def load_images(self) -> dict[str, pygame.Surface]:
        return {name: pygame.image.load(path) for (name, path) in IMAGES.items()}

def main():
    Game(WINDOW_WIDTH, WINDOW_HEIGHT)

if __name__ == "__main__":
    main()
