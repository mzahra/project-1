import os
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SCRIPT_SYSTEM_PROMPT = """You are a podcast scriptwriter. Turn the key points below into a natural,
engaging, single-narrator podcast script for a general/educated audience interested in science
and technology.Stress the potential of the technology.

Requirements:
- Write in a conversational, spoken tone (contractions, natural rhythm); NOT an essay or bullet list.
- Structure: a short welcoming intro (hook the listener, state what the episode covers),
  a well-paced main body walking through the key points with natural transitions between ideas,
  and a brief outro that wraps up with a takeaway and sign-off.
- Do not use markdown formatting, headers, or bullet points; this text will be read aloud by
  a text-to-speech engine, so it must be plain spoken prose only.
- Avoid citation-style references (no "[1]", "et al.", etc.); just explain ideas in plain language.
- Target length: roughly 600-900 words (up to 5 minutes of spoken audio)."""


@dataclass
class PodcastScript:
    script: str
    title: str


def generate_script(key_points: str, title: str = "", model: str = "gpt-4o-mini") -> PodcastScript:
    if not key_points or len(key_points.strip()) < 50:
        raise ValueError("Key points input is too short to generate a script from.")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {title}\n\nKey points:\n{key_points}"},
            ],
            temperature=0.7,  # a bit more creative/natural for spoken tone
        )
    except Exception as e:
        raise RuntimeError(f"LLM API call failed: {e}")

    script_text = response.choices[0].message.content.strip()

    if not script_text:
        raise RuntimeError("LLM returned an empty script.")

    return PodcastScript(script=script_text, title=title)



# --- quick test ---
if __name__ == "__main__":
    with open("output/key_points.txt", "r", encoding="utf-8") as f:
        key_points = f.read()

    result = generate_script(
        key_points,
        title="Non-Invasive Brain-Computer Interfaces: State of the Art and Trends"
    )
    print(result.script)

    with open("output/podcast_script.txt", "w", encoding="utf-8") as f:
        f.write(result.script)