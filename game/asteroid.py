import pygame
import random
from game.consts import *

class Asteroid:
    def __init__(self):
        self.radius = random.randint(15, 30)
        self.hp = self.radius
        
        # Pick positions until one is far enough from the player
        margin = 100
        self.position = pygame.Vector2(
            random.choice((random.uniform(-margin, 0), random.uniform(WIDTH, WIDTH + margin))),
            random.choice((random.uniform(-margin, 0), random.uniform(HEIGHT, HEIGHT + margin)))
        )

        self.velocity = pygame.Vector2(
            random.uniform(-200, 200),
            random.uniform(-200, 200)
        )
        self.mass = self.radius ** 2
        self.elasticity = 0.5
        self.color = tuple(random.randint(0, 255) for _ in range(3))
        self.font = pygame.font.Font(None, round(self.radius) * 2)
        self.dead = False

    def wrapAroundWall(self):
        if self.position.x < -self.radius:
            self.position.x = self.radius + WIDTH
        elif self.position.x > self.radius + WIDTH:
            self.position.x = -self.radius
        if self.position.y < -self.radius:
            self.position.y = self.radius + HEIGHT
        elif self.position.y > self.radius + HEIGHT:
            self.position.y = -self.radius

    def collideWithAsteroid(self, other):
        offset = other.position - self.position
        if offset.x > WIDTH / 2:
            offset.x -= WIDTH
        elif offset.x < -WIDTH / 2:
            offset.x += WIDTH
        if offset.y > HEIGHT / 2:
            offset.y -= HEIGHT
        elif offset.y < -HEIGHT / 2:
            offset.y += HEIGHT

        distance = offset.length()
        minimumDistance = self.radius + other.radius
        if distance >= minimumDistance: return
        if distance == 0:
            normal = pygame.Vector2(1, 0)
        else:
            normal = offset / distance

        relativeVelocity = other.velocity - self.velocity
        velocityAlongNormal = relativeVelocity.dot(normal)

        if velocityAlongNormal >= 0: return

        overlap = minimumDistance - distance
        totalMass = self.mass + other.mass
        self.position -= normal * overlap * (other.mass / totalMass)
        other.position += normal * overlap * (self.mass / totalMass)

        elasticity = min(self.elasticity, other.elasticity)
        impulseMagnitude = (
            -(1 + elasticity) * velocityAlongNormal
            / (1 / self.mass + 1 / other.mass)
        )
        impulse = normal * impulseMagnitude
        self.velocity -= impulse / self.mass
        other.velocity += impulse / other.mass

    def takeDamage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.radius = max(0, self.hp)
        self.mass = max(self.radius ** 2, 1)

        if self.hp <= 0 or self.radius < MIN_ASTEROID_RADIUS:
            self.dead = True

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrapAroundWall()

        if self.hp <= 0:
            self.dead = True

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            self.radius
        )