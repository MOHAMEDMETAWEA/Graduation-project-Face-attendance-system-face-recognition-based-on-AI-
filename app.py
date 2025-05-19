# app.py - Final version with Picamera2 support and streamlined flow

import os
import pickle
import datetime
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify, session, after_this_request
import cv2
import face_recognition
import numpy as np
from werkzeug.utils import secure_filename
from anti_spoof import test as anti_spoof_test
import logging
from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__)
app.secret_key = 'face_recognition_secret_key'

# Configuration
DB_DIR = './db'
LOG_PATH = './log.txt'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ANTI_SPOOF_MODEL_DIR = '/home/sallam/face-attendance-system/anti_spoof_models'
DEBUG_MODE = True

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEBUG_DIR'] = './debug_images'

# Global variable for camera frame
latest_frame = None
frame_lock = threading.Lock()

# Create necessary directories
for directory in [DB_DIR, UPLOAD_FOLDER, app.config['DEBUG_DIR']]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def recognize_face(img):
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_img)
    
    if len(face_encodings) == 0:
        return 'no_persons_found'
    
    unknown_encoding = face_encodings[0]
    
    for db_file in sorted(os.listdir(DB_DIR)):
        if not db_file.endswith('.pickle'):
            continue
            
        with open(os.path.join(DB_DIR, db_file), 'rb') as file:
            known_encoding = pickle.load(file)
            
        if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
            return db_file[:-7]
    
    return 'unknown_person'

def log_activity(name, action):
    with open(LOG_PATH, 'a') as f:
        f.write(f'{name},{datetime.datetime.now()},{action}\n')
        
class NoGetFrameLoggingRequestHandler(WSGIRequestHandler):
    def log_request(self, code='-', size='-'):
        if self.path.startswith('/get_frame'):
            return
        super().log_request(code, size)
        
def check_anti_spoofing(img, debug_info=None):
    try:
        if DEBUG_MODE and debug_info:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_path = os.path.join(app.config['DEBUG_DIR'], f"{debug_info}_{timestamp}.jpg")
            cv2.imwrite(debug_path, img)
        
        result = anti_spoof_test(
            image=img,
            model_dir=ANTI_SPOOF_MODEL_DIR,
            device_id=0
        )
        
        return (True, "Real face detected") if result == 1 else (False, "Fake face detected")
    except Exception as e:
        print(f"Anti-spoofing error: {e}")
        return False, f"Anti-spoofing error: {e}"

def camera_thread():
    """Background thread for Pi Camera"""
    global latest_frame
    from picamera2 import Picamera2
    
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    
    print("Pi Camera initialized successfully!")
    
    try:
        while True:
            frame_bgr = picam2.capture_array()
            with frame_lock:
                _, buffer = cv2.imencode('.jpg', frame_bgr)
                latest_frame = buffer.tobytes()
            time.sleep(0.1)
    except Exception as e:
        print(f"Error in camera thread: {e}")
    finally:
        picam2.stop()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'name' not in request.form or 'file' not in request.files:
            flash('Missing name or image')
            return redirect(request.url)
            
        name = request.form['name']
        file = request.files['file']
        
        if file.filename == '' or name == '':
            flash('Name and image are required')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = cv2.imread(filepath)
            
            is_real_face, message = check_anti_spoofing(img, f"register_{name}")
            if not is_real_face:
                flash(f'Security check failed: {message}')
                os.remove(filepath)
                return redirect(request.url)
            
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_img)
            
            if len(face_encodings) == 0:
                flash('No face detected')
                os.remove(filepath)
                return redirect(request.url)
                
            with open(os.path.join(DB_DIR, f'{name}.pickle'), 'wb') as f:
                pickle.dump(face_encodings[0], f)
                
            os.remove(filepath)
            flash(f'User {name} registered successfully!')
            return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No image selected')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No image selected')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = cv2.imread(filepath)
            
            is_real_face, message = check_anti_spoofing(img, "login_attempt")
            if not is_real_face:
                flash(f'Security check failed: {message}')
                os.remove(filepath)
                return redirect(request.url)
            
            name = recognize_face(img)
            os.remove(filepath)
            
            if name in ['unknown_person', 'no_persons_found']:
                flash('Unknown user. Please register or try again.')
                return redirect(url_for('index'))
            else:
                session['logged_in'] = True
                session['username'] = name
                session['just_logged_in'] = True  # Set login flag
                log_activity(name, 'in')
                flash(f'Welcome back, {name}!')
                return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No image selected')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No image selected')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = cv2.imread(filepath)
            
            is_real_face, message = check_anti_spoofing(img, "logout_attempt")
            if not is_real_face:
                flash(f'Security check failed: {message}')
                os.remove(filepath)
                return redirect(request.url)
            
            name = recognize_face(img)
            os.remove(filepath)
            
            if name in ['unknown_person', 'no_persons_found']:
                flash('Unknown user')
                return redirect(url_for('index'))
            else:
                log_activity(name, 'out')
                session.pop('logged_in', None)
                username = session.pop('username', None)
                session['just_logged_out'] = True  # Set logout flag
                flash(f'Goodbye, {username}!')
                return redirect(url_for('dashboard'))
    
    return render_template('logout.html')

@app.route('/dashboard')
def dashboard():
    # Check session flags
    just_logged_in = session.pop('just_logged_in', False)
    just_logged_out = session.pop('just_logged_out', False)
    
    if not session.get('logged_in') and not just_logged_out:
        flash('Please log in first')
        return redirect(url_for('login'))
        
    username = session.get('username', 'Guest')
    
    # Clear session if user just logged out
    if just_logged_out:
        @after_this_request
        def clear_session(response):
            session.clear()
            return response
    
    return render_template('dashboard.html',
                         username=username,
                         just_logged_in=just_logged_in,
                         just_logged_out=just_logged_out)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    global latest_frame
    while True:
        with frame_lock:
            frame_data = latest_frame
        
        if frame_data is None:
            time.sleep(0.1)
            continue
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        time.sleep(0.05)

@app.route('/get_frame')
def get_frame():
    global latest_frame
    with frame_lock:
        if latest_frame is None:
            blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
            _, buffer = cv2.imencode('.jpg', blank_image)
            frame_data = buffer.tobytes()
        else:
            frame_data = latest_frame
            
    return Response(frame_data, mimetype='image/jpeg')

@app.route('/test_anti_spoofing', methods=['POST'])
def test_anti_spoofing():
    """Test endpoint for anti-spoofing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Save the uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read the image
        img = cv2.imread(filepath)
        
        # Check anti-spoofing
        is_real_face, message = check_anti_spoofing(img, "test_endpoint")
        
        # Remove the temporary file
        os.remove(filepath)
        
        return jsonify({
            'is_real_face': is_real_face,
            'message': message
        })
    
    return jsonify({'error': 'Invalid file'}), 400
    

@app.route('/test')
def test_page():
    """Test page for anti-spoofing"""
    return render_template('test_anti_spoofing.html')


if __name__ == '__main__':
    camera_thread = threading.Thread(target=camera_thread)
    camera_thread.daemon = True
    camera_thread.start()
    time.sleep(2)
    app.run(host='0.0.0.0', port=5000, request_handler=NoGetFrameLoggingRequestHandler)
