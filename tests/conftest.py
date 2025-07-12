"""
Test configuration and fixtures for Dicto tests
"""
import pytest
import tempfile
import os
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage
from io import BytesIO

from website import create_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create and configure a test Flask app instance"""
    # Create a test app with testing configuration
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        # Disable CORS during testing
        'WTF_CSRF_ENABLED': False
    })
    
    yield test_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask app"""
    return app.test_client()


@pytest.fixture
def mock_audio_file() -> FileStorage:
    """Create a mock audio file for testing uploads"""
    # Create mock audio data (just some bytes)
    audio_data = b'mock_audio_data_webm_format' * 100  # Make it reasonably sized
    
    return FileStorage(
        stream=BytesIO(audio_data),
        filename='test_audio.webm',
        content_type='audio/webm'
    )


@pytest.fixture
def empty_audio_file() -> FileStorage:
    """Create an empty audio file for testing validation"""
    return FileStorage(
        stream=BytesIO(b''),
        filename='empty.webm',
        content_type='audio/webm'
    )


@pytest.fixture
def sample_markdown() -> str:
    """Sample markdown text for testing conversions"""
    return """# Main Title
    
## Subtitle

This is a paragraph with **bold text** and *italic text*.

- Bullet point 1
- Bullet point 2
* Another bullet

1. Numbered item 1
2. Numbered item 2

### Subheading

Here's some `inline code` and a [link](https://example.com).

> This is a blockquote

**Important:** This is emphasized text.
"""


@pytest.fixture
def sample_transcript() -> str:
    """Sample transcript for testing"""
    return "This is a sample transcript from the audio recording. It contains multiple sentences and should be processed correctly."


@pytest.fixture
def sample_summary() -> str:
    """Sample summary in markdown format"""
    return """## Meeting Summary

**Key Points:**
- Discussed project timeline
- Assigned tasks to team members
- Set deadline for next milestone

**Action Items:**
- Complete research by Friday
- Schedule follow-up meeting
- Review documentation
"""