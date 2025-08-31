#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr poppler-utils ffmpeg libsndfile1

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/app"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p audio_samples
mkdir -p temp_audio
