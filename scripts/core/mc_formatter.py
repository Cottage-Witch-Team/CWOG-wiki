import re
from dataclasses import dataclass

COLOR_MAP = {
    "l": "blue",
    "1": "navy",
    "5": "purple",
    "b": "aqua",
    "c": "red",
    "d": "pink",
    "a": "green",
    "e": "yellow",
    "6": "gold",
    "o": "italic",
}


@dataclass
class Chunk:
    text: str
    styles: list[str]


def _mc_to_chunks(text: str) -> list[Chunk]:
    chunks = []

    current_style: list[str] = []
    buffer = []

    i = 0

    def _flush() -> None:
        if buffer:
            chunks.append(Chunk("".join(buffer), current_style.copy()))
            buffer.clear()

    while i < len(text):
        if text[i] == "&" and i + 1 < len(text):
            code = text[i + 1].lower()

            # reset
            if code == "r":
                _flush()
                current_style.clear()
                i += 2
                continue

            # colour change
            if code in COLOR_MAP:
                _flush()
                current_style = [COLOR_MAP[code]]
                i += 2
                continue

        buffer.append(text[i])
        i += 1

    _flush()
    return chunks


def _chunks_to_markdown(chunks: list[Chunk]) -> str:
    out = []

    for c in chunks:
        text = c.text.strip()

        if not text:
            continue

        if c.styles:
            cls = " ".join(c.styles)
            out.append(f"**{text}**{{.{cls}}}")
        else:
            out.append(text)

    return " ".join(out)


def parse_mc_formatting_to_markdown(text: str) -> str:
    """Convert mc formatting to markdown/css format."""
    chunks = _mc_to_chunks(text)
    md = _chunks_to_markdown(chunks)
    return re.sub(r"\s+([,\.])", r"\1", md)
