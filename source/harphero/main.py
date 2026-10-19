import pygame
import random
import sys
from pathlib import Path
from Modulo_audio import pitch_sample, sample_energy, sample_attack
from Modulo_MIDI import read_midi, midi_devices, select_midi_device

# ==========================================================
# PERCORSI (chatgpt)
# ==========================================================

if getattr(sys, "frozen", False):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(__file__).resolve().parent

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

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
# AUDIO + DIZIONARI NOTE E INTERVALLI
# ==========================================================

sample = pygame.mixer.Sound(BASE_PATH / "Hp-ord-C3-ff-N-N.wav")

notes = [
    "C3",
    "D3",
    "E3",
    "F3",
    "G3",
    "A3",
    "B3",
    "C4"
]

altered_notes = [
    "C#3",
    "D#3",
    "F#3",
    "G#3",
    "A#3"
]

note_semitones = {
    "C3": 0,
    "C#3": 1,
    "D3": 2,
    "D#3": 3,
    "E3": 4,
    "F3": 5,
    "F#3": 6,
    "G3": 7,
    "G#3": 8,
    "A3": 9,
    "A#3": 10,
    "B3": 11,
    "C4": 12
}

interval_semitones = {
    "2m": 1,
    "2M": 2,
    "3m": 3,
    "3M": 4,
    "4G": 5,
    "5G": 7,
    "6m": 8,
    "6M": 9,
    "7m": 10,
    "7M": 11,
    "8G": 12
}

harp_sounds = {}

for note in notes:
    harp_sounds[note] = pitch_sample(sample,note_semitones[note])

for note in altered_notes:
    harp_sounds[note] = pitch_sample(sample,note_semitones[note])

# ==========================================================
# GRAFICA
# ==========================================================

background = pygame.image.load(BASE_PATH / "sfondo.png").convert()
background = pygame.transform.scale(background,(WORLD_WIDTH, WORLD_HEIGHT))
target_image = pygame.image.load(BASE_PATH / "mirino.png").convert_alpha()
target_image = pygame.transform.scale(target_image,(80, 80))
plus_one_image = pygame.image.load(BASE_PATH / "+1.png").convert_alpha()
plus_one_image = pygame.transform.scale(plus_one_image,(120, 120))

# ==========================================================
# EROE
# ==========================================================

