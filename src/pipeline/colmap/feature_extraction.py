"""
COLMAP Feature Extraction Module
"""
import os
import subprocess
import sys
from config import config

def run_cmd(cmd, cwd=None):
    """Run a command and handle errors"""
    print(f"[COLMAP] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[COLMAP][ERROR] Command failed: {' '.join(cmd)}\n{result.stderr}")
        sys.exit(result.returncode)
    print(f"[COLMAP] Command completed successfully")
    return result

def feature_extraction(database_path, images_folder):
    """Extract features from images using COLMAP"""
    print(f"[COLMAP] Starting feature extraction for {images_folder}")
    
    # Validate input
    if not os.path.exists(images_folder):
        print(f"[COLMAP][ERROR] Images folder not found: {images_folder}")
        sys.exit(1)
    
    # Count images in folder
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = [f for f in os.listdir(images_folder) 
                   if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not image_files:
        print(f"[COLMAP][ERROR] No image files found in {images_folder}")
        print(f"[COLMAP][ERROR] Supported formats: {', '.join(image_extensions)}")
        sys.exit(1)
    
    print(f"[COLMAP] Found {len(image_files)} images: {', '.join(image_files[:5])}{'...' if len(image_files) > 5 else ''}")
    
    # Validate image files are readable
    print(f"[COLMAP] Validating image files...")
    valid_images = []
    for img_file in image_files:
        img_path = os.path.join(images_folder, img_file)
        try:
            # Try to open image to check if it's valid
            from PIL import Image
            with Image.open(img_path) as img:
                width, height = img.size
                if width > 0 and height > 0:
                    valid_images.append(img_file)
                    print(f"[COLMAP] ✓ {img_file}: {width}x{height}")
                else:
                    print(f"[COLMAP] ✗ {img_file}: Invalid dimensions")
        except Exception as e:
            print(f"[COLMAP] ✗ {img_file}: {e}")
    
    if not valid_images:
        print(f"[COLMAP][ERROR] No valid images found in {images_folder}")
        print(f"[COLMAP][ERROR] All images appear to be corrupted or unreadable")
        sys.exit(1)
    
    print(f"[COLMAP] {len(valid_images)}/{len(image_files)} images are valid")
    
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_image_size = getattr(config, 'colmap_params', {}).get('max_image_size', 1600)
    max_features = getattr(config, 'colmap_params', {}).get('max_features', 2048)
    
    # Run feature extraction with CUDA GPU acceleration
    print(f"[COLMAP] Running CUDA GPU-accelerated feature extraction...")
    
    # Build command with essential options
    cmd = [
        colmap_cmd, "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--ImageReader.camera_model", "PINHOLE",
        "--FeatureExtraction.use_gpu", "1",  # Enable CUDA GPU acceleration
        "--FeatureExtraction.gpu_index", "0"  # Use first CUDA GPU device
    ]
    
    # Add SiftExtraction options if they're supported (try-catch approach)
    try:
        # Test if SiftExtraction options are supported
        test_cmd = [colmap_cmd, "feature_extractor", "--help"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if "--SiftExtraction.max_image_size" in result.stdout:
            cmd.extend(["--SiftExtraction.max_image_size", str(max_image_size)])
        if "--SiftExtraction.max_num_features" in result.stdout:
            cmd.extend(["--SiftExtraction.max_num_features", str(max_features)])
    except:
        # If help command fails, just use basic options
        pass
    
    run_cmd(cmd)
    print(f"[COLMAP] CUDA GPU-accelerated feature extraction completed")
    
    # Validate that features were actually extracted
    if not os.path.exists(database_path):
        print(f"[COLMAP][ERROR] Database was not created: {database_path}")
        sys.exit(1)
    
    db_size = os.path.getsize(database_path)
    if db_size < 1024:
        print(f"[COLMAP][ERROR] Database is too small after feature extraction: {db_size} bytes")
        print(f"[COLMAP][ERROR] This suggests no features were extracted")
        sys.exit(1)
    
    print(f"[COLMAP] Feature extraction completed successfully")
    print(f"[COLMAP] Database size: {db_size} bytes")
    
    # Try to get feature count from database
    try:
        import sqlite3
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Check if keypoints table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='keypoints'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM keypoints")
            keypoint_count = cursor.fetchone()[0]
            print(f"[COLMAP] Extracted {keypoint_count} keypoints from {len(image_files)} images")
            
            if keypoint_count == 0:
                print(f"[COLMAP][ERROR] No keypoints extracted - images may be corrupted or unsuitable")
                print(f"[COLMAP][ERROR] Check image quality, format, and content")
                sys.exit(1)
        else:
            print(f"[COLMAP][WARNING] Keypoints table not found in database")
            
        conn.close()
    except Exception as e:
        print(f"[COLMAP][WARNING] Could not verify keypoint count: {e}")
        print(f"[COLMAP] Continuing with database size validation only") 