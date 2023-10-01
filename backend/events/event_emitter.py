class EventEmitter:
    def __init__(self):
        self._events = {}

    def on(self, event_name, callback):
        """Register an event handler for the given event."""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)

    def off(self, event_name, callback):
        """Remove an event handler for the given event."""
        if event_name in self._events:
            self._events[event_name].remove(callback)

    def emit(self, event_name, *args, **kwargs):
        """Trigger all handlers for the given event."""
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)
