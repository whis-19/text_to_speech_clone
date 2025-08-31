import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play
import os
from pathlib import Path
import re
from tqdm import tqdm
import torch
import soundfile as sf
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Define valid vocabulary (alphanumeric + basic punctuation)
VALID_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-")

# Set device (GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on device: {device}")

# Convert any audio file to WAV format
def convert_audio_to_wav(input_path, output_path=None):
    """
    Convert any supported audio file to WAV format.
    
    Args:
        input_path (str): Path to input audio file
        output_path (str, optional): Path for output WAV file. If None, creates in same directory
    
    Returns:
        str: Path to the converted WAV file, or None if conversion failed
    """
    try:
        # Supported audio formats
        supported_formats = ['mp3', 'm4a', 'flac', 'ogg', 'wma', 'aac', 'wav']
        file_extension = Path(input_path).suffix.lower().lstrip('.')
        
        if file_extension not in supported_formats:
            print(f"Unsupported audio format: {file_extension}")
            return None
        
        # If already WAV, return the path
        if file_extension == 'wav':
            return input_path
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Generate output path if not provided
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.wav'))
        
        # Export as WAV
        audio.export(output_path, format="wav")
        print(f"Converted {input_path} to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error converting audio file: {str(e)}")
        return None

# Clean text by replacing invalid characters with spaces
def clean_text(text):
    return ''.join(c if c in VALID_CHARS else ' ' for c in text)

# Validate audio file
def validate_audio_file(file_path):
    try:
        sf.read(file_path)  # Try loading with soundfile
        return True
    except:
        return False

# Extract text from PDF (selectable or scanned) with optional word limit
def extract_text_from_pdf(pdf_path, max_words=None):
    try:
        text = ""
        with tqdm(total=1, desc="Extracting text from PDF") as pbar:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "
            if not text.strip():
                images = convert_from_path(pdf_path)
                for img in images:
                    text += pytesseract.image_to_string(img) + " "
            pbar.update(1)
        text = text.strip()
        if max_words is not None:
            words = text.split()
            text = " ".join(words[:max_words])
        cleaned_text = clean_text(text)
        return cleaned_text or None
    except:
        return None

# Split text into chunks for TTS processing
def split_text(text, max_length=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# Convert text to intermediate audio
def text_to_intermediate_audio(text, temp_output_base, output_dir):
    try:
        tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=(device == "cuda"))
        chunks = split_text(text)
        temp_files = []
        
        with tqdm(total=len(chunks), desc="Generating intermediate audio") as pbar:
            for i, chunk in enumerate(chunks):
                temp_file = f"{output_dir}/{temp_output_base}_{i}.wav"
                tts.tts_to_file(text=chunk, file_path=temp_file)
                temp_files.append(temp_file)
                pbar.update(1)
        
        # Combine audio chunks
        combined = AudioSegment.empty()
        for temp_file in temp_files:
            combined += AudioSegment.from_file(temp_file)
            os.remove(temp_file)
        
        combined_output = f"{output_dir}/{temp_output_base}.wav"
        combined.export(combined_output, format="wav")
        print(f"Intermediate audio saved: {combined_output}")
        return combined_output
    except:
        return None

# Clone voice to match provided audio sample
def clone_voice_to_audio(text, voice_sample, output_path):
    try:
        if not validate_audio_file(voice_sample):
            print("Error: Invalid voice sample. Try converting to WAV using: ffmpeg -i trox.m4a trox.wav")
            return None
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=(device == "cuda"))
        chunks = split_text(text)
        temp_files = []
        
        with tqdm(total=len(chunks), desc="Cloning voice") as pbar:
            for i, chunk in enumerate(chunks):
                temp_file = f"{os.path.dirname(output_path)}/cloned_temp_{i}.wav"
                tts.tts_to_file(text=chunk, file_path=temp_file, speaker_wav=voice_sample, language="en")
                temp_files.append(temp_file)
                pbar.update(1)
        
        # Combine audio chunks
        combined = AudioSegment.empty()
        for temp_file in temp_files:
            combined += AudioSegment.from_file(temp_file)
            os.remove(temp_file)
        
        combined.export(output_path, format="wav")
        print(f"Cloned audio saved: {output_path}")
        return output_path
    except:
        return None

# Main workflow
def main(pdf_path="life_3_0.pdf", voice_sample="trox.m4a", output_audio="cloned_output.wav", max_words=None):
    # Create output directory named after voice sample (without extension)
    voice_base = os.path.splitext(os.path.basename(voice_sample))[0]
    output_dir = voice_base
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_audio)
    temp_audio_path = "temp_audio"

    # Step 1: Extract text from PDF
    text = extract_text_from_pdf(pdf_path, max_words=max_words)
    if not text:
        return

    # Step 2: Convert text to intermediate audio
    intermediate_audio = text_to_intermediate_audio(text, temp_audio_path, output_dir)
    if not intermediate_audio:
        return

    # Step 3: Clone voice using the original text and voice sample
    final_audio = clone_voice_to_audio(text, voice_sample, output_path)
    if not final_audio:
        return

    # Step 4: Play the first 30 seconds of the final cloned audio
    with tqdm(total=1, desc="Playing first 30 seconds of audio") as pbar:
        try:
            audio = AudioSegment.from_file(final_audio)
            audio = audio[:30000]  # Trim to first 30 seconds (30,000 ms)
            play(audio)
            pbar.update(1)
        except:
            pass

if __name__ == "__main__":
    main(pdf_path="life_3_0.pdf", voice_sample="whis.wav", max_words=1000)