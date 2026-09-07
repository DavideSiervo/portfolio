import asyncio
import pygame
import random
from Modulo_audio import pitch_sample


pygame.init()
pygame.mixer.init()


# ==========================================================
# MONDO DI GIOCO
# ==========================================================

# Tutta la logica del gioco avviene SEMPRE in 1920x1080.
# La finestra/browser può invece avere qualsiasi dimensione.

WORLD_WIDTH = 1920
WORLD_HEIGHT = 1080
FPS = 60

# Superficie sulla quale viene realmente disegnato il gioco
game_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))

# Dimensione iniziale della finestra web.
# Può essere ridimensionata senza modificare la fisica del gioco.
window = pygame.display.set_mode(
    (960, 540),
    pygame.RESIZABLE
)

pygame.display.set_caption("HarpHero")


# ==========================================================
# AUDIO
# ==========================================================

odyssey_sound = pygame.mixer.Sound("odysseyC3.wav")

notes = [
    "C3",
    "D3",
    "E3",
    "F3",
    "G3",
    "A3",
    "B3"
]

note_semitones = {
    "C3": 0,
    "D3": 2,
    "E3": 4,
    "F3": 5,
    "G3": 7,
    "A3": 9,
    "B3": 11
}

harp_sounds = {}

for note in notes:
    harp_sounds[note] = pitch_sample(
        odyssey_sound,
        note_semitones[note]
    )


# ==========================================================
# GRAFICA
# ==========================================================

background = pygame.image.load("sfondo.png").convert()
background = pygame.transform.scale(
    background,
    (WORLD_WIDTH, WORLD_HEIGHT)
)

hero_image = pygame.image.load("Eroe_idle.png").convert_alpha()


# ==========================================================
# EROE
# ==========================================================

hero_rect = pygame.Rect(0, 0, 180, 180)

hero_image = pygame.transform.scale(
    hero_image,
    (hero_rect.width, hero_rect.height)
)

hero_rect.center = (
    WORLD_WIDTH // 2,
    WORLD_HEIGHT // 2
)

hero_life = 3
hero_direction = "down"

played_note = ""


# ==========================================================
# NEMICI
# ==========================================================

enemies = []

enemy_size = 40
enemy_velocity = 3

last_spawn = 0
spawn_interval = random.randint(1000, 3000)


# ==========================================================
# FONT
# ==========================================================

hud_font = pygame.font.SysFont("Arial", 24)
font = pygame.font.SysFont("Arial", 24)

clock = pygame.time.Clock()


# ==========================================================
# FUNZIONE PER ADATTARE IL GIOCO ALLA FINESTRA
# ==========================================================

def draw_scaled_game():

    screen_width, screen_height = window.get_size()

    scale = min(
        screen_width / WORLD_WIDTH,
        screen_height / WORLD_HEIGHT
    )

    scaled_width = int(WORLD_WIDTH * scale)
    scaled_height = int(WORLD_HEIGHT * scale)

    scaled_surface = pygame.transform.smoothscale(
        game_surface,
        (scaled_width, scaled_height)
    )

    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2

    window.fill((0, 0, 0))

    window.blit(
        scaled_surface,
        (x, y)
    )


# ==========================================================
# MAIN
# ==========================================================

