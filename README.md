# Local AI Voice Assistant

This project provides a local AI conversational assistant. It listens, remembers your conversations, and responds using local models. It combines OpenAI-compatible LLM endpoints, GPT-SoVITS voice synthesis, and Faster-Whisper ASR into a fully configurable pipeline.

**tested with python 3.10 Windows >10 and Linux Ubuntu**
## ✨ Features

- 💬 **LLM-based dialogue** using any OpenAI-compatible local AI (e.g., LM Studio, Ollama, Hermes) or the local **`opencode`** CLI (free tier supported)
- 🧠 **Conversation memory** to keep context during interactions
- 🔊 **Voice generation** via GPT-SoVITS API
- 🎧 **Speech recognition** using Faster-Whisper
- 📁 Clean YAML-based config for personality configuration


## ⚙️ Configuration

All prompts and parameters are stored in `character_config.yaml`.

```yaml
# LLM backend: "openai" uses any OpenAI-compatible endpoint (see base_url below);
# "opencode" drives the locally installed `opencode` CLI (supports the free tier).
llm_provider: openai

OPENAI_API_KEY: sk-local
# To use a local API (e.g., LM Studio, Ollama with OpenAI compatibility, vLLM), provide the base_url here:
base_url: "http://localhost:1234/v1"
history_file: chat_history.json
model: "hermes-local"

# Settings for llm_provider: opencode. Requires the `opencode` CLI on PATH.
opencode:
  command: opencode
  model: opencode/big-pickle
  agent: voice-chat
  timeout: 180

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

Conversation history is stored in `history_file` (default `chat_history.json`). If that file is ever unreadable (empty, corrupt, or the wrong shape), the assistant starts a fresh conversation and moves the bad file to `chat_history.json.corrupt` instead of crashing.

### Using the `opencode` CLI as the LLM backend

Set `llm_provider: opencode` to run conversations through the local [`opencode`](https://opencode.ai) CLI instead of an HTTP endpoint. This needs **no API key** and can use opencode's anonymous free-tier models.

1. Install the `opencode` CLI and make sure it is on your `PATH`:
   ```bash
   opencode --version
   ```
2. Set `llm_provider: opencode` in `character_config.yaml` and pick a free model, e.g. `opencode/big-pickle`.
3. That's it — the assistant runs `opencode run` per turn, feeding the conversation in and echoing the reply into the same `chat_history.json` used by the OpenAI backend, so you can switch providers freely.

The project ships an `opencode.json` that defines a `voice-chat` agent (configured via `opencode.agent`). It disables every tool except `read`, which keeps replies fast and conversational.

> **Free-tier note:** the opencode free tier requires the `read` tool to stay enabled **and** allowed. Disabling or denying `read` makes the free tier return `403 FreeTierError`. If you use a paid model/account, you can disable `read` too.
>
> **Emoji:** local models may reply with emoji, which text-to-speech reads awkwardly. Add "Do not use emoji." to `system_prompt` if you want clean speech.


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


