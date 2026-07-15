from dataclasses import dataclass
from pypdf import PdfReader
import re

@dataclass
class ArticleData:
    title: str
    text: str
    source: str


class PDFProcessor:
    """Extracts clean text from a PDF (e.g., a research article)."""

    def fetch(self, pdf_path: str, title: str = None) -> ArticleData:
        try:
            reader = PdfReader(pdf_path)
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF: {e}")

        if reader.is_encrypted:
            raise ValueError("This PDF is encrypted/password-protected and can't be read.")

        pages_text = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception:
                continue  # skip pages that fail to parse

        full_text = "\n".join(pages_text).strip()

        if len(full_text) < 200:
            raise ValueError("Could not extract enough text from this PDF (it may be scanned/image-based).")

        # crude cleanup: collapse excess whitespace/line breaks from PDF extraction
        full_text = " ".join(full_text.split())

        return ArticleData(
            title=title or pdf_path.split("/")[-1].rsplit(".", 1)[0],
            text=full_text,
            source=pdf_path,
        )

    def strip_references(self, text: str) -> str:
        """Cuts everything from the References section onward."""
        match = re.search(r'\bREFERENCES\b', text)
        if match:
            return text[:match.start()].strip()
        return text


# --- test the class ---
if __name__ == "__main__":
    processor = PDFProcessor()
    data = processor.fetch(
        "sources/Non-Invasive_Brain-Computer_Interfaces_State_of_the_Art_and_Trends.pdf",
        title="Non-Invasive Brain-Computer Interfaces: State of the Art and Trends"
    )
    print("Title:", data.title)
    print("Text length:", len(data.text))
    print(data.text[:500])

    clean_text = processor.strip_references(data.text)
    print(f"Original: {len(data.text)} chars -> After stripping references: {len(clean_text)} chars")

    with open('output/title.txt', 'w', encoding="utf-8") as f:
        f.write(data.title)

    with open('output/full_text.txt', 'w', encoding="utf-8") as f:
        f.write(data.text)

    print(f"Wrote {len(data.text)} characters to output/full_text.txt")