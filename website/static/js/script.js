class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        
        this.recordBtn = document.getElementById('recordBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.status = document.getElementById('status');
        
        this.init();
    }
    
    init() {
        this.recordBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
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
            const response = await fetch('/api/process-audio', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                this.displaySummary(result.summary);
            } else {
                throw new Error('Server error');
            }
        } catch (error) {
            console.error('Error sending audio:', error);
            this.status.textContent = 'Error: Could not process audio. Server not running?';
            this.updateUI('ready');
        }
    }
    
    displaySummary(summary) {
        const summarySection = document.querySelector('.summary-section');
        const summaryOutput = document.getElementById('summaryOutput');
        
        summaryOutput.textContent = summary;
        summarySection.style.display = 'block';
        this.status.textContent = 'Summary complete! Record again anytime.';
        
        // Reset for new recording
        this.updateUI('ready');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new AudioRecorder();
});