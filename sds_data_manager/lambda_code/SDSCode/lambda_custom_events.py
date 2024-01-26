"""Stores custom EventBridge PutEvent structure"""
import json
from dataclasses import asdict, dataclass


@dataclass
class EventDetail:
    file_to_create: str
    status: str
    dependency: str


@dataclass
class IMAPLambdaPutEvent:
    detail_type: str
    detail: EventDetail
    source: str = "imap.lambda"

    def to_event(self):
        return {
            "DetailType": self.detail_type,
            "Source": self.source,
            "Detail": json.dumps(asdict(self.detail)),
        }
