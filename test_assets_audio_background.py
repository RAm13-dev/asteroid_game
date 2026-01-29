"""Tests for assets, audio, and background helpers."""
import math
import os

import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"

from pygame_fallback import ensure_pygame

pygame = ensure_pygame()
pygame.init()

if not hasattr(pygame, "mixer"):
    class _DummySound:
        def __init__(self, *args, **kwargs):
            return None

        def play(self, *args, **kwargs):
            return None

        def set_volume(self, *args, **kwargs):
            return None

    class _DummyMixer:
        Sound = _DummySound

        @staticmethod
        def init(*args, **kwargs):
            return None

    pygame.mixer = _DummyMixer()

import assets
import audio
from background import BackgroundLayer, BackgroundParticle
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


def _surface_size(surface):
    if hasattr(surface, "get_size"):
        return surface.get_size()
    return surface.size


class TestAssets:
    def test_load_sprite_caches_by_name_and_size(self):
        first = assets.load_sprite("__missing_sprite__", size=16)
        second = assets.load_sprite("__missing_sprite__", size=16)
        assert first is second

    def test_load_sprite_uses_requested_size(self):
        surface = assets.load_sprite("__missing_sprite__", size=(12, 18))
        assert _surface_size(surface) == (12, 18)

    def test_load_sprite_sheet_builds_expected_frames(self):
        frames = assets.load_sprite_sheet("__missing_sheet__", (8, 6), columns=3, rows=2)
        assert len(frames) == 6
        for frame in frames:
            assert _surface_size(frame) == (8, 6)


class TestAudio:
    def test_clamp_limits_samples(self):
        assert audio._clamp(2.0) == 32767
        assert audio._clamp(-2.0) == -32768
        assert audio._clamp(0.5) == 16383

    def test_build_wave_returns_stereo_frames(self):
        duration = 0.01
        data = audio._build_wave(duration, lambda _t: 0.25)
        expected_frames = int(audio.SAMPLE_RATE * duration)
        assert len(data) == expected_frames * 2
        assert max(data) <= 32767
        assert min(data) >= -32768

    def test_play_sound_noop_when_audio_not_ready(self):
        audio.play_sound("shoot")


class TestBackground:
    def test_particle_wraps_and_twinkles(self):
        particle = BackgroundParticle(
            SCREEN_WIDTH - 1,
            SCREEN_HEIGHT - 1,
            radius=1.0,
            color=(255, 255, 255),
            base_alpha=120,
            twinkle_speed=1.5,
            phase=math.tau - 0.1,
        )
        particle.update(1.0, velocity=(5.0, 7.0))

        assert 0 <= particle.x < SCREEN_WIDTH
        assert 0 <= particle.y < SCREEN_HEIGHT
        assert 0 <= particle.phase < math.tau

    def test_layer_builds_particles_and_updates(self):
        layer = BackgroundLayer(
            particle_count=3,
            speed=10.0,
            radius_range=(1.0, 2.0),
            color_range=((10, 20, 30), (40, 50, 60)),
            alpha_range=(100, 140),
            twinkle_speed_range=(0.2, 0.4),
            drift=(1.0, 0.0),
        )
        assert len(layer.particles) == 3
        initial_x = layer.particles[0].x
        layer.update(0.5)
        assert layer.particles[0].x != pytest.approx(initial_x)
