from abc import ABC, abstractmethod
from pathlib import Path

from podcaster.models import SpeechTranscriptItem, Transcript
from .tts_client import TTSClient, Voice

class SpeechToAudioConverter(ABC):
    """Interface for converting a SpeechTranscriptItem to an audio file."""

    @abstractmethod
    async def convert_speech_transcript_item_to_audio_async(self, transcript: Transcript, item: SpeechTranscriptItem, output_dir: Path):
        """Convert a single SpeechTranscriptItem to an audio file."""
        pass

class DefaultSpeechToAudioConverter(SpeechToAudioConverter):

    def __init__(self, tts_client: TTSClient):
        self._tts_client = tts_client

    async def convert_speech_transcript_item_to_audio_async(self, transcript: Transcript, item: SpeechTranscriptItem, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        text = item.content
        speaker = item.speaker_id
        filename = f"{item.order}-{speaker}.wav"
        output_path = output_dir / filename

        host = next((host for host in transcript.hosts if host.id == speaker), None)
        if host is None:
            raise ValueError(f"Host with id {speaker} not found in transcript.")
        
        await self._tts_client.synthesize_speech_async(text, host.voice, output_path)
