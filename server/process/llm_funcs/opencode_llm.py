# LLM backend that drives the locally installed `opencode` CLI.
#
# This lets the voice assistant talk to opencode's models (including the
# anonymous free tier) without any API key or OpenAI-compatible endpoint.
# It runs `opencode run` as a child process, feeds the conversation as a
# single prompt on stdin, and parses the streamed JSON to extract the reply.
import json
import os
import shutil
import subprocess

# Windows: do not flash a console window for the child process.
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# Project root: this file is <root>/server/process/llm_funcs/opencode_llm.py
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def resolve_command(configured=None):
    """Resolve the opencode executable name/path to a runnable path."""
    for candidate in (configured, "opencode", "opencode.cmd"):
        if not candidate:
            continue
        found = shutil.which(candidate)
        if found:
            return found
    raise FileNotFoundError(
        "Could not find the 'opencode' executable. Install opencode or set "
        "'opencode.command' in character_config.yaml."
    )


def _flatten(content):
    """Flatten an OpenAI-style message content (str or list of parts) to text."""
    if isinstance(content, list):
        # Accept any part carrying text (input_text / output_text / text).
        return "".join(
            str(part.get("text", ""))
            for part in content
            if isinstance(part, dict)
        )
    return content or ""


def build_transcript(messages):
    """Render the message list into one prompt for `opencode run`.

    The leading system message becomes instructions; the remaining turns are
    shown as a labelled transcript ending with the latest user message.
    """
    system_parts = []
    turns = []
    for msg in messages:
        role = msg.get("role")
        text = _flatten(msg.get("content"))
        if role == "system":
            system_parts.append(text)
        elif role == "user":
            turns.append(("User", text))
        else:
            turns.append(("Assistant", text))

    lines = []
    if system_parts:
        lines.append("\n".join(system_parts).strip())
        lines.append("")
    if len(turns) > 1:
        lines.append("Conversation so far:")
        for label, text in turns[:-1]:
            lines.append("%s: %s" % (label, text))
        lines.append("")
    if turns:
        lines.append(
            "Continue the conversation as the assistant, replying to the last "
            "user message. Output only your reply."
        )
        lines.append("User: %s" % turns[-1][1])
    return "\n".join(lines)


def parse_reply(stdout):
    """Extract the assistant text from opencode's `--format json` output."""
    parts = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if event.get("type") == "text":
            text = event.get("part", {}).get("text")
            if text:
                parts.append(text)
    return "".join(parts).strip()


def get_opencode_response(messages, command=None, model=None, agent=None,
                          timeout=180, workdir=None):
    """Send the conversation to `opencode run` and return the reply text."""
    exe = resolve_command(command)

    argv = [exe, "run", "--format", "json"]
    if model:
        argv += ["--model", model]
    if agent:
        argv += ["--agent", agent]

    prompt = build_transcript(messages)
    try:
        proc = subprocess.run(
            argv,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            creationflags=_CREATE_NO_WINDOW,
            cwd=workdir or _PROJECT_ROOT,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("opencode timed out after %ss" % timeout) from exc

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[:500]
        raise RuntimeError("opencode exited with %s: %s" % (proc.returncode, detail))

    reply = parse_reply(proc.stdout)
    if not reply:
        raise RuntimeError(
            "opencode returned no text: %s" % (proc.stdout or "").strip()[:500]
        )
    return reply
