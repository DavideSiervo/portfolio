import pygame
import numpy as np
import random
import math

def pitch_sample(sound, semitones):
    ratio = 2 ** (semitones / 12)
    original = pygame.sndarray.array(sound)
    original_length = len(original)
    new_length = int(original_length / ratio)
    old_positions = np.arange(original_length)
    new_positions = np.linspace(0,original_length - 1,new_length)
    if original.ndim == 1:
        resampled = np.interp(new_positions, old_positions, original)
    elif original.ndim == 2:
        left = np.interp(new_positions, old_positions, original[:, 0])
        right = np.interp(new_positions, old_positions, original[:, 1])
        resampled = np.column_stack((left, right))
    resampled = resampled.astype(original.dtype) # chatgpt
    return pygame.sndarray.make_sound(resampled)

def sample_energy(sound, lives):
    if lives >= 50:
        amplitude = 1.0
    elif lives >= 20:
        amplitude = 0.7
    elif lives >= 10:
        amplitude = 0.4
    else:
        amplitude = 0.25
    original = pygame.sndarray.array(sound)
    modified = (original * amplitude).astype(original.dtype)
    return pygame.sndarray.make_sound(modified)

def sample_attack(sound, lives):
    original = pygame.sndarray.array(sound)
    if lives >= 50:
        attack_ms = random.randint(0, 5)
    elif lives >= 20:
        attack_ms = random.randint(10, 15)
    else:
        attack_ms = random.randint(15, 20)
    sample_rate = pygame.mixer.get_init()[0]
    attack_samples = int(sample_rate * (attack_ms / 1000))
    if attack_samples > 0:
        attack_envelope = np.linspace(0, 1, attack_samples)
        modified = original.copy()
        modified[:attack_samples] = (modified[:attack_samples].T * attack_envelope).T.astype(original.dtype)
    else:
        modified = original
    return pygame.sndarray.make_sound(modified)
    
    
    


