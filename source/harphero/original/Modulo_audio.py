import pygame
import numpy as np


def pitch_sample(sound, semitones):
    ratio = 2 ** (semitones / 12)

    original = pygame.sndarray.array(sound)

    original_length = len(original)
    new_length = int(original_length / ratio)

    old_positions = np.arange(original_length)
    new_positions = np.linspace(
        0,
        original_length - 1,
        new_length
    )

    if original.ndim == 2:
        left = np.interp(
            new_positions,
            old_positions,
            original[:, 0]
        )

        right = np.interp(
            new_positions,
            old_positions,
            original[:, 1]
        )

        resampled = np.column_stack((left, right))

    resampled = resampled.astype(original.dtype)

    return pygame.sndarray.make_sound(resampled)