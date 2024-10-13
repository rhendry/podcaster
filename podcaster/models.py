from pydantic import BaseModel, Field

class TranscriptItem(BaseModel):
    speakers: str = Field(description="The speakers of the item, separated by commas.")
    content: str = Field(description="The content of the item.")
    order: int = Field(description="The order of the item in the transcript. To have people speak at the same time, they should have the same order.")

class Transcript(BaseModel):
    items: list[TranscriptItem] = Field(description="The items in the transcript.")

class Source(BaseModel):
    text: str = Field(description="The text of the source.")

class TextFileSource(Source):
    filepath: str = Field(description="The filepath of the source.")
