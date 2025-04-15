from datetime import datetime


class UserEvent:
    def __init__(self, event_type: str, payload: dict):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            "type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        }
