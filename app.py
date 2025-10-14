# app.py
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

from pydub import AudioSegment
AudioSegment.ffmpeg = r"E:/voice2_Project_Material/ffmpeg-8.0-essentials_build/ffmpeg-8.0-essentials_build/bin/ffmpeg.exe"
AudioSegment.ffprobe = r"E:/voice2_Project_Material/ffmpeg-8.0-essentials_build/ffmpeg-8.0-essentials_build/bin/ffprobe.exe"

import os
# print("ffprobe exists:", os.path.exists("/usr/bin/ffprobe"))

import time
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from utils.audio_utils import ensure_wav_mono_16k, chunk_audio, duration_seconds
from utils.gemini_client import upload_file, transcribe_file, summarize_text, answer_question
from utils.export_utils import create_docx_from_text, create_pdf_from_text




st.set_page_config(page_title="Lecture → Notes", layout="wide")
st.title("Lecture Voice → Notes (Streamlit + Gemini)")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

st.sidebar.header("Settings")
chunk_minutes = st.sidebar.slider("Chunk length (minutes)", 1, 10, 5)
summary_mode = st.sidebar.selectbox("Summary verbosity", ["concise", "detailed"])
throttle_seconds = st.sidebar.slider("Throttle between chunk requests (s)", 1, 10, 3)



# Processing status with better warnings
processing_warning = st.empty()
if st.session_state.get('last_processing_time'):
    import time
    time_since_last = time.time() - st.session_state['last_processing_time']
    if time_since_last < 120:  # Less than 2 minutes
        processing_warning.warning(
            f"⚠️ Last processing was {int(time_since_last)} seconds ago. "
            f"Wait {120 - int(time_since_last)} more seconds to avoid rate limits."
        )

# st.markdown("Upload a lecture audio (mp3/wav/m4a/mp4). We'll convert → chunk → upload → transcribe → summarize.")

# API Usage Tips
# with st.expander("💡 Tips for avoiding API limits"):
#     st.markdown("""
#     **If you get upload/quota errors:**
#     - ⏱️ **Wait 5-10 minutes** before retrying
#     - 📏 **Use shorter audio files** (under 10 minutes for testing)
#     - 🔧 **Increase chunk size** (5-10 minutes) to reduce API calls
#     - ⏸️ **Increase throttle delay** (2-3 seconds) in sidebar
#     - 📊 **Check your [Google API quotas](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)**
#     """)

uploaded = st.file_uploader("Upload audio file", type=["mp3", "wav", "m4a", "ogg", "mp4"])
if uploaded is None:
    st.info("No file uploaded yet. Example files: short lecture (1-10 min) are best to test.")
