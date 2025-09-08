# Speak-to-LLM

Created a text to speech-speech to text/llm integration application.

## Overview

Speak-to-LLM is an AI-powered application that combines:
- **Text-to-Speech (TTS)**: Convert text to natural-sounding speech
- **Speech-to-Text (STT)**: Convert spoken words to text
- **Large Language Model (LLM)**: Process and generate intelligent responses

## Features

- 🎤 Real-time speech recognition
- 🗣️ Natural text-to-speech synthesis
- 🧠 LLM integration for intelligent conversations
- 🔄 Seamless voice-to-voice interaction
- 📝 Text input/output support

## Architecture

```
speak-to-llm/
├── src/
│   ├── tts/          # Text-to-Speech modules
│   ├── stt/          # Speech-to-Text modules
│   ├── llm/          # LLM integration
│   └── utils/        # Utility functions
├── examples/         # Example usage
├── docs/            # Documentation
├── tests/           # Test files
└── requirements.txt # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for web interface)
- Microphone access

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (if using web interface)
npm install
```

### Basic Usage

```python
from speak_to_llm import SpeakToLLM

# Initialize the application
app = SpeakToLLM()

# Start voice conversation
app.start_conversation()
```

## Technologies Used

- **Speech Recognition**: OpenAI Whisper, SpeechRecognition
- **Text-to-Speech**: pyttsx3, gTTS, ElevenLabs
- **LLM**: OpenAI GPT, Hugging Face Transformers, Ollama
- **Audio Processing**: PyAudio, librosa
- **Web Interface**: React.js, Web Audio API

## Configuration

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_key
ELEVENLABS_API_KEY=your_elevenlabs_key
HUGGINGFACE_API_KEY=your_hf_key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Author

Benjamin Chidera - AI/Software Engineer
- Portfolio: https://www.discoverbenix.com
- Email: benjaminchidera72@gmail.com