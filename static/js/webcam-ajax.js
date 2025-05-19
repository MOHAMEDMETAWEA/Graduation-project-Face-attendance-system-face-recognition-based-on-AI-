// static/js/webcam-ajax.js

document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-btn');
    const preview = document.getElementById('preview');
    const fileInput = document.getElementById('file');
    const submitBtn = document.getElementById('submit-btn');
    
    // Access the webcam
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
                video.play();
            })
            .catch(function(error) {
                console.error("Error accessing the webcam:", error);
                alert("Could not access the webcam. Please make sure you have a webcam connected and have granted permission.");
            });
    } else {
        alert("Your browser doesn't support webcam access. Please try a different browser.");
    }
    
    // Capture image when the button is clicked
    captureBtn.addEventListener('click', function() {
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw video frame to canvas
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get the image data as base64
        const imageData = canvas.toDataURL('image/jpeg');
        
        // Display preview
        preview.src = imageData;
        
        // For form submission
        canvas.toBlob(function(blob) {
            // Create a File object
            const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
            
            // Create a FileList-like object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            
            // Set the file input's files
            fileInput.files = dataTransfer.files;
            
            // Enable submit button - we'll re-enable it only after verification
            submitBtn.disabled = true;
        }, 'image/jpeg');
        
        // Send the image data to the server for recognition and anti-spoofing check
        fetch('/capture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                submitBtn.disabled = true;
            } else if (data.name === 'unknown_person' || data.name === 'no_persons_found') {
                alert('Unknown user. Please register first or try again.');
                submitBtn.disabled = false;  // Still allow submission for registration
            } else {
                // Show recognition result
                alert(`Recognized as: ${data.name}`);
                
                // Enable the submit button to proceed with login/logout
                submitBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during face recognition. Please try again.');
            submitBtn.disabled = true;
        });
    });
});