else:
    # File validation
    max_size_mb = 100  # 100MB limit
    if uploaded.size > max_size_mb * 1024 * 1024:
        st.error(f"File too large! Maximum size is {max_size_mb}MB. Your file is {uploaded.size/1024/1024:.1f}MB")
        st.stop()
    
    if uploaded.size == 0:
        st.error("Empty file uploaded. Please select a valid audio file.")
        st.stop()
    
    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded.name}")
    try:
        tmp.write(uploaded.getvalue())
        tmp.flush()
        uploaded_path = tmp.name
        st.success(f"Saved uploaded file: {uploaded.name} ({uploaded.size/1024/1024:.1f}MB)")
    except Exception as e:
        st.error(f"Failed to save uploaded file: {e}")
        st.stop()

    # show estimated duration
    try:
        dur = duration_seconds(uploaded_path)
        if dur > 3600:  # 1 hour limit
            st.warning(f"Very long audio ({dur // 60}m {dur % 60}s). Consider shorter files for better performance.")
        else:
            st.info(f"Estimated duration: {dur // 60}m {dur % 60}s")
    except Exception as e:
        st.warning("Could not determine duration: " + str(e))

    if st.button("Process (convert → chunk → transcribe → summarize)"):
        # Rate limiting check
        if st.session_state.get('last_processing_time'):
            time_since_last = time.time() - st.session_state['last_processing_time']
            if time_since_last < 120:  # Less than 2 minutes
                st.error(f"⚠️ **Rate Limit Protection**: Please wait {120 - int(time_since_last)} more seconds before processing again.")
                st.info("💡 This prevents API rate limit errors. Free tier Google Gemini has strict usage limits.")
                st.stop()
        
        # Validate API key
        if not os.getenv("GEMINI_API_KEY"):
            st.error("GEMINI_API_KEY not found in environment variables!")
            st.stop()
        
        # Set processing time
        st.session_state['last_processing_time'] = time.time()
        processing_warning.empty()  # Clear the warning
            
        wav_path = None
        chunks = []
        try:
            with st.spinner("Converting and chunking audio..."):
                try:
                    wav_path = ensure_wav_mono_16k(uploaded_path)
                    st.success("✅ Audio converted successfully")
                except Exception as e:
                    st.error(f"❌ Conversion failed: {e}")
                    st.stop()

                try:
                    chunks = chunk_audio(wav_path, chunk_length_seconds=chunk_minutes * 60)
                    st.success(f"✅ Created {len(chunks)} chunk(s)")
                    if len(chunks) > 10:
                        st.warning("⚠️ Many chunks detected. This will take significant time and API credits.")
                except Exception as e:
                    st.error(f"❌ Chunking failed: {e}")
                    st.stop()

            transcripts = []
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            for idx, (chunk_path, start_sec, end_sec) in enumerate(chunks):
                progress_bar.progress(int((idx / len(chunks)) * 100))
                status_placeholder.info(f"Processing chunk {idx+1}/{len(chunks)} (start {start_sec//60:02d}:{start_sec%60:02d}) ...")
                
                try:
                    status_placeholder.info(f"Uploading chunk {idx+1}/{len(chunks)}...")
                    file_obj = upload_file(chunk_path)
                    status_placeholder.info(f"Transcribing chunk {idx+1}/{len(chunks)}...")
                    text = transcribe_file(file_obj, model=GEMINI_MODEL)
                    transcripts.append((start_sec, text))
                    status_placeholder.success(f"✅ Chunk {idx+1} completed")
                except Exception as e:
                    error_msg = str(e)
                    
                    # Provide specific guidance for API limit errors
                    if any(phrase in error_msg.lower() for phrase in [
                        "api upload limit reached", "quota", "rate limit", "429", 
                        "too many requests", "resource exhausted"
                    ]):
                        st.error(f"🚫 **API Rate Limit Reached!**")
                        st.error("**What to do:**")
                        st.error("• ⏱️ Wait 2-3 minutes before trying again")
                        st.error("• 📏 Use shorter audio files (1-2 minutes)")
                        st.error("• ⚙️ Increase throttle delay to 5-10 seconds")
                        st.error("• � Consider upgrading to paid API tier")
                        st.info("💡 Free tier Google Gemini allows ~15 requests per minute maximum")
                        st.stop()  # Stop processing entirely
                    elif "503" in error_msg or "unavailable" in error_msg.lower():
                        st.warning(f"⚠️ Chunk {idx+1} failed: Google API temporarily unavailable. Try again in a few minutes.")
                    else:
                        st.warning(f"⚠️ Chunk {idx+1} failed: {str(e)[:100]}...")
                    
                    transcripts.append((start_sec, f"[ERROR: {str(e)[:50]}...]"))
                
                if idx < len(chunks) - 1:  # Don't sleep after last chunk
                    time.sleep(throttle_seconds)
            
            progress_bar.progress(100)
            status_placeholder.success(f"🎉 All chunks processed!")

            # Merge transcripts with simple timestamps
            merged = []
            for start, txt in transcripts:
                merged.append(f"[{start//60:02d}:{start%60:02d}] {txt.strip()}")
            merged_transcript = "\n\n".join(merged)
            
            # Store in session state for persistent Q&A
            st.session_state['transcript'] = merged_transcript
            st.session_state['summary'] = None  # Will be set after summarization

            st.header("📝 Merged transcript (preview)")
            st.text_area("Transcript", merged_transcript[:20000], height=300, help="Showing first 20,000 characters")

            st.header("🤖 Generate structured notes")
            with st.spinner("Creating summary..."):
                try:
                    summary_text = summarize_text(merged_transcript, mode=summary_mode)
                    st.session_state['summary'] = summary_text  # Store in session
                    st.success("✅ Summary generated successfully")
                except Exception as e:
                    st.error(f"❌ Summarization failed: {e}")
                    summary_text = f"ERROR: Summarization failed - {str(e)}"
                    st.session_state['summary'] = summary_text

        except Exception as e:
            st.error(f"❌ Processing failed: {e}")
            st.stop()
        finally:
            # Simple cleanup with better error handling
            cleanup_files = []
            if 'wav_path' in locals() and wav_path and os.path.exists(wav_path):
                cleanup_files.append(wav_path)
            if 'chunks' in locals():
                for chunk_path, _, _ in chunks:
                    if os.path.exists(chunk_path):
                        cleanup_files.append(chunk_path)
            if 'uploaded_path' in locals() and uploaded_path and os.path.exists(uploaded_path):
                cleanup_files.append(uploaded_path)
            
            # Try cleanup once, ignore errors
            for file_path in cleanup_files:
                try:
                    os.unlink(file_path)
                except:
                    pass  # Silently ignore cleanup errors

        st.subheader("📋 Summary / Notes (generated)")
        st.markdown(summary_text)

        # Export options
        st.markdown("### ⬇️ Download Options")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.download_button("📄 Transcript (TXT)", merged_transcript, file_name="transcript.txt", mime="text/plain")
        with col2:
            st.download_button("📝 Notes (MD)", summary_text, file_name="lecture_notes.md", mime="text/markdown")
        with col3:
            try:
                docx_bytes = create_docx_from_text(summary_text)
                st.download_button("📄 Notes (DOCX)", docx_bytes, file_name="lecture_notes.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(f"DOCX generation failed: {e}")
        with col4:
            try:
                pdf_bytes = create_pdf_from_text(summary_text)
                st.download_button("📄 Notes (PDF)", pdf_bytes, file_name="lecture_notes.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
