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
from podcaster.speech_to_audio_converter import DefaultSpeechToAudioConverter
from podcaster.transcript_generator import LLMTranscriptGenerator
from podcaster.llm_client import OpenAILLMClient
from podcaster.transcript_repository import LocalTranscriptRepository
from podcaster.transcript_to_audio_converter import DefaultTranscriptToAudioConverter
from podcaster.tts_client import OpenAITTSClient
from pydub import AudioSegment
from podcaster.audio_stitcher import LibrosaAudioClipStitcher, PydubAudioClipStitcher, WaveAudioClipStitcher

dotenv.load_dotenv()

async def main_async():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='(%(asctime)s) %(name)s [%(levelname)s]: %(message)s'
    )

    console = Console()
    # Clear the terminal
    console.clear()

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
            choices=[
                'Generate a transcript',
                'Convert transcript to audio',
                'Stitch audio clips into podcast'
            ],
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
        console.print('[bold green]Fetching available transcripts...[/bold green]')
        transcripts = await transcript_repository.list_transcripts_async()

        if not transcripts:
            console.print('[bold red]No transcripts found. Please generate a transcript first.[/bold red]')
            return

        # Prompt the user to select a transcript
        transcript_question = [
            inquirer.List(
                'transcript',
                message='Select a transcript to convert',
                choices=transcripts,
            )
        ]
        transcript_answer = inquirer.prompt(transcript_question)

        if not transcript_answer:
            console.print('[bold red]No transcript selected. Exiting...[/bold red]')
            return

        selected_transcript_file = transcript_answer['transcript']

        # Load the selected transcript
        transcript = await transcript_repository.read_transcript_async(selected_transcript_file)

        # Convert the selected transcript to audio
        console.print(f"[bold green]Converting transcript '{selected_transcript_file}' to audio...[/bold green]")
        transcript_to_audio_converter = DefaultTranscriptToAudioConverter(
            speech_to_audio_converter=DefaultSpeechToAudioConverter(
                tts_client=OpenAITTSClient(api_key=os.getenv('OPENAI_API_KEY') or '')
            )
        )
        await transcript_to_audio_converter.convert_transcript_to_audio_async(transcript)
        console.print('[bold green]Audio conversion completed.[/bold green]')

    elif answers['action'] == 'Stitch audio clips into podcast':
        console.print('[bold green]Fetching available clip directories...[/bold green]')
        clip_dirs = [
            d for d in os.listdir('output/clips/')
            if os.path.isdir(os.path.join('output/clips/', d))
        ]

        if not clip_dirs:
            console.print('[bold red]No clip directories found. Please convert a transcript to audio first.[/bold red]')
            return

        # Prompt the user to select a clip directory
        clip_dir_question = [
            inquirer.List(
                'clip_dir',
                message='Select a clip directory to stitch',
                choices=clip_dirs,
            )
        ]
        clip_dir_answer = inquirer.prompt(clip_dir_question)

        if not clip_dir_answer:
            console.print('[bold red]No clip directory selected. Exiting...[/bold red]')
            return

        selected_clip_dir = clip_dir_answer['clip_dir']
        clip_dir_path = os.path.join('output/clips/', selected_clip_dir)

        # Stitch the audio clips into a podcast
        console.print(f"[bold green]Stitching audio clips from '{selected_clip_dir}'...[/bold green]")
        audio_stitcher = LibrosaAudioClipStitcher()
        await audio_stitcher.stitch_audio_clips_async(
            clip_dir_path,
            'output/podcasts',
            f'{selected_clip_dir}_podcast.wav'
        )
        console.print('[bold green]Audio stitching completed.[/bold green]')

if __name__ == "__main__":
    asyncio.run(main_async())
