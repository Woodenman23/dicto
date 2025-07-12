"""
Utility functions for Dicto-DX
Shared functionality across modules
"""

import re


def markdown_to_plain_text(markdown_text: str) -> str:
    """Convert markdown to plain text suitable for copy/email - uses UPPERCASE for emphasis"""
    text = markdown_text

    # Convert headers to UPPERCASE with extra spacing - fix regex to handle trailing ##
    text = re.sub(r"^### (.+?) ###?$", lambda m: m.group(1).upper() + "\n", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+?) ##?$", lambda m: m.group(1).upper() + "\n", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+?) #?$", lambda m: m.group(1).upper() + "\n", text, flags=re.MULTILINE)
    
    # Also handle headers without trailing ##
    text = re.sub(r"^### (.+)$", lambda m: m.group(1).upper() + "\n", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", lambda m: m.group(1).upper() + "\n", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", lambda m: m.group(1).upper() + "\n", text, flags=re.MULTILINE)

    # Convert bold formatting to UPPERCASE
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: m.group(1).upper(), text)
    text = re.sub(r"__(.+?)__", lambda m: m.group(1).upper(), text)
    
    # Remove italic formatting but keep the text
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)

    # Convert bullet points to proper bullets
    text = re.sub(r"^[-*+] (.+)$", r"• \1", text, flags=re.MULTILINE)

    # Keep numbered lists as numbers (don't convert to bullets for plain text)
    # This preserves the ordering which is important when copying text

    # Handle links - keep both text and URL for copying
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1 (\2)", text)

    # Remove inline code formatting
    text = re.sub(r"`(.+?)`", r"\1", text)

    # Handle blockquotes
    text = re.sub(r"^> (.+)$", r"> \1", text, flags=re.MULTILINE)

    # Clean up excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def markdown_to_pdf_text(markdown_text: str) -> str:
    """Convert markdown to formatted text suitable for PDF export - uses HTML tags for formatting"""
    text = markdown_text

    # Convert headers to plain text with extra spacing - fix regex to handle trailing ##
    text = re.sub(r"^### (.+?) ###?$", r"\1\n", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+?) ##?$", r"\1\n", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+?) #?$", r"\1\n", text, flags=re.MULTILINE)
    
    # Also handle headers without trailing ##
    text = re.sub(r"^### (.+)$", r"\1\n", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"\1\n", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", r"\1\n", text, flags=re.MULTILINE)

    # Convert bold formatting to HTML tags for ReportLab
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    
    # Remove italic formatting but keep the text
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)

    # Convert bullet points to proper bullets
    text = re.sub(r"^[-*+] (.+)$", r"• \1", text, flags=re.MULTILINE)

    # Keep numbered lists as numbers (preserve ordering in PDFs too)
    # This maintains the sequence which is important for step-by-step content

    # Handle links - keep the text, remove the URL
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)

    # Remove inline code formatting
    text = re.sub(r"`(.+?)`", r"\1", text)

    # Handle blockquotes
    text = re.sub(r"^> (.+)$", r"> \1", text, flags=re.MULTILINE)

    # Clean up excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text