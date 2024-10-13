from abc import ABC, abstractmethod
from pathlib import Path
import aiofiles
from openai import AsyncOpenAI

from podcaster.models import Voice

class TTSClient(ABC):
    """Interface for Text-to-Speech clients."""

    @abstractmethod
    async def synthesize_speech_async(self, text: str, voice: Voice, output_file: Path) -> None:
        """Convert text to speech audio bytes and save to a file."""
        pass

class OpenAITTSClient(TTSClient):
    """Implementation of TTSClient using OpenAI's Text-to-Speech API."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = AsyncOpenAI(api_key=self._api_key)

    async def synthesize_speech_async(self, text: str, voice: Voice, output_file: Path) -> None:
        response = await self._client.audio.speech.create(
            model="tts-1",
            voice=voice.value,
            input=text
        )
        async with aiofiles.open(output_file, 'wb') as file:
            for chunk in response.iter_bytes():
                await file.write(chunk)
