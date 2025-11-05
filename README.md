# 🎙️ Voice2Notes - AI-Powered Lecture Transcription

Convert audio lectures into structured notes using Google Gemini AI.

## 🚀 Features

- **Audio Processing**: Supports MP3, WAV, M4A, OGG, MP4 formats
- **AI Transcription**: Powered by Google Gemini 2.5 Flash/Pro
- **Smart Chunking**: Handles long audio files with automatic chunking
- **Multiple Exports**: TXT, Markdown, DOCX, and PDF formats
- **Interactive Q&A**: Ask questions about your transcribed content
- **Streamlit Interface**: Easy-to-use web interface

## 🔧 Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd voice2notes
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API key
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**Get your API key**: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 4. Run the Application
```bash
streamlit run app.py
```

## 📁 Project Structure

```
voice2notes/
├── app.py                 # Main Streamlit application
├── check_config.py        # Configuration validation script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusions
├── DEPLOYMENT.md         # Deployment guide
├── SECURITY.md           # Security guidelines
└── utils/
    ├── audio_utils.py    # Audio processing utilities
    ├── export_utils.py   # Document export functions
    └── gemini_client.py  # Google Gemini API client
```

## 🔒 Security

This project implements several security measures:

- ✅ API keys stored securely in environment variables
- ✅ Input validation and sanitization
- ✅ File type and size restrictions
- ✅ Secure temporary file handling
- ✅ Path traversal protection

**Important**: Never commit your `.env` file to version control!

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

## 🚀 Usage

1. **Upload Audio**: Select an audio file (max 100MB)
2. **Configure Settings**: Adjust chunk size and summary verbosity
3. **Process**: Click "Process" to transcribe and summarize
4. **Export**: Download your notes in preferred format
5. **Q&A**: Ask questions about the transcribed content

## ⚠️ **Important for Free Tier Users**

**Google Gemini Free Tier has strict limits:**
- 📊 **~15 requests per minute maximum**
- ⏱️ **Wait 2-3 minutes between processing sessions**
- 📏 **Keep audio files under 5 minutes for best results**
- 🔧 **Use 3+ seconds throttle delay**

**If you encounter rate limit errors:**
- ⏸️ Stop processing and wait 2-3 minutes
- 📱 Try smaller audio files (1-2 minutes)
- ⚙️ Increase throttle delay to 5-10 seconds
- 📈 Consider upgrading to paid tier for heavy usage

## ⚙️ Configuration

### Environment Variables
- `GEMINI_API_KEY` (required): Your Google Gemini API key
- `GEMINI_MODEL` (optional): Model to use (default: gemini-2.5-flash)

### Supported Models
- `gemini-2.5-flash` (recommended - fast and cost-effective)
- `gemini-2.5-pro` (higher quality, slower)
- `gemini-2.0-flash` (previous generation)

## 🔧 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Ensure `.env` file exists with your API key
   - Check that the key is valid

2. **"File too large" errors**
   - Maximum file size: 200MB
   - Consider splitting longer recordings

3. **API quota/rate limit errors**
   - Wait 5-10 minutes before retrying
   - Consider using shorter audio files
   - Increase throttle delay in settings

4. **Unicode encoding errors**
   - These should be automatically handled
   - Report if issues persist

### Performance Tips
- Use shorter audio files (1-10 minutes) for testing
- Adjust chunk size based on file length
- Use throttling (1-3 seconds) to respect API limits
- Choose appropriate model for your needs

## 📋 Configuration Check

Run the configuration checker to verify your setup:

```bash
python check_config.py
```

This will validate:
- Environment variables
- Required dependencies
- File structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Follow security guidelines in `SECURITY.md`
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and personal use.

## ⚠️ Disclaimer

- This tool processes audio files locally and uploads them to Google's Gemini API
- Ensure you have permission to process and transcribe any audio content
- Review Google's terms of service for API usage limits and policies
- Be mindful of privacy when processing sensitive content

## 🔗 Links

- [Google Gemini API Documentation](https://ai.google.dev/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Security Guidelines](SECURITY.md)
- [Deployment Guide](DEPLOYMENT.md)
