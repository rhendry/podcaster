from abc import ABC, abstractmethod
import os
import aiofiles
import json
from podcaster.models import Transcript

class TranscriptRepository(ABC):
    """Interface for handling transcripts."""

    @abstractmethod
    async def list_transcripts_async(self) -> list:
        """List all available transcripts."""
        pass

    @abstractmethod
    async def write_transcript_async(self, transcript: Transcript) -> None:
        """Write a transcript to storage."""
        pass

    @abstractmethod
    async def read_transcript_async(self, filename: str) -> Transcript:
        """Read a transcript from storage by filename."""
        pass

class LocalTranscriptRepository(TranscriptRepository):
    """Local filesystem implementation of TranscriptRepository."""

    def __init__(self, directory: str = 'output/transcripts'):
        self._directory = directory
        # Ensure the directory exists
        os.makedirs(self._directory, exist_ok=True)

    async def list_transcripts_async(self) -> list:
        """Asynchronously list all transcript files in the directory."""
        files = []
        for filename in os.listdir(self._directory):
            if filename.endswith('.txt'):
                files.append(filename)
        return files

    async def write_transcript_async(self, transcript: Transcript) -> None:
        """Asynchronously write the transcript to a file."""
        filename = f"{transcript.title.replace(' ', '_')}.txt"
        output_path = os.path.join(self._directory, filename)
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:
            await file.write(transcript.model_dump_json(indent=4))

    async def read_transcript_async(self, filename: str) -> Transcript:
        """Asynchronously read a transcript from a file."""
        input_path = os.path.join(self._directory, filename)
        async with aiofiles.open(input_path, 'r', encoding='utf-8') as file:
            content = await file.read()
            transcript_data = json.loads(content)
            return Transcript(**transcript_data)
