from typing import Optional, Any, Dict, Callable, TypeVar, Union

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


def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)