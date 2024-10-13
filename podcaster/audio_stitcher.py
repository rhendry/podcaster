from abc import ABC, abstractmethod
import os
from pydub import AudioSegment
import wave
import logging
import librosa
import numpy as np
import soundfile as sf

class AudioClipStitcher(ABC):
    @abstractmethod
    async def stitch_audio_clips_async(
        self,
        input_directory: str,
        output_directory: str,
        output_file_name: str
    ) -> None:
        """Stitches audio clips from the input directory into a single audio file."""
        pass

class PydubAudioClipStitcher(AudioClipStitcher):
    async def stitch_audio_clips_async(
        self,
        input_directory: str,
        output_directory: str,
        output_file_name: str
    ) -> None:
        # Collect all .wav files in the input directory and group by the order prefix
        wav_files = [
            f for f in os.listdir(input_directory)
            if f.endswith('.wav')
        ]
        if not wav_files:
            raise FileNotFoundError('No .wav files found in the specified directory.')

        # Group files by their order prefix
        grouped_files = {}
        for wav_file in wav_files:
            order = int(wav_file.split('-')[0])
            if order not in grouped_files:
                grouped_files[order] = []
            grouped_files[order].append(wav_file)

        # Initialize the final audio segment
        final_audio = AudioSegment.empty()

        # Process each group in order
        for order in sorted(grouped_files.keys()):
            combined_segment = AudioSegment.empty()
            for wav_file in grouped_files[order]:
                audio_path = os.path.join(input_directory, wav_file)
                audio_segment = AudioSegment.from_wav(audio_path)
                combined_segment = combined_segment.overlay(audio_segment)
            final_audio += combined_segment

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Export the final stitched audio file
        output_path = os.path.join(output_directory, output_file_name)
        final_audio.export(output_path, format='wav')

class WaveAudioClipStitcher(AudioClipStitcher):
    async def stitch_audio_clips_async(
        self,
        input_directory: str,
        output_directory: str,
        output_file_name: str
    ) -> None:
        # Collect all .wav files in the input directory and group by the order prefix
        wav_files = [
            f for f in os.listdir(input_directory)
            if f.endswith('.wav')
        ]
        if not wav_files:
            raise FileNotFoundError('No .wav files found in the specified directory.')

        # Group files by their order prefix
        grouped_files = {}
        for wav_file in wav_files:
            order = int(wav_file.split('-')[0])
            if order not in grouped_files:
                grouped_files[order] = []
            grouped_files[order].append(wav_file)

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Initialize the output file
        output_path = os.path.join(output_directory, output_file_name)

        # Assume all clips have the same format as the first one
        sorted_clips = [os.path.join(input_directory, wav_files[0])]
        with wave.open(sorted_clips[0], 'rb') as first_clip:
            params = first_clip.getparams()

        with wave.open(output_path, 'wb') as outfile:
            # Set parameters for the output file
            outfile.setparams(params)

            for order in sorted(grouped_files.keys()):
                for wav_file in grouped_files[order]:
                    clip_path = os.path.join(input_directory, wav_file)
                    with wave.open(clip_path, 'rb') as clip:
                        outfile.writeframes(clip.readframes(clip.getnframes()))

        logging.info(f"Stitched audio saved to {output_path}")

class LibrosaAudioClipStitcher(AudioClipStitcher):
    async def stitch_audio_clips_async(
        self,
        input_directory: str,
        output_directory: str,
        output_file_name: str
    ) -> None:
        # Collect all .wav files in the input directory and group by the order prefix
        wav_files = [
            f for f in os.listdir(input_directory)
            if f.endswith('.wav')
        ]
        if not wav_files:
            raise FileNotFoundError('No .wav files found in the specified directory.')

        # Group files by their order prefix
        grouped_files = {}
        for wav_file in wav_files:
            order = int(wav_file.split('-')[0])
            if order not in grouped_files:
                grouped_files[order] = []
            grouped_files[order].append(wav_file)

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Initialize variables for final audio and sample rate
        final_audio = None
        sample_rate = None

        # Process each group in order
        for order in sorted(grouped_files.keys()):
            combined_audio = None
            for wav_file in grouped_files[order]:
                audio_path = os.path.join(input_directory, wav_file)
                audio_data, sr = librosa.load(audio_path, sr=None, mono=False)
                if sample_rate is None:
                    sample_rate = sr
                elif sr != sample_rate:
                    raise ValueError(f"Sample rate mismatch in file {wav_file}")

                if combined_audio is None:
                    combined_audio = audio_data
                else:
                    # Pad the shorter array with zeros
                    max_length = max(combined_audio.shape[-1], audio_data.shape[-1])
                    if audio_data.ndim == 1:
                        # Mono audio
                        padded_combined = np.pad(
                            combined_audio,
                            (0, max_length - combined_audio.shape[0]),
                            mode='constant'
                        )
                        padded_audio_data = np.pad(
                            audio_data,
                            (0, max_length - audio_data.shape[0]),
                            mode='constant'
                        )
                    else:
                        # Stereo audio
                        padded_combined = np.pad(
                            combined_audio,
                            ((0, 0), (0, max_length - combined_audio.shape[1])),
                            mode='constant'
                        )
                        padded_audio_data = np.pad(
                            audio_data,
                            ((0, 0), (0, max_length - audio_data.shape[1])),
                            mode='constant'
                        )
                    # Mix the audio clips together (overlay)
                    combined_audio = padded_combined + padded_audio_data

            if final_audio is None:
                final_audio = combined_audio
            else:
                # Concatenate the combined segment
                final_audio = np.concatenate((final_audio, combined_audio), axis=-1)

        # Export the final stitched audio file
        output_path = os.path.join(output_directory, output_file_name)
        sf.write(output_path, final_audio, sample_rate)
