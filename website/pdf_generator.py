"""
PDF Generation for Dicto-DX
Dyslexia-friendly PDF export with optimal formatting
"""

from typing import Optional
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from flask import Response
from .utils import markdown_to_pdf_text


def create_dyslexia_friendly_pdf(
    transcript: str, summary: str, timestamp: Optional[datetime] = None
) -> bytes:

    if timestamp is None:
        timestamp = datetime.now()

    # Create a BytesIO buffer to hold the PDF
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.2 * inch,  # Generous margins
        rightMargin=1.2 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = _create_dyslexia_styles()

    story = []

    # Extract title from summary (first line after converting from markdown)
    pdf_formatted_summary = markdown_to_pdf_text(summary)
    lines = pdf_formatted_summary.split("\n")
    summary_title = lines[0].strip() if lines else "Voice Note Summary"
    summary_body = (
        "\n".join(lines[1:]).strip() if len(lines) > 1 else pdf_formatted_summary
    )

    # Title
    title = Paragraph(summary_title, styles["title"])
    story.append(title)
    story.append(Spacer(1, 0.2 * inch))

    # Created timestamp
    date_str = timestamp.strftime("%B %d, %Y at %I:%M %p")
    date_para = Paragraph(f"Created: {date_str}", styles["metadata"])
    story.append(date_para)
    story.append(Spacer(1, 0.3 * inch))

    # Summary body
    summary_formatted = _format_text_for_dyslexia(summary_body)
    summary_para = Paragraph(summary_formatted, styles["body"])
    story.append(summary_para)
    story.append(Spacer(1, 0.4 * inch))

    # Footer - Created by Dicto-DX
    footer_para = Paragraph(
        'Created by <a href="https://josephfoster.me/dicto">Dicto</a>',
        styles["metadata"],
    )
    story.append(footer_para)

    # Build PDF
    doc.build(story)

    # Get the PDF content
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    buffer.close()

    return pdf_content


def _create_dyslexia_styles() -> dict:
    base_styles = getSampleStyleSheet()

    styles = {}

    # Title style
    styles["title"] = ParagraphStyle(
        "DyslexiaTitle",
        parent=base_styles["Title"],
        fontName="Helvetica",  # Arial-equivalent in ReportLab
        fontSize=20,
        leading=30,  # 1.5x line spacing
        alignment=TA_LEFT,
        spaceAfter=12,
        textColor="black",
    )

    # Heading style
    styles["heading"] = ParagraphStyle(
        "DyslexiaHeading",
        parent=base_styles["Heading1"],
        fontName="Helvetica",
        fontSize=16,
        leading=24,  # 1.5x line spacing
        alignment=TA_LEFT,
        spaceAfter=8,
        spaceBefore=12,
        textColor="black",
    )

    # Body text style
    styles["body"] = ParagraphStyle(
        "DyslexiaBody",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=12,  # 12pt minimum for dyslexic readers
        leading=18,  # 1.5x line spacing
        alignment=TA_LEFT,  # Left-aligned, never justified
        spaceAfter=12,  # Clear paragraph breaks
        leftIndent=0,
        rightIndent=0,
        textColor="black",
    )

    # Metadata style
    styles["metadata"] = ParagraphStyle(
        "DyslexiaMetadata",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        alignment=TA_LEFT,
        textColor="#666666",
    )

    return styles


def _format_text_for_dyslexia(text: str) -> str:
    """Format text for optimal dyslexic readability in PDF"""
    if not text:
        return ""

    # First convert markdown to PDF-formatted text using shared utility
    pdf_text = markdown_to_pdf_text(text)

    # Split into paragraphs and clean up
    paragraphs = pdf_text.split("\n")
    formatted_paragraphs = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Ensure paragraphs aren't too long (max ~70 characters per line)
        # ReportLab will handle line wrapping, but we can break very long paragraphs
        if len(para) > 400:  # Rough estimate for very long paragraphs
            # Split on sentences if possible
            sentences = para.split(". ")
            current_para = ""

            for i, sentence in enumerate(sentences):
                if i < len(sentences) - 1:
                    sentence += ". "

                if len(current_para + sentence) > 300:
                    if current_para:
                        formatted_paragraphs.append(current_para.strip())
                        current_para = sentence
                    else:
                        formatted_paragraphs.append(sentence)
                        current_para = ""
                else:
                    current_para += sentence

            if current_para:
                formatted_paragraphs.append(current_para.strip())
        else:
            formatted_paragraphs.append(para)

    # Join paragraphs with proper spacing
    return "<br/><br/>".join(formatted_paragraphs)


def generate_pdf_filename(timestamp: Optional[datetime] = None) -> str:
    if timestamp is None:
        timestamp = datetime.now()

    # Format: DictoDX_VoiceNote_YYYY-MM-DD_HHMM.pdf
    date_str = timestamp.strftime("%Y-%m-%d_%H%M")
    return f"Dicto_VoiceNote_{date_str}.pdf"


def create_pdf_response(
    transcript: str, summary: str, timestamp: Optional[datetime] = None
) -> Response:
    pdf_content = create_dyslexia_friendly_pdf(transcript, summary, timestamp)
    filename = generate_pdf_filename(timestamp)

    response = Response(
        pdf_content,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": len(pdf_content),
        },
    )

    return response
