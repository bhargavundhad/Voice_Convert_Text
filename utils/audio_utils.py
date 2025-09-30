# utils/audio_utils.py
import os
import math
import tempfile
from pathlib import Path
from pydub import AudioSegment

def ensure_wav_mono_16k(src_path: str, out_path: str = None):
    """
    Convert any audio file to mono 16k WAV (Gemini often works better with 16k mono).
    Returns output path.
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source audio file not found: {src_path}")
    
    # Security: Validate file path
    resolved_src = os.path.abspath(src_path)
    if not os.path.isfile(resolved_src):
        raise ValueError("Source path is not a valid file")
    
    try:
        if out_path is None:
            # Create secure temporary file
            temp_dir = tempfile.mkdtemp(prefix="voice2notes_")
            out_path = os.path.join(temp_dir, Path(src_path).stem + "_normalized.wav")
        
        # Validate output path
        out_dir = os.path.dirname(out_path)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, mode=0o700)  # Secure permissions
        
        audio = AudioSegment.from_file(src_path)
        
        # Validate audio
        if len(audio) == 0:
            raise ValueError("Audio file appears to be empty or corrupted")
        
        # Security: Limit audio duration to prevent resource exhaustion
        max_duration_ms = 3 * 60 * 60 * 1000  # 3 hours
        if len(audio) > max_duration_ms:
            raise ValueError(f"Audio file too long: {len(audio)/1000/60:.1f} minutes (max 180 minutes)")
        
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(out_path, format="wav")
        return out_path
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")

def duration_seconds(path: str):
    """Get duration of audio file in seconds"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file not found: {path}")
    
    try:
        audio = AudioSegment.from_file(path)
        return math.ceil(len(audio) / 1000)
    except Exception as e:
        raise Exception(f"Could not read audio duration: {str(e)}")

def chunk_audio(wav_path: str, chunk_length_seconds: int = 300):
    """
    Splits wav_path into chunks of chunk_length_seconds.
    Returns list of (chunk_path, start_seconds, end_seconds).
    """
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")
    
    if chunk_length_seconds <= 0:
        raise ValueError("Chunk length must be positive")
    
    # Security: Limit chunk length
    if chunk_length_seconds > 3600:  # 1 hour max per chunk
        raise ValueError("Chunk length too large (max 3600 seconds)")
    
    try:
        audio = AudioSegment.from_file(wav_path)
        total_ms = len(audio)
        
        if total_ms == 0:
            raise ValueError("Audio file is empty")
        
        chunk_ms = chunk_length_seconds * 1000
        chunks = []
        
        # Create secure temporary directory
        tmpdir = Path(tempfile.mkdtemp(prefix="voice2notes_chunks_"))
        
        start = 0
        idx = 0
        
        # Security: Limit number of chunks to prevent resource exhaustion
        max_chunks = 1000
        
        while start < total_ms and idx < max_chunks:
            end = min(start + chunk_ms, total_ms)
            chunk = audio[start:end]
            
            # Skip very short chunks (less than 1 second)
            if len(chunk) < 1000:
                break
                
            chunk_path = tmpdir / f"chunk_{idx:04d}_{start//1000}_{end//1000}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append((str(chunk_path), start // 1000, end // 1000))
            idx += 1
            start += chunk_ms
        
        if idx >= max_chunks:
            raise ValueError(f"Too many chunks generated (max {max_chunks})")
            
        return chunks
    except Exception as e:
        raise Exception(f"Audio chunking failed: {str(e)}")
