// static/js/webcam.js

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
        
        // Convert canvas to blob
        canvas.toBlob(function(blob) {
            // Create a File object
            const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
            
            // Create a FileList-like object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            
            // Set the file input's files
            fileInput.files = dataTransfer.files;
            
            // Display preview
            preview.src = URL.createObjectURL(blob);
            
            // Enable submit button
            submitBtn.disabled = false;
        }, 'image/jpeg');
    });
});
