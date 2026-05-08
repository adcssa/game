from __future__ import annotations

import math
import struct
import wave
from pathlib import Path


OUTPUT = Path(__file__).resolve().parent / "bgm.wav"
SAMPLE_RATE = 44100
DURATION = 28
VOLUME = 0.22


def envelope(position: int, total: int) -> float:
    fade = int(SAMPLE_RATE * 1.2)
    if position < fade:
        return position / fade
    if position > total - fade:
        return max(0.0, (total - position) / fade)
    return 1.0


def note_frequency(semitone: int) -> float:
    return 220.0 * (2 ** (semitone / 12))


def melody_segments() -> list[tuple[int, float]]:
    return [
        (0, 1.6),
        (3, 1.2),
        (5, 1.2),
        (7, 1.6),
        (10, 1.0),
        (7, 1.4),
        (5, 1.4),
        (3, 1.6),
        (0, 1.6),
        (-2, 1.2),
        (0, 1.2),
        (3, 1.6),
        (5, 1.2),
        (7, 1.6),
        (3, 1.6),
        (0, 2.0),
    ]


def build_music() -> bytes:
    total_frames = SAMPLE_RATE * DURATION
    data = bytearray()
    segments = melody_segments()
    segment_frames = []
    for note, seconds in segments:
        segment_frames.append((note_frequency(note), int(seconds * SAMPLE_RATE)))

    segment_cursor = 0
    segment_index = 0
    current_freq, current_length = segment_frames[segment_index]

    for frame in range(total_frames):
        if segment_cursor >= current_length:
            segment_index = (segment_index + 1) % len(segment_frames)
            current_freq, current_length = segment_frames[segment_index]
            segment_cursor = 0

        t = frame / SAMPLE_RATE
        lead = math.sin(2 * math.pi * current_freq * t)
        pad = math.sin(2 * math.pi * (current_freq / 2) * t)
        shimmer = math.sin(2 * math.pi * (current_freq * 1.5) * t)
        wobble = 0.85 + 0.15 * math.sin(2 * math.pi * 0.18 * t)
        sample = VOLUME * envelope(frame, total_frames) * wobble * (0.58 * lead + 0.28 * pad + 0.14 * shimmer)
        packed = struct.pack("<h", max(-32767, min(32767, int(sample * 32767))))
        data.extend(packed)
        segment_cursor += 1

    return bytes(data)


def main() -> None:
    music = build_music()
    with wave.open(str(OUTPUT), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(music)


if __name__ == "__main__":
    main()
