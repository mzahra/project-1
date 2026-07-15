import os
import re
from openai import OpenAI
from pydub import AudioSegment

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_CHARS = 6000
TTS_INSTRUCTIONS = "Speak like a warm, engaging podcast host explaining an interesting science topic to a curious general audience. Natural pacing, clear articulation, not rushed."


def split_text_for_tts(text: str, max_chars: int = MAX_CHARS) -> list:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, current = [], ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
        else:
            if current:
                chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return chunks


def generate_audio(script_text: str, output_path: str = "output/podcast.mp3",
                    voice: str = "alloy", model: str = "gpt-4o-mini-tts") -> str:
    if not script_text or len(script_text.strip()) < 20:
        raise ValueError("Script text is too short to generate audio from.")

    chunks = split_text_for_tts(script_text)
    temp_files = []

    try:
        for i, chunk in enumerate(chunks):
            temp_path = f"output/_chunk_{i}.mp3"
            try:
                with client.audio.speech.with_streaming_response.create(
                    model=model,
                    voice=voice,
                    input=chunk,
                    instructions=TTS_INSTRUCTIONS,
                ) as response:
                    response.stream_to_file(temp_path)
            except Exception as e:
                raise RuntimeError(f"TTS API call failed on chunk {i+1}/{len(chunks)}: {e}")

            temp_files.append(temp_path)

        if len(temp_files) == 1:
            os.replace(temp_files[0], output_path)
        else:
            combined = AudioSegment.empty()
            for path in temp_files:
                combined += AudioSegment.from_mp3(path)
            combined.export(output_path, format="mp3")
            for path in temp_files:
                os.remove(path)

    finally:
        for path in temp_files:
            if os.path.exists(path):
                os.remove(path)

    return output_path


# --- test ---
if __name__ == "__main__":
    with open("output/podcast_script.txt", "r", encoding="utf-8") as f:
        script = f.read()

    audio_path = generate_audio(script, output_path="output/podcast.mp3")
    print(f"Audio saved to: {audio_path}")