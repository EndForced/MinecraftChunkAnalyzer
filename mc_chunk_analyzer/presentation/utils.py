from dataclasses import asdict, dataclass
from collections import defaultdict
from .models.events import EVENT_PAYLOAD, Event

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event: Event, handler):
        self._handlers[event].append(handler)

    def emit(self, event: Event, payload: dataclass):
        expected = EVENT_PAYLOAD.get(event)

        if expected is None:
            raise ValueError(f"No payload registered for {event}")

        if not isinstance(payload, expected):
            raise TypeError(
                f"{event} expects {expected.__name__}, "
                f"got {type(payload).__name__}"
            )
        for handler in self._handlers[event]:
            handler(**asdict(payload))