hero_rect = pygame.Rect(0, 0, 180, 180)
hero_image = pygame.image.load(BASE_PATH / "Eroe_idle.png").convert_alpha()
hero_image = pygame.transform.scale(hero_image,(hero_rect.width, hero_rect.height))
hero_rect.center = (WORLD_WIDTH // 2,WORLD_HEIGHT // 2)
hero_life = 100
played_note = ""
interval_progress = 0
interval_target = None
interval_start_time = 0
first_bicord_note = ""
bicord_tolerance = 100

# ==========================================================
# NEMICI
# ==========================================================

enemies = []
enemy_size = 40
enemies_killed = 0
enemy_speed = 1
threshold_kill = 10
last_spawn = 0
spawn_interval = random.randint(1000, 3000)
enemy_rect = pygame.Rect(0, 0, 150, 150)
enemy_image = pygame.image.load(BASE_PATH / "Nemico_idle.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image,(enemy_rect.width, enemy_rect.height))
kill_effects = []

# ==========================================================
# INPUT
# ==========================================================

key_to_note = {
    pygame.K_a: "C3",
    pygame.K_w: "C#3",
    pygame.K_s: "D3",
    pygame.K_e: "D#3",
    pygame.K_d: "E3",
    pygame.K_f: "F3",
    pygame.K_t: "F#3",
    pygame.K_g: "G3",
    pygame.K_y: "G#3",
    pygame.K_h: "A3",
    pygame.K_u: "A#3",
    pygame.K_j: "B3",
    pygame.K_k: "C4"
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
# MENÙ PRINCIPALE 
# ==========================================================

running = True
difficulty = ""
show_intermediate_intro = False
while difficulty == "":
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = "Facile"
            elif event.key == pygame.K_2:
                difficulty = "Intermedio"
                show_intermediate_intro = True
            elif event.key == pygame.K_3:
                difficulty = "Difficile"

    # ==========================================================
    # GRAFICA MENÙ PRINCIPALE 
    # ==========================================================

    game_surface.blit(background,(0, 0))
    vertical_offset = 0
    for text in ["Harp Hero", "1: Facile", "2: Intermedio", "3: Difficile"]:
        title_text = hud_font.render(text, True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WORLD_WIDTH // 2, WORLD_HEIGHT // 4 + vertical_offset))
        game_surface.blit(title_text, title_rect)
        vertical_offset += 50
    draw_scaled_game()
    pygame.display.flip()
    clock.tick(FPS)

# ==========================================================
# MAIN
# ==========================================================

selected_midi = False

while not selected_midi:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0:
                select_midi_device(None)
                selected_midi = True
            elif event.unicode.isdigit():
                choice = int(event.unicode) - 1
                if 0 <= choice < len(midi_devices):
                    select_midi_device(midi_devices[choice][0])
                    selected_midi = True

    game_surface.blit(background, (0, 0))

    title = hud_font.render("SELEZIONA IL DISPOSITIVO MIDI", True, (255, 215, 100))
    game_surface.blit(title, title.get_rect(center=(WORLD_WIDTH // 2, 250)))

    no_midi_text = font.render("0 - Gioca senza tastiera MIDI", True, (255, 255, 255))
    game_surface.blit(no_midi_text, no_midi_text.get_rect(center=(WORLD_WIDTH // 2, 350)))

    for i, (device_id, device_name) in enumerate(midi_devices[:9]):
        device_text = font.render(f"{i + 1} - {device_name}", True, (255, 255, 255))
        device_rect = device_text.get_rect(center=(WORLD_WIDTH // 2, 420 + i * 50))
        game_surface.blit(device_text, device_rect)

    draw_scaled_game()
    pygame.display.flip()
    clock.tick(FPS)
    
while show_intermediate_intro:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                show_intermediate_intro = False
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    game_surface.blit(background,(0, 0))
   
    title = hud_font.render("LIVELLO INTERMEDIO -GLI INTERVALLI-", True, (255, 215, 100))
    game_surface.blit(title, title.get_rect(center=(WORLD_WIDTH // 2, 100)))

    intro_lines = [
        "Un intervallo musicale e' la distanza in altezza tra due note.",
        "Si identifica attraverso il numero di gradi e la distanza in semitoni.",
        "",
        "FASE 1 - INTERVALLI MELODICI (0-49 KILL)",
        "C3 -> E3",
        "Suona le due note una dopo l'altra, nell'ordine indicato.",
        "",
        "FASE 2 - BICORDI (DA 50 KILL)",
        "(C3, E3)",
        "Suona le due note contemporaneamente.",
        "",
        "Segui il mirino per individuare il nemico da eliminare.",
        "",
        "PREMI INVIO PER INIZIARE"
    ]

    for i, line in enumerate(intro_lines):
        color = (255, 215, 100) if "FASE" in line or "PREMI INVIO" in line else (255, 255, 255)
        text = font.render(line, True, color)
        text_rect = text.get_rect(center=(WORLD_WIDTH // 2, 270 + i * 45))
        game_surface.blit(text, text_rect)

    draw_scaled_game()
    pygame.display.flip()
    clock.tick(FPS)

def main():
    global hero_life
    global played_note
    global interval_progress
    global interval_target
    global interval_start_time
    global first_bicord_note
    global last_spawn
    global spawn_interval
    global enemies_killed
    global enemy_speed
    global threshold_kill
    running = True

        # ==================================================
        # EVENTI
        # ==================================================
   
    while running:
        played_notes = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in key_to_note:
                    played_note = key_to_note[event.key]
                    played_notes.append(played_note)
                    processed_sound = sample_energy(harp_sounds[played_note], hero_life)
                    processed_sound = sample_attack(processed_sound, hero_life)
                    processed_sound.play()
        for midi_note in read_midi():
            played_notes.append(midi_note)
            if midi_note in harp_sounds:
                played_note = midi_note
                processed_sound = sample_energy(harp_sounds[played_note], hero_life)
                processed_sound = sample_attack(processed_sound, hero_life)
                processed_sound.play()
                
        # ==================================================
        # SPAWN NEMICO
        # ==================================================
        
        current_time = pygame.time.get_ticks()
        if current_time - last_spawn >= spawn_interval and len(enemies) < 6:
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

            if difficulty == "Facile":
                if enemies_killed < 30:
                    enemy_note = random.choice(notes)
                else:
                    enemy_note = random.choice(notes + altered_notes)
            elif difficulty == "Intermedio":
                second_semitone = 13
                while second_semitone > 12:
                    if enemies_killed < 30:
                        first_note = random.choice(notes)
                    else:
                        first_note = random.choice(notes + altered_notes)
                    interval = random.choice(list(interval_semitones.keys()))
                    second_semitone = note_semitones[first_note] + interval_semitones[interval]
                for note in note_semitones:
                    if note_semitones[note] == second_semitone:
                        second_note = note
                enemy_note = (first_note, second_note)

            # Direzione calcolata una sola volta alla nascita (chatgpt)
            direction = pygame.Vector2(
                hero_rect.centerx - enemy_rect.centerx,
                hero_rect.centery - enemy_rect.centery
            )

            if direction.length() != 0:
                direction = direction.normalize()

            # Posizione in virgola mobile per mantenere
            # precisione durante il movimento (chatgpt)
            enemy_position = pygame.Vector2(
                enemy_rect.x,
                enemy_rect.y
            )

            enemy_components = [enemy_rect, enemy_note, enemy_position, direction]
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
            enemy_position += (enemy_direction * enemy_speed)
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

        # =============================================================
        # NOTA CORRETTA + AUMENTO VELOCITÀ NEMICI + CONTROLLO VITTORIA
        # =============================================================

        if interval_target is not None and not any(enemy is interval_target for enemy in enemies):
            interval_progress = 0
            interval_target = None
        if nearest_enemy is not None:
            if difficulty == "Facile":
                if played_note == nearest_enemy[1]:
                    kill_effects.append([nearest_enemy[0].centerx, nearest_enemy[0].centery, pygame.time.get_ticks()])
                    enemies.remove(nearest_enemy)
                    enemies_killed += 1
            elif difficulty == "Intermedio":
                if enemies_killed < 50:
                    if played_note != "":
                        if interval_progress == 0:
                            if played_note == nearest_enemy[1][0]:
                                interval_progress = 1
                                interval_target = nearest_enemy
                        elif interval_progress == 1:
                            if played_note == interval_target[1][1]:
                                kill_effects.append([nearest_enemy[0].centerx, nearest_enemy[0].centery, pygame.time.get_ticks()])
                                enemies.remove(interval_target)
                                enemies_killed += 1
                                interval_progress = 0
                                interval_target = None
                            else:
                                interval_progress = 0
                                interval_target = None
                else:
                    if interval_progress == 1:
                        if pygame.time.get_ticks() - interval_start_time > bicord_tolerance:
                            interval_progress = 0
                            interval_target = None
                    for played_note in played_notes:
                        if interval_progress == 0:
                            if played_note in nearest_enemy[1]:
                                interval_progress = 1
                                interval_target = nearest_enemy
                                interval_start_time = pygame.time.get_ticks()
                                first_bicord_note = played_note
                        elif interval_progress == 1:
                            if played_note in interval_target[1] and played_note != first_bicord_note:
                                kill_effects.append([interval_target[0].centerx, interval_target[0].centery, pygame.time.get_ticks()])
                                enemies.remove(interval_target)
                                enemies_killed += 1
                                interval_progress = 0
                                interval_target = None
                                break
                            else:
                                interval_progress = 0
                                interval_target = None
        if difficulty != "Difficile" and enemies_killed >= 100:
            print("Hai vinto!")
            running = False
        if difficulty == "Facile" and enemies_killed <= 50:
            if enemies_killed >= threshold_kill:
                enemy_speed += 1
                threshold_kill += 10
        if difficulty == "Intermedio":
            if enemies_killed < 50 and enemies_killed >= threshold_kill:
                enemy_speed += 0.5
                threshold_kill += 10
                print(enemy_speed)
                print(enemies_killed)
            if enemies_killed == 50 and threshold_kill == 50:
                enemy_speed = 3
                threshold_kill = 60
                print(enemy_speed)
                print(enemies_killed)
            if enemies_killed > 50 and threshold_kill <= 80 and enemies_killed >= threshold_kill:
                enemy_speed += 0.5
                threshold_kill += 10
                print(enemy_speed)
                print(enemies_killed)
        if difficulty == "Difficile":
            if enemies_killed < 50 and enemies_killed >= threshold_kill:
                enemy_speed += 2
                threshold_kill += 10
            if enemies_killed == 50 and threshold_kill == 50:
                enemy_speed = 9
                threshold_kill = 60
            if enemies_killed > 50 and enemies_killed >= threshold_kill:
                enemy_speed += 3
                threshold_kill += 10

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
        kill_text = hud_font.render(f"Kill: {enemies_killed}",True,(255, 255, 255))
        game_surface.blit(kill_text,(20, 60))

        # NEMICI
        for enemy in enemies:
            enemy_rect = enemy[0]
            enemy_note = enemy[1]
            enemy_image_rect = enemy_image.get_rect(center=enemy_rect.center)
            game_surface.blit(enemy_image,enemy_image_rect)
            first_note_color = (255, 255, 255)
            if difficulty == "Facile":
                text = font.render(enemy_note,True,(255, 255, 255))
                text_rect = text.get_rect(center=(enemy_rect.centerx,enemy_rect.top - 15))
                game_surface.blit(text,text_rect)
            elif difficulty == "Intermedio":
                if enemies_killed < 50:
                    first_note_color = (255, 255, 255)
                    if interval_progress == 1 and interval_target is enemy:
                        first_note_color = (0, 255, 0)
                    first_text = font.render(enemy_note[0], True, first_note_color)
                    arrow_text = font.render(" -> ", True, (255, 255, 255))
                    second_text = font.render(enemy_note[1], True, (255, 255, 255))
                    total_width = first_text.get_width() + arrow_text.get_width() + second_text.get_width()
                    start_x = enemy_rect.centerx - total_width / 2
                    text_y = enemy_rect.top - 35
                    game_surface.blit(first_text, (start_x, text_y))
                    game_surface.blit(arrow_text, (start_x + first_text.get_width(), text_y))
                    game_surface.blit(second_text, (start_x + first_text.get_width() + arrow_text.get_width(), text_y))
                else:
                    interval_text = str(enemy_note)
                    text = font.render(interval_text, True, (255, 255, 255))
                    text_rect = text.get_rect(midbottom=(enemy_rect.centerx, enemy_rect.top - 10))
                    game_surface.blit(text, text_rect)
        target_enemy = nearest_enemy
        if interval_progress == 1 and interval_target is not None:
            target_enemy = interval_target
        if target_enemy is not None:
            target_rect = target_image.get_rect(center=target_enemy[0].center)
            game_surface.blit(target_image, target_rect)

        # EFFETTO +1

        for effect in kill_effects[:]:
            elapsed_time = pygame.time.get_ticks() - effect[2]
            if elapsed_time >= 1000:
                kill_effects.remove(effect)
            else:
                progress = elapsed_time / 1000
                effecct_image = plus_one_image.copy()
                effecct_image.set_alpha(255 * (1 - progress))
                effect_rect = effecct_image.get_rect(center=(effect[0], effect[1] - progress * 60))
                game_surface.blit(effecct_image, effect_rect)

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