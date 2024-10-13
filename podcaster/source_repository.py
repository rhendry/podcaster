import aiofiles
from abc import ABC, abstractmethod

from podcaster.models import Source, TextFileSource


class SourceRepository(ABC):
    @abstractmethod
    async def load_sources_async(self) -> list[Source]:
        pass

class TextFileSourceRepository(SourceRepository):
    def __init__(self, filepaths: list[str]):
        self._filepaths = filepaths

    async def load_sources_async(self) -> list[Source]:
        sources: list[Source] = []
        for filepath in self._filepaths:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as file:
                text = await file.read()
                sources.append(TextFileSource(text=text, filepath=filepath))
        return sources

