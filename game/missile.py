import pygame
from game.consts import * 
from game.asteroid import Asteroid
from game.ship import Ship

class Missile:
    allMissiles: list["Missile"] = []
    def __init__(self, playerPosition, normalDirection, damage, enemy = False, speed = 300):
        self.speed = speed
        self.radius = 10
        self.position: pygame.math.Vector2 = playerPosition.copy()
        self.velocity = normalDirection * self.speed
        self.forward = normalDirection.copy()
        self.damage = damage
        self.isEnemy = enemy
        Missile.allMissiles.append(self)
        
    def outsideScreen(self):
        return (
            self.position.x < -self.radius
            or self.position.x > WIDTH + self.radius
            or self.position.y < -self.radius
            or self.position.y > HEIGHT + self.radius
        )
        
    def collideWithAsteroid(self, asteroid: Asteroid):
        if self.isEnemy: 
            return

        distance = self.position.distance_to(asteroid.position)

        if distance < self.radius + asteroid.radius:
            asteroid.takeDamage(self.damage)
            if self in Missile.allMissiles:
                Missile.allMissiles.remove(self)
            return True

        return False

    def collideWithEnemy(self, enemy):
        """Player missiles damage the enemy ship."""
        if self.isEnemy or not enemy.alive:
            return False

        distance = self.position.distance_to(enemy.position)

        if distance < self.radius + enemy.radius:
            enemy.takeDamage(self.damage)
            if self in Missile.allMissiles:
                Missile.allMissiles.remove(self)
            return True

        return False

    def collideWithPlayer(self, player: Ship):
        """Enemy missiles damage the player (and grant brief immunity)."""
        if not self.isEnemy or player.immune:
            return False

        distance = self.position.distance_to(player.position)

        if distance < self.radius + player.radius:
            player.hp -= 1
            player.immune = True
            player.i_at = None  # restart immunity timer
            if self in Missile.allMissiles:
                Missile.allMissiles.remove(self)
            return True

        return False
        
    
    def update(self, dt):
        self.position += self.velocity * dt
        if self.outsideScreen() and self in Missile.allMissiles:
            Missile.allMissiles.remove(self)
            
    def draw(self, player, screen):
        if self.forward is None:
            self.forward = player.direction

        forward = self.forward

        right = pygame.Vector2(-forward.y, forward.x)

        # Tip pointing along travel direction
        tip = self.position + forward * self.radius
        # Back-left and Back-right wings
        left = self.position - forward * (self.radius * 0.8) + right * (self.radius * 0.6)
        right_pt = self.position - forward * (self.radius * 0.8) - right * (self.radius * 0.6)

        color = (255, 80, 80) if self.isEnemy else (255, 255, 0)
        pygame.draw.polygon(screen, color, [tip, left, right_pt])