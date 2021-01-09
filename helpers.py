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