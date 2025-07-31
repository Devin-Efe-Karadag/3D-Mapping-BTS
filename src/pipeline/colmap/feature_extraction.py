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
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_image_size = getattr(config, 'colmap_params', {}).get('max_image_size', 1600)
    max_features = getattr(config, 'colmap_params', {}).get('max_features', 2048)
    
    run_cmd([
        colmap_cmd, "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--ImageReader.camera_model", "PINHOLE",
        "--SiftExtraction.max_image_size", str(max_image_size),
        "--SiftExtraction.max_num_features", str(max_features)
    ])
    print(f"[COLMAP] Feature extraction completed") 