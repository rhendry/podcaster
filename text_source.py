from abc import ABC, abstractmethod

class TextSource(ABC):
    @abstractmethod
    async def get_content_async(self) -> str:
        pass
