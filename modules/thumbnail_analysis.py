import os
import requests
import cv2
import numpy as np
from PIL import Image
from skimage.exposure import is_low_contrast
import pytesseract
from modules.utils import logger, THUMBNAILS_DIR

# Check if Tesseract is installed and usable
TESSERACT_AVAILABLE = False
try:
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
except Exception:
    logger.warning("Tesseract OCR is not installed or not added to system PATH. OCR detection will be skipped.")

# Load OpenCV's built-in Haar Cascade Face Detector
FACE_CASCADE = None
try:
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    FACE_CASCADE = cv2.CascadeClassifier(cascade_path)
    if FACE_CASCADE.empty():
        logger.warning("Haar Cascade Face XML could not be loaded.")
        FACE_CASCADE = None
except Exception as e:
    logger.warning(f"Error loading Haar Cascade: {e}")

def download_thumbnail(channel_id, video_id, url):
    """
    Download a thumbnail image from its URL and save it locally.
    Returns the absolute local file path if successful, else None.
    """
    if not url:
        return None
        
    safe_channel_id = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in channel_id])
    safe_video_id = "".join([c if c.isalnum() or c in ('-', '_') else '_' for c in video_id])
    
    filename = f"{safe_channel_id}_{safe_video_id}.jpg"
    local_path = os.path.join(THUMBNAILS_DIR, filename)
    
    if os.path.exists(local_path):
        return local_path
        
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            return local_path
        else:
            logger.warning(f"Failed to download thumbnail from {url}. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading thumbnail {url}: {e}")
        
    return None

def compute_colorfulness(img_bgr):
    """
    Calculate colorfulness score using the Hasler and Suesstrunk opponent color space metric.
    """
    # Convert BGR to float
    img = img_bgr.astype(np.float32)
    b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    
    # Compute opponent color spaces
    rg = r - g
    yb = 0.5 * (r + g) - b
    
    # Compute mean and standard deviation
    mean_rg = np.mean(rg)
    std_rg = np.std(rg)
    
    mean_yb = np.mean(yb)
    std_yb = np.std(yb)
    
    # Calculate colorfulness
    std_rgyb = np.sqrt(std_rg**2 + std_yb**2)
    mean_rgyb = np.sqrt(mean_rg**2 + mean_yb**2)
    
    colorfulness = std_rgyb + 0.3 * mean_rgyb
    return float(colorfulness)

def analyze_single_thumbnail(local_path, ocr_enabled=True, face_enabled=True, thresholds=None):
    """
    Perform deep rule-based visual quality checks on a single local thumbnail image.
    """
    if not local_path or not os.path.exists(local_path):
        return {"error": "Image file not found"}
        
    if thresholds is None:
        thresholds = {
            "blur_variance": 100.0,
            "contrast_low": 0.05,
            "colorfulness_low": 20.0,
            "max_ocr_text_length": 50,
            "clutter_ratio": 0.15
        }

    results = {
        "blur_score": 0.0,
        "contrast_score": 0.0,
        "colorfulness_score": 0.0,
        "brightness_score": 0.0,
        "width": 0,
        "height": 0,
        "ocr_text": "",
        "ocr_char_count": 0,
        "face_detected": False,
        "clutter_score": 0.0,
        "issues": []
    }

    try:
        # Load image via OpenCV
        img_bgr = cv2.imread(local_path)
        if img_bgr is None:
            return {"error": "Failed to read image with OpenCV"}
            
        h, w, c = img_bgr.shape
        results["width"] = w
        results["height"] = h
        
        # 1. Resolution Check
        if w < 640 or h < 360:
            results["issues"].append("low_resolution")
            
        # Convert to Grayscale for texture/blur/face analyses
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # 2. Blur detection: Variance of Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_var = float(laplacian.var())
        results["blur_score"] = blur_var
        if blur_var < thresholds.get("blur_variance", 100.0):
            results["issues"].append("blurry")
            
        # 3. Contrast detection
        # Low contrast check using skimage
        is_low = bool(is_low_contrast(gray, fraction_threshold=thresholds.get("contrast_low", 0.05)))
        results["contrast_score"] = float(np.std(gray)) # Standard deviation is a direct indicator of contrast
        if is_low or results["contrast_score"] < 15.0:
            results["issues"].append("low_contrast")
            
        # 4. Colorfulness check
        colorful = compute_colorfulness(img_bgr)
        results["colorfulness_score"] = colorful
        if colorful < thresholds.get("colorfulness_low", 20.0):
            results["issues"].append("dull_colors")
            
        # 5. Brightness Check (from HSV V channel)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        brightness = float(np.mean(hsv[:, :, 2]))
        results["brightness_score"] = brightness
        if brightness < 45.0:
            results["issues"].append("low_brightness") # Too dark
        elif brightness > 215.0:
            results["issues"].append("high_brightness") # Overexposed

        # 6. Face Detection (Haar Cascades)
        if face_enabled and FACE_CASCADE is not None:
            faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
            face_count = len(faces)
            results["face_detected"] = face_count > 0
            if face_count == 0:
                results["issues"].append("no_clear_face")
        else:
            results["face_detected"] = False
            
        # 7. Clutter Score (Ratio of Canny Edges)
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.sum(edges == 255)
        total_pixels = gray.size
        clutter = float(edge_pixels / total_pixels)
        results["clutter_score"] = clutter
        if clutter > thresholds.get("clutter_ratio", 0.15):
            results["issues"].append("cluttered")

        # 8. OCR Text Count
        if ocr_enabled and TESSERACT_AVAILABLE:
            try:
                pil_img = Image.open(local_path)
                ocr_txt = pytesseract.image_to_string(pil_img).strip()
                results["ocr_text"] = ocr_txt
                results["ocr_char_count"] = len(ocr_txt)
                
                if len(ocr_txt) > thresholds.get("max_ocr_text_length", 50):
                    results["issues"].append("too_much_text")
            except Exception as e:
                logger.warning(f"Failed to execute OCR on thumbnail: {e}")
                
    except Exception as e:
        logger.error(f"Error analyzing thumbnail {local_path}: {e}")
        
    return results

def compute_hsv_histogram(img_path):
    """
    Compute normalized HSV histogram for consistency comparison.
    """
    try:
        img = cv2.imread(img_path)
        if img is None:
            return None
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Compute 2D histogram on H & S channels
        hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist
    except Exception:
        return None

def analyze_brand_consistency(thumbnail_paths, consistency_threshold=0.8):
    """
    Evaluate brand consistency across downloaded thumbnails using HSV histogram comparison.
    """
    valid_paths = [p for p in thumbnail_paths if p and os.path.exists(p)]
    if len(valid_paths) < 2:
        return True, 1.0  # Assumed consistent if less than 2 thumbnails
        
    hists = []
    for path in valid_paths:
        hist = compute_hsv_histogram(path)
        if hist is not None:
            hists.append(hist)
            
    if len(hists) < 2:
        return True, 1.0
        
    # Compare consecutive thumbnail pairs
    similarities = []
    for i in range(len(hists) - 1):
        # correlation comparison (HISTCMP_CORREL): 1 is perfect match, -1 is completely mismatched
        sim = cv2.compareHist(hists[i], hists[i+1], cv2.HISTCMP_CORREL)
        similarities.append(max(0.0, sim)) # Clamp at 0
        
    avg_similarity = float(np.mean(similarities))
    is_consistent = avg_similarity >= consistency_threshold
    
    return is_consistent, avg_similarity
