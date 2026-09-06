import asyncio
import random
import pygame


WIDTH = 960
HEIGHT = 540
FPS = 60
NOTES = ("C3", "D3", "E3", "F3", "G3", "A3", "B3")
KEYS = {
    pygame.K_c: "C3",
    pygame.K_d: "D3",
    pygame.K_e: "E3",
    pygame.K_f: "F3",
    pygame.K_g: "G3",
    pygame.K_a: "A3",
    pygame.K_b: "B3",
}


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HarpHero")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("Arial", 64, bold=True)
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)

sounds = {note: pygame.mixer.Sound(f"sounds/{note}.wav") for note in NOTES}


def centered_text(text, used_font, color, y):
    surface = used_font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))


def new_game():
    hero = pygame.Rect(0, 0, 52, 52)
    hero.center = (WIDTH // 2, HEIGHT // 2)
    return {
        "hero": hero,
        "life": 3,
        "score": 0,
        "enemies": [],
        "last_spawn": pygame.time.get_ticks(),
        "spawn_interval": random.randint(1000, 2200),
    }


def spawn_enemy(state):
    size = 36
    side = random.randint(1, 4)
    if side == 1:
        x, y = -size, random.randint(40, HEIGHT - size)
    elif side == 2:
        x, y = WIDTH, random.randint(40, HEIGHT - size)
    elif side == 3:
        x, y = random.randint(0, WIDTH - size), -size
    else:
        x, y = random.randint(0, WIDTH - size), HEIGHT

    state["enemies"].append([pygame.Rect(x, y, size, size), random.choice(NOTES)])
    state["last_spawn"] = pygame.time.get_ticks()
    state["spawn_interval"] = random.randint(1000, 2200)


def draw_start():
    screen.fill((10, 10, 10))
    centered_text("HarpHero", title_font, (245, 188, 104), 145)
    centered_text("Difendi il centro suonando la nota del nemico più vicino.", font, (235, 232, 224), 235)
    centered_text("Tasti: C  D  E  F  G  A  B", font, (245, 188, 104), 285)
    centered_text("Premi SPAZIO per iniziare", small_font, (170, 167, 159), 365)


def draw_game(state):
    screen.fill((7, 7, 7))
    hero = state["hero"]

    for enemy_rect, enemy_note in state["enemies"]:
        pygame.draw.rect(screen, (175, 54, 44), enemy_rect, border_radius=5)
        label = small_font.render(enemy_note, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=(enemy_rect.centerx, enemy_rect.top - 12)))

    pygame.draw.rect(screen, (245, 188, 104), hero, border_radius=8)
    pygame.draw.rect(screen, (255, 231, 184), hero, 2, border_radius=8)

    info = small_font.render(
        f"Vite: {state['life']}     Punteggio: {state['score']}",
        True,
        (235, 232, 224),
    )
    screen.blit(info, (18, 16))
    keys = small_font.render("C  D  E  F  G  A  B", True, (170, 167, 159))
    screen.blit(keys, (WIDTH - keys.get_width() - 18, 16))


def draw_game_over(state):
    screen.fill((10, 10, 10))
    centered_text("Game over", title_font, (175, 54, 44), 175)
    centered_text(f"Punteggio: {state['score']}", font, (235, 232, 224), 270)
    centered_text("Premi SPAZIO per ricominciare", small_font, (170, 167, 159), 345)


async def main():
    state = new_game()
    mode = "start"
    running = True

    while running:
        played_note = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and mode in ("start", "game_over"):
                    state = new_game()
                    mode = "playing"
                elif mode == "playing" and event.key in KEYS:
                    played_note = KEYS[event.key]
                    sounds[played_note].play()

        if mode == "playing":
            now = pygame.time.get_ticks()
            if now - state["last_spawn"] >= state["spawn_interval"]:
                spawn_enemy(state)

            hero = state["hero"]
            for enemy in state["enemies"]:
                enemy_rect = enemy[0]
                direction = pygame.Vector2(
                    hero.centerx - enemy_rect.centerx,
                    hero.centery - enemy_rect.centery,
                )
                if direction.length_squared():
                    direction = direction.normalize()
                    enemy_rect.x += direction.x * 2.2
                    enemy_rect.y += direction.y * 2.2

            for enemy in state["enemies"][:]:
                if enemy[0].colliderect(hero):
                    state["life"] -= 1
                    state["enemies"].remove(enemy)

            if state["enemies"] and played_note:
                nearest = min(
                    state["enemies"],
                    key=lambda enemy: pygame.Vector2(enemy[0].center).distance_to(hero.center),
                )
                if played_note == nearest[1]:
                    state["enemies"].remove(nearest)
                    state["score"] += 1

            if state["life"] <= 0:
                mode = "game_over"
            draw_game(state)
        elif mode == "start":
            draw_start()
        else:
            draw_game_over(state)

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
