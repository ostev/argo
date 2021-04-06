from typing import Optional, Any, Dict, Callable, TypeVar, Union, Tuple

T1 = TypeVar("T1")
T2 = TypeVar("T2")

# ANSI colour code sequences
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
BLUE = "\033[1;34m"
RESET = "\033[0m"


def clamp(value: float, minimum: float, maximum: float):
    return min(maximum, max(value, minimum))


def switch(
    cases: Dict[Callable[[T1], bool], Callable[[T1], T2]], value: T1
) -> Optional[T2]:
    match: Optional[T2] = None
    for key in cases:
        if key(value):
            match = cases[key](value)
            break
    return match


default = lambda _: True

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def angle_to_tank(angle: int, throttle: float) -> Tuple[float, float]:
    if angle == 90:
        return (throttle, throttle * -1)
    elif angle == -90:
        return (throttle * -1, throttle)
    else:
        translatedSteering = map_range(angle, -90, 90, -1, 1)
        left_speed = throttle
        right_speed = throttle

        if translatedSteering < 0:
            left_speed *= 1.0 - (-translatedSteering)
        elif translatedSteering > 0:
            right_speed *= 1.0 - translatedSteering

        return (round(left_speed, 2), round(right_speed, 2))