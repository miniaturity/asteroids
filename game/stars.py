import random
from dataclasses import dataclass

import pygame

type Position = tuple[float, float]


def draw_circle_alpha(surface, color, center, radius):
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    
    surface.blit(shape_surf, target_rect)


@dataclass
class Star:
    size: float
    pos: Position


class StarLayer:
    def __init__(
        self,
        size: float,
        speed: float, # 1 = cam speed
        screen: pygame.Surface,
        count: int | None = None,
        size_jitter: float = 0.4,
    ):
        self.size = size
        self.speed = speed
        self.tile_w, self.tile_h = screen.get_size()
        self.transparency = max(0, min(256 - (size * 25), 256))

        if count is None:

            density = 0.00012
            count = max(4, int(self.tile_w * self.tile_h * density))
        self.count = count

        self.stars: list[Star] = [
            Star(
                size=random.uniform(size * (1 - size_jitter), size * (1 + size_jitter)),
                pos=(random.uniform(0, self.tile_w), random.uniform(0, self.tile_h)),
            )
            for _ in range(self.count)
        ]

    def draw(self, surface: pygame.Surface, cam_pos: Position) -> None:
        screen_w, screen_h = surface.get_size()

        for star in self.stars:

            base_x = (star.pos[0] - cam_pos[0] * self.speed) % self.tile_w
            base_y = (star.pos[1] - cam_pos[1] * self.speed) % self.tile_h

            for ox in (0.0, -self.tile_w):
                x = base_x + ox
                if x < -star.size or x > screen_w + star.size:
                    continue  # whole column off-screen, skip
                for oy in (0.0, -self.tile_h):
                    y = base_y + oy
                    if y < -star.size or y > screen_h + star.size:
                        continue
                    draw_circle_alpha(surface, (255, 255, 255, self.transparency), (x, y), star.size)


class StarBackground:
    def __init__(
        self,
        size_range: tuple[float, float],
        screen: pygame.Surface,
        layer_count: int = 4,
        idle_speed: float = 15.0,
        speed_range: tuple[float, float] = (0.2, 1.0),
    ):
        self.cam_pos: Position = (0.0, 0.0)
        self.size_range = size_range
        self.idle_speed = idle_speed  # px/sec

        min_size, max_size = size_range
        min_speed, max_speed = speed_range

        self.layers: list[StarLayer] = []
        for i in range(layer_count):
            # spread layers evenly between the size/speed extremes
            t = i / max(1, layer_count - 1)
            size = min_size + t * (max_size - min_size)
            speed = min_speed + t * (max_speed - min_speed)
            self.layers.append(StarLayer(size=size, speed=speed, screen=screen))

    def update(self, dt: float, dx: float = 0.0, dy: float = 0.0) -> None:
        cx, cy = self.cam_pos
        self.cam_pos = (cx + dx, cy - self.idle_speed * dt + dy)

    def draw(self, surface: pygame.Surface) -> None:
        for layer in self.layers:
            layer.draw(surface, self.cam_pos)