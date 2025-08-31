import streamlit as st
import os
import tempfile
from pathlib import Path
import warnings

# Import functions from the existing pdf_to_speech.py file
from pdf_to_speech import (
    clean_text,
    validate_audio_file,
    extract_text_from_pdf,
    split_text,
    text_to_intermediate_audio,
    clone_voice_to_audio,
    convert_audio_to_wav,
    device
)

# Suppress all warnings
warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="PDF to Speech Converter",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎤 PDF to Speech Converter</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    st.sidebar.markdown('<h2 class="sub-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
    
    # Device information
    st.sidebar.info(f"🖥️ Running on: {device.upper()}")
    
    # Model selection
    model_option = st.sidebar.selectbox(
        "Choose TTS Model:",
        ["YourTTS (Voice Cloning)", "Tacotron2 (Standard)"],
        help="YourTTS allows voice cloning, Tacotron2 is faster but standard voice"
    )
    
    # Word limit
    max_words = st.sidebar.number_input(
        "Maximum words to process:",
        min_value=10,
        max_value=10000,
        value=1000,
        step=100,
        help="Limit the number of words to process from the PDF"
    )
    
    # Audio quality settings
    st.sidebar.markdown('<h3 class="sub-header">🎵 Audio Settings</h3>', unsafe_allow_html=True)
    
    sample_rate = st.sidebar.selectbox(
        "Sample Rate:",
        [22050, 44100, 48000],
        index=0,
        help="Higher sample rate = better quality but larger file"
    )
    
    # Text chunk size
    chunk_size = st.sidebar.slider(
        "Text Chunk Size:",
        min_value=500,
        max_value=2000,
        value=1000,
        step=100,
        help="Size of text chunks for processing (smaller = more stable, larger = faster)"
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📄 Upload PDF</h2>', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload a PDF file to convert to speech"
        )
        
        if uploaded_pdf:
            st.success(f"✅ PDF uploaded: {uploaded_pdf.name}")
            
            # Display PDF info
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_pdf.getvalue())
                pdf_path = tmp_file.name
            
            # Extract and display text preview
            if st.button("📖 Preview Extracted Text"):
                with st.spinner("Extracting text from PDF..."):
                    text = extract_text_from_pdf(pdf_path, max_words=max_words)
                    if text:
                        st.markdown('<div class="info-box">', unsafe_allow_html=True)
                        st.markdown("**Extracted Text Preview:**")
                        st.text_area("Text", text[:500] + "..." if len(text) > 500 else text, height=200)
                        st.markdown(f"**Total characters:** {len(text)}")
                        st.markdown(f"**Total words:** {len(text.split())}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("Failed to extract text from PDF")
    
    with col2:
        st.markdown('<h2 class="sub-header">🎵 Voice Sample</h2>', unsafe_allow_html=True)
        
        if model_option == "YourTTS (Voice Cloning)":
            uploaded_voice = st.file_uploader(
                "Upload voice sample (for cloning)",
                type=['wav', 'mp3', 'm4a', 'flac', 'ogg', 'aac'],
                help="Upload a voice sample to clone the voice. Supports multiple formats."
            )
            
            if uploaded_voice:
                st.success(f"✅ Voice sample uploaded: {uploaded_voice.name}")
                
                # Save voice sample temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_voice.name.split(".")[-1]}') as tmp_file:
                    tmp_file.write(uploaded_voice.getvalue())
                    voice_path = tmp_file.name
                
                # Convert to WAV if needed
                if uploaded_voice.name.lower().endswith('.wav'):
                    wav_path = voice_path
                else:
                    with st.spinner("Converting audio to WAV format..."):
                        wav_path = convert_audio_to_wav(voice_path)
                        if wav_path:
                            st.success("✅ Audio converted to WAV format")
                        else:
                            st.error("❌ Failed to convert audio to WAV")
                            wav_path = None
                
                # Play voice sample
                if wav_path:
                    st.audio(uploaded_voice, format=f'audio/{uploaded_voice.name.split(".")[-1]}')
                    
                    # Show audio info
                    try:
                        from pydub import AudioSegment
                        audio_info = AudioSegment.from_file(wav_path)
                        st.info(f"📊 Audio Info: Duration: {len(audio_info)/1000:.1f}s, Sample Rate: {audio_info.frame_rate}Hz")
                    except:
                        pass
        else:
            st.info("Using standard Tacotron2 voice - no voice sample needed")
            wav_path = None
    
    # Process button
    st.markdown("---")
    
    if st.button("🚀 Convert PDF to Speech", type="primary", use_container_width=True):
        if not uploaded_pdf:
            st.error("Please upload a PDF file first!")
            return
        
        if model_option == "YourTTS (Voice Cloning)" and not uploaded_voice:
            st.error("Please upload a voice sample for voice cloning!")
            return
        
        # Create output directory
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Process the PDF
        with st.spinner("Processing PDF to speech..."):
            try:
                # Extract text
                st.info("📖 Extracting text from PDF...")
                text = extract_text_from_pdf(pdf_path, max_words=max_words)
                
                if not text:
                    st.error("Failed to extract text from PDF")
                    return
                
                st.success(f"✅ Extracted {len(text.split())} words from PDF")
                
                # Generate audio
                if model_option == "YourTTS (Voice Cloning)":
                    st.info("🎤 Cloning voice and generating audio...")
                    output_path = os.path.join(output_dir, f"cloned_{uploaded_pdf.name.replace('.pdf', '.wav')}")
                    final_audio = clone_voice_to_audio(text, wav_path, output_path)
                else:
                    st.info("🎤 Generating standard audio...")
                    temp_audio_path = "temp_audio"
                    final_audio = text_to_intermediate_audio(text, temp_audio_path, output_dir)
                    if final_audio:
                        output_path = os.path.join(output_dir, f"standard_{uploaded_pdf.name.replace('.pdf', '.wav')}")
                        os.rename(final_audio, output_path)
                        final_audio = output_path
                
                if final_audio:
                    st.success("✅ Audio generation completed!")
                    
                    # Display audio player
                    st.markdown('<h3 class="sub-header">🎵 Generated Audio</h3>', unsafe_allow_html=True)
                    
                    with open(final_audio, 'rb') as audio_file:
                        st.audio(audio_file.read(), format='audio/wav')
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Audio",
                        data=open(final_audio, 'rb').read(),
                        file_name=os.path.basename(final_audio),
                        mime="audio/wav"
                    )
                    
                    # Audio info
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(final_audio)
                    st.info(f"📊 Audio Info: Duration: {len(audio)/1000:.1f} seconds, Sample Rate: {audio.frame_rate} Hz")
                    
                else:
                    st.error("Failed to generate audio")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Built with Streamlit • Powered by TTS and YourTTS</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
