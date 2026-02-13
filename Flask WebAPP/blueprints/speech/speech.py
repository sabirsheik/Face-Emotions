from flask import Flask, request, jsonify, render_template, Blueprint
import numpy as np
import librosa
import os
import time
import threading
from tensorflow.keras.models import load_model
import sounddevice as sd
from scipy.io.wavfile import write
import glob

speech_bp = Blueprint("speech", __name__, static_folder='static', template_folder='templates')

model = load_model('blueprints/speech/speech_model.h5')

emotion_map = {
    0: 'Neutral', 1: 'Calm', 2: 'Happy', 3: 'Sad',
    4: 'Angry', 5: 'Fearful', 6: 'Disgust', 7: 'Surprised'
}

latest_emotion = "N/A"
recording = False
audio_data = []
recording_thread = None


def record_audio(duration=5, sample_rate=48000):
    global recording, audio_data
    audio_data = []
    print("Recording...")

    def callback(indata, frames, time_info, status):
        if recording:
            audio_data.append(indata.copy())

    try:
        with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
            while recording:
                sd.sleep(100)

        audio_filename = os.path.join('blueprints/speech/static', f'temp_audio.wav')
        write(audio_filename, sample_rate, (np.concatenate(audio_data) * 32767).astype(np.int16))
        print(f"Recording complete. File saved as '{audio_filename}'.")
    except Exception as e:
        print(f"Error during recording: {e}")
        recording = False


@speech_bp.route('/')
def index():
    return render_template('index.html')


@speech_bp.route('/start_recording', methods=['POST'])
def start_recording():
    global recording, recording_thread
    if not recording:
        previous_file = 'blueprints/speech/static/temp_audio.wav'
        if os.path.exists(previous_file):
            os.remove(previous_file)
            print(f"Deleted previous recording: {previous_file}")

        recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()

    return jsonify({'status': 'Recording started'})


@speech_bp.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, recording_thread
    recording = False
    if recording_thread and recording_thread.is_alive():
        recording_thread.join()  # Wait for the thread to finish
    return jsonify({'status': 'Recording stopped'})


@speech_bp.route('/predict_emotion', methods=['POST'])
def predict_emotion():
    global latest_emotion

    time.sleep(0.5)

    audio_filename = 'blueprints/speech/static/temp_audio.wav'
    if not os.path.exists(audio_filename):
        return jsonify({'error': 'Audio file not found.'}), 404

    try:
        y, sr = librosa.load(audio_filename, sr=None)
        mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
        x = np.expand_dims(np.expand_dims(mfccs, axis=1), axis=0)

        predictions = model.predict(x)
        predicted_class = np.argmax(predictions, axis=1)[0]
        detected_emotion = emotion_map.get(predicted_class, 'unknown')

        latest_emotion = detected_emotion

        # Delete the audio file after prediction
        os.remove(audio_filename)
        print(f"Deleted '{audio_filename}' after prediction.")

        return jsonify({'emotion': latest_emotion})

    except Exception as e:
        print("Error during processing:", str(e))
        return jsonify({'error': str(e)}), 500
