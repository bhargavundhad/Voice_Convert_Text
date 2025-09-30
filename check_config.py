#!/usr/bin/env python3
"""
Configuration and deployment readiness check for Voice2Notes application
"""
import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment configuration...")
    
    load_dotenv()
    
    # Required environment variables
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key for transcription and summarization'
    }
    
    # Optional environment variables with defaults
    optional_vars = {
        'GEMINI_MODEL': 'gemini-2.5-flash (or gemini-2.5-pro for better quality)'
    }
    
    missing_vars = []
    
    print("\n📋 Required Environment Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20} (hidden)")
        else:
            print(f"❌ {var}: NOT SET - {description}")
            missing_vars.append(var)
    
    print("\n📋 Optional Environment Variables:")
    for var, default in optional_vars.items():
        value = os.getenv(var, default.split(' ')[0])
        print(f"ℹ️  {var}: {value}")
    
    return len(missing_vars) == 0, missing_vars

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'google.genai',
        'pydub', 
        'dotenv',
        'docx',
        'fpdf'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google.genai':
                from google import genai
            elif package == 'docx':
                from docx import Document
            else:
                __import__(package)
            print(f"✅ {package}: installed")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        '.env',
        'utils/audio_utils.py',
        'utils/export_utils.py', 
        'utils/gemini_client.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: exists")
        else:
            print(f"❌ {file_path}: MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

def main():
    """Main check function"""
    print("🚀 Voice2Notes Deployment Readiness Check\n")
    
    checks = [
        ("Environment Variables", check_environment),
        ("Dependencies", check_dependencies), 
        ("Required Files", check_files)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        passed, issues = check_func()
        if not passed:
            all_passed = False
            print(f"\n❌ {check_name} check failed:")
            for issue in issues:
                print(f"   - {issue}")
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 All checks passed! Application is ready for deployment.")
        print("\n📝 To run the application:")
        print("   streamlit run app.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above before deployment.")
        print("\n📝 Common fixes:")
        print("   - Set GEMINI_API_KEY in .env file")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Ensure all files are in the correct location")
        return 1

if __name__ == "__main__":
    sys.exit(main())