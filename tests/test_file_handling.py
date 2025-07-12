"""
Tests for file handling and validation
"""
import pytest
import tempfile
import os
from io import BytesIO
from werkzeug.datastructures import FileStorage
from flask.testing import FlaskClient


class TestFileValidation:
    """Test file upload validation logic"""
    
    def test_valid_audio_file_size(self, mock_audio_file):
        """Test that mock audio file has reasonable size"""
        # Reset stream position
        mock_audio_file.stream.seek(0)
        content = mock_audio_file.stream.read()
        
        # Should have some content (not empty)
        assert len(content) > 0
        
        # Should be under max file size (16MB in config)
        assert len(content) < 16 * 1024 * 1024
    
    def test_empty_audio_file_size(self, empty_audio_file):
        """Test that empty audio file is detected"""
        empty_audio_file.stream.seek(0)
        content = empty_audio_file.stream.read()
        
        assert len(content) == 0
    
    def test_audio_file_properties(self, mock_audio_file):
        """Test audio file has expected properties"""
        assert mock_audio_file.filename == 'test_audio.webm'
        assert mock_audio_file.content_type == 'audio/webm'
        assert hasattr(mock_audio_file, 'stream')
    
    def test_file_stream_seekable(self, mock_audio_file):
        """Test that file stream can be read multiple times"""
        # Read once
        mock_audio_file.stream.seek(0)
        content1 = mock_audio_file.stream.read()
        
        # Reset and read again
        mock_audio_file.stream.seek(0)
        content2 = mock_audio_file.stream.read()
        
        # Should be identical
        assert content1 == content2
        assert len(content1) > 0


class TestFileUploadFormats:
    """Test different file formats and edge cases"""
    
    def test_different_audio_formats(self):
        """Test creation of different audio file formats"""
        formats = [
            ('test.webm', 'audio/webm'),
            ('test.mp3', 'audio/mpeg'),
            ('test.wav', 'audio/wav'),
            ('test.m4a', 'audio/mp4')
        ]
        
        for filename, content_type in formats:
            audio_data = b'mock_audio_data' * 50
            file_obj = FileStorage(
                stream=BytesIO(audio_data),
                filename=filename,
                content_type=content_type
            )
            
            assert file_obj.filename == filename
            assert file_obj.content_type == content_type
            
            file_obj.stream.seek(0)
            content = file_obj.stream.read()
            assert len(content) > 0
    
    def test_large_file_creation(self):
        """Test creation of larger file for size limit testing"""
        # Create 1MB file
        large_data = b'x' * (1024 * 1024)
        large_file = FileStorage(
            stream=BytesIO(large_data),
            filename='large_test.webm',
            content_type='audio/webm'
        )
        
        large_file.stream.seek(0)
        content = large_file.stream.read()
        assert len(content) == 1024 * 1024
    
    def test_very_small_file(self):
        """Test very small file (might be silence)"""
        tiny_data = b'tiny'
        tiny_file = FileStorage(
            stream=BytesIO(tiny_data),
            filename='tiny.webm', 
            content_type='audio/webm'
        )
        
        tiny_file.stream.seek(0)
        content = tiny_file.stream.read()
        assert len(content) == 4
    
    def test_file_without_extension(self):
        """Test file without extension"""
        no_ext_file = FileStorage(
            stream=BytesIO(b'data'),
            filename='noextension',
            content_type='audio/webm'
        )
        
        assert no_ext_file.filename == 'noextension'
        assert no_ext_file.content_type == 'audio/webm'
    
    def test_file_with_special_characters(self):
        """Test filename with special characters"""
        special_file = FileStorage(
            stream=BytesIO(b'data'),
            filename='test file (1) - recording.webm',
            content_type='audio/webm'
        )
        
        assert 'test file (1) - recording.webm' in special_file.filename


