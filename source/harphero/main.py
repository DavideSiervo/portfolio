import pygame
import random
import sys
from pathlib import Path
from Modulo_audio import pitch_sample

# ==========================================================
# PERCORSI (chatgpt)
# ==========================================================

if getattr(sys, "frozen", False):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(__file__).resolve().parent

pygame.init()
pygame.mixer.init()

# ==========================================================
# MONDO DI GIOCO
# ==========================================================

WORLD_WIDTH = 1920
WORLD_HEIGHT = 1080
FPS = 60
game_surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
window = pygame.display.set_mode((960, 540),pygame.RESIZABLE)
pygame.display.set_caption("HarpHero")

# ==========================================================
# AUDIO
# ==========================================================

odyssey_sound = pygame.mixer.Sound(BASE_PATH / "odysseyC3.wav")

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

for note in notes:harp_sounds[note] = pitch_sample(odyssey_sound,note_semitones[note])

# ==========================================================
# GRAFICA
# ==========================================================

background = pygame.image.load(BASE_PATH / "sfondo.png").convert()
background = pygame.transform.scale(background,(WORLD_WIDTH, WORLD_HEIGHT))
hero_image = pygame.image.load(BASE_PATH / "Eroe_idle.png").convert_alpha()

# ==========================================================
# EROE
# ==========================================================

hero_rect = pygame.Rect(0, 0, 180, 180)
hero_image = pygame.transform.scale(hero_image,(hero_rect.width, hero_rect.height))
hero_rect.center = (WORLD_WIDTH // 2,WORLD_HEIGHT // 2)
hero_life = 3
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
# INPUT
# ==========================================================

key_to_note = {
    pygame.K_c: "C3",
    pygame.K_d: "D3",
    pygame.K_e: "E3",
    pygame.K_f: "F3",
    pygame.K_g: "G3",
    pygame.K_a: "A3",
    pygame.K_b: "B3"
}

# ==========================================================
# FONT
# ==========================================================

hud_font = pygame.font.SysFont("Arial", 24)
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

# ==========================================================
# ADATTAMENTO ALLA FINESTRA (chatgpt)
# ==========================================================

def draw_scaled_game():
    screen_width, screen_height = window.get_size()
    scale = min(screen_width / WORLD_WIDTH,screen_height / WORLD_HEIGHT)
    scaled_width = int(WORLD_WIDTH * scale)
    scaled_height = int(WORLD_HEIGHT * scale)
    scaled_surface = pygame.transform.smoothscale(game_surface,(scaled_width, scaled_height))
    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2
    window.fill((0, 0, 0))
    window.blit(scaled_surface,(x, y))

# ==========================================================
# MAIN
# ==========================================================

def main():
    global hero_life
    global played_note
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in key_to_note:
                    played_note = key_to_note[event.key]
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
                enemy_y = random.randint(0,WORLD_HEIGHT - enemy_size)

            # DESTRA
            elif side == 2:
                enemy_x = WORLD_WIDTH
                enemy_y = random.randint(0,WORLD_HEIGHT - enemy_size)

            # ALTO
            elif side == 3:
                enemy_x = random.randint(0,WORLD_WIDTH - enemy_size)
                enemy_y = -enemy_size

            # BASSO
            else:
                enemy_x = random.randint(0,WORLD_WIDTH - enemy_size)
                enemy_y = WORLD_HEIGHT

            enemy_rect = pygame.Rect(enemy_x,enemy_y,enemy_size,enemy_size)
            enemy_note = random.choice(notes)

            # Direzione calcolata una sola volta alla nascita (chatgpt)
            direction = pygame.Vector2(
                hero_rect.centerx - enemy_rect.centerx,
                hero_rect.centery - enemy_rect.centery
            )

            if direction.length() != 0:
                direction = direction.normalize()

            # Posizione in virgola mobile per mantenere
            # precisione durante il movimento
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
            spawn_interval = random.randint(1000, 3000)


        # ==================================================
        # MOVIMENTO NEMICI
        # ==================================================

        for enemy in enemies:
            enemy_rect = enemy[0]
            enemy_position = enemy[2]
            enemy_direction = enemy[3]
            enemy_position += (enemy_direction * enemy_velocity)
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
            ) # chatgpt

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
        played_note = ""

        # ==================================================
        # GAME OVER
        # ==================================================

        if hero_life <= 0:
            print("L'eroe è morto!")
            running = False

        # ==================================================
        # DISEGNO
        # ==================================================

        game_surface.blit(background,(0, 0))

        # HUD
        life_text = hud_font.render(f"Vite: {hero_life}",True,(255, 255, 255))
        game_surface.blit(life_text,(20, 20))

        # NEMICI
        for enemy in enemies:
            enemy_rect = enemy[0]
            enemy_note = enemy[1]
            pygame.draw.rect(game_surface,(255, 0, 0),enemy_rect)
            text = font.render(enemy_note,True,(255, 255, 255))
            text_rect = text.get_rect(center=(enemy_rect.centerx,enemy_rect.top - 15))
            game_surface.blit(text,text_rect)

        # EROINA
        hero_image_rect = hero_image.get_rect(center=hero_rect.center)
        game_surface.blit(hero_image,hero_image_rect)

        # ==================================================
        # VISUALIZZAZIONE
        # ==================================================

        draw_scaled_game()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

main()
