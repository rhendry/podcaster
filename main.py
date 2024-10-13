import asyncio
import aiofiles
from podcaster.prompt_renderer import JinjaPromptRenderer
from podcaster.source_repository import (
    TextFileSourceRepository,
)
from podcaster.transcript_generator import LLMTranscriptGenerator
from podcaster.llm_client import OpenAILLMClient

async def main_async():
    # Load text sources
    text_source_files = [
        'sources/article1.txt',
        'sources/article2.txt'
    ]
    source_repository = TextFileSourceRepository(text_source_files)
    sources = await source_repository.load_sources_async()

    # Load outlines
    outline_files = [
        'outlines/outline1.txt'
    ]
    outline_repository = TextFileSourceRepository(outline_files)
    outlines = await outline_repository.load_sources_async()

    # Hosts (hardcoded for now)
    hosts = ['Jane Doe', 'John Smith']

    # Initialize LLM client and transcript generator
    llm_client = OpenAILLMClient(api_key='YOUR_OPENAI_API_KEY')
    prompt_renderer = JinjaPromptRenderer(template_folder='prompts')
    transcript_generator = LLMTranscriptGenerator(llm_client, prompt_renderer)

    # Generate transcripts
    for outline in outlines:
        transcript = await transcript_generator.generate_transcript_async(
            hosts, sources, outline
        )
        # Write the transcript to a file
        output_path = f"output/transcripts/{outline.text.replace(' ', '_')}.txt"
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as file:
            await file.write(transcript.model_dump_json(indent=4))
        print(f"Transcript generated and saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main_async())
