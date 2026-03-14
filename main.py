import pygame
from random import randrange

# CONSTANTS
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60
GAME_TITLE = "A PENNY FOR YOUR TIME"
BACKGROUND_COLOR = (100, 100, 200)
HUD_BG_COLOR = (0, 0, 0)
HUD_FONT_COLOR = (255, 255, 255)
HUD_HEIGHT = 30
HUD_FONT = "Arial"
HUD_FONT_SIZE = 20
LEVEL_TIME_LIMIT = 30
PLAYER_SPEED = 3
FOE_SPEED = 1
COIN_SAFE_ZONE = 70
FOE_SAFE_ZONE = 140
COIN_PROGRESSION_PACE = 2
FOE_PROGRESSION_PACE = 3
WAIT_TIME_BETWEEN_LEVELS = 1000
IMAGES = {
    "robot": "robo.png",
    "door": "ovi.png",
    "coin": "kolikko.png",
    "foe": "hirvio.png"
    }

# EVENTS
ONE_SECOND_TIMER_EVENT = pygame.USEREVENT + 1

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

    def decrement(self) -> None:
        if self.__value > 0:
            self.__value -= 1

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
        x = x - self.width // 2
        y = y - self.height // 2
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

class Hud:
    def __init__(self, display: pygame.Surface) -> None:
        self.display = display
        self.font = pygame.font.SysFont(HUD_FONT, HUD_FONT_SIZE)

    def draw(self, coins_remaining: int, time_remaining: int, levelcount: int, bestlevel: int):
        hud_text = f"Coins remaining: {coins_remaining}   Time remaining: {time_remaining}   Level: {levelcount}   Best Level: {bestlevel}"
        pygame.draw.rect(self.display, HUD_BG_COLOR, (0, WINDOW_HEIGHT - HUD_HEIGHT, WINDOW_WIDTH, HUD_HEIGHT))
        rendered_text = self.font.render(hud_text, True, HUD_FONT_COLOR)
        self.display.blit(rendered_text, (10, WINDOW_HEIGHT - HUD_HEIGHT + 3))

class Timer:
    # Interval in milliseconds
    def __init__(self, event: int, interval: int) -> None:
        self.event = event
        pygame.time.set_timer(event, interval)
    
    def disable(self):
        pygame.time.set_timer(self.event, 0)


class Level:
    def __init__(self, display: pygame.Surface, images: dict[str, pygame.Surface], clock: pygame.time.Clock, end_of_level_handler, number_of_coins: int, number_of_foes: int, levelcount: int, bestlevel: int) -> None:
        self.display = display
        self.images = images
        self.clock = clock

        self.hud = Hud(display)
        self.time_remaining = Counter(LEVEL_TIME_LIMIT)
        self.timer = Timer(ONE_SECOND_TIMER_EVENT, 1000)
        self.levelcount = levelcount
        self.bestlevel = bestlevel

        player, door, coins, foes = self.spawn(number_of_coins, number_of_foes)
        self.player = player
        self.door = door
        self.coins = coins
        self.foes = foes

        self.mouse_pos = Point(0, 0)
        self.end_of_level_handler = end_of_level_handler
        self.first_pass = True
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
                if tapahtuma.type == ONE_SECOND_TIMER_EVENT:
                    self.time_remaining.decrement()

    def check_time_remaining(self) -> None:
        if self.time_remaining.value == 0:
            self.game_over()

    def render(self) -> None:
        self.display.fill(BACKGROUND_COLOR)
        for item in [self.door, *self.coins, *self.foes, self.player]:
            image, pos = item.image, (item.x, item.y)
            self.display.blit(image, pos)
        self.hud.draw(self.coins_remaining(), self.time_remaining.value, self.levelcount, self.bestlevel)
        pygame.display.flip()

    def game_loop(self) -> None:
        edges = Point(self.display.get_width(), self.display.get_height() - HUD_HEIGHT)
        while True:
            self.handle_collisions()
            self.check_events()
            self.check_time_remaining()
            self.player.move(self.mouse_pos, edges)
            for foe in self.foes:
                foe.move(edges)
            self.render()
            if self.first_pass:
                self.wait()
                self.first_pass = False
            self.clock.tick(FPS)

    def coins_remaining(self):
        return len(self.coins)

    def pick_up_coin(self, coin_index: int):
        self.coins.pop(coin_index)

    def enter_door(self):
        if self.coins_remaining() == 0:
            self.end_of_level_handler("next_level")
    
    def game_over(self):
        self.timer.disable()
        self.wait()
        self.end_of_level_handler("game_over")

    def spawn(self, coin_amount:int, foe_amount:int) -> tuple[Player, Renderable, list[Renderable], list[Foe]]:
        player_location = Point(self.display.get_width() // 2 - self.images["robot"].get_width() // 2, (self.display.get_height() - HUD_HEIGHT) // 2  - self.images["robot"].get_height() // 2)
        door_location = Point(self.display.get_width() // 2 - self.images["door"].get_width() // 2, (self.display.get_height() - HUD_HEIGHT) // 2  - self.images["door"].get_height() // 2)
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
    
    def wait(self):
        pygame.time.wait(WAIT_TIME_BETWEEN_LEVELS)

class Game:
    def __init__(self, display_width: int, display_height: int) -> None:
        pygame.init()
        self.display = pygame.display.set_mode(((display_width, display_height)))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.images = self.load_images()
        self.levelcount = Counter(1)
        self.bestlevel = 1
        self.level = self.end_of_level_handler("next_level")

    def load_images(self) -> dict[str, pygame.Surface]:
        return {name: pygame.image.load(path) for (name, path) in IMAGES.items()}
    
    def end_of_level_handler(self, condition: str):

        if condition == "next_level":
            self.levelcount.increment()
            self.level = Level(self.display, self.images, self.clock, self.end_of_level_handler, *self.level_progression(), self.levelcount.value, self.bestlevel)
        elif condition == "game_over":
            self.define_best_level()
            self.levelcount.reset()
            self.level = Level(self.display, self.images, self.clock, self.end_of_level_handler, *self.level_progression(), self.levelcount.value, self.bestlevel)

    def level_progression(self) -> tuple[int, int]:
        coins = 1 + self.levelcount.value // COIN_PROGRESSION_PACE
        foes = 1 + self.levelcount.value // FOE_PROGRESSION_PACE
        return (coins, foes)
    
    def define_best_level(self):
        self.bestlevel = max(self.bestlevel, self.levelcount.value)

def main():
    Game(WINDOW_WIDTH, WINDOW_HEIGHT)

if __name__ == "__main__":
    main()
