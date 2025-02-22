from dataclasses import dataclass
from typing import Dict, Any, Optional
from pydantic import BaseModel


@dataclass
class Message:
    """Data container for Slack messages."""

    text: str
    channel: str
    user: str
    ts: str
    thread_ts: str

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> Optional["Message"]:
        if event.get("subtype") == "bot_message":
            return None

        if event.get("subtype") == "message_changed":
            message_data = event.get("message", {})
            return cls(
                text=message_data.get("text", ""),
                channel=event.get("channel", ""),
                user=message_data.get("user", ""),
                ts=message_data.get("ts", ""),
                thread_ts=message_data.get("thread_ts"),
            )

        return cls(
            **{
                k: event.get(k, "")
                for k in ["text", "channel", "user", "ts", "thread_ts"]
            }
        )


class MessageResponse(BaseModel):
    """Slack Block Kit formatted translation response."""

    thread_ts: str
    text: str
    blocks: list[Dict[str, Any]]
