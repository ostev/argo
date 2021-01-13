from typing import Tuple
from helpers import translate


def angle_to_tank(angle: int, throttle: float) -> Tuple[float, float]:
    if angle >= 85:
        return (1, -1)
    elif angle <= -85:
        return (-1, 1)
    else:
        translatedSteering = translate(angle, -90, 90, -1, 1)
        left_speed = throttle
        right_speed = throttle

        if translatedSteering < 0:
            left_speed *= 1.0 - (-translatedSteering)
        elif translatedSteering > 0:
            right_speed *= 1.0 - translatedSteering

        return (round(left_speed, 2), round(right_speed, 2))