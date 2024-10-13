import os
from pathlib import Path
from abc import ABC, abstractmethod

from podcaster.models import SpeechTranscriptItem, Transcript
from .speech_to_audio_converter import SpeechToAudioConverter

class TranscriptToAudioConverter(ABC):
    """Interface for converting transcripts to audio files."""

    @abstractmethod
    async def convert_transcript_to_audio_async(self, transcript: Transcript):
        """Convert a single transcript to audio files."""
        pass


class DefaultTranscriptToAudioConverter(TranscriptToAudioConverter):
    """Implementation of TranscriptToAudioConverter."""

    def __init__(self, speech_to_audio_converter: SpeechToAudioConverter):
        self._speech_to_audio_converter = speech_to_audio_converter

    async def convert_transcript_to_audio_async(self, transcript: Transcript):
        """Convert a single transcript to audio files."""
        podcast_title = transcript.title.replace(' ', '_')

        for segment in transcript.items:
            if isinstance(segment, SpeechTranscriptItem):
                output_dir = Path('output') / 'clips' / podcast_title
                await self._speech_to_audio_converter.convert_speech_transcript_item_to_audio_async(transcript, segment, output_dir)
