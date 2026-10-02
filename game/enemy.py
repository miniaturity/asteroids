import random
import pygame

from game.consts import *
from game.missile import Missile
from game.ship import Ship

WAYPOINT_REACHED = 20 

class Enemy(Ship):
    def __init__(self, pos=None) -> None:
        super().__init__(isPlayer=False)
        self.speed = 150
        self.color = (180, 80, 255)
        self._hp = ENEMY_MAX_HP
        if pos is not None:
            self.position = pygame.Vector2(pos)

        self.waypoint: pygame.Vector2 | None = None
        self.waypoint_timer = 0.0
        self.fire_timer = 1.0  

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, newHp):
        self._hp = max(0, newHp)
        if self._hp <= 0:
            self.alive = False

    def takeDamage(self, amount):
        self.hp -= amount

    def delete(self):
        if self in Ship.ships:
            Ship.ships.remove(self)

    def fireMissile(self, targetPosition):
        diff = targetPosition - self.position
        if diff.length_squared() == 0:
            return None
        return Missile(
            self.position,
            diff.normalize(),
            self.damage,
            enemy=True,
            speed=ENEMY_MISSILE_SPEED,
        )

    def pickWaypoint(self):
        margin = 40
        self.waypoint = pygame.Vector2(
            random.uniform(margin, WIDTH - margin),
            random.uniform(margin, HEIGHT - margin),
        )
        self.waypoint_timer = random.uniform(2.0, 4.0)

    def roam(self, toPosition, dt):
        offset = toPosition - self.position
        if offset.length_squared() > 0:
            self.acceleration = offset.normalize() * self.speed / self.mass
        else:
            self.acceleration = pygame.Vector2(0, 0)

        self.velocity += self.acceleration * dt
        if self.drag > 0:
            self.velocity *= max(1.0 - self.drag * dt, 0.0)
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        self.position += self.velocity * dt
        self.wrapAroundWall()

    def update(self, dt, player):
        if not self.alive or dt <= 0:
            return

        # Face the player (used for drawing)
        self.point_to(player.position)

        # Roam
        self.waypoint_timer -= dt
        if (
            self.waypoint is None
            or self.waypoint_timer <= 0
            or self.position.distance_to(self.waypoint) < WAYPOINT_REACHED
        ):
            self.pickWaypoint()
        self.roam(self.waypoint, dt)

        # Shoot
        self.fire_timer -= dt
        if self.fire_timer <= 0 and player.alive:
            self.fireMissile(player.position)
            self.fire_timer = ENEMY_FIRE_INTERVAL * random.uniform(0.8, 1.2)

    def draw(self, screen):
        if not self.alive:
            return
        super().draw(screen)

        textSurface = self.font.render(str(self.hp), True, "white")
        textRect = textSurface.get_rect(center=self.position)
        screen.blit(textSurface, textRect)