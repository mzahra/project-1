# Podcast Studio

Podcast Studio is a simple pipeline that turns a research paper into a short podcast episode. You upload a PDF, the application extracts the text, uses an LLM to identify the main ideas, generates a natural podcast script, and finally converts it into narrated audio. Everything is available through a Gradio web interface.

The project works like an **Article-to-Podcast Converter**. It takes a research paper as input and produces a podcast episode, similar to NotebookLM's Audio Overviews.

## Features

- Upload a research PDF and automatically extract the text.
- Automatically remove the references section.
- Two-stage LLM pipeline for key points and podcast script.
- Convert the script into speech using `gpt-4o-mini-tts`.
- Gradio web interface.
- Reload the last generated podcast without using API credits again.
- Error handling for every pipeline stage.

## Tech Stack

- OpenAI `gpt-4o-mini`
- OpenAI `gpt-4o-mini-tts`
- `pypdf`
- `pydub`
- Gradio
