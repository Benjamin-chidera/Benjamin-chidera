# Installation Guide

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Node.js 16+ (for web interface, optional)
- Microphone for voice input
- Speakers or headphones for audio output

### 2. Installation

```bash
# Clone or copy the speak-to-llm directory
cd speak-to-llm

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Node.js dependencies for web interface
npm install
```

### 3. Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here  # Optional
```

### 4. Basic Usage

```python
from src import SpeakToLLM

# Initialize the application
app = SpeakToLLM()

# Start voice conversation
await app.start_conversation()
```

## Detailed Setup

### Audio Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
sudo apt-get install espeak espeak-data libespeak1 libespeak-dev
sudo apt-get install ffmpeg
```

#### macOS
```bash
brew install portaudio
brew install espeak
brew install ffmpeg
```

#### Windows
- Install Windows Build Tools
- Download and install PortAudio
- Install Visual C++ redistributables

### Provider-Specific Setup

#### OpenAI Whisper (Local)
```bash
# This is included in requirements.txt
pip install openai-whisper
```

#### Whisper Models
Models will be downloaded automatically on first use:
- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: Even better accuracy
- `large`: Best accuracy, slowest

#### ElevenLabs TTS
```bash
pip install elevenlabs
```
Requires API key from [ElevenLabs](https://elevenlabs.io/)

#### Ollama (Local LLM)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama2
ollama pull mistral
```

### Testing Installation

Run the test suite:
```bash
python -m pytest tests/ -v
```

Run basic examples:
```bash
python examples/basic_usage.py
```

### Common Issues

#### PyAudio Installation Problems
```bash
# Linux
sudo apt-get install portaudio19-dev
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Windows - use precompiled wheel
pip install pipwin
pipwin install pyaudio
```

#### Permission Issues (Linux/macOS)
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
```

#### Microphone Not Working
1. Check system audio settings
2. Test with other applications
3. Run audio device detection:
```python
from src.utils.audio_utils import AudioUtils
utils = AudioUtils()
print(utils.get_audio_devices())
```

### Performance Optimization

#### For CPU-constrained systems:
- Use `whisper tiny` model
- Use `pyttsx3` for TTS
- Use lighter LLM models

#### For GPU-accelerated systems:
- Install CUDA-enabled PyTorch
- Use larger Whisper models
- Use local GPU-accelerated LLMs

### API Rate Limits

- OpenAI: Track usage in dashboard
- ElevenLabs: Has character limits
- Consider implementing local alternatives for high usage

## Development Setup

### Setting up development environment:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run code formatting
black src/
flake8 src/

# Run tests
pytest tests/
```

### Project Structure

```
speak-to-llm/
├── src/
│   ├── __init__.py          # Main SpeakToLLM class
│   ├── stt/                 # Speech-to-Text
│   ├── tts/                 # Text-to-Speech  
│   ├── llm/                 # LLM processing
│   └── utils/               # Utilities
├── examples/                # Usage examples
├── tests/                   # Test suite
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
└── README.md               # Main documentation
```