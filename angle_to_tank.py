from typing import Tuple
from helpers import translate


def angle_to_tank(angle: int, speed: int) -> Tuple[int, int]:
    translated = translate(angle, -90, 90, -1, 1)
    left_speed = speed
    right_speed = speed