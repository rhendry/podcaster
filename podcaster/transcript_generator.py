from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader

from podcaster.models import Transcript, Source
from podcaster.llm_client import LLMClient
from podcaster.prompt_renderer import PromptRenderer

class TranscriptGenerator(ABC):
    @abstractmethod
    async def generate_transcript_async(
        self, hosts: list[str], sources: list[Source], outline: Source
    ) -> Transcript:
        pass

class LLMTranscriptGenerator(TranscriptGenerator):
    def __init__(self, llm_client: LLMClient, prompt_renderer: PromptRenderer):
        self.llm_client = llm_client
        self.prompt_renderer = prompt_renderer

    async def generate_transcript_async(
        self, hosts: list[str], sources: list[Source], outline: Source
    ) -> Transcript:
        # Prepare the context for the template
        context = {
            "hosts": hosts,
            "sources": sources,
            "outline": outline.text,
        }

        # Render the prompt using the template
        prompt = self.prompt_renderer.render_prompt("generate_transcript.jinja", context)

        # Get the transcript content from the LLM
        return await self.llm_client.generate_model_async(prompt, Transcript)
