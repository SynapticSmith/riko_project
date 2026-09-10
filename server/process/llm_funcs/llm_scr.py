# OpenAI tool calling with history 
### Uses a sample function
import yaml
import gradio as gr
import json
import os
from openai import OpenAI

with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

# Connects to OpenAI API by default. For local AI endpoints, it will use base_url if present.
client_args = {"api_key": char_config.get('OPENAI_API_KEY', 'sk-local')}
if 'base_url' in char_config and char_config['base_url']:
    client_args['base_url'] = char_config['base_url']

client = OpenAI(**client_args)

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
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return SYSTEM_PROMPT

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)



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

    response = client.chat.completions.create(
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