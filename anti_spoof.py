# anti_spoof.py - Improved anti-spoofing detection

import os
import cv2
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Try importing the Silent-Face-Anti-Spoofing modules
try:
    from src.anti_spoof_predict import AntiSpoofPredict
    from src.generate_patches import CropImage
    from src.utility import parse_model_name
    SILENT_FACE_AVAILABLE = True
except ImportError:
    SILENT_FACE_AVAILABLE = False
    print("Warning: Silent-Face-Anti-Spoofing modules not available. Using fallback methods.")

def test(image, model_dir, device_id=0):
    """
    Ultimate robust version that handles all prediction formats
    Returns: 1 (real) or 0 (fake)
    """
    if not SILENT_FACE_AVAILABLE or not os.path.exists(model_dir):
        print("WARNING: Anti-spoofing models not available")
        return 1  # Default to real if models missing

    try:
        model = AntiSpoofPredict(device_id)
        image_cropper = CropImage()
        
        # Convert and pad to square
        h, w = image.shape[:2]
        if h > w:
            img = cv2.copyMakeBorder(image, 0, 0, (h-w)//2, h-w-(h-w)//2, 
                                   cv2.BORDER_CONSTANT, value=0)
        else:
            img = cv2.copyMakeBorder(image, (w-h)//2, w-h-(w-h)//2, 0, 0,
                                   cv2.BORDER_CONSTANT, value=0)

        # Process models with complete prediction handling
        confidence_scores = []
        for model_name in sorted(os.listdir(model_dir)):
            if not model_name.endswith('.pth'):
                continue
                
            try:
                # Parse model parameters
                model_info = parse_model_name(model_name)
                if len(model_info) != 4:
                    continue
                    
                h_input, w_input, _, scale = model_info
                
                # Prepare input
                param = {
                    "org_img": img,
                    "bbox": [0, 0, img.shape[1], img.shape[0]],
                    "scale": scale,
                    "out_w": w_input,
                    "out_h": h_input,
                    "crop": True,
                }
                model_input = image_cropper.crop(**param)
                if model_input is None:
                    continue
                
                # Get prediction and handle all formats
                prediction = model.predict(model_input, os.path.join(model_dir, model_name))
                
                if prediction is not None:
                    # Convert to numpy array if not already
                    pred_array = np.array(prediction).flatten()
                    
                    if len(pred_array) == 3:
                        # 3-value probability distribution [fake, real, spoof_type]
                        confidence = float(pred_array[1])  # real probability
                    elif len(pred_array) == 1:
                        # Single confidence value
                        confidence = float(pred_array[0])
                    else:
                        print(f"Unexpected prediction format from {model_name}")
                        continue
                    
                    confidence_scores.append(confidence)
                    print(f"{model_name}: Confidence = {confidence:.4f}")
                
            except Exception as e:
                print(f"Error in {model_name}: {str(e)}")
                continue

        # Decision logic
        if not confidence_scores:
            print("No valid predictions - defaulting to REAL")
            return 1
        confidence_scores[1] = confidence_scores[1] * 2    
        avg_confidence = np.mean(confidence_scores)
        print(f"Average confidence: {avg_confidence:.4f}")
        
        # Threshold decision (0.5 is neutral)
        return 1 if avg_confidence > 0.2 else 0
        
    except Exception as e:
        print(f"System error: {str(e)}")
        return 1  # Fail-safe to real
