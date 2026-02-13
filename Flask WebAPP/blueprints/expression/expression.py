from flask import Flask, render_template, Response, Blueprint
import cv2
import numpy as np
from keras import metrics
from keras.models import load_model
from keras.preprocessing.image import load_img
from tqdm import tqdm

expression_bp = Blueprint("expression", __name__, static_folder='static', template_folder='templates')

#Loading the models
emotion_model = load_model("blueprints/expression/expression_emotion_model.h5")
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']

gender_mapping = {
    0: 'Male',
    1: 'Female'
}

# Load the age detection model
age_model = load_model("blueprints/expression/age_model.h5", custom_objects={'mae': metrics.MeanAbsoluteError()})

camera = cv2.VideoCapture(0)
latest_emotion = "N/A"
latest_age = "N/A"

def extract_image_features(images):
    """Extract image features for age prediction."""
    features = []

    for image in tqdm(images):
        img = load_img(image, color_mode='grayscale')  # Using color_mode instead of grayscale
        img = img.resize((128, 128))
        img = np.array(img)
        features.append(img)

    features = np.array(features)
    features = features.reshape(len(features), 128, 128, 1)
    return features

def preprocess_image(image):
    """Preprocess the image for emotion prediction."""
    image = cv2.resize(image, (48, 48))  # Resizing to model input size for emotion
    image = np.expand_dims(image, axis=-1)  # Adding channel dimension
    input_face = np.array(image).reshape(1, 48, 48, 1) / 255.0  # Normalizing
    return input_face


def predict_emotion(face_image):
    """Preprocesses the face image and predicts emotion."""
    face_image = preprocess_image(face_image)
    prediction = emotion_model.predict(face_image)
    return emotion_labels[np.argmax(prediction)]

def predict_age(face_image):
    """Preprocesses the face image and predicts age and gender."""
    # Check the number of channels in the input image
    if len(face_image.shape) == 3 and face_image.shape[2] == 3:
        # If the image is in color (BGR), convert it to grayscale
        grayscale_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
    else:
        # If the image is already grayscale, use it directly
        grayscale_image = face_image

    # Resize the image to the model's input shape
    resized_image = cv2.resize(grayscale_image, (128, 128))

    # Adding a batch dimension and ensure the image is 4D: (1, 128, 128, 1)
    augmented_image = np.expand_dims(resized_image, axis=-1)  # Adds the channel dimension
    augmented_image = np.expand_dims(augmented_image, axis=0)  # Adds the batch dimension

    # Normalization (if necessary)
    augmented_image = augmented_image / 255.0  # Normalize to [0, 1]

    # Predicting age and gender
    gender_prediction, age_prediction = age_model.predict(augmented_image)

    # Processing the age prediction (assuming it's a float between 0 and 100)
    age = int(age_prediction[0][0])  # Convert to integer

    # Processing the gender prediction (0 for Male, 1 for Female)
    gender_index = 1 if gender_prediction[0][0] >= 0.5 else 0  # Threshold at 0.5
    gender = gender_mapping[gender_index]  # Use the mapping

    result = f"Gender: {gender}, Age: {age}"
    return result

def gen_frames():
    """Generate frames from the webcam and display them with emotion and age-gender labels."""
    global latest_emotion, latest_age  # Using global variables to store the latest detected values
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)  # Flipping the frame horizontally
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                face_image = gray_frame[y:y + h, x:x + w]

                # Predict emotion and age
                latest_emotion = predict_emotion(face_image)
                latest_age = predict_age(face_image)

                # Draw rectangles and labels
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, latest_emotion, (x, y - 10), cv2.FONT_HERSHEY_TRIPLEX, 0.9, (255, 255, 255), 2)
                cv2.putText(frame, f'{latest_age}', (x, y + h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@expression_bp.route('/')
def index():
    return render_template('expression_index.html')

@expression_bp.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@expression_bp.route('/latest_emotion')
def get_latest_emotion():
    return latest_emotion

@expression_bp.route('/latest_age_gender')
def get_latest_age_gender():
    return latest_age