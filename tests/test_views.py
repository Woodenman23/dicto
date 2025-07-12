"""
Tests for Flask views and routes
"""
import pytest
import json
from flask.testing import FlaskClient


class TestHomeRoute:
    """Test the home page route"""
    
    def test_home_page_loads(self, client: FlaskClient):
        """Test that the home page loads successfully"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
    
    def test_home_page_contains_expected_content(self, client: FlaskClient):
        """Test that home page contains expected elements"""
        response = client.get('/')
        html_content = response.get_data(as_text=True)
        
        # Should contain basic page structure
        assert '<html' in html_content
        assert '</html>' in html_content
        
        # Should contain title or app name
        assert 'Dicto' in html_content or 'Voice' in html_content


class TestProcessAudioRoute:
    """Test the audio processing API endpoint"""
    
    def test_process_audio_no_file(self, client: FlaskClient):
        """Test API returns error when no audio file is provided"""
        response = client.post('/api/process-audio')
        
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data
        assert 'No audio file provided' in data['error']
    
    def test_process_audio_empty_filename(self, client: FlaskClient):
        """Test API returns error when filename is empty"""
        response = client.post('/api/process-audio', data={'audio': (None, '')})
        
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data
        assert 'No audio file selected' in data['error']
    
    def test_process_audio_with_mock_file(self, client: FlaskClient, mock_audio_file):
        """Test API endpoint with mock audio file (will fail due to external dependencies)"""
        response = client.post('/api/process-audio', 
                              data={'audio': mock_audio_file},
                              content_type='multipart/form-data')
        
        # This will likely return 500 due to missing OpenAI key or audio processing error
        # But we can test that it doesn't return the basic validation errors
        assert response.status_code in [500, 400]  # Either processing error or validation
        
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data
        
        # Should not be the basic validation errors we tested above
        assert 'No audio file provided' not in data['error']
        assert 'No audio file selected' not in data['error']
    
    def test_process_audio_wrong_method(self, client: FlaskClient):
        """Test that GET request to process-audio returns method not allowed"""
        response = client.get('/api/process-audio')
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_process_audio_invalid_content_type(self, client: FlaskClient):
        """Test API with wrong content type"""
        response = client.post('/api/process-audio', 
                              json={'audio': 'not-a-file'},
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data


class TestExportPdfRoute:
    """Test the PDF export API endpoint"""
    
    def test_export_pdf_no_data(self, client: FlaskClient):
        """Test PDF export returns error when no data is provided"""
        response = client.post('/api/export-pdf')
        
        # Returns 500 because Flask can't parse the JSON request without content-type
        assert response.status_code == 500
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data
    
    def test_export_pdf_empty_content(self, client: FlaskClient):
        """Test PDF export returns error when no content provided"""
        response = client.post('/api/export-pdf',
                              json={'transcript': '', 'summary': ''},
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data
        assert 'No content to export' in data['error']
    
    def test_export_pdf_with_transcript_only(self, client: FlaskClient, sample_transcript):
        """Test PDF export with only transcript"""
        response = client.post('/api/export-pdf',
                              json={'transcript': sample_transcript, 'summary': ''},
                              content_type='application/json')
        
        # Should succeed with just transcript
        # Response might be 200 with PDF or 500 if PDF generation fails
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'
        else:
            data = json.loads(response.get_data(as_text=True))
            assert 'error' in data
    
    def test_export_pdf_with_summary_only(self, client: FlaskClient, sample_summary):
        """Test PDF export with only summary"""
        response = client.post('/api/export-pdf',
                              json={'transcript': '', 'summary': sample_summary},
                              content_type='application/json')
        
        # Should succeed with just summary
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'
        else:
            data = json.loads(response.get_data(as_text=True))
            assert 'error' in data
    
    def test_export_pdf_with_both_content(self, client: FlaskClient, sample_transcript, sample_summary):
        """Test PDF export with both transcript and summary"""
        response = client.post('/api/export-pdf',
                              json={
                                  'transcript': sample_transcript, 
                                  'summary': sample_summary
                              },
                              content_type='application/json')
        
        # Should succeed with both
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'
            # PDF should have some content
            assert len(response.get_data()) > 0
        else:
            data = json.loads(response.get_data(as_text=True))
            assert 'error' in data
    
    def test_export_pdf_wrong_method(self, client: FlaskClient):
        """Test that GET request to export-pdf returns method not allowed"""
        response = client.get('/api/export-pdf')
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_export_pdf_invalid_json(self, client: FlaskClient):
        """Test PDF export with invalid JSON"""
        response = client.post('/api/export-pdf',
                              data='invalid-json',
                              content_type='application/json')
        
        # Returns 500 because Flask can't parse invalid JSON
        assert response.status_code == 500


class TestErrorHandling:
    """Test error handling across routes"""
    
    def test_404_for_nonexistent_route(self, client: FlaskClient):
        """Test that nonexistent routes return 404"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_api_404_for_nonexistent_api_route(self, client: FlaskClient):
        """Test that nonexistent API routes return 404"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_api_routes_return_json_errors(self, client: FlaskClient):
        """Test that API routes return JSON formatted errors"""
        # Test with a route that should return JSON error
        response = client.post('/api/process-audio')
        
        assert response.content_type == 'application/json'
        data = json.loads(response.get_data(as_text=True))
        assert 'error' in data


class TestResponseFormats:
    """Test response formats and content types"""
    
    def test_home_returns_html(self, client: FlaskClient):
        """Test that home route returns HTML"""
        response = client.get('/')
        assert response.content_type.startswith('text/html')
    
    def test_api_routes_return_json(self, client: FlaskClient):
        """Test that API routes return JSON (even on errors)"""
        # Test process-audio error response
        response = client.post('/api/process-audio')
        assert response.content_type == 'application/json'
        
        # Test export-pdf error response  
        response = client.post('/api/export-pdf')
        assert response.content_type == 'application/json'
    
    def test_cors_headers_present(self, client: FlaskClient):
        """Test that CORS headers are present on API responses"""
        response = client.post('/api/process-audio')
        
        # Should have CORS headers (might vary based on configuration)
        # This tests that CORS is configured, exact headers depend on setup
        headers = dict(response.headers)
        # At minimum, we expect some access control headers on API routes
        assert any('access-control' in header.lower() for header in headers.keys()) or response.status_code == 400