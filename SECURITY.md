# 🔒 Security Guidelines for Voice2Notes

## Overview
This document outlines the security measures implemented in Voice2Notes and best practices for secure deployment.

## Security Features Implemented

### 1. Environment Variable Protection
- ✅ API keys stored in `.env` file (excluded from version control)
- ✅ `.env.example` provided for setup guidance
- ✅ Runtime validation of required environment variables

### 2. Input Validation & Sanitization
- ✅ File size limits (100MB upload, 50MB per chunk)
- ✅ Audio duration limits (3 hours maximum)
- ✅ File type validation (only audio formats allowed)
- ✅ Prompt sanitization for API calls
- ✅ Path traversal protection

### 3. Secure File Handling
- ✅ Temporary files created with secure permissions (0o700)
- ✅ Automatic cleanup of temporary files
- ✅ Unique temporary directory names to prevent conflicts
- ✅ Limited number of chunks to prevent resource exhaustion

### 4. API Security
- ✅ Rate limiting and retry logic for API calls
- ✅ Error message sanitization to prevent information leakage
- ✅ Input size limits for all API requests

## Deployment Security Checklist

### Before Pushing to GitHub
- [ ] Ensure `.env` file is in `.gitignore`
- [ ] Verify no API keys are hardcoded in source files
- [ ] Check that sensitive files are excluded from version control
- [ ] Validate all user inputs are properly sanitized

### Production Deployment
- [ ] Use HTTPS for all connections
- [ ] Set up proper logging without exposing sensitive data
- [ ] Implement proper error handling
- [ ] Use environment variables for all configuration
- [ ] Regular security updates for dependencies

## Environment Variables Required

```bash
# Required
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional (with secure defaults)
GEMINI_MODEL=gemini-2.5-flash
```

## File Exclusions (.gitignore)
The following files/directories are excluded from version control:
- `.env` (contains API keys)
- `__pycache__/` (Python cache files)
- `*.pyc` (compiled Python files)
- `temp/`, `tmp/` (temporary files)
- Audio files (`*.mp3`, `*.wav`, etc.)
- Generated documents (`*.pdf`, `*.docx`)
- OS-specific files (`.DS_Store`, `Thumbs.db`)

## Security Vulnerabilities to Avoid

### ❌ What NOT to do:
1. Never commit API keys to version control
2. Don't hardcode sensitive information in source files
3. Avoid running with excessive file permissions
4. Don't skip input validation for user uploads
5. Never expose detailed error messages to end users

### ✅ What TO do:
1. Use environment variables for all secrets
2. Validate all user inputs
3. Implement proper error handling
4. Use secure temporary file handling
5. Regularly update dependencies

## Security Contact
For security issues or questions, please review the code carefully before deployment and ensure all security guidelines are followed.

## Additional Recommendations

### For Enhanced Security:
1. **Authentication**: Consider adding user authentication for production use
2. **Logging**: Implement secure logging without exposing sensitive data
3. **Monitoring**: Set up monitoring for unusual API usage patterns
4. **Updates**: Regularly update dependencies to patch security vulnerabilities
5. **Backup**: Secure backup procedures for any persistent data

### Development Security:
1. Use virtual environments to isolate dependencies
2. Regularly audit dependencies for known vulnerabilities
3. Use code scanning tools before deployment
4. Follow the principle of least privilege for file permissions