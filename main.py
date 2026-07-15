import os
import gradio as gr

from article_processor import PDFProcessor
from keypoint_generator import extract_key_points
from llm_processor import generate_script
from tts_generator import generate_audio

pdf_processor = PDFProcessor()

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral"]

OUTPUT_DIR = "output"
AUDIO_PATH = os.path.join(OUTPUT_DIR, "podcast.mp3")
KEY_POINTS_PATH = os.path.join(OUTPUT_DIR, "key_points.txt")
SCRIPT_PATH = os.path.join(OUTPUT_DIR, "podcast_script.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_pipeline(pdf_file, title, voice, progress=gr.Progress()):
    if pdf_file is None:
        raise gr.Error("Please upload a PDF first.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        progress(0.1, desc="Extracting text from PDF...")
        article = pdf_processor.fetch(pdf_file.name, title=title or None)
        clean_text = pdf_processor.strip_references(article.text)
    except Exception as e:
        raise gr.Error(f"PDF extraction failed: {e}")

    try:
        progress(0.35, desc="Extracting key points with LLM...")
        key_points = extract_key_points(clean_text, title=article.title)
        with open(KEY_POINTS_PATH, "w", encoding="utf-8") as f:
            f.write(key_points.summary)
    except Exception as e:
        raise gr.Error(f"Key point extraction failed: {e}")

    try:
        progress(0.6, desc="Writing podcast script...")
        script = generate_script(key_points.summary, title=article.title)
        with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(script.script)
    except Exception as e:
        raise gr.Error(f"Script generation failed: {e}")

    try:
        progress(0.85, desc="Generating audio (this can take a minute)...")
        audio_path = generate_audio(script.script, output_path=AUDIO_PATH, voice=voice)
    except Exception as e:
        raise gr.Error(f"Audio generation failed: {e}")

    progress(1.0, desc="Done!")
    return key_points.summary, script.script, audio_path


def load_existing_podcast():
    if not os.path.exists(AUDIO_PATH):
        raise gr.Error("No existing podcast found yet — generate one first.")

    key_points_text = ""
    if os.path.exists(KEY_POINTS_PATH):
        with open(KEY_POINTS_PATH, "r", encoding="utf-8") as f:
            key_points_text = f.read()

    script_text = ""
    if os.path.exists(SCRIPT_PATH):
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            script_text = f.read()

    return key_points_text, script_text, AUDIO_PATH


with gr.Blocks(title="Podcast Studio") as demo:
    gr.Markdown("# 🎙️ Podcast Studio\nUpload a research PDF and generate a podcast episode from it.")

    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            title_input = gr.Textbox(label="Title (optional)", placeholder="Leave blank to use the filename")
            voice_input = gr.Dropdown(choices=VOICES, value="echo", label="Voice")

            with gr.Row():
                generate_btn = gr.Button("Generate Podcast", variant="primary")
                listen_btn = gr.Button("Listen to Existing Podcast")

        with gr.Column(scale=1):
            audio_output = gr.Audio(label="Podcast Audio", type="filepath")
            with gr.Accordion("Key Points (extracted)", open=False):
                key_points_output = gr.Textbox(label="", lines=10, show_label=False)
            with gr.Accordion("Podcast Script", open=False):
                script_output = gr.Textbox(label="", lines=15, show_label=False)

    generate_btn.click(
        fn=run_pipeline,
        inputs=[pdf_input, title_input, voice_input],
        outputs=[key_points_output, script_output, audio_output],
    )

    listen_btn.click(
        fn=load_existing_podcast,
        inputs=[],
        outputs=[key_points_output, script_output, audio_output],
    )

if __name__ == "__main__":
    demo.launch()