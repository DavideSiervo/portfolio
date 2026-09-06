import pygame
import random
from Modulo_audio import pitch_sample

pygame.init()
pygame.mixer.init()
odyssey_sound = pygame.mixer.Sound("odysseyC3.wav")

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

window_width = 1920
window_height = 1080

window = pygame.display.set_mode((window_width, window_height))

# EROE
hero_rect = pygame.Rect(0, 0, 60, 60)
hero_rect.center = (window_width // 2, window_height // 2)

hero_life = 3

played_note = ""

# NEMICI
enemies = []

enemy_size = 40
enemy_velocity = 3

last_spawn = 0
spawn_interval = random.randint(1000, 3000)

# NOTA
notes = ["C3", "D3", "E3", "F3", "G3", "A3", "B3"]

for note in notes:
    harp_sounds[note] = pitch_sample(odyssey_sound, note_semitones[note])

font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                played_note = "C3"
                harp_sounds[played_note].play()
            if event.key == pygame.K_d:
                played_note = "D3"
                harp_sounds[played_note].play()
            if event.key == pygame.K_e:
                played_note = "E3"
                harp_sounds[played_note].play()
            if event.key == pygame.K_f:
                played_note = "F3"
                harp_sounds[played_note].play()
            if event.key == pygame.K_g:
                played_note = "G3"
                harp_sounds[played_note].play()
            if event.key == pygame.K_a:
                played_note = "A3"
                harp_sounds[played_note].play()
            if event.key == pygame.K_b:
                played_note = "B3"
                harp_sounds[played_note].play()

        if event.type == pygame.QUIT:
            exit()

    current_time = pygame.time.get_ticks()

    # SPAWN NEMICO
    if current_time - last_spawn >= spawn_interval:

        side = random.randint(1, 4)

        # Sinistra
        if side == 1:
            enemy_x = -enemy_size
            enemy_y = random.randint(0, window_height - enemy_size)

        # Destra
        elif side == 2:
            enemy_x = window_width
            enemy_y = random.randint(0, window_height - enemy_size)

        # Alto
        elif side == 3:
            enemy_x = random.randint(0, window_width - enemy_size)
            enemy_y = -enemy_size

        # Basso
        else:
            enemy_x = random.randint(0, window_width - enemy_size)
            enemy_y = window_height

        enemy_rect = pygame.Rect(
            enemy_x,
            enemy_y,
            enemy_size,
            enemy_size
        )

        enemy_note = random.choice(notes)
        enemy_components = [enemy_rect, enemy_note]
        enemies.append(enemy_components)

        last_spawn = current_time
        spawn_interval = random.randint(1000, 3000)

    # MOVIMENTO NEMICI
    for enemy in enemies:
        enemy_rect = enemy[0]
        enemy_note = enemy[1]

        direction = pygame.Vector2(
            hero_rect.centerx - enemy_rect.centerx,
            hero_rect.centery - enemy_rect.centery
        )

        if direction.length() != 0:
            direction = direction.normalize()

            enemy_rect.x += direction.x * enemy_velocity
            enemy_rect.y += direction.y * enemy_velocity

    # COLLISIONI
    for enemy in enemies[:]:
        enemy_rect = enemy[0]

        if enemy_rect.colliderect(hero_rect):

            print("Il nemico ha colpito l'eroe!")

            hero_life -= 1

            enemies.remove(enemy)

            print("Vite:", hero_life)

    # TARGET
    nearest_enemy = None
    nearest_distance = None

    for enemy in enemies:
        enemy_rect = enemy[0]
        enemy_note = enemy[1]

        distance = pygame.Vector2(enemy_rect.center).distance_to(hero_rect.center)

        if nearest_distance == None:
            nearest_distance = distance
            nearest_enemy = enemy
        else:
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = enemy 

    if nearest_enemy != None:
        if played_note == nearest_enemy[1]:
            enemies.remove(nearest_enemy)

    played_note = ""

    # print(nearest_enemy[1])

    # GAME OVER
    if hero_life <= 0:
        print("L'eroe è morto!")
        exit()

    # DISEGNO
    window.fill((0, 0, 0))

    for enemy in enemies:
        enemy_rect = enemy[0]
        enemy_note = enemy[1]

        pygame.draw.rect(
            window,
            (255, 0, 0),
            enemy_rect
        )

        text = font.render(enemy_note, True, (255, 255, 255))

        text_rect = text.get_rect(
        center=(enemy_rect.centerx, enemy_rect.top - 15)
        )

        window.blit(text, text_rect)

    pygame.draw.rect(
        window,
        (0, 255, 0),
        hero_rect
    )

    pygame.display.flip()

    clock.tick(60)