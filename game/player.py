import pygame
import random

from game.consts import *
from game.missile import Missile
from game.asteroid import Asteroid
from game.ship import Ship

class Player(Ship):
    score = 0

    def __init__(self):
        super().__init__()

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, newHp):
        self._hp = max(0, newHp)
        if self._hp <= 0:
            self.alive = False


    def activateDoubleShot(self):
        self.double_shot = True
        self.ds_at = None  # reset timer so a fresh pickup gives the full duration

    def fireMissile(self, targetPosition):
        diff = targetPosition - self.position
        if diff.length_squared() == 0:
            return None

        normalDirection = diff.normalize()

        if self.double_shot:
            right = pygame.Vector2(-normalDirection.y, normalDirection.x)
            offset = right * self.double_shot_offset
            return [
                Missile(self.position + offset, normalDirection, self.damage),
                Missile(self.position - offset, normalDirection, self.damage),
            ]

        return Missile(self.position, normalDirection, self.damage)

    def update(self, dt):
        if not self.alive:
            return
        
        now = pygame.time.get_ticks()

        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        self.point_to(mouse_pos)

        # 1. Reset acceleration to zero every frame
        self.acceleration = pygame.math.Vector2(0, 0)

        keys = pygame.key.get_pressed()

        if not self.out_of_control:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.acceleration += (self.direction * self.speed) / self.mass 
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.acceleration -= (self.direction * self.speed) / self.mass

        if dt <= 0:
            return
            
        self.velocity += self.acceleration * dt

        if self.drag > 0:
            self.velocity *= max(1.0 - self.drag * dt, 0.0)

        if not self.out_of_control and self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        self.position += self.velocity * dt

        if self.immune and self.i_at is None:
            self.i_at = pygame.time.get_ticks()
        elif self.immune and self.i_at is not None:
            if now - self.i_at >= self.i_ms:
                self.immune = False
                self.i_at = None

        if self.out_of_control and self.ooc_at is None:
            self.ooc_at = pygame.time.get_ticks()
        elif self.out_of_control and self.ooc_at is not None:
            if now - self.ooc_at >= self.ooc_ms:
                self.out_of_control = False
                self.ooc_at = None

        if self.double_shot and self.ds_at is None:
            self.ds_at = pygame.time.get_ticks()
        elif self.double_shot and self.ds_at is not None:
            if now - self.ds_at >= self.ds_ms:
                self.double_shot = False
                self.ds_at = None
        
        self.wrapAroundWall()

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

        textSurface = self.font.render(str(Player.score), True, "white")
        textRect = textSurface.get_rect(center = self.position)
        screen.blit(textSurface, textRect)