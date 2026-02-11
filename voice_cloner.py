"""
Voice Cloning module for Quran Reciter application.
Uses XTTS v2 for Arabic text-to-speech with voice cloning.
"""

import os
import torch
import soundfile as sf
from pathlib import Path
from pydub import AudioSegment
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Voice Cloner running on: {device}")


def validate_audio_file(file_path: str) -> bool:
    """Validate that an audio file can be read."""
    try:
        sf.read(file_path)
        return True
    except:
        return False


def convert_audio_to_wav(input_path: str, output_path: str = None) -> str:
    """Convert any audio file to WAV format."""
    try:
        supported_formats = ['mp3', 'm4a', 'flac', 'ogg', 'wma', 'aac', 'wav']
        file_extension = Path(input_path).suffix.lower().lstrip('.')
        
        if file_extension not in supported_formats:
            print(f"Unsupported audio format: {file_extension}")
            return None
        
        if file_extension == 'wav':
            return input_path
        
        audio = AudioSegment.from_file(input_path)
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.wav'))
        
        audio.export(output_path, format="wav")
        return output_path
        
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None


def split_arabic_text(text: str, max_length: int = 250) -> list:
    """
    Split Arabic text into chunks suitable for TTS.
    Respects sentence boundaries where possible.
    """
    # Arabic sentence endings
    sentence_endings = ['۔', '؟', '!', '،', '.', '\n']
    
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by common delimiters
    words = text.split()
    
    for word in words:
        test_chunk = current_chunk + " " + word if current_chunk else word
        
        if len(test_chunk) <= max_length:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


class QuranVoiceCloner:
    """Voice cloning for Quran recitation using XTTS v2."""
    
    def __init__(self):
        self.tts = None
        self.model_loaded = False
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    
    def load_model(self):
        """Load the XTTS v2 model."""
        if self.model_loaded:
            return True
        
        try:
            from TTS.api import TTS
            print("Loading XTTS v2 model (this may take a moment on first run)...")
            self.tts = TTS(self.model_name, gpu=(device == "cuda"))
            self.model_loaded = True
            print("XTTS v2 model loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading XTTS v2 model: {e}")
            return False
    
    def clone_voice(
        self,
        text: str,
        voice_sample_path: str,
        output_path: str,
        language: str = "ar"
    ) -> str:
        """
        Clone voice and generate speech for given text.
        
        Args:
            text: Arabic text to synthesize
            voice_sample_path: Path to voice sample WAV file
            output_path: Path for output audio file
            language: Language code (default: "ar" for Arabic)
        
        Returns:
            Path to generated audio file, or None if failed
        """
        if not self.load_model():
            return None
        
        if not validate_audio_file(voice_sample_path):
            print("Invalid voice sample file.")
            return None
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Split text into manageable chunks
            chunks = split_arabic_text(text)
            
            if len(chunks) == 1:
                # Single chunk - direct generation
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=voice_sample_path,
                    language=language,
                    split_sentences=True
                )
                return output_path
            
            # Multiple chunks - generate and combine
            temp_files = []
            output_dir = os.path.dirname(output_path) or '.'
            
            with tqdm(total=len(chunks), desc="Generating audio") as pbar:
                for i, chunk in enumerate(chunks):
                    temp_file = os.path.join(output_dir, f"temp_chunk_{i}.wav")
                    
                    self.tts.tts_to_file(
                        text=chunk,
                        file_path=temp_file,
                        speaker_wav=voice_sample_path,
                        language=language,
                        split_sentences=False
                    )
                    temp_files.append(temp_file)
                    pbar.update(1)
            
            # Combine audio chunks
            combined = AudioSegment.empty()
            for temp_file in temp_files:
                combined += AudioSegment.from_file(temp_file)
                os.remove(temp_file)
            
            combined.export(output_path, format="wav")
            print(f"Audio saved: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            # Clean up temp files on error
            for temp_file in temp_files if 'temp_files' in locals() else []:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return None
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds."""
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
        except:
            return 0.0
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(file_path)
        except:
            return 0


# Global instance
cloner = QuranVoiceCloner()


def generate_recitation(
    text: str,
    voice_sample: str,
    output_path: str,
    language: str = "ar"
) -> str:
    """
    Generate Quran recitation with cloned voice.
    
    Args:
        text: Arabic Quran text
        voice_sample: Path to voice sample
        output_path: Path for output file
        language: Language code
    
    Returns:
        Path to generated audio, or None
    """
    return cloner.clone_voice(text, voice_sample, output_path, language)
