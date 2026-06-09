"""
Sistema simple de eventos para desacoplar módulos.
"""
from typing import Callable, Dict, List


class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event: str, callback: Callable):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def dispatch(self, event: str, **data):
        for callback in self._listeners.get(event, []):
            callback(**data)