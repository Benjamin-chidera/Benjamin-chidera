# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### PyAudio Installation Failed

**Problem:** `pip install pyaudio` fails with compilation errors.

**Solutions:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

#### FFmpeg Not Found

**Problem:** Audio conversion fails with "ffmpeg not found".

**Solutions:**

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/
- Add to PATH environment variable

---

### Audio Issues

#### Microphone Not Working

**Problem:** No audio captured during recording.

**Diagnosis:**
```python
from src.utils.audio_utils import AudioUtils

utils = AudioUtils()
devices = utils.get_audio_devices()

for device in devices:
    if device['max_input_channels'] > 0:
        print(f"Input device: {device['name']}")
```

**Solutions:**
1. Check system audio settings
2. Grant microphone permissions
3. Test with other applications
4. Try different audio device index

#### Audio Playback Issues

**Problem:** No sound output during text-to-speech.

**Solutions:**
1. Check system volume settings
2. Verify speakers/headphones are connected
3. Try different TTS provider
4. Test with:
```bash
python -c "import pygame; pygame.mixer.init(); print('Audio system OK')"
```

#### Permission Denied (Linux/macOS)

**Problem:** Audio access denied.

**Solution:**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in
```

---

### API Issues

#### OpenAI API Key Invalid

**Problem:** OpenAI API calls fail with authentication error.

**Solutions:**
1. Verify API key in `.env` file
2. Check API key has sufficient credits
3. Ensure no extra spaces in key
4. Test API key:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.openai.com/v1/models
```

#### Rate Limiting

**Problem:** API calls fail with rate limit errors.

**Solutions:**
1. Implement retry logic with exponential backoff
2. Use local models for high-volume usage
3. Upgrade API plan
4. Add delays between requests

#### ElevenLabs API Issues

**Problem:** ElevenLabs TTS fails.

**Solutions:**
1. Check character quota in dashboard
2. Verify voice ID exists
3. Try different voice ID
4. Check API key permissions

---

### Model Issues

#### Whisper Model Download Fails

**Problem:** Local Whisper model fails to download.

**Solutions:**
1. Check internet connection
2. Clear Whisper cache:
```bash
rm -rf ~/.cache/whisper
```
3. Try smaller model first:
```python
config = {"provider": "whisper_local", "whisper_model": "tiny"}
```

#### Out of Memory Errors

**Problem:** Large models cause memory errors.

**Solutions:**
1. Use smaller models:
   - Whisper: "tiny" or "base"
   - LLM: Use API instead of local
2. Increase system RAM
3. Close other applications
4. Use GPU if available

#### Ollama Connection Failed

**Problem:** Cannot connect to Ollama server.

**Solutions:**
1. Start Ollama service:
```bash
ollama serve
```
2. Check if model is installed:
```bash
ollama list
ollama pull llama2
```
3. Verify URL in config:
```python
config = {"provider": "ollama", "ollama_url": "http://localhost:11434"}
```

---

### Performance Issues

#### Slow Speech Recognition

**Problem:** STT takes too long.

**Solutions:**
1. Use smaller Whisper model
2. Use API instead of local model
3. Reduce audio quality
4. Use GPU acceleration if available

#### Slow Text Generation

**Problem:** LLM responses are slow.

**Solutions:**
1. Use faster models (gpt-3.5-turbo vs gpt-4)
2. Reduce max_tokens
3. Use local models with GPU
4. Implement streaming responses

#### High CPU Usage

**Problem:** Application uses too much CPU.

**Solutions:**
1. Use API services instead of local models
2. Optimize audio processing settings
3. Reduce audio quality/sample rate
4. Close unnecessary applications

---

### Network Issues

#### Connection Timeouts

**Problem:** API calls timeout.

**Solutions:**
1. Check internet connection
2. Increase timeout values
3. Use retry mechanisms
4. Switch to local models

#### SSL/Certificate Errors

**Problem:** HTTPS requests fail.

**Solutions:**
1. Update certificates:
```bash
pip install --upgrade certifi
```
2. Check system time is correct
3. Try different network

---

### Configuration Issues

#### Configuration Validation Fails

**Problem:** Config validation returns errors.

**Solutions:**
1. Run validation:
```bash
python main.py --validate-config
```
2. Check required API keys are set
3. Verify provider names are correct
4. Check model names exist

#### Environment Variables Not Loaded

**Problem:** .env file not read.

**Solutions:**
1. Ensure .env file is in project root
2. Install python-dotenv:
```bash
pip install python-dotenv
```
3. Check file format (no spaces around =)
4. Restart application

---

### Development Issues

#### Import Errors

**Problem:** Cannot import modules.

**Solutions:**
1. Check Python path:
```python
import sys
sys.path.insert(0, 'src')
```
2. Verify file structure
3. Check __init__.py files exist
4. Use absolute imports

#### Async/Await Issues

**Problem:** Async functions not working.

**Solutions:**
1. Run in async context:
```python
import asyncio
asyncio.run(main())
```
2. Use await with async functions
3. Check event loop is running

---

## Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test STT only
from src.stt.speech_recognizer import SpeechRecognizer
config = {"provider": "whisper_local"}
recognizer = SpeechRecognizer(config)

# Test TTS only
from src.tts.speech_synthesizer import SpeechSynthesizer
config = {"provider": "pyttsx3"}
synthesizer = SpeechSynthesizer(config)

# Test LLM only
from src.llm.llm_processor import LLMProcessor
config = {"provider": "openai"}
processor = LLMProcessor(config)
```

### Check System Resources

```bash
# Check memory usage
free -h

# Check CPU usage
top

# Check disk space
df -h

# Check audio devices
aplay -l  # Linux
system_profiler SPAudioDataType  # macOS
```

### Test Audio System

```python
# Test audio recording
from src.utils.audio_utils import record_audio_to_file
await record_audio_to_file("test.wav", duration=3)

# Test audio playback
from src.utils.audio_utils import play_audio_file
await play_audio_file("test.wav")
```

---

## Getting Help

### Check Logs

Look for error messages in console output and log files.

### Minimal Reproduction

Create a minimal script that reproduces the issue:

```python
import asyncio
from src import SpeakToLLM

async def test():
    app = SpeakToLLM()
    response = await app.process_text_input("Hello")
    print(response)

asyncio.run(test())
```

### System Information

Collect system information for bug reports:

```python
import platform
import sys

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()}")

# Check dependencies
try:
    import openai
    print(f"OpenAI: {openai.__version__}")
except ImportError:
    print("OpenAI: Not installed")

try:
    import whisper
    print("Whisper: Installed")
except ImportError:
    print("Whisper: Not installed")
```

### Community Resources

- GitHub Issues: Report bugs and feature requests
- Documentation: Check API reference and examples
- Examples: Study working example code
- Tests: Run test suite to verify installation