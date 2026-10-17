# Local AI Voice Assistant

This project provides a local AI conversational assistant. It listens, remembers your conversations, and responds using local models. It combines OpenAI-compatible LLM endpoints, GPT-SoVITS voice synthesis, and Faster-Whisper ASR into a fully configurable pipeline.

**tested with python 3.10 Windows >10 and Linux Ubuntu**
## ✨ Features

- 💬 **LLM-based dialogue** using any OpenAI-compatible local AI (e.g., LM Studio, Ollama, Hermes)
- 🧠 **Conversation memory** to keep context during interactions
- 🔊 **Voice generation** via GPT-SoVITS API
- 🎧 **Speech recognition** using Faster-Whisper
- 📁 Clean YAML-based config for personality configuration


## ⚙️ Configuration

All prompts and parameters are stored in `character_config.yaml`.

```yaml
OPENAI_API_KEY: sk-local
# To use a local API (e.g., LM Studio, Ollama with OpenAI compatibility, vLLM), provide the base_url here:
base_url: "http://localhost:1234/v1"
history_file: chat_history.json
model: "hermes-local"
presets:
  default:
    system_prompt: |
      You are a helpful, neutral AI assistant.
      You provide clear, accurate, and concise answers.

sovits_ping_config:
  text_lang: en
  prompt_lang : en
  ref_audio_path : character_files/main_sample.wav
  prompt_text : This is a sample voice for the text to speech synthesis.
  
```

You can define personalities and connect to different local runners by modifying the config file.


## 🛠️ Setup

### Install Dependencies

```bash
pip install uv 
uv pip install -r extra-req.txt
uv pip install -r requirements.txt
```

**If you want to use GPU support for Faster whisper** Make sure you also have:

* CUDA & cuDNN installed correctly (for Faster-Whisper GPU support)
* `ffmpeg` installed (for audio processing)


## 🧪 Usage

### 1. Launch the GPT-SoVITS API 

### 2. Run the main script:


```bash
python main_chat.py
```

The flow:

1. The AI listens to your voice via microphone (push to talk)
2. Transcribes it with Faster-Whisper
3. Passes it to the local LLM (with history)
4. Generates a response
5. Synthesizes the AI's voice using GPT-SoVITS
6. Plays the output back to you


## 📌 TODO / Future Improvements

* [ ] GUI or web interface
* [ ] Live microphone input support
* [ ] Emotion or tone control in speech synthesis
* [ ] Frontend interface


## 🧑‍🎤 Credits

* Voice synthesis powered by [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
* ASR via [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
* Language model originally powered by [OpenAI GPT](https://platform.openai.com)


## 📜 License

MIT — feel free to clone, modify, and build your own local AI voice companion.


