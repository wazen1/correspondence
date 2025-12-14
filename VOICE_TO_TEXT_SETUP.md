# Voice-to-Text Feature - FFmpeg Installation Guide

## ⚠️ Important Requirement

The Voice-to-Text feature requires **FFmpeg** to convert audio formats (WebM, MP3, M4A) to WAV for speech recognition.

## 🔧 Installation Instructions

### Ubuntu/Debian (Recommended)
```bash
sudo apt update
sudo apt install -y ffmpeg
```

### Verify Installation
```bash
ffmpeg -version
ffprobe -version
```

### After Installation
```bash
cd /home/erp/frappe-bench
bench restart
```

## 📝 Alternative: Use WAV Files Only

If you cannot install FFmpeg, you can still use the Voice-to-Text feature by:

1. **Recording in WAV format** - Some recording apps allow you to save directly as WAV
2. **Converting files manually** - Use online converters to convert MP3/M4A to WAV before uploading
3. **Using browser recording** - The live recording feature saves as WebM, which requires FFmpeg

## 🎯 Supported Audio Formats

### With FFmpeg Installed:
- ✅ WAV (recommended)
- ✅ MP3
- ✅ M4A
- ✅ WebM (browser recordings)
- ✅ OGG
- ✅ FLAC

### Without FFmpeg:
- ✅ WAV only

## 🐛 Troubleshooting

### Error: "FFmpeg is not installed"
**Solution:** Install FFmpeg using the commands above

### Error: "Failed to convert audio format"
**Solutions:**
1. Install FFmpeg (preferred)
2. Upload WAV files instead
3. Check file is not corrupted

### FFmpeg installed but still getting errors
**Solution:** Restart the bench after installation:
```bash
bench restart
```

## 📞 Need Help?

If you're unable to install FFmpeg due to system restrictions, contact your system administrator or use WAV files only.

## ✨ Once FFmpeg is Installed

The Voice-to-Text feature will support:
- 🎤 Live microphone recording
- 📁 Multiple audio formats
- 🌍 8 languages (English, Arabic, French, German, Spanish, Italian, Chinese, Japanese)
- ⏱️ Real-time recording timer
- 🎧 Audio preview before conversion
