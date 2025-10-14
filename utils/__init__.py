"""utils package for Voice_Convert_Text

This file makes the `utils` directory a regular Python package so imports
like `from utils.audio_utils import ...` work reliably under different
execution environments (Streamlit runner, Docker, etc.).
"""

# Optionally expose common helpers at package level
from .audio_utils import ensure_wav_mono_16k, chunk_audio, duration_seconds
from .gemini_client import upload_file, transcribe_file, summarize_text, answer_question
from .export_utils import create_docx_from_text, create_pdf_from_text

__all__ = [
    "ensure_wav_mono_16k",
    "chunk_audio",
    "duration_seconds",
    "upload_file",
    "transcribe_file",
    "summarize_text",
    "answer_question",
    "create_docx_from_text",
    "create_pdf_from_text",
]
