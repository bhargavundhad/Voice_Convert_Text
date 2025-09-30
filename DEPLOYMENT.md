# 🚀 Voice2Notes Deployment Guide

## Prerequisites

### Required Environment Variables
Create a `.env` file with:
```bash
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash  # Optional, defaults to gemini-2.5-flash
```

### Required Dependencies
```bash
pip install -r requirements.txt
```

## Quick Deployment Check

### 1. Environment Variables
```bash
# Check if .env file exists and has required variables
cat .env
```

### 2. Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Test imports
python -c "import streamlit, google.genai, pydub, dotenv, docx, fpdf; print('All dependencies OK')"
```

### 3. Run Application
```bash
streamlit run app.py
```

## File Structure
```
voice2notes/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── .env                  # Environment variables (create this)
└── utils/
    ├── audio_utils.py    # Audio processing
    ├── export_utils.py   # Document export
    └── gemini_client.py  # API client
```

## Supported Models
- `gemini-2.5-flash` (recommended - fast)
- `gemini-2.5-pro` (higher quality, slower)
- `gemini-2.0-flash` (previous generation)

## Troubleshooting

### Common Issues
1. **"GEMINI_API_KEY not found"** → Check .env file exists and has correct key
2. **"Model not found"** → Use supported model names listed above
3. **"Unicode encoding error"** → Should be fixed in latest version
4. **"File too large"** → Max 100MB upload, max 50MB per chunk

### Performance Tips
- Use shorter audio files (1-10 minutes) for testing
- Adjust chunk size based on file length
- Use throttling (1-3 seconds) to respect API limits

## Security Notes
- Never commit `.env` file to version control
- Keep API keys secure
- File uploads are processed locally and temporarily