let startButton = document.getElementById("startButton");
let stopButton = document.getElementById("stopButton");
let video = document.getElementById("video");
let emotionResult = document.getElementById("emotionResult");
let ageResult = document.getElementById("ageResult");

// Start Webcam Feed
startButton.addEventListener('click', function() {
    video.src = "/expression-age/video_feed";  // Starts the webcam feed
    startButton.disabled = true;  // Disable Start button
    stopButton.disabled = false;   // Enable Stop button

    // Start fetching the latest emotion and age every second
    fetchInterval = setInterval(fetchLatestData, 1000);
});

// Stop Webcam Feed
stopButton.addEventListener('click', function() {
    video.src = "";  // Clears the image source to stop the feed
    startButton.disabled = false;  // Enable Start button
    stopButton.disabled = true;     // Disable Stop button

    // Stop fetching the latest emotion and age
    clearInterval(fetchInterval);

    emotionResult.textContent = "N/A";  // Reset emotion display
    ageResult.textContent = "N/A";  // Reset age display
});

// Fetch the latest detected emotion and age from the server
function fetchLatestData() {
    fetch('/expression-age/latest_emotion')
        .then(response => response.text())
        .then(emotion => {
            emotionResult.textContent = emotion;  // Update the emotion display
        })
        .catch(error => console.error('Error fetching emotion:', error));
        
    fetch('/expression-age/latest_age_gender')
        .then(response => response.text())
        .then(age_gender => {
            ageResult.textContent = age_gender;  // Update the age-gender display
        })
        .catch(error => console.error('Error fetching age_gender:', error));
}