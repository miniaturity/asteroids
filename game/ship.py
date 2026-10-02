import pygame
from game.consts import *
from game.asteroid import Asteroid

class Ship:
    ships: list["Ship"] = []

    def __init__(self, isPlayer = True) -> None:
        self.isPlayer = isPlayer
        self.speed = 200 # px/s
        self.position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)

        self.acceleration = pygame.math.Vector2(0, 0) # px^2/s
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(1, 0)

        self.mass = 1.0
        self.drag = 1.5
        self.max_speed = 350

        self.damage = 10

        self.radius = 20

        self.alive = True
        self.immune = False
        self.out_of_control = False

        self.i_ms = 1500 # immunity time
        self.i_at: float | None = None

        self.ooc_ms = 650 # ooc time
        self.ooc_at: float | None = None

        self.double_shot = False
        self.ds_ms = 10000 # double shot (DamageUp) duration
        self.ds_at: float | None = None
        self.double_shot_offset = 12 # px between the two parallel lasers

        self._hp = 5

        self.font = pygame.font.Font(None, round(self.radius) * 2)

        self.color = "brown2"
        Ship.ships.append(self)

    def collideWithAsteroid(self, asteroid: Asteroid):
            if self.immune:
                return
    
            diff = self.position - asteroid.position
            distance = diff.length()
    
            distance = self.position.distance_to(asteroid.position)
    
            if distance < self.radius + asteroid.radius:
                self.hp -= 1
                self.immune = True
                self.out_of_control = True
                self.i_at = None   # Reset timers so full duration triggers
                self.ooc_at = None
    
                if distance > 0:
                    normal = diff.normalize()
                else:
                    normal = pygame.Vector2(1, 0)
    
                knockback_speed = 25
                self.velocity = normal * knockback_speed * asteroid.radius
    
    def point_to(self, to):
        if self.out_of_control:
            return
        
        direction_to_target = to - self.position
        if direction_to_target.length_squared() > 0:
            self.direction = direction_to_target.normalize()

    def draw(self, screen):
        if self.immune:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return 

        forward = self.direction
        right = pygame.Vector2(-forward.y, forward.x)

        # Tip pointing to the mouse
        tip = self.position + forward * self.radius
        # Back-left and Back-right wings
        left = self.position - forward * (self.radius * 0.8) + right * (self.radius * 0.6)
        right_pt = self.position - forward * (self.radius * 0.8) - right * (self.radius * 0.6)

        pygame.draw.polygon(screen, self.color, [tip, left, right_pt])

    def wrapAroundWall(self):
        if self.position.x < -self.radius:
            self.position.x = self.radius + WIDTH
        elif self.position.x > self.radius + WIDTH:
            self.position.x = -self.radius
        if self.position.y < -self.radius:
            self.position.y = self.radius + HEIGHT
        elif self.position.y > self.radius + HEIGHT:
            self.position.y = -self.radius

    def update(self):
        pass # implement in inhereted
