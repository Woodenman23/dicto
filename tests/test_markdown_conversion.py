"""
Tests for markdown conversion functions
"""
import pytest
from website.utils import markdown_to_plain_text, markdown_to_pdf_text


class TestMarkdownToPlainText:
    """Test the markdown_to_plain_text function"""
    
    def test_headers_converted_to_uppercase(self):
        """Test that headers are converted to uppercase"""
        markdown = "# Main Title\n## Subtitle\n### Subheading"
        result = markdown_to_plain_text(markdown)
        
        assert "MAIN TITLE" in result
        assert "SUBTITLE" in result  
        assert "SUBHEADING" in result
        assert "#" not in result
    
    def test_headers_with_trailing_hashes(self):
        """Test headers with trailing ## are handled correctly"""
        markdown = "# Title #\n## Subtitle ##\n### Sub ###"
        result = markdown_to_plain_text(markdown)
        
        assert "TITLE" in result
        assert "SUBTITLE" in result
        assert "SUB" in result
        assert "#" not in result
    
    def test_bold_text_converted_to_uppercase(self):
        """Test that bold formatting becomes uppercase"""
        markdown = "This has **bold text** and __also bold__"
        result = markdown_to_plain_text(markdown)
        
        assert "BOLD TEXT" in result
        assert "ALSO BOLD" in result
        assert "**" not in result
        assert "__" not in result
    
    def test_italic_text_preserved_without_formatting(self):
        """Test that italic text is preserved but formatting removed"""
        markdown = "This has *italic text* and _also italic_"
        result = markdown_to_plain_text(markdown)
        
        assert "italic text" in result
        assert "also italic" in result
        assert "*" not in result.replace("• ", "")  # Exclude bullet symbols
        assert "_" not in result.replace("_", "")   # Handle underscores in text
    
    def test_bullet_points_converted_to_bullets(self):
        """Test that various bullet point formats become •"""
        markdown = "- Item 1\n* Item 2\n+ Item 3"
        result = markdown_to_plain_text(markdown)
        
        assert "• Item 1" in result
        assert "• Item 2" in result
        assert "• Item 3" in result
    
    def test_numbered_lists_preserved(self):
        """Test that numbered lists are preserved (not converted to bullets)"""
        markdown = "1. First item\n2. Second item\n10. Tenth item"
        result = markdown_to_plain_text(markdown)
        
        # Should keep the original numbering
        assert "1. First item" in result
        assert "2. Second item" in result  
        assert "10. Tenth item" in result
        
        # Should NOT convert to bullets
        assert "• First item" not in result
        assert "• Second item" not in result
    
    def test_links_include_url(self):
        """Test that links include both text and URL for copying"""
        markdown = "Check out [this link](https://example.com) for more info"
        result = markdown_to_plain_text(markdown)
        
        assert "this link (https://example.com)" in result
        assert "[" not in result
        assert "]" not in result
    
    def test_multiple_links(self):
        """Test handling of multiple links"""
        markdown = "Visit [Google](https://google.com) and [GitHub](https://github.com)"
        result = markdown_to_plain_text(markdown)
        
        assert "Google (https://google.com)" in result
        assert "GitHub (https://github.com)" in result
    
    def test_inline_code_formatting_removed(self):
        """Test that inline code backticks are removed"""
        markdown = "Use the `print()` function to output text"
        result = markdown_to_plain_text(markdown)
        
        assert "print()" in result
        assert "`" not in result
    
    def test_blockquotes_preserved(self):
        """Test that blockquotes are preserved with > marker"""
        markdown = "> This is a quote\n> Multi-line quote"
        result = markdown_to_plain_text(markdown)
        
        assert "> This is a quote" in result
        assert "> Multi-line quote" in result
    
    def test_excessive_whitespace_cleaned(self):
        """Test that excessive newlines are reduced"""
        markdown = "Line 1\n\n\n\nLine 2"
        result = markdown_to_plain_text(markdown)
        
        # Should have at most 2 consecutive newlines
        assert "\n\n\n" not in result
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_complex_markdown_conversion(self, sample_markdown):
        """Test conversion of complex markdown with multiple elements"""
        result = markdown_to_plain_text(sample_markdown)
        
        # Check headers converted
        assert "MAIN TITLE" in result
        assert "SUBTITLE" in result
        assert "SUBHEADING" in result
        
        # Check formatting conversions
        assert "BOLD TEXT" in result
        assert "italic text" in result
        assert "• Bullet point 1" in result
        assert "1. Numbered item 1" in result  # Should preserve numbering
        assert "link (https://example.com)" in result  # Should include URL
        assert "inline code" in result
        assert "`" not in result
        assert "IMPORTANT:" in result


