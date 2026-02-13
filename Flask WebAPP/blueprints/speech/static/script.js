const waveformContainer = document.getElementById('waveform');
const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const recordingStatus = document.getElementById('recordingStatus');  // Updated to match the new ID
const detectedEmotionText = document.getElementById('predictionResult');  // Keep this for emotion display

const wavesurfer = WaveSurfer.create({
    container: waveformContainer,
    waveColor: 'violet',
    progressColor: 'purple',

});

// Initialize detected emotion text
detectedEmotionText.textContent = 'N/A';

startButton.addEventListener('click', async () => {
    recordingStatus.textContent = 'Starting recording...';
    detectedEmotionText.textContent = 'N/A'; // Reset on new recording
    startButton.disabled = true;
    stopButton.disabled = false;

    try {
        const response = await fetch('/speech/start_recording', { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            recordingStatus.textContent = result.status;
        } else {
            recordingStatus.textContent = 'Error: ' + result.error;
        }
    } catch (error) {
        recordingStatus.textContent = 'Network error: ' + error.message;
    }
});

stopButton.addEventListener('click', async () => {
    recordingStatus.textContent = 'Stopping recording...';
    startButton.disabled = false;
    stopButton.disabled = true;

    try {
        const response = await fetch('/speech/stop_recording', { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            recordingStatus.textContent = 'Idle';

            // Removed wavesurfer.load as the file is deleted after prediction
            detectEmotion();
        } else {
            recordingStatus.textContent = 'Error: ' + result.error;
        }
    } catch (error) {
        recordingStatus.textContent = 'Network error: ' + error.message;
    }
});

async function detectEmotion() {
    try {
        recordingStatus.textContent = 'Predicting emotion...';
        const response = await fetch('/speech/predict_emotion', { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            detectedEmotionText.textContent = result.emotion;  // Display the detected emotion
            recordingStatus.textContent = 'Idle';  // Set status back to "Idle" after prediction
        } else {
            detectedEmotionText.textContent = 'Error: ' + result.error;
            recordingStatus.textContent = 'Idle';  // Reset to "Idle" even if there’s an error
        }
    } catch (error) {
        detectedEmotionText.textContent = 'Network error: ' + error.message;
        recordingStatus.textContent = 'Idle';  // Reset to "Idle" on network error
    }
}

