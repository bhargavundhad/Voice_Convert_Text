# 🚀 Quick Start Guide for Free Tier Users

## ⚡ **TL;DR - Free Tier Best Practices**

1. **📏 Use SHORT audio files** (1-5 minutes max)
2. **⏱️ Wait 2-3 minutes between processing sessions**
3. **🔧 Set throttle delay to 3+ seconds**
4. **📊 Process max 2-3 audio files per session**

## 🔬 **Free Tier Limits (Google Gemini)**

- **Requests**: ~15 requests per minute
- **Daily Quota**: Limited daily usage
- **File Size**: Up to 50MB per upload
- **Processing**: Best with files under 5 minutes

## 📋 **Recommended Workflow**

### ✅ **Good Practice:**
```
1. Upload 2-3 minute audio file
2. Set throttle to 3-5 seconds
3. Process the file
4. Wait 2-3 minutes before next file
5. Repeat
```

### ❌ **Avoid This:**
```
❌ Upload 10+ minute files
❌ Process multiple files quickly
❌ Use throttle delay < 3 seconds
❌ Process 4-5 files in 1 minute
```

## 🆘 **If You Hit Rate Limits**

### **Error Messages You Might See:**
- "API upload limit reached"
- "Quota exceeded" 
- "Rate limit exceeded"
- "Too many requests"

### **What to Do:**
1. **⏸️ STOP** processing immediately
2. **⏱️ WAIT** 2-3 minutes (set a timer!)
3. **📏 USE** shorter audio files (1-2 minutes)
4. **⚙️ INCREASE** throttle delay to 5-10 seconds
5. **🔄 TRY** again with smaller files

## 🎯 **Optimization Tips**

### **Audio Preparation:**
- **Split long recordings** into 2-3 minute chunks
- **Use good quality audio** (clear speech)
- **Avoid background noise** when possible

### **App Settings:**
- **Chunk Length**: 2-3 minutes for free tier
- **Throttle Delay**: 3-5 seconds minimum
- **Summary Mode**: Start with "concise"

### **Usage Patterns:**
- **Morning Session**: Process 2-3 files, then break
- **Afternoon Session**: Process 2-3 more files
- **Don't rush**: Quality over speed

## 📈 **When to Consider Paid Tier**

Consider upgrading if you:
- Process 10+ minutes of audio daily
- Need real-time processing
- Work with long lectures (20+ minutes)
- Use the app professionally

## 🔧 **Technical Details**

**Free Tier Quotas:**
- **Per Minute**: ~15 API calls
- **Per Day**: Limited total requests
- **File Upload**: 50MB max per file
- **Model Access**: All models available

**Each Audio Processing Uses:**
- 1 request per audio chunk upload
- 1 request per transcription
- 1 request for summarization
- = 3 requests per 5-minute audio chunk

**Example Calculation:**
- 10-minute audio = 2 chunks = 6 requests
- With throttle delays = safe processing
- Without delays = risk hitting limits

## 💡 **Pro Tips for Free Tier**

1. **Batch Process**: Prepare all audio files, then process one by one with breaks
2. **Test First**: Start with 1-2 minute test files
3. **Monitor Usage**: Keep track of how many files you've processed
4. **Plan Ahead**: Don't wait until deadlines to process important audio
5. **Quality Audio**: Better audio = better transcription = better value

## 🆘 **Troubleshooting**

**Problem**: "Rate limit exceeded"
**Solution**: Wait 2-3 minutes, use shorter files

**Problem**: "Quota exceeded" 
**Solution**: Wait until next day or upgrade

**Problem**: App stops mid-processing
**Solution**: Wait, then restart with smaller chunks

**Problem**: Poor transcription quality
**Solution**: Use clearer audio, try different chunk sizes