import pygame
import asyncio
import random
from game import *
from game.powerup import SIZE

def drawUI(screen: pygame.Surface, player: Player):
    hp_padding = 8 # px
    hp_spacing = 5 
    
    hp_image = pygame.image.load("heart.png").convert_alpha()
    scaled_hp_image = pygame.transform.scale(hp_image, (25, 25))

    for i in range(player.hp):
        x_pos = hp_padding + i * (25 + hp_spacing)
        y_pos = HEIGHT - hp_padding - 25
        
        screen.blit(scaled_hp_image, (x_pos, y_pos))


def drawRestartScreen(screen: pygame.Surface, font: pygame.font.Font):
    lines = ["You lose!", "Press R to restart."]
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    start_y = HEIGHT / 2 - total_height / 2

    for i, line in enumerate(lines):
        textSurface = font.render(line, True, "red")
        textRect = textSurface.get_rect(
            center=(WIDTH / 2, start_y + line_height * i + line_height / 2)
        )
        screen.blit(textSurface, textRect)



def spawnRandomPowerup():
    margin = SIZE / 2
    pos = (
        random.uniform(margin, WIDTH - margin),
        random.uniform(margin, HEIGHT - margin),
    )
    powerupType = random.choice((Heal, DamageUp))
    powerupType(pos)


def spawnEnemy(player: Player):
    pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
    for _ in range(20):
        pos = pygame.Vector2(
            random.uniform(40, WIDTH - 40),
            random.uniform(40, HEIGHT - 40),
        )
        if pos.distance_to(player.position) > 200:
            break
    return Enemy(pos)


def newGameState():
    return {
        "st": pygame.time.get_ticks(),
        "numberAsteroids": 0,
        "waves": {
            5: 2,
            15: 4,
            30: 6,
            60: 10,
            120: 12,
        },
        "triggered_waves": set(),
        "player": Player(),
        "allAsteroids": [],
        "nextPowerupTime": POWERUP_SPAWN_INTERVAL,
        "enemy": None,
        "nextEnemySpawnTime": ENEMY_FIRST_SPAWN,
    }


async def main():
    running = True

    pygame.init()
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rayhan Alwi Peri    od 5: Crazy Asteroids")
    clock = pygame.time.Clock()
    bg = StarBackground(size_range=(1.0, 3.0), screen=screen, layer_count=4)
    restart_font = pygame.font.Font(None, 48)

    dt = 0 # delta time
    et_ms = 0 # elapsed time in ms
    et_s = 0 # elapsed time in s

    # Clear any missiles/powerups left over from a previous run
    Missile.allMissiles.clear()
    PowerUp.powerups.clear()

    state = newGameState()
    player = state["player"]
    allAsteroids = state["allAsteroids"]
    waves = state["waves"]
    triggered_waves = state["triggered_waves"]
    st = state["st"]
    numberAsteroids = state["numberAsteroids"]
    nextPowerupTime = state["nextPowerupTime"]
    enemy = state["enemy"]
    nextEnemySpawnTime = state["nextEnemySpawnTime"]

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and player.alive:
                    targetPosition = pygame.Vector2(event.pos)
                    player.fireMissile(targetPosition)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not player.alive:
                    if enemy is not None:
                        enemy.delete()
                    Missile.allMissiles.clear()
                    PowerUp.powerups.clear()
                    Player.score = 0
                    state = newGameState()
                    player = state["player"]
                    allAsteroids = state["allAsteroids"]
                    waves = state["waves"]
                    triggered_waves = state["triggered_waves"]
                    st = state["st"]
                    numberAsteroids = state["numberAsteroids"]
                    nextPowerupTime = state["nextPowerupTime"]
                    enemy = state["enemy"]
                    nextEnemySpawnTime = state["nextEnemySpawnTime"]

        # Delta Time & Timer
        dt = min(clock.tick(60) / 1000, 0.06)

        bg.update(dt)

        if player.alive:
            et_ms = pygame.time.get_ticks() - st
            et_s = et_ms / 1000.0

            # Wave Trigger Check
            for wave_time, wave_target in waves.items():
                if et_s >= wave_time and wave_time not in triggered_waves:
                    for _ in range(wave_target):
                        allAsteroids.append(Asteroid())
                    triggered_waves.add(wave_time)

            if et_s in waves:
                newWave = waves[et_s]

                for i in range(newWave - numberAsteroids):
                    allAsteroids.append(Asteroid())

            # Powerup Spawn Timer
            if et_s >= nextPowerupTime:
                spawnRandomPowerup()
                nextPowerupTime += POWERUP_SPAWN_INTERVAL

            # Enemy Spawn
            if enemy is None and et_s >= nextEnemySpawnTime:
                enemy = spawnEnemy(player)

        # Background
        screen.fill("black")

        bg.draw(screen)

        if player.alive:
            # Update Player
            player.update(dt)

            # Update Enemy (roams + shoots the player; ignores asteroids)
            if enemy is not None:
                enemy.update(dt, player)

            # Powerup pickup
            for powerup in PowerUp.powerups[:]:
                powerup.checkCollision(player)

            # Update Missiles
            for missile in Missile.allMissiles[:]:
                missile.update(dt)
            for missile in Missile.allMissiles[:]:
                # Enemy missiles only hurt the player
                if missile.isEnemy:
                    missile.collideWithPlayer(player)
                    continue

                hitAsteroid = False
                for asteroid in allAsteroids[:]:
                    if missile.collideWithAsteroid(asteroid):
                        if asteroid.dead and asteroid in allAsteroids:
                            allAsteroids.remove(asteroid)
                            allAsteroids.append(Asteroid())
                            Player.score += 1
                        hitAsteroid = True
                        break
                if hitAsteroid:
                    continue

                if enemy is not None and missile.collideWithEnemy(enemy):
                    if not enemy.alive:
                        enemy.delete()
                        enemy = None
                        Player.score += ENEMY_KILL_SCORE
                        nextEnemySpawnTime = et_s + ENEMY_RESPAWN_DELAY

            # Update Asteroids
            for i in range(len(allAsteroids)):
                player.collideWithAsteroid(allAsteroids[i])
                for j in range(i + 1, len(allAsteroids)):
                    allAsteroids[i].collideWithAsteroid(allAsteroids[j])
            for asteroid in allAsteroids:
                asteroid.update(dt)

        # Draw Player
        player.draw(screen)

        # Draw Missiles
        for missile in Missile.allMissiles:
            missile.draw(player, screen)

        # Draw Asteroids
        for asteroid in allAsteroids:
            asteroid.draw(screen)

        # Draw Enemy
        if enemy is not None:
            enemy.draw(screen)

        # Draw Powerups
        for powerup in PowerUp.powerups:
            powerup.draw(screen)

        drawUI(screen, player)

        if not player.alive:
            drawRestartScreen(screen, restart_font)

        # Display
        pygame.display.flip()

        await asyncio.sleep(0)
    pygame.quit()

asyncio.run(main())