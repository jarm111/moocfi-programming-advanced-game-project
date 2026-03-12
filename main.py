import pygame
from random import randrange

# CONSTANTS
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60
GAME_TITLE = "Hot Coins"
BACKGROUND_COLOR = (100, 100, 200)
PLAYER_SPEED = 3
FOE_SPEED = 1
COIN_SAFE_ZONE = 70
FOE_SAFE_ZONE = 140
COIN_PROGRESSION_PACE = 2
FOE_PROGRESSION_PACE = 3
IMAGES = {
            "robot": "robo.png",
            "door": "ovi.png",
            "coin": "kolikko.png",
            "foe": "hirvio.png"
        }


class Point:
    def __init__(self, x: int , y: int) -> None:
        self.x = x
        self.y = y
    
    def tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

class Counter:
    def __init__(self, initial_value: int) -> None:
        self.__value = initial_value
        self.__initial_value = initial_value
    
    @property
    def value(self) -> int:
        return self.__value
    
    def increment(self) -> None:
        self.__value += 1

    def reset(self) -> None:
        self.__value = self.__initial_value

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

class Level:
    def __init__(self, display: pygame.Surface, images: dict[str, pygame.Surface], clock: pygame.time.Clock, end_of_level_handler, number_of_coins: int, number_of_foes: int) -> None:
        self.display = display
        self.images = images
        self.clock = clock

        player, door, coins, foes = self.spawn(number_of_coins, number_of_foes)
        self.player = player
        self.door = door
        self.coins = coins
        self.foes = foes

        self.mouse_pos = Point(0, 0)
        self.end_of_level_handler = end_of_level_handler
        self.game_loop()

    def handle_collisions(self) -> None:
        def detect(a: Renderable, b: Renderable) -> bool:
            return (a.x < b.x + b.width and
                    a.x + a.width > b.x and
                    a.y < b.y + b.height and
                    a.y + a.height > b.y)
        
        for i, coin in enumerate(self.coins):
            if detect(self.player, coin):
                self.coins.pop(i)

        for foe in self.foes:
            if detect(self.player, foe):
                self.game_over()
        
        if detect(self.player, self.door):
            self.enter_door()

    def check_events(self) -> None:
        for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()
                if tapahtuma.type == pygame.MOUSEMOTION:
                    self.mouse_pos = Point(*tapahtuma.pos)

    def render(self) -> None:
        self.display.fill(BACKGROUND_COLOR)
        for item in [self.door, *self.coins, *self.foes, self.player]:
            image, pos = item.image, (item.x, item.y)
            self.display.blit(image, pos)
        pygame.display.flip()

    def game_loop(self) -> None:
        edges = Point(self.display.get_width(), self.display.get_height())
        while True:
           self.handle_collisions()
           self.check_events()
           self.player.move(self.mouse_pos, edges)
           for foe in self.foes:
               foe.move(edges)
           self.render()
           self.clock.tick(FPS)

    def coins_remaining(self):
        return len(self.coins)

    def pick_up_coin(self, coin_index: int):
        self.coins.pop(coin_index)

    def enter_door(self):
        if self.coins_remaining() == 0:
            self.end_of_level_handler("next_level")
    
    def game_over(self):
        self.end_of_level_handler("game_over")

    def spawn(self, coin_amount:int, foe_amount:int) -> tuple[Player, Renderable, list[Renderable], list[Foe]]:
        player_location = Point(self.display.get_width() // 2 - self.images["robot"].get_width() // 2, self.display.get_height() // 2  - self.images["robot"].get_height() // 2)
        door_location = Point(self.display.get_width() // 2 - self.images["door"].get_width() // 2, self.display.get_height() // 2  - self.images["door"].get_height() // 2)
        coin_locations = self.generate_spawn_locations(coin_amount, self.images["coin"].get_width(), self.images["coin"].get_height(), COIN_SAFE_ZONE)
        foe_locations = self.generate_spawn_locations(foe_amount, self.images["foe"].get_width(), self.images["foe"].get_height(), FOE_SAFE_ZONE)
        player = Player(self.images["robot"], player_location, 3)
        door = Renderable(self.images["door"], door_location)
        coins = [Renderable(self.images["coin"], location) for location in coin_locations]
        foes = [Foe(self.images["foe"], location, FOE_SPEED) for location in foe_locations]
        return (player, door, coins, foes)
    
    def generate_spawn_locations(self, amount: int, gridx: int, gridy:int, safe_zone: int) -> list[Point]:
        mid = Point(self.display.get_width() // 2, self.display.get_height() // 2)
        locations: list[Point] = []
        for n in range(amount):
            while True:
                location = Point(randrange(0, self.display.get_width() - gridx, gridx), randrange(0, self.display.get_height() - gridy, gridy))
                if location not in locations or location.x not in range(mid.x - safe_zone, mid.x + safe_zone) and location.y not in range(mid.y - safe_zone, mid.y + safe_zone):
                    locations.append(location)
                    break
        return locations

class Game:
    def __init__(self, display_width: int, display_height: int) -> None:
        pygame.init()
        self.display = pygame.display.set_mode(((display_width, display_height)))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.images = self.load_images()
        self.levelcount = Counter(1)
        self.level = self.end_of_level_handler("next_level")

    def load_images(self) -> dict[str, pygame.Surface]:
        return {name: pygame.image.load(path) for (name, path) in IMAGES.items()}
    
    def end_of_level_handler(self, condition: str):

        if condition == "next_level":
            self.levelcount.increment()
            self.level = Level(self.display, self.images, self.clock, self.end_of_level_handler, *self.level_progression())
        elif condition == "game_over":
            self.levelcount.reset()
            self.level = Level(self.display, self.images, self.clock, self.end_of_level_handler, *self.level_progression())

    def level_progression(self) -> tuple[int, int]:
        coins = 1 + self.levelcount.value // 2
        foes = 1 + self.levelcount.value // 3
        print(self.levelcount.value)
        return (coins, foes)

def main():
    Game(WINDOW_WIDTH, WINDOW_HEIGHT)

if __name__ == "__main__":
    main()
