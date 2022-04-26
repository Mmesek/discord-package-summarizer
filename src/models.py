import re

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from itertools import chain
from typing import Optional

import numpy as np

NON_WORDS = re.compile("[^\w ]")


class Index:
    channels: dict[int, "Channel"]
    servers: dict[int, "Server"]

    def __init__(self) -> None:
        self.channels = {}
        self.servers = {}

    def load_channels(self, channels: dict) -> None:
        self.channels.update({int(k): Channel(_index=self, id=int(k), name=v) for k, v in channels.items()})

    def load_servers(self, servers: dict) -> None:
        self.servers.update({int(k): Server(_index=self, id=int(k), name=v) for k, v in servers.items()})

    def update_channels(self, data: dict):
        self.channels[data["id"]].type = data["type"]

    def message(self, n: int, start_: int = 0) -> list["Message"]:
        return sorted(
            np.concatenate([channel.messages for channel in self.channels.values()]), key=lambda x: x.timestamp
        )[start_:n]

    @property
    def total_messages(self) -> int:
        return sum([len(i.messages) for i in self.channels.values()])

    @property
    def total_characters(self) -> int:
        return sum([sum([len(m.contents) for m in i.messages]) for i in self.channels.values()])

    @property
    def clean_words(self) -> list[str]:
        return list(chain(*[c.clean_words for c in self.channels.values()]))

    @property
    def words(self) -> Counter:
        return Counter(self.clean_words)

    @property
    def length(self) -> int:
        return sum([c.length for c in self.channels.values()])

    @property
    def word_count(self) -> int:
        return sum([c.word_count for c in self.channels.values()])

    @property
    def channel_stats(self):
        return list(
            (
                channel.name or channel.id,
                len(channel.messages or []),
                sum(len(i.contents or "") for i in channel.messages or []),
            )
            for channel in self.channels.values()
        )


@dataclass(slots=True)
class Server:
    _index: Index
    id: int
    name: str


@dataclass(slots=True)
class Channel:
    _index: Index
    id: int
    name: str
    type: int = None
    messages: list["Message"] = list
    guild_id: Optional[int] = None
    recipents: Optional[list[int]] = list

    def update_channel(self, data):
        self.type = data["type"]
        gid = data.get("guild", {}).get("id")
        self.guild_id = int(gid) if gid else 0
        self.recipents = data.get("recipents")

    def load_messages(self, rows: list[dict]) -> None:
        self.messages = [
            Message(
                _index=self._index,
                channel_id=int(self.id),
                id=row["ID"],
                timestamp=row["Timestamp"],
                contents=row["Contents"],
                attachments=row["Attachments"],
            )
            for row in rows
        ]

    @property
    def guild(self) -> Server:
        return self._index.servers[self.guild_id]

    @property
    def clean_words(self) -> list[str]:
        return list(chain(*[m.clean_words for m in self.messages]))

    @property
    def words(self) -> Counter:
        return Counter(self.clean_words)

    @property
    def length(self) -> int:
        return sum([m.length for m in self.messages])

    @property
    def word_count(self) -> int:
        return sum([m.word_count for m in self.messages])


@dataclass(slots=True)
class Message:
    _index: Index
    id: int
    channel_id: int
    timestamp: datetime
    contents: Optional[str] = None
    attachments: Optional[list] = list

    @property
    def channel(self) -> Channel:
        return self._index.channels[self.channel_id]

    @property
    def guild(self) -> Server:
        return self._index.servers[self.channel.guild_id]

    @property
    def clean_words(self) -> list[str]:
        return [word.lower() for word in NON_WORDS.sub("", self.contents).split(" ")]

    @property
    def words(self) -> Counter:
        return Counter(self.clean_words)

    @property
    def length(self) -> int:
        return len(self.contents)

    @property
    def word_count(self) -> int:
        return len(self.contents.split(" "))
