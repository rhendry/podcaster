from typing import Literal, Union
from pydantic import BaseModel, Field

class TranscriptItem(BaseModel):
    type: str = Field(description="The type of the item in the transcript.")
    order: int = Field(description="The order of the item in the transcript. To have people speak at the same time, they should have the same order.")

class SpeechTranscriptItem(TranscriptItem):
    type: Literal["speech"] = Field(description="The type of the item in the transcript.")
    speakers: str = Field(description="The speakers of the item, separated by commas.")
    content: str = Field(description="The content of the item.")

class MusicThemeTranscriptItem(TranscriptItem):
    type: Literal["music_theme"] = Field(description="The type of the item in the transcript.")
    theme: str = Field(description="The name of the music theme to play.")

TranscriptItemType = Union[SpeechTranscriptItem, MusicThemeTranscriptItem]

class Transcript(BaseModel):
    title: str = Field(description="The title of the podcast.")
    items: list[TranscriptItemType] = Field(description="The items in the transcript.")

class Source(BaseModel):
    text: str = Field(description="The text of the source.")

class TextFileSource(Source):
    filepath: str = Field(description="The filepath of the source.")