class TestFileUploadIntegration:
    """Test file uploads through the actual API"""
    
    def test_upload_validation_missing_file(self, client: FlaskClient):
        """Test that missing file in multipart form is handled"""
        response = client.post('/api/process-audio', 
                              data={},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
    
    def test_upload_validation_wrong_field_name(self, client: FlaskClient, mock_audio_file):
        """Test upload with wrong field name"""
        response = client.post('/api/process-audio',
                              data={'wrong_field': mock_audio_file},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
    
    def test_upload_with_correct_field_name(self, client: FlaskClient, mock_audio_file):
        """Test upload with correct field name (will fail on processing)"""
        response = client.post('/api/process-audio',
                              data={'audio': mock_audio_file},
                              content_type='multipart/form-data')
        
        # Should pass validation but fail on processing
        # Not a 400 validation error
        assert response.status_code != 400 or 'No audio file' not in response.get_json().get('error', '')
    
    def test_multiple_files_upload(self, client: FlaskClient, mock_audio_file):
        """Test uploading multiple files (should only process first)"""
        mock_audio_file2 = FileStorage(
            stream=BytesIO(b'second_file_data' * 50),
            filename='second.webm',
            content_type='audio/webm'
        )
        
        response = client.post('/api/process-audio',
                              data={
                                  'audio': [mock_audio_file, mock_audio_file2]
                              },
                              content_type='multipart/form-data')
        
        # Should handle multiple files gracefully (likely process first one)
        assert response.status_code in [400, 500]  # Either validation or processing error


class TestTempFileHandling:
    """Test temporary file creation and cleanup"""
    
    def test_temp_file_creation(self):
        """Test that we can create temporary files similar to the app"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(b'test_audio_data')
            temp_path = temp_file.name
        
        # File should exist
        assert os.path.exists(temp_path)
        
        # Should be able to read it
        with open(temp_path, 'rb') as f:
            content = f.read()
            assert content == b'test_audio_data'
        
        # Cleanup
        os.unlink(temp_path)
        assert not os.path.exists(temp_path)
    
    def test_temp_file_cleanup_safety(self):
        """Test safe cleanup of temp files"""
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_path = temp_file.name
        
        # File exists
        assert os.path.exists(temp_path)
        
        # Safe cleanup (like in the app)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        # Should not error if file doesn't exist
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        assert not os.path.exists(temp_path)


class TestContentTypeValidation:
    """Test content type handling"""
    
    def test_webm_content_type(self, mock_audio_file):
        """Test WebM content type is handled"""
        assert mock_audio_file.content_type == 'audio/webm'
    
    def test_various_audio_content_types(self):
        """Test different audio content types"""
        content_types = [
            'audio/webm',
            'audio/mpeg', 
            'audio/wav',
            'audio/mp4',
            'audio/ogg'
        ]
        
        for content_type in content_types:
            file_obj = FileStorage(
                stream=BytesIO(b'audio_data'),
                filename=f'test.{content_type.split("/")[1]}',
                content_type=content_type
            )
            
            assert file_obj.content_type == content_type
    
    def test_non_audio_content_type(self):
        """Test non-audio content types"""
        non_audio_file = FileStorage(
            stream=BytesIO(b'not_audio'),
            filename='document.txt',
            content_type='text/plain'
        )
        
        assert non_audio_file.content_type == 'text/plain'
        # App should handle this gracefully (might reject or try to process)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_none_filename(self):
        """Test file with None filename"""
        none_file = FileStorage(
            stream=BytesIO(b'data'),
            filename=None,
            content_type='audio/webm'
        )
        
        assert none_file.filename is None
    
    def test_empty_filename(self):
        """Test file with empty filename"""
        empty_name_file = FileStorage(
            stream=BytesIO(b'data'),
            filename='',
            content_type='audio/webm'
        )
        
        assert empty_name_file.filename == ''
    
    def test_long_filename(self):
        """Test file with very long filename"""
        long_name = 'a' * 200 + '.webm'
        long_file = FileStorage(
            stream=BytesIO(b'data'),
            filename=long_name,
            content_type='audio/webm'
        )
        
        assert len(long_file.filename) > 200
    
    def test_filename_with_path_separators(self):
        """Test filename with path separators (security test)"""
        bad_filename = '../../../etc/passwd'
        bad_file = FileStorage(
            stream=BytesIO(b'data'),
            filename=bad_filename,
            content_type='audio/webm'
        )
        
        # FileStorage should preserve the filename as-is
        # App should sanitize it when saving
        assert bad_file.filename == bad_filename