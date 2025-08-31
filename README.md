# PDF to Speech Converter - Streamlit App

A user-friendly web application for converting PDF documents to speech using advanced Text-to-Speech technology with voice cloning capabilities.

## Features

- 📄 **PDF Upload**: Upload any PDF file for text extraction
- 🎤 **Voice Cloning**: Clone voices using YourTTS model
- 🔊 **Standard TTS**: Use Tacotron2 for faster processing
- 📊 **Text Preview**: Preview extracted text before processing
- 🎵 **Audio Playback**: Listen to generated audio directly in the browser
- 📥 **Download**: Download generated audio files
- ⚙️ **Configurable**: Adjust word limits and model settings

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install System Dependencies** (if not already installed):
   - **Tesseract OCR**: Required for scanned PDF processing
     - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
     - macOS: `brew install tesseract`
     - Linux: `sudo apt-get install tesseract-ocr`

   - **Poppler**: Required for PDF to image conversion
     - Windows: Download from http://blog.alivate.com.au/poppler-windows/
     - macOS: `brew install poppler`
     - Linux: `sudo apt-get install poppler-utils`

## Running the App

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## How to Use

### 1. Upload PDF
- Click "Browse files" in the PDF upload section
- Select any PDF file from your computer
- The app will automatically detect and process the file

### 2. Choose TTS Model
- **YourTTS (Voice Cloning)**: Upload a voice sample to clone that voice
- **Tacotron2 (Standard)**: Use the default high-quality voice (faster processing)

### 3. Configure Settings
- **Maximum words**: Limit the number of words to process (100-10,000)
- **Device**: Automatically detects GPU/CPU availability

### 4. Voice Sample (for Voice Cloning)
- Upload an audio file (WAV, MP3, M4A, FLAC)
- The sample should be clear speech for best results
- Preview the uploaded audio in the app

### 5. Process and Generate
- Click "Convert PDF to Speech"
- Monitor progress with real-time status updates
- Listen to the generated audio
- Download the final audio file

## Supported File Formats

### Input
- **PDF**: Any PDF file (text-based or scanned)
- **Audio**: WAV, MP3, M4A, FLAC (for voice cloning)

### Output
- **Audio**: WAV format

## Tips for Best Results

1. **Voice Cloning**:
   - Use clear, high-quality voice samples
   - Avoid background noise in voice samples
   - Longer voice samples (10-30 seconds) work better

2. **PDF Processing**:
   - Text-based PDFs process faster than scanned documents
   - For large documents, use the word limit feature
   - Preview extracted text to ensure quality

3. **Performance**:
   - GPU acceleration is automatically used if available
   - Larger documents take longer to process
   - Voice cloning is more resource-intensive than standard TTS

## Troubleshooting

### Common Issues

1. **"Error extracting text from PDF"**
   - Ensure Tesseract OCR is properly installed
   - Try with a different PDF file
   - Check if the PDF is password-protected

2. **"Invalid voice sample"**
   - Convert audio to WAV format using: `ffmpeg -i input.m4a output.wav`
   - Ensure the audio file is not corrupted
   - Try a different audio file

3. **Slow processing**
   - Reduce the word limit
   - Use Tacotron2 instead of YourTTS for faster processing
   - Ensure GPU is available for acceleration

4. **Memory errors**
   - Reduce the word limit
   - Close other applications
   - Restart the app

### System Requirements

- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 2GB+ free space for models
- **GPU**: Optional but recommended for faster processing
- **Internet**: Required for initial model download

## File Structure

```
├── app.py                 # Main Streamlit application
├── pdf_to_speech.py       # Original command-line script
├── requirements.txt       # Python dependencies
├── README_Streamlit.md    # This file
├── output/               # Generated audio files
└── [other project files]
```

## Advanced Configuration

### Environment Variables
- `CUDA_VISIBLE_DEVICES`: Control GPU usage
- `TTS_CACHE_DIR`: Set custom model cache directory

### Custom Models
The app uses pre-trained models from the TTS library. You can modify the model selection in the code:
- YourTTS: `tts_models/multilingual/multi-dataset/your_tts`
- Tacotron2: `tts_models/en/ljspeech/tacotron2-DDC`

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project uses the TTS library which is licensed under the MIT License.
