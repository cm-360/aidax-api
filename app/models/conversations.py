from collections import deque
from dataclasses import dataclass


@dataclass
class Message:

    role: str
    content: str

    def assistant(content: str):
        return Message(role="assistant", content=content)

    def system(content: str):
        return Message(role="system", content=content)

    def user(content: str):
        return Message(role="user", content=content)

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }

@dataclass
class Conversation:

    def __init__(self, max_messages: int=30):
        self.messages = deque(maxlen=max_messages)

    def to_dict(self):
        return {
            "messages": [m.to_dict() for m in messages]
        }
