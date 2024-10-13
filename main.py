import asyncio
import os
import aiofiles
import dotenv
import logging
import inquirer
from rich.console import Console
from podcaster.prompt_renderer import JinjaPromptRenderer
from podcaster.source_repository import (
    TextFileSourceRepository,
)
from podcaster.transcript_generator import LLMTranscriptGenerator
from podcaster.llm_client import OpenAILLMClient
from podcaster.transcript_repository import LocalTranscriptRepository

dotenv.load_dotenv()

async def main_async():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='(%(asctime)s) %(name)s [%(levelname)s]: %(message)s'
    )

    console = Console()

    console.print(r"""
[bold blue] ________  ________  ________  ________  ________  ________  _________  _______   ________     [/bold blue]
[bold cyan]|\   __  \|\   __  \|\   ___ \|\   ____\|\   __  \|\   ____\|\___   ___\\  ___ \ |\   __  \    [/bold cyan]
[bold green]\ \  \|\  \ \  \|\  \ \  \_|\ \ \  \___|\ \  \|\  \ \  \___|\|___ \  \_\ \   __/|\ \  \|\  \   [/bold green]
[bold yellow] \ \   ____\ \  \\\  \ \  \ \\ \ \  \    \ \   __  \ \_____  \   \ \  \ \ \  \_|/ \ \  \_  _\  [/bold yellow]
[bold magenta]  \ \  \___|\ \  \\\  \ \  \_\\ \ \  \____\ \  \ \  \|____|\  \   \ \  \ \ \  \_|\ \ \  \\  \| [/bold magenta]
[bold red]   \ \__\    \ \_______\ \_______\ \_______\ \__\ \__\____\_\  \   \ \__\ \ \______\\ \__\\ _\ [/bold red]
[bold blue]    \|__|     \|_______|\|_______|\|_______|\|__|\|__|\_________\   \|__|  \|_______|\|__|\|__|[/bold blue]
[bold blue]                                                     \|_________|[/bold blue]                                                                       
    """)

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

    # Initialize TranscriptRepository
    transcript_repository = LocalTranscriptRepository()

    # Initialize LLM client and transcript generator
    llm_client = OpenAILLMClient(api_key=os.getenv('OPENAI_API_KEY') or '')
    prompt_renderer = JinjaPromptRenderer(template_folder='prompts')
    transcript_generator = LLMTranscriptGenerator(
        llm_client,
        prompt_renderer
    )

    # Present CLI options to the user
    questions = [
        inquirer.List(
            'action',
            message='What would you like to do?',
            choices=['Generate a transcript', 'Convert transcript to audio'],
        )
    ]
    answers = inquirer.prompt(questions)

    if not answers:
        console.print('[bold red]No action selected. Exiting...[/bold red]')
        return

    if answers['action'] == 'Generate a transcript':
        # Generate transcripts
        for outline in outlines:
            logging.info(f'Processing outline: {outline}')
            transcript = await transcript_generator.generate_transcript_async(
                hosts, sources, outline
            )
            await transcript_repository.write_transcript_async(transcript)
            logging.info(f"Transcript for outline '{outline}' generated and saved.")

        # List available transcripts
        transcripts = await transcript_repository.list_transcripts_async()
        logging.info(f"Available transcripts: {transcripts}")

    elif answers['action'] == 'Convert transcript to audio':
        # Stub handler for converting transcripts to audio
        console.print('[bold yellow]This feature is under development.[/bold yellow]')
    

if __name__ == "__main__":
    asyncio.run(main_async())
