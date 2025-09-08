# API Reference

## Core Classes

### SpeakToLLM

Main application class that orchestrates the entire workflow.

```python
from src import SpeakToLLM

app = SpeakToLLM(config_path="config.json")
```

#### Methods

##### `async start_conversation()`
Start an interactive voice conversation.

```python
await app.start_conversation()
```

##### `async process_voice_input() -> Optional[str]`
Capture and process voice input.

**Returns:** Transcribed text or None if recognition fails

##### `async process_text_with_llm(text: str) -> Optional[str]`
Process text through the LLM.

**Parameters:**
- `text`: Input text to process

**Returns:** LLM response or None if processing fails

##### `async speak_response(text: str) -> bool`
Convert text to speech and play it.

**Parameters:**
- `text`: Text to convert to speech

**Returns:** True if successful, False otherwise

##### `async process_text_input(text: str) -> Optional[str]`
Process text input directly (without speech-to-text).

**Parameters:**
- `text`: Input text

**Returns:** LLM response

##### `get_conversation_history() -> list`
Get the current conversation history.

**Returns:** List of conversation messages

##### `clear_conversation_history()`
Clear the conversation history.

---

### SpeechRecognizer

Speech-to-Text recognition with multiple backend support.

```python
from src.stt.speech_recognizer import SpeechRecognizer

config = {"provider": "whisper_local", "language": "en"}
recognizer = SpeechRecognizer(config)
```

#### Methods

##### `async listen(duration: Optional[float] = None) -> Optional[bytes]`
Listen for audio input from microphone.

**Parameters:**
- `duration`: Duration to record in seconds. If None, records until silence.

**Returns:** Audio data as bytes or None if recording fails

##### `async transcribe(audio_data: Union[bytes, str, Path]) -> Optional[str]`
Transcribe audio to text.

**Parameters:**
- `audio_data`: Audio data as bytes, file path, or Path object

**Returns:** Transcribed text or None if transcription fails

##### `set_language(language: str)`
Set the recognition language.

**Parameters:**
- `language`: Language code (e.g., "en", "es", "fr")

---

### SpeechSynthesizer

Text-to-Speech synthesis with multiple backend support.

```python
from src.tts.speech_synthesizer import SpeechSynthesizer

config = {"provider": "pyttsx3", "language": "en"}
synthesizer = SpeechSynthesizer(config)
```

#### Methods

##### `async synthesize(text: str, output_file: Optional[str] = None) -> Optional[bytes]`
Convert text to speech audio.

**Parameters:**
- `text`: Text to convert to speech
- `output_file`: Optional file path to save audio

**Returns:** Audio data as bytes or None if synthesis fails

##### `async speak(text: str) -> bool`
Synthesize and immediately play speech.

**Parameters:**
- `text`: Text to speak

**Returns:** True if successful, False otherwise

##### `set_voice(voice_id: str)`
Set the voice for speech synthesis.

##### `set_speed(speed: int)`
Set the speech speed (words per minute).

##### `set_volume(volume: float)`
Set the speech volume (0.0 to 1.0).

##### `get_available_voices() -> list`
Get list of available voices.

**Returns:** List of voice dictionaries with id, name, and language

---

### LLMProcessor

Large Language Model processing for generating intelligent responses.

```python
from src.llm.llm_processor import LLMProcessor

config = {"provider": "openai", "model_name": "gpt-3.5-turbo"}
processor = LLMProcessor(config)
```

#### Methods

##### `async generate_response(message: str, conversation_history: Optional[List[Dict[str, str]]] = None, **kwargs) -> Optional[str]`
Generate a response to the given message.

**Parameters:**
- `message`: User message
- `conversation_history`: Previous conversation messages
- `**kwargs`: Additional parameters for generation

**Returns:** Generated response or None if generation fails

##### `async generate_streaming_response(message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> AsyncGenerator[str, None]`
Generate a streaming response.

**Parameters:**
- `message`: User message
- `conversation_history`: Previous conversation messages

**Yields:** Response chunks as they're generated

##### `async summarize_conversation(conversation_history: List[Dict[str, str]]) -> str`
Generate a summary of the conversation history.

**Parameters:**
- `conversation_history`: List of conversation messages

**Returns:** Conversation summary

##### `set_system_prompt(prompt: str)`
Set a custom system prompt.

##### `set_temperature(temperature: float)`
Set the generation temperature (0.0 to 2.0).

##### `set_max_tokens(max_tokens: int)`
Set the maximum number of tokens to generate.

---

## Utility Classes

### Config

Configuration management for the application.

```python
from src.utils.config import Config

config = Config("config.json")
```

#### Properties

- `stt_config`: Speech-to-Text configuration
- `tts_config`: Text-to-Speech configuration
- `llm_config`: LLM configuration
- `audio_config`: Audio configuration

#### Methods

##### `update_config(path: str, value: Any)`
Update a configuration value.

**Parameters:**
- `path`: Dot-separated path to configuration key (e.g., "stt.provider")
- `value`: New value

##### `get_config_value(path: str, default: Any = None) -> Any`
Get a configuration value by path.

##### `validate_config() -> List[str]`
Validate configuration and return list of issues.

##### `save_config(file_path: str)`
Save current configuration to file.

---

### AudioUtils

Audio processing utilities.

```python
from src.utils.audio_utils import AudioUtils

audio_utils = AudioUtils()
```

#### Methods

##### `async play_audio(audio_data: bytes, file_format: str = "wav") -> bool`
Play audio data.

##### `async record_audio(duration: Optional[float] = None) -> Optional[bytes]`
Record audio from microphone.

##### `get_audio_devices() -> List[Dict]`
Get list of available audio devices.

##### `analyze_audio(audio_data: bytes) -> Dict`
Analyze audio properties.

##### `detect_silence(audio_data: bytes, threshold: float = 0.01) -> List[Tuple[float, float]]`
Detect silence segments in audio.

##### `trim_silence(audio_data: bytes, threshold: float = 0.01) -> Optional[bytes]`
Remove silence from beginning and end of audio.

---

## Convenience Functions

### Quick Functions

```python
# Quick LLM chat
from src.llm.llm_processor import chat_with_llm
response = await chat_with_llm("Hello!", provider="openai")

# Quick TTS
from src.tts.speech_synthesizer import text_to_speech, speak_text
audio_data = await text_to_speech("Hello world!")
await speak_text("Hello world!")

# Quick STT
from src.stt.speech_recognizer import transcribe_audio, transcribe_file
text = await transcribe_audio(audio_data)
text = await transcribe_file("audio.wav")

# Quick audio utilities
from src.utils.audio_utils import play_audio_file, record_audio_to_file
await play_audio_file("audio.wav")
await record_audio_to_file("recording.wav", duration=5.0)
```

---

## Configuration Options

### STT Providers

- `whisper_local`: Local Whisper model
- `whisper_api`: OpenAI Whisper API
- `google`: Google Speech Recognition

### TTS Providers

- `pyttsx3`: Offline TTS engine
- `gtts`: Google Text-to-Speech
- `elevenlabs`: ElevenLabs premium TTS
- `openai`: OpenAI TTS API

### LLM Providers

- `openai`: OpenAI GPT models
- `huggingface`: Hugging Face transformers
- `ollama`: Local Ollama models

### Configuration Example

```json
{
  "stt": {
    "provider": "whisper_local",
    "whisper_model": "base",
    "language": "en"
  },
  "tts": {
    "provider": "elevenlabs",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "speed": 150
  },
  "llm": {
    "provider": "openai",
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 150
  }
}
```