class TestMarkdownToPdfText:
    """Test the markdown_to_pdf_text function"""
    
    def test_headers_converted_to_plain_text(self):
        """Test that headers lose markdown formatting but keep text"""
        markdown = "# Main Title\n## Subtitle\n### Subheading"
        result = markdown_to_pdf_text(markdown)
        
        assert "Main Title" in result
        assert "Subtitle" in result
        assert "Subheading" in result
        assert "#" not in result
    
    def test_bold_text_converted_to_html_tags(self):
        """Test that bold formatting becomes HTML <b> tags"""
        markdown = "This has **bold text** and __also bold__"
        result = markdown_to_pdf_text(markdown)
        
        assert "<b>bold text</b>" in result
        assert "<b>also bold</b>" in result
        assert "**" not in result
        assert "__" not in result
    
    def test_bullet_points_converted_properly(self):
        """Test bullet point conversion for PDF"""
        markdown = "- Item 1\n* Item 2\n+ Item 3"
        result = markdown_to_pdf_text(markdown)
        
        assert "• Item 1" in result
        assert "• Item 2" in result
        assert "• Item 3" in result
    
    def test_numbered_lists_preserved_in_pdf(self):
        """Test numbered lists are preserved in PDF format (not converted to bullets)"""
        markdown = "1. First\n2. Second\n10. Tenth"
        result = markdown_to_pdf_text(markdown)
        
        # Should preserve the numbering in PDFs too
        assert "1. First" in result
        assert "2. Second" in result
        assert "10. Tenth" in result
        
        # Should NOT convert to bullets
        assert "• First" not in result
        assert "• Second" not in result
    
    def test_pdf_vs_plain_text_differences(self):
        """Test that PDF and plain text conversions differ appropriately"""
        markdown = "**Bold text** and 1. Numbered item"
        
        plain_result = markdown_to_plain_text(markdown)
        pdf_result = markdown_to_pdf_text(markdown)
        
        # Plain text should be uppercase, PDF should use HTML tags
        assert "BOLD TEXT" in plain_result
        assert "<b>Bold text</b>" in pdf_result
        
        # Both should preserve numbering now
        assert "1. Numbered item" in plain_result
        assert "1. Numbered item" in pdf_result
        
        # Both should remove markdown syntax
        assert "**" not in plain_result
        assert "**" not in pdf_result


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_string(self):
        """Test conversion of empty string"""
        assert markdown_to_plain_text("") == ""
        assert markdown_to_pdf_text("") == ""
    
    def test_whitespace_only(self):
        """Test conversion of whitespace-only string"""
        whitespace = "   \n\n   \n   "
        assert markdown_to_plain_text(whitespace) == ""
        assert markdown_to_pdf_text(whitespace) == ""
    
    def test_no_markdown_formatting(self):
        """Test plain text without any markdown"""
        plain_text = "This is just plain text with no formatting."
        
        plain_result = markdown_to_plain_text(plain_text)
        pdf_result = markdown_to_pdf_text(plain_text)
        
        assert plain_result == plain_text
        assert pdf_result == plain_text
    
    def test_malformed_markdown(self):
        """Test handling of malformed markdown"""
        malformed = "**Unclosed bold and *unclosed italic"
        
        # Should not crash and should handle gracefully
        plain_result = markdown_to_plain_text(malformed)
        pdf_result = markdown_to_pdf_text(malformed)
        
        assert isinstance(plain_result, str)
        assert isinstance(pdf_result, str)
    
    def test_link_edge_cases(self):
        """Test various link formats"""
        # Test link without URL
        assert "text" in markdown_to_plain_text("[text]()")
        
        # Test nested brackets
        assert "text with [brackets]" in markdown_to_plain_text("[text with [brackets]](url)")
        
        # Test URL with special characters
        result = markdown_to_plain_text("[API](https://api.example.com/v1?key=value)")
        assert "API (https://api.example.com/v1?key=value)" in result