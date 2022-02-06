from typing import Tuple
from helpers import map_range


def angle_to_tank(angle: float, throttle: float) -> Tuple[float, float]:
    if angle == 1:
        return (throttle, throttle * -1)
    elif angle == -1:
        return (throttle * -1, throttle)
    else:
        left_speed = throttle
        right_speed = throttle

        if angle < 0:
            left_speed *= 1.0 - (-angle)
        elif angle > 0:
            right_speed *= 1.0 - angle

        return (round(left_speed, 2), round(right_speed, 2))
