import pygame
from game.player import Player

SIZE = 30


class PowerUp:
    powerups: list["PowerUp"] = []

    def __init__(self, pos: tuple[float, float]):
        self.position = pygame.Vector2(pos)
        self.radius = SIZE / 2
        self.color = (255, 255, 255)
        PowerUp.powerups.append(self)

    def checkCollision(self, player: Player):
        if not player.alive:
            return
        distance = self.position.distance_to(player.position)
        if distance < self.radius + player.radius:
            self.consume(player)

    def consume(self, player: Player):
        self.delete()

    def delete(self):
        if self in PowerUp.powerups:
            PowerUp.powerups.remove(self)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)


class Heal(PowerUp):
    def __init__(self, pos: tuple[float, float]):
        super().__init__(pos)
        self.color = (60, 220, 60)

    def consume(self, player: Player):
        player.hp += 1
        self.delete()


class DamageUp(PowerUp):
    def __init__(self, pos: tuple[float, float]):
        super().__init__(pos)
        self.color = (220, 60, 60)

    def consume(self, player: Player):
        player.activateDoubleShot()
        self.delete()