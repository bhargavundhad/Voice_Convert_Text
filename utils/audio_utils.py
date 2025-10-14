# utils/audio_utils.py
import os
import math
import tempfile
from pathlib import Path
import warnings

# Try to configure ffmpeg/ffprobe from imageio-ffmpeg BEFORE importing pydub.
# This prevents pydub from emitting "Couldn't find ffmpeg/ffprobe" warnings
# during import in environments where system binaries are missing.
try:
    import imageio_ffmpeg
    _img_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if _img_ffmpeg:
        # Set environment variables early so pydub picks them up without warnings
        os.environ.setdefault("FFMPEG_PATH", _img_ffmpeg)
        # Try to locate ffprobe next to ffmpeg
        candidate_probe = os.path.join(os.path.dirname(_img_ffmpeg), "ffprobe")
        if os.path.exists(candidate_probe):
            os.environ.setdefault("FFPROBE_PATH", candidate_probe)
except Exception:
    # imageio-ffmpeg not available — we'll handle later
    _img_ffmpeg = None

from pydub import AudioSegment
from pydub.utils import which

# Allow overriding ffmpeg/ffprobe via environment variables. This helps deployments
# (Streamlit Cloud, Docker, servers) where system ffmpeg may be missing or in a
# non-standard location. If environment variables are not set, pydub will try to
# find ffmpeg/ffprobe on PATH and will emit a RuntimeWarning (the original error
# you saw). We proactively check and set the paths here for clearer messages.
_FFMPEG_PATH = os.environ.get("FFMPEG_PATH")
_FFPROBE_PATH = os.environ.get("FFPROBE_PATH")

if _FFMPEG_PATH:
    AudioSegment.converter = _FFMPEG_PATH
else:
    # if not provided, try to auto-discover; if discovery fails pydub will warn later
    _found = which("ffmpeg")
    if _found:
        AudioSegment.converter = _found

if _FFPROBE_PATH:
    AudioSegment.ffprobe = _FFPROBE_PATH
else:
    _found_probe = which("ffprobe")
    if _found_probe:
        AudioSegment.ffprobe = _found_probe
# Try imageio-ffmpeg as a fallback (works on many cloud platforms when ffmpeg
# isn't installed system-wide). This avoids the frequent RuntimeWarning and the
# 'No such file or directory: ffprobe' error during conversions.
if (not getattr(AudioSegment, "converter", None)) or (not getattr(AudioSegment, "ffprobe", None)):
    try:
        import imageio_ffmpeg
        # imageio_ffmpeg.get_ffmpeg_exe() provides a bundled ffmpeg binary path
        _img_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        if _img_ffmpeg and not getattr(AudioSegment, "converter", None):
            AudioSegment.converter = _img_ffmpeg
        # imageio_ffmpeg doesn't always expose ffprobe; try to find ffprobe near ffmpeg
        if _img_ffmpeg and not getattr(AudioSegment, "ffprobe", None):
            candidate = os.path.join(os.path.dirname(_img_ffmpeg), "ffprobe")
            if os.path.exists(candidate):
                AudioSegment.ffprobe = candidate
    except Exception:
        # imageio-ffmpeg not available or failed — fall back to warning.
        pass

if not getattr(AudioSegment, "converter", None) or not getattr(AudioSegment, "ffprobe", None):
    warnings.warn(
        "ffmpeg or ffprobe not configured. On Streamlit Cloud install ffmpeg or set FFMPEG_PATH and FFPROBE_PATH environment variables. "
        "As a workaround, consider adding 'imageio-ffmpeg' to requirements.txt so a bundled ffmpeg is available.",
        RuntimeWarning,
    )

def ffmpeg_status():
    """Return (ffmpeg_path, ffprobe_path, ok_bool) where ok_bool is True if both are set."""
    conv = getattr(AudioSegment, "converter", None)
    probe = getattr(AudioSegment, "ffprobe", None)
    return conv, probe, bool(conv and probe)


def ensure_ffmpeg_available(raise_on_missing: bool = True):
    """Ensure ffmpeg/ffprobe are available for audio conversion.

    If raise_on_missing is True this raises RuntimeError with an actionable
    message explaining how to fix the environment. Otherwise returns False.
    """
    conv, probe, ok = ffmpeg_status()
    if ok:
        return True

    msg_lines = [
        "ffmpeg or ffprobe not available for audio conversion.",
        "Possible fixes:",
        " 1) Add 'imageio-ffmpeg' to requirements.txt so a bundled ffmpeg is available in the virtualenv.",
        " 2) Set environment variables FFMPEG_PATH and FFPROBE_PATH to the full paths of ffmpeg/ffprobe.",
        " 3) Install system ffmpeg on the host (apt/yum/brew or include in your Docker image).",
        "\nCurrent detection:",
        f"  ffmpeg (pydub AudioSegment.converter) = {conv}",
        f"  ffprobe (pydub AudioSegment.ffprobe) = {probe}",
    ]
    msg = "\n".join(msg_lines)
    if raise_on_missing:
        raise RuntimeError(msg)
    return False

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
