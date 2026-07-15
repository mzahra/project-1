import os
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@dataclass
class KeyPoints:
    summary: str
    source_title: str


SYSTEM_PROMPT = """You are a research analyst who prepares source material for a podcast writer.
Given the full text of an academic paper, extract the key points a general/educated audience
would find interesting. make the tone interesting engaging. 
Focus on: the core problem/motivation, main findings or contributions,
important methods or approaches (explained simply, no heavy jargon), real-world implications,
and open challenges or future directions.
Ignore: author affiliations, funding acknowledgments, and any reference/citation lists.
Output as clear, organized bullet points grouped under short headers
(e.g., "Motivation", "Key Findings", "Implications", "Open Challenges").
Keep it concise, aim for 400-700 words total."""


def extract_key_points(text: str, title: str = "", model: str = "gpt-4o-mini") -> KeyPoints:
    if not text or len(text.strip()) < 200:
        raise ValueError("Input text is too short to extract meaningful key points.")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Title: {title}\n\nPaper text:\n{text}"},
            ],
            temperature=0.3,
        )
    except Exception as e:
        raise RuntimeError(f"LLM API call failed: {e}")

    summary = response.choices[0].message.content.strip()

    if not summary:
        raise RuntimeError("LLM returned an empty response.")

    return KeyPoints(summary=summary, source_title=title)


# --- test ---
if __name__ == "__main__":
    with open("output/full_text.txt", "r", encoding="utf-8") as f:
        clean_text = f.read()

    result = extract_key_points(
        clean_text,
        title="Non-Invasive Brain-Computer Interfaces: State of the Art and Trends"
    )
    print(result.summary)

    with open("output/key_points.txt", "w", encoding="utf-8") as f:
        f.write(result.summary)