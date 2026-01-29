import math
import random
from array import array
from typing import Dict, Optional

import pygame

SAMPLE_RATE = 44100
CHANNELS = 2

_AUDIO_READY = False
_SOUNDS: Dict[str, pygame.mixer.Sound] = {}
_MUSIC: Optional[pygame.mixer.Sound] = None


def _clamp(sample: float) -> int:
    return max(-32768, min(32767, int(sample * 32767)))


def _build_wave(duration_s: float, sample_fn) -> array:
    frames = int(SAMPLE_RATE * duration_s)
    data = array("h")
    for idx in range(frames):
        t = idx / SAMPLE_RATE
        sample = sample_fn(t)
        value = _clamp(sample)
        data.append(value)
        data.append(value)
    return data


def _tone(freq: float, duration_s: float, volume: float = 0.7) -> pygame.mixer.Sound:
    data = _build_wave(duration_s, lambda t: math.sin(2 * math.pi * freq * t) * volume)
    return pygame.mixer.Sound(buffer=data.tobytes())


def _laser(duration_s: float = 0.18) -> pygame.mixer.Sound:
    def sample(t: float) -> float:
        sweep = 900 - 600 * (t / duration_s)
        return math.sin(2 * math.pi * sweep * t) * (1 - t / duration_s) * 0.8

    data = _build_wave(duration_s, sample)
    return pygame.mixer.Sound(buffer=data.tobytes())


def _noise_burst(duration_s: float = 0.35, volume: float = 0.8) -> pygame.mixer.Sound:
    def sample(t: float) -> float:
        decay = (1 - t / duration_s) ** 2
        return random.uniform(-1, 1) * decay * volume

    data = _build_wave(duration_s, sample)
    return pygame.mixer.Sound(buffer=data.tobytes())


def _impact(duration_s: float = 0.22) -> pygame.mixer.Sound:
    def sample(t: float) -> float:
        base = 140 + 60 * math.sin(2 * math.pi * 2 * t)
        return math.sin(2 * math.pi * base * t) * (1 - t / duration_s) * 0.7

    data = _build_wave(duration_s, sample)
    return pygame.mixer.Sound(buffer=data.tobytes())


def _ambient_loop(duration_s: float = 6.0) -> pygame.mixer.Sound:
    def sample(t: float) -> float:
        chord = (
            math.sin(2 * math.pi * 110 * t)
            + 0.6 * math.sin(2 * math.pi * 165 * t)
            + 0.4 * math.sin(2 * math.pi * 220 * t)
        )
        wobble = 0.6 + 0.4 * math.sin(2 * math.pi * 0.2 * t)
        return chord * wobble * 0.18

    data = _build_wave(duration_s, sample)
    return pygame.mixer.Sound(buffer=data.tobytes())


def init_audio() -> None:
    global _AUDIO_READY, _SOUNDS, _MUSIC
    if _AUDIO_READY:
        return
    try:
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=CHANNELS, buffer=512)
    except pygame.error:
        _AUDIO_READY = False
        return

    _SOUNDS = {
        "shoot": _laser(),
        "explode": _noise_burst(),
        "hit": _impact(),
        "ui": _tone(520, 0.12, 0.5),
    }
    _SOUNDS["shoot"].set_volume(0.35)
    _SOUNDS["explode"].set_volume(0.5)
    _SOUNDS["hit"].set_volume(0.45)
    _SOUNDS["ui"].set_volume(0.25)

    _MUSIC = _ambient_loop()
    _MUSIC.set_volume(0.25)
    _AUDIO_READY = True


def play_sound(name: str) -> None:
    if not _AUDIO_READY:
        return
    sound = _SOUNDS.get(name)
    if sound is None:
        return
    sound.play()


def play_music() -> None:
    if not _AUDIO_READY or _MUSIC is None:
        return
    _MUSIC.play(loops=-1)


def stop_music() -> None:
    if _MUSIC is None:
        return
    _MUSIC.stop()
