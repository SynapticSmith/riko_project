# OpenAI tool calling with history 
### Uses a sample function
import yaml
import gradio as gr
import json
import os
import copy

try:
    from .opencode_llm import get_opencode_response
except ImportError:
    from opencode_llm import get_opencode_response

with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

# LLM backend selection: "openai" (any OpenAI-compatible endpoint) or "opencode".
LLM_PROVIDER = char_config.get('llm_provider', 'openai')

# Settings for the opencode CLI backend.
opencode_config = char_config.get('opencode', {}) or {}
OPENCODE_COMMAND = opencode_config.get('command', 'opencode')
OPENCODE_MODEL = opencode_config.get('model')
OPENCODE_AGENT = opencode_config.get('agent')
OPENCODE_TIMEOUT = opencode_config.get('timeout', 180)

# The OpenAI client is created lazily so the opencode backend works even when
# the openai package or a server endpoint is not available.
client = None

def get_client():
    global client
    if client is None:
        from openai import OpenAI
        # Connects to OpenAI API by default. For local AI endpoints, it will use base_url if present.
        client_args = {"api_key": char_config.get('OPENAI_API_KEY', 'sk-local')}
        if 'base_url' in char_config and char_config['base_url']:
            client_args['base_url'] = char_config['base_url']
        client = OpenAI(**client_args)
    return client

# Constants
HISTORY_FILE = char_config['history_file']
MODEL = char_config['model']
SYSTEM_PROMPT =  [
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": char_config['presets']['default']['system_prompt']  
                }
            ]
        }
    ]

# Load/save chat history
def _quarantine_bad_history():
    """Move an unreadable/unusable history file aside so it is not re-read."""
    backup = HISTORY_FILE + ".corrupt"
    try:
        if os.path.exists(backup):
            os.remove(backup)
        os.replace(HISTORY_FILE, backup)
        print(f"[llm_scr] Unreadable history moved to '{backup}'.")
    except OSError as exc:
        print(f"[llm_scr] Could not quarantine '{HISTORY_FILE}': {exc}")


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return copy.deepcopy(SYSTEM_PROMPT)
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"[llm_scr] Warning: could not read '{HISTORY_FILE}' ({exc}); starting fresh.")
        _quarantine_bad_history()
        return copy.deepcopy(SYSTEM_PROMPT)
    if not isinstance(history, list) or not history:
        print(f"[llm_scr] Warning: '{HISTORY_FILE}' is not a message list; starting fresh.")
        _quarantine_bad_history()
        return copy.deepcopy(SYSTEM_PROMPT)
    return history

def save_history(history):
    # Write to a temp file then replace, so an interrupted write can't leave a
    # half-written (corrupt) history behind.
    tmp_path = HISTORY_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
    os.replace(tmp_path, HISTORY_FILE)



def get_ai_response_no_tool(messages):

    # Standard OpenAI chat completions endpoint.
    # Depending on your local Hermes server support, you might need to adjust formatting.
    # We are using standard chat.completions since it is widely supported by local OpenAI wrappers

    # We reformat the messages here since many local runners don't yet support the beta "input_text" format
    standard_messages = []
    for msg in messages:
        if isinstance(msg.get("content"), list):
             # Just grab the first text item for simplicity
             standard_messages.append({"role": msg["role"], "content": msg["content"][0]["text"]})
        else:
             standard_messages.append({"role": msg["role"], "content": msg["content"]})

    response = get_client().chat.completions.create(
        model=MODEL,
        messages=standard_messages,
        temperature=0.7,
        top_p=1,
        max_tokens=2048,
        stream=False,
    )

    return response


def llm_response(user_input):

    messages = load_history()

    # Append user message to memory
    messages.append({
        "role": "user",
        "content": [
            {"type": "input_text", "text": user_input}
        ]
    })


    if LLM_PROVIDER == 'opencode':
        response_text = get_opencode_response(
            messages,
            command=OPENCODE_COMMAND,
            model=OPENCODE_MODEL,
            agent=OPENCODE_AGENT,
            timeout=OPENCODE_TIMEOUT,
        )
    else:
        ai_test_response = get_ai_response_no_tool(messages)
        response_text = ai_test_response.choices[0].message.content

    # just append assistant message to regular response. 
    messages.append({
    "role": "assistant",
    "content": [
        {"type": "output_text", "text": response_text}
    ]
    })

    save_history(messages)
    return response_text


if __name__ == "__main__":
    print('running main')