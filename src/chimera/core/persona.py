from pathlib import Path
from typing import Dict, List


def _normalize_title(title: str) -> str:
    t = title.strip().lower()
    t = t.replace("&", "and")
    t = t.replace(" ", "_")
    return t


def parse_soul_md(path: str) -> Dict[str, List[str] | str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()

    persona = {}
    current = None
    buffer: List[str] = []

    def flush():
        nonlocal current, buffer
        if not current:
            return
        key = _normalize_title(current)
        items = [ln.strip()[2:].strip() for ln in buffer if ln.strip().startswith("- ")]
        if items:
            persona[key] = items
        else:
            persona[key] = "\n".join([ln.strip() for ln in buffer if ln.strip()])
        buffer = []

    for ln in lines:
        if ln.strip().startswith("## "):
            flush()
            current = ln.strip()[3:]
            buffer = []
        else:
            if current:
                buffer.append(ln)

    flush()

    mapped = {}
    if "backstory" in persona:
        mapped["backstory"] = persona["backstory"]
    if "voice_and_tone" in persona:
        mapped["voice_tone"] = persona["voice_and_tone"]
    if "voice_and_tone" not in persona and "voice_&_tone" in persona:
        mapped["voice_tone"] = persona["voice_&_tone"]
    if "core_beliefs" in persona:
        mapped["core_beliefs"] = persona["core_beliefs"]
    if "values" in persona:
        mapped["values"] = persona["values"]
    if "directives" in persona:
        mapped["directives"] = persona["directives"]

    for k, v in persona.items():
        if k not in mapped:
            mapped[k] = v

    return mapped
