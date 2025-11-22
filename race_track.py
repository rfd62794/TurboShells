import random
from settings import TRACK_LENGTH_LOGIC

SEGMENT_LENGTH = 10


def generate_track(length: int | None = None):
    """Generate a simple terrain track as a list of terrain types.

    Uses probabilities similar to the original simulation:
      - ~60% grass
      - ~20% water
      - ~20% rock
    """
    if length is None:
        length = TRACK_LENGTH_LOGIC

    segment_count = int(length / SEGMENT_LENGTH) + 100
    track = []
    for _ in range(segment_count):
        r = random.random()
        if r < 0.6:
            track.append("grass")
        elif r < 0.8:
            track.append("water")
        else:
            track.append("rock")
    return track


def get_terrain_at(track, distance: float) -> str:
    """Return terrain type for a given logical race distance."""
    if not track:
        return "grass"
    idx = int(distance / SEGMENT_LENGTH)
    if idx < 0:
        idx = 0
    if idx >= len(track):
        idx = len(track) - 1
    return track[idx]
