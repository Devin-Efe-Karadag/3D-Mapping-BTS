"""
COLMAP Feature Extraction Module
"""
import os
import subprocess
import sys
from config import config
import multiprocessing

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
    """Extract features from images using COLMAP with aggressive speed optimization"""
    print(f"[COLMAP] Starting FAST feature extraction for {images_folder}")
    
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
    
    # BALANCED SPEED OPTIMIZATION PARAMETERS
    # These settings balance speed with quality to prevent downstream crashes
    max_image_size = getattr(config, 'colmap_params', {}).get('max_image_size', 1400)  # Increased from 1200 for better quality
    max_features = getattr(config, 'colmap_params', {}).get('max_features', 1536)      # Increased from 1024 for better quality
    
    print(f"[COLMAP] 🚀 Using BALANCED speed optimization:")
    print(f"[COLMAP]   - max_image_size: {max_image_size} (balanced speed/quality)")
    print(f"[COLMAP]   - max_features: {max_features} (balanced speed/quality)")
    print(f"[COLMAP]   - GPU acceleration: ENABLED")
    
    # Run feature extraction with BALANCED speed optimization
    print(f"[COLMAP] Running BALANCED CUDA GPU-accelerated feature extraction...")
    
    # Build command with BALANCED speed optimization options
    cmd = [
        colmap_cmd, "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--ImageReader.camera_model", "PINHOLE",
        "--FeatureExtraction.use_gpu", "1",  # Enable CUDA GPU acceleration
        "--FeatureExtraction.gpu_index", "0",  # Use first CUDA GPU device
        "--FeatureExtraction.num_threads", str(multiprocessing.cpu_count()),  # Use all CPU cores
        # BALANCED SIFT OPTIMIZATIONS FOR SPEED + QUALITY
        "--SiftExtraction.max_image_size", str(max_image_size),      # Balanced size for quality
        "--SiftExtraction.max_num_features", str(max_features),      # Balanced features for quality
        "--SiftExtraction.num_octaves", "3",                        # Reduced from 4 = faster
        "--SiftExtraction.octave_resolution", "2",                  # Reduced from 3 = faster
        "--SiftExtraction.peak_threshold", "0.012",                 # Balanced threshold
        "--SiftExtraction.edge_threshold", "9",                     # Balanced threshold
        "--SiftExtraction.estimate_affine_shape", "1",              # Keep enabled for better features
        "--SiftExtraction.max_num_orientations", "1",               # Reduced from 2 = faster
        "--SiftExtraction.upright", "1",                            # Keep enabled for better matching
        "--SiftExtraction.domain_size_pooling", "0",                # Disabled = faster
        "--SiftExtraction.dsp_min_scale", "0.2",                    # Balanced range
        "--SiftExtraction.dsp_max_scale", "2.5",                    # Balanced range
        "--SiftExtraction.dsp_num_scales", "6"                      # Balanced scales
    ]
    
    print(f"[COLMAP] Speed optimization summary:")
    print(f"[COLMAP]   • Image size: {max_image_size}px (vs default 3200px)")
    print(f"[COLMAP]   • Max features: {max_features} (vs default 8192)")
    print(f"[COLMAP]   • Octaves: 3 (vs default 4)")
    print(f"[COLMAP]   • Octave resolution: 2 (vs default 3)")
    print(f"[COLMAP]   • Peak threshold: 0.012 (vs default 0.0067)")
    print(f"[COLMAP]   • CPU threads: {multiprocessing.cpu_count()}")
    print(f"[COLMAP]   • GPU acceleration: ENABLED")
    
    run_cmd(cmd)
    print(f"[COLMAP] 🎉 BALANCED CUDA GPU-accelerated feature extraction completed!")
    print(f"[COLMAP] Expected speed improvement: 2-3x faster than default settings")
    print(f"[COLMAP] Note: Balanced for quality to prevent downstream crashes")
    
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