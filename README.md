# Podcast Studio

Podcast Studio is a simple application that converts a research paper into a short podcast episode. Instead of reading a long academic paper, users can upload a PDF and receive a natural audio summary generated with Large Language Models (LLMs) and OpenAI's Text-to-Speech model.

The application follows a multi-stage pipeline. It first extracts the text from the PDF, identifies the most important ideas, generates a conversational podcast script, and finally converts that script into narrated audio. Everything is available through an easy-to-use Gradio web interface.

The idea is similar to NotebookLM's Audio Overviews, but focuses on research papers and provides users with both the generated script and the podcast audio.

---

# Features

- Upload a research paper in PDF format.
- Automatically extract and clean the document text.
- Remove the References section before sending the content to the LLM.
- Two-stage LLM workflow:
  - Extract key points from the paper.
  - Generate a natural podcast script from those key points.
- Convert the script into speech using OpenAI's `gpt-4o-mini-tts`.
- Choose different narration voices.
- Simple Gradio interface.
- Reload the previously generated podcast without making new API calls.
- Error handling for every stage of the pipeline.

---

# Project Structure

```text
podcast-studio/
│
├── article_processor.py      # Extracts text from PDFs and removes references
├── keypoint_generator.py     # Generates key points using GPT
├── llm_processor.py          # Creates the podcast script
├── tts_generator.py          # Converts the script into speech
├── main.py                   # Gradio application
├── requirements.txt
├── .env
├── README.md
│
└── output/
    ├── key_points.txt
    ├── podcast_script.txt
    └── podcast.mp3
```

---

# How the Pipeline Works

## Step 1: PDF → Text

The application reads the uploaded PDF using **pypdf**. After extracting the text, it automatically removes everything after the **References** section. Since citation lists are not useful for podcast listeners, removing them reduces token usage and improves the quality of the generated summary.

---

## Step 2: Text → Key Points

The cleaned text is sent to **gpt-4o-mini**.

Instead of asking the model to directly generate a podcast, the application first extracts the most important information, including:

- Research motivation
- Problem statement
- Main findings
- Contributions
- Practical implications
- Future work

Splitting the process into two LLM calls produces more focused and consistent results.

---

## Step 3: Key Points → Podcast Script

The extracted key points are passed to another **gpt-4o-mini** prompt.

This stage generates a natural single-speaker podcast script with:

- Introduction
- Main discussion
- Conclusion

The script is written as spoken language rather than an academic summary, making it more engaging for listeners.

---

## Step 4: Script → Audio

The generated script is converted into speech using **gpt-4o-mini-tts**.

If the script exceeds the model's input limit, it is automatically divided into smaller chunks. The generated audio pieces are then merged into one final podcast using **pydub**.

---

## Step 5: Gradio Interface

The Gradio application connects all stages of the pipeline.

Users simply:

1. Upload a PDF.
2. Enter an optional title.
3. Select a voice.
4. Click **Generate Podcast**.

The application displays the extracted key points, generated script, and the final audio player.

Users can also click **Listen to Existing Podcast** to reload the most recently generated output without calling the APIs again.

---

# Installation

## Prerequisites

- Python 3.8 or newer
- ffmpeg
- OpenAI API key

Install ffmpeg:

**macOS**

```bash
brew install ffmpeg
```

**Conda**

```bash
conda install -c conda-forge ffmpeg
```

---

## Clone the Repository

```bash
git clone https://github.com/mzahra/project-1.git
cd project-1
```

---

## Create a Virtual Environment

```bash
conda create -n podcast-studio
conda activate podcast-studio
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure the API Key

Create a `.env` file:

```text
OPENAI_API_KEY=openai-api-key
```

---

# Run the Application

```bash
python main.py
```

The application starts locally at:

```
http://127.0.0.1:7860
```

---

# Usage

1. Upload a research paper in PDF format.
2. Optionally enter a custom title.
3. Select a narration voice.
4. Click **Generate Podcast**.
5. Wait for the pipeline to finish.
6. Read the generated key points.
7. Review the generated podcast script.
8. Listen to or download the generated podcast.

To avoid additional API costs, click **Listen to Existing Podcast** to reload the latest generated episode.

---

# Example

The sample output included with this project was generated from:

> **Non-Invasive Brain-Computer Interfaces: State of the Art and Trends**  
> Edelman et al., IEEE Reviews in Biomedical Engineering (2025)

Generated files are saved in the `output` folder.

---

# Current Limitations

- Only PDF files are currently supported.
- Generating a new podcast overwrites the previous output.
- Complex PDF layouts (multiple columns or many figures) may not be extracted perfectly.
- Processing large research papers takes longer because the pipeline performs multiple LLM calls.

---

# Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | OpenAI `gpt-4o-mini` |
| Text-to-Speech | OpenAI `gpt-4o-mini-tts` |
| PDF Processing | `pypdf` |
| Audio Processing | `pydub` + `ffmpeg` |
| User Interface | Gradio |
