# utils/gemini_client.py
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Try imports for different SDK variants
_client = None
_client_type = None
try:
    # new SDK: google-genai
    from google import genai
    _client = genai.Client(api_key=GEMINI_KEY)
    _client_type = "google-genai"
except Exception:
    try:
        # older package shape
        import google.generativeai as genai_old  # type: ignore
        genai_old.configure(api_key=GEMINI_KEY)
        _client = genai_old
        _client_type = "google-generativeai-old"
    except Exception:
        raise ImportError("Unable to import a supported Google GenAI SDK. Install 'google-genai'")

def _get_model_name(model: str) -> str:
    """Normalize model name for the SDK being used"""
    if _client_type == "google-genai":
        # New SDK requires models/ prefix
        if not model.startswith("models/"):
            return f"models/{model}"
        return model
    else:
        # Older SDK uses model name as-is
        return model

def upload_file(path: str):
    """
    Upload local file to Gemini Files API and return a "file object" that can be used in calls.
    For google-genai, this returns an object; for the older SDK, adjust accordingly.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    # Security: Validate file path to prevent directory traversal
    resolved_path = os.path.abspath(path)
    if not resolved_path.startswith(os.path.abspath(os.path.dirname(path))):
        raise ValueError("Invalid file path detected")
    
    file_size = os.path.getsize(path)
    if file_size == 0:
        raise ValueError("Cannot upload empty file")
    
    if file_size > 50 * 1024 * 1024:  # 50MB limit per chunk
        raise ValueError(f"File too large: {file_size/1024/1024:.1f}MB (max 50MB per chunk)")
    
    # Validate file extension for security
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.ogg', '.mp4', '.avi', '.mov', '.webm'}
    file_ext = os.path.splitext(path)[1].lower()
    if file_ext not in allowed_extensions:
        raise ValueError(f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}")
    
    # Retry logic for file upload with longer delays for API limits
    import time
    for attempt in range(3):
        try:
            if _client_type == "google-genai":
                f = _client.files.upload(file=path)
                return f
            else:
                # older style
                return _client.upload_file(path)
        except Exception as e:
            error_str = str(e)
            
            # Check for various API limit errors with more comprehensive detection
            rate_limit_indicators = [
                "503", "service unavailable", "unavailable",
                "upload status is not finalized", "rate limit", 
                "quota", "too many requests", "429",
                "resource exhausted", "deadline exceeded"
            ]
            
            if any(phrase in error_str.lower() for phrase in rate_limit_indicators):
                if attempt < 2:  # Not last attempt
                    wait_time = 30 * (attempt + 1)  # Wait 30, 60 seconds (longer for free tier)
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt - give helpful error message for free tier
                    if "upload status is not finalized" in error_str.lower():
                        raise Exception("API upload limit reached. Free tier users: wait 2-3 minutes before trying again.")
                    elif any(phrase in error_str.lower() for phrase in ["quota", "rate limit", "429", "resource exhausted"]):
                        raise Exception("API quota/rate limit exceeded. Free tier users: wait 2-3 minutes and use shorter audio files.")
                    else:
                        raise Exception("API temporarily unavailable. Please try again in 2-3 minutes.")
            
            # For other errors, don't retry
            raise Exception(f"File upload failed: {error_str}")

def transcribe_file(file_obj, model: str = MODEL, prompt: str = None):
    """
    Ask Gemini to transcribe the uploaded audio file.
    `file_obj` is the return value from upload_file.
    """
    if prompt is None:
        prompt = "Transcribe the audio to plain text. Provide timestamps for major sections if available. Output only spoken text."

    # Sanitize prompt for security
    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string")
    
    # Remove potentially harmful characters
    import re
    prompt = re.sub(r'[^\w\s\.\,\?\!\:\;\-\(\)]', '', prompt)
    
    if len(prompt) > 10000:
        raise ValueError("Prompt too long (max 10,000 characters)")
    
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty after sanitization")

    # Retry logic for API calls with better free tier handling
    import time
    for attempt in range(3):
        try:
            if _client_type == "google-genai":
                resp = _client.models.generate_content(
                    model=_get_model_name(model),
                    contents=[file_obj, prompt]
                )
                return resp.text
            else:
                # older SDK usage
                return _client.generate_text([file_obj, prompt], model_name=model).text
        except Exception as e:
            error_str = str(e)
            rate_limit_indicators = ["503", "UNAVAILABLE", "429", "quota", "rate limit", "resource exhausted"]
            
            if any(phrase in error_str.lower() for phrase in rate_limit_indicators):
                if attempt < 2:  # Not last attempt
                    wait_time = 30 * (attempt + 1)  # Wait 30, 60 seconds for free tier
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("API rate limit exceeded. Free tier users: wait 2-3 minutes before trying again.")
            
            raise Exception(f"Transcription failed: {str(e)}")

def summarize_text(text: str, model: str = MODEL, mode: str = "concise"):
    if not text or not text.strip():
        raise ValueError("Cannot summarize empty text")
    
    if len(text) > 100000:  # 100k character limit
        text = text[:100000] + "...(truncated)"
    
    if mode == "concise":
        instr = "Produce: (A) One-line TL;DR, (B) 6-12 bullet key takeaways, (C) 3 action items, (D) short glossary if present. Keep bullets concise."
    else:
        instr = "Create detailed lecture notes: one-line TL;DR, section headings, lists of points, short explanations, and next steps."

    prompt = f"{instr}\n\nTranscript:\n\n{text}"
    
    try:
        if _client_type == "google-genai":
            resp = _client.models.generate_content(model=_get_model_name(model), contents=[prompt])
            return resp.text
        else:
            return _client.generate_text(prompt, model_name=model).text
    except Exception as e:
        raise Exception(f"Summarization failed: {str(e)}")

def answer_question(context_text: str, question: str, model: str = MODEL):
    if not context_text or not context_text.strip():
        raise ValueError("Context text is required")
    
    if not question or not question.strip():
        raise ValueError("Question is required")
    
    # Limit input sizes
    if len(context_text) > 50000:
        context_text = context_text[:50000] + "...(truncated)"
    
    if len(question) > 1000:
        question = question[:1000]
    
    prompt = f"Context:\n{context_text}\n\nQuestion: {question}\nAnswer concisely using the context; if unsure, say 'Not stated in the transcript.'"
    
    try:
        if _client_type == "google-genai":
            resp = _client.models.generate_content(model=_get_model_name(model), contents=[prompt])
            return resp.text
        else:
            return _client.generate_text(prompt, model_name=model).text
    except Exception as e:
        raise Exception(f"Question answering failed: {str(e)}")
