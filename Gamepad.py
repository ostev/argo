from typing import Dict, Union, Tuple
from enum import Enum

from helpers import map_range, switch

from inputs import get_gamepad


class EventType(Enum):
    key = "key",
    axis = "axis"


Event = Tuple[EventType, str, Union[bool, float]]


class Gamepad:
    names: Dict[str, str] = {}

    def transformRawEvent(self, rawEvent) -> Event:
        type_ = switch({
            (lambda x: True if x == "Key" or x == "Absolute" else False):
                (lambda x: EventType.key if x == "Key" else EventType.axis)
        }, rawEvent.ev_type)

        name = None

        try:
            name = self.names[rawEvent.code]
        except KeyError:
            pass

        value = (map_range(rawEvent.state,
                           0,
                           255,
                           0,
                           1) - 0.5) * 2\
            if type_ == EventType.axis \
            else (True if rawEvent.state == 1 else False)

        return (type_, name, value) if name != None and type_ != None else None

    def get_next_event(self) -> Event:
        rawEvents = get_gamepad()

        ev = self.transformRawEvent(rawEvents[0])

        return ev
