from enum import Enum
from typing import Literal, Union
from pydantic import BaseModel, Field

class Voice(Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class Host(BaseModel):
    name: str = Field(description="The name of the host.")
    voice: Voice = Field(description="The voice of the host.")
    id: str = Field(description="The id of the host (e.g. first name).")

class TranscriptItem(BaseModel):
    type: str = Field(description="The type of the item in the transcript.")
    order: int = Field(description="The order of the item in the transcript. To have people speak at the same time, they should have the same order.")

class SpeechTranscriptItem(TranscriptItem):
    type: Literal["speech"] = Field(description="The type of the item in the transcript.")
    speaker_id: str = Field(description="The id of the speaker of the item. Must be one of the ids of the hosts.")
    content: str = Field(description="The content of the item.")

class MusicThemeTranscriptItem(TranscriptItem):
    type: Literal["music_theme"] = Field(description="The type of the item in the transcript.")
    theme: str = Field(description="The name of the music theme to play.")

TranscriptItemType = Union[SpeechTranscriptItem, MusicThemeTranscriptItem]

class Transcript(BaseModel):
    title: str = Field(description="The title of the podcast.")
    hosts: list[Host] = Field(description="The hosts of the podcast.")
    items: list[TranscriptItemType] = Field(description="The items in the transcript.")

class Source(BaseModel):
    text: str = Field(description="The text of the source.")

class TextFileSource(Source):
    filepath: str = Field(description="The filepath of the source.")
