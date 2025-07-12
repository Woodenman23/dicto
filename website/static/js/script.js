class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.plainTextForCopy = '';
        this.currentTranscript = '';
        this.currentSummary = '';

        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.status = document.getElementById('status');
        this.copyBtn = document.getElementById('copyBtn');
        this.exportPdfBtn = document.getElementById('exportPdfBtn');

        this.init();
    }

    init() {
        this.recordBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        this.copyBtn.addEventListener('click', () => this.copyToClipboard());
        this.exportPdfBtn.addEventListener('click', () => this.exportToPdf());
    }

    async startRecording() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });

            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };

            this.mediaRecorder.start(100);
            this.isRecording = true;

            this.updateUI('recording');
            this.status.textContent = 'Recording... Click stop when finished';

        } catch (error) {
            console.error('Error starting recording:', error);
            this.status.textContent = 'Error: Could not access microphone';
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            this.updateUI('stopped');
            this.status.textContent = 'Processing recording...';
        }
    }

    processRecording() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });

        // Validate recording has content
        if (audioBlob.size < 1000) { // Less than 1KB likely means silence
            this.status.textContent = 'Recording too short or silent. Please try again.';
            this.updateUI('ready');
            return;
        }

        // Store the blob and auto-send
        this.recordedBlob = audioBlob;
        this.status.textContent = 'Processing your recording...';
        this.sendAudio();
    }

    updateUI(state) {
        switch (state) {
            case 'recording':
                this.recordBtn.disabled = true;
                this.stopBtn.disabled = false;
                this.recordBtn.classList.add('recording');
                break;
            case 'stopped':
                this.recordBtn.disabled = false;
                this.stopBtn.disabled = true;
                this.recordBtn.classList.remove('recording');
                break;
            case 'ready':
                this.recordBtn.disabled = false;
                this.stopBtn.disabled = true;
                this.recordBtn.classList.remove('recording');
                break;
        }
    }

    async sendAudio() {
        if (!this.recordedBlob) {
            this.status.textContent = 'No recording to send';
            this.updateUI('ready');
            return;
        }

        this.status.textContent = 'Transcribing and summarizing...';

        const formData = new FormData();
        formData.append('audio', this.recordedBlob, 'recording.webm');

        try {
            const basePath = window.BASE_PATH || '';
            const response = await fetch(`${basePath}/api/process-audio`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.displaySummary(result.summary, result.plain_text, result.transcript);
            } else {
                const errorText = await response.text();
                console.error('Server error response:', errorText);
                throw new Error(`Server error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error sending audio:', error);
            this.status.textContent = 'Error: Could not process audio. Please try again.';
            this.updateUI('ready');
        }
    }

    displaySummary(summary, plainText, transcript = '') {
        const summarySection = document.querySelector('.summary-section');
        const summaryOutput = document.getElementById('summaryOutput');

        // Use marked.js to parse the markdown summary for nice HTML formatting  
        summaryOutput.innerHTML = marked.parse(summary);
        this.plainTextForCopy = plainText;
        this.currentTranscript = transcript;
        this.currentSummary = summary;
        
        summarySection.style.display = 'block';
        this.exportPdfBtn.style.display = 'inline-block';
        this.status.textContent = 'Summary complete! Record again anytime.';

        // Reset for new recording
        this.updateUI('ready');
    }

    async copyToClipboard() {
        if (!this.plainTextForCopy.trim()) {
            this.status.textContent = 'No summary to copy';
            return;
        }

        try {
            await navigator.clipboard.writeText(this.plainTextForCopy);

            // Visual feedback
            const textSpan = this.copyBtn.querySelector('span');
            const originalText = textSpan.textContent;
            textSpan.textContent = 'Copied!';
            this.copyBtn.classList.add('copied');

            setTimeout(() => {
                textSpan.textContent = originalText;
                this.copyBtn.classList.remove('copied');
            }, 2000);

        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            this.status.textContent = 'Failed to copy to clipboard';
        }
    }

    async exportToPdf() {
        if (!this.currentSummary.trim()) {
            this.status.textContent = 'No summary to export';
            return;
        }

        try {
            const exportData = {
                transcript: this.currentTranscript,
                summary: this.currentSummary
            };

            const basePath = window.BASE_PATH || '';
            const response = await fetch(`${basePath}/api/export-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(exportData)
            });

            if (response.ok) {
                // Create a blob from the response
                const blob = await response.blob();
                
                // Get the filename from the response headers
                const contentDisposition = response.headers.get('content-disposition');
                let filename = 'dicto-summary.pdf';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }

                // Create download link and trigger download
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                
                // Cleanup
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.status.textContent = 'PDF downloaded successfully!';
            } else {
                throw new Error(`Server error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error exporting PDF:', error);
            this.status.textContent = 'Error: Could not export PDF. Please try again.';
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new AudioRecorder();
});