async def main():

    global hero_life
    global played_note
    global hero_direction
    global last_spawn
    global spawn_interval

    running = True

    while running:

        # ==================================================
        # EVENTI
        # ==================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_c:
                    played_note = "C3"

                elif event.key == pygame.K_d:
                    played_note = "D3"

                elif event.key == pygame.K_e:
                    played_note = "E3"

                elif event.key == pygame.K_f:
                    played_note = "F3"

                elif event.key == pygame.K_g:
                    played_note = "G3"

                elif event.key == pygame.K_a:
                    played_note = "A3"

                elif event.key == pygame.K_b:
                    played_note = "B3"

                if played_note != "":
                    harp_sounds[played_note].play()


        current_time = pygame.time.get_ticks()


        # ==================================================
        # SPAWN NEMICO
        # ==================================================

        if current_time - last_spawn >= spawn_interval:

            side = random.randint(1, 4)

            # SINISTRA
            if side == 1:

                enemy_x = -enemy_size

                enemy_y = random.randint(
                    0,
                    WORLD_HEIGHT - enemy_size
                )

            # DESTRA
            elif side == 2:

                enemy_x = WORLD_WIDTH

                enemy_y = random.randint(
                    0,
                    WORLD_HEIGHT - enemy_size
                )

            # ALTO
            elif side == 3:

                enemy_x = random.randint(
                    0,
                    WORLD_WIDTH - enemy_size
                )

                enemy_y = -enemy_size

            # BASSO
            else:

                enemy_x = random.randint(
                    0,
                    WORLD_WIDTH - enemy_size
                )

                enemy_y = WORLD_HEIGHT


            enemy_rect = pygame.Rect(
                enemy_x,
                enemy_y,
                enemy_size,
                enemy_size
            )

            enemy_note = random.choice(notes)


            # ----------------------------------------------
            # DIREZIONE CALCOLATA UNA SOLA VOLTA
            # ----------------------------------------------

            direction = pygame.Vector2(
                hero_rect.centerx - enemy_rect.centerx,
                hero_rect.centery - enemy_rect.centery
            )

            if direction.length() != 0:
                direction = direction.normalize()


            # Posizione in virgola mobile.
            # Serve per evitare gli errori di arrotondamento dei Rect.
            enemy_position = pygame.Vector2(
                enemy_rect.x,
                enemy_rect.y
            )


            enemy_components = [
                enemy_rect,
                enemy_note,
                enemy_position,
                direction
            ]

            enemies.append(enemy_components)


            last_spawn = current_time

            spawn_interval = random.randint(
                1000,
                3000
            )


        # ==================================================
        # MOVIMENTO NEMICI
        # ==================================================

        for enemy in enemies:

            enemy_rect = enemy[0]
            enemy_position = enemy[2]
            enemy_direction = enemy[3]


            # La direzione NON viene più ricalcolata.
            enemy_position += (
                enemy_direction * enemy_velocity
            )


            enemy_rect.x = round(enemy_position.x)
            enemy_rect.y = round(enemy_position.y)


        # ==================================================
        # COLLISIONI CON L'EROE
        # ==================================================

        for enemy in enemies[:]:

            enemy_rect = enemy[0]

            if enemy_rect.colliderect(hero_rect):

                print("Il nemico ha colpito l'eroe!")

                hero_life -= 1

                enemies.remove(enemy)

                print("Vite:", hero_life)


        # ==================================================
        # TARGET PIÙ VICINO
        # ==================================================

        nearest_enemy = None
        nearest_distance = None


        for enemy in enemies:

            enemy_rect = enemy[0]

            distance = pygame.Vector2(
                enemy_rect.center
            ).distance_to(
                hero_rect.center
            )


            if nearest_distance is None:

                nearest_distance = distance
                nearest_enemy = enemy

            elif distance < nearest_distance:

                nearest_distance = distance
                nearest_enemy = enemy


        # ==================================================
        # NOTA CORRETTA
        # ==================================================

        if nearest_enemy is not None:

            if played_note == nearest_enemy[1]:

                enemies.remove(nearest_enemy)

                nearest_enemy = None


        played_note = ""


        # ==================================================
        # DIREZIONE EROINA
        # ==================================================

        if nearest_enemy is not None:

            target_rect = nearest_enemy[0]

            dx = (
                target_rect.centerx
                - hero_rect.centerx
            )

            dy = (
                target_rect.centery
                - hero_rect.centery
            )


            if abs(dx) > abs(dy):

                if dx > 0:
                    hero_direction = "right"

                else:
                    hero_direction = "left"

            else:

                if dy > 0:
                    hero_direction = "down"

                else:
                    hero_direction = "up"


        # ==================================================
        # GAME OVER
        # ==================================================

        if hero_life <= 0:

            print("L'eroe è morto!")

            running = False


        # ==================================================
        # DISEGNO
        # ==================================================

        game_surface.blit(
            background,
            (0, 0)
        )


        # HUD

        life_text = hud_font.render(
            f"Vite: {hero_life}",
            True,
            (255, 255, 255)
        )

        game_surface.blit(
            life_text,
            (20, 20)
        )


        # NEMICI

        for enemy in enemies:

            enemy_rect = enemy[0]
            enemy_note = enemy[1]

            pygame.draw.rect(
                game_surface,
                (255, 0, 0),
                enemy_rect
            )


            text = font.render(
                enemy_note,
                True,
                (255, 255, 255)
            )

            text_rect = text.get_rect(
                center=(
                    enemy_rect.centerx,
                    enemy_rect.top - 15
                )
            )

            game_surface.blit(
                text,
                text_rect
            )


        # EROINA

        hero_image_rect = hero_image.get_rect(
            center=hero_rect.center
        )

        game_surface.blit(
            hero_image,
            hero_image_rect
        )


        # ==================================================
        # SCALA IL FRAME ALLA FINESTRA/BROWSER
        # ==================================================

        draw_scaled_game()

        pygame.display.flip()

        clock.tick(FPS)

        # Necessario per l'esecuzione nel browser
        await asyncio.sleep(0)


    pygame.quit()


asyncio.run(main())
