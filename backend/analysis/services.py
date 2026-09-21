import json
from anthropic import Anthropic
from .pokemon_map import POKEMON_SONGS

client = Anthropic()

THEMES = [
    "hopeful", "melancholy", "determined", "peaceful", "lonely",
    "adventurous", "nostalgic", "anxious", "joyful", "reflective"
]

PROMPT = """Analyze this journal entry and identify 1-3 emotional themes.
Only choose from this exact list: {themes}

Return ONLY a valid JSON array of theme strings, nothing else.
Example: ["hopeful", "determined"]

Journal entry:
{content}"""


def analyze_entry(content: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": PROMPT.format(
                themes=", ".join(THEMES),
                content=content
            )
        }]
    )

    themes = json.loads(response.content[0].text)

    # return a song for every detected theme
    songs = [POKEMON_SONGS[theme] for theme in themes if theme in POKEMON_SONGS]

    # fallback if nothing matched
    if not songs:
        songs = [POKEMON_SONGS["default"]]

    return {
        "themes": themes,
        "songs": songs
    }