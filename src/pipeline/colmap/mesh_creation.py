"""
COLMAP Basic Pipeline Module (Sparse Reconstruction Only)
"""
import os
import subprocess
import sys
import multiprocessing
from config import config

def run_cmd(cmd, cwd=None):
    """Run a command and handle errors"""
    print(f"[COLMAP] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[COLMAP][ERROR] Command failed: {' '.join(cmd)}\n{result.stderr}")
        sys.exit(result.returncode)
    print(f"[COLMAP] ✓ Command completed successfully")
    return result

def run_colmap_pipeline(images_folder, output_folder):
    """Run basic COLMAP pipeline (sparse reconstruction only)"""
    database_path = os.path.join(output_folder, "database.db")
    sparse_folder = os.path.join(output_folder, "sparse")
    dense_folder = os.path.join(output_folder, "dense")
    
    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(sparse_folder, exist_ok=True)
    os.makedirs(dense_folder, exist_ok=True)
    
    print(f"[COLMAP] 🚀 Starting pipeline for {images_folder}")
    print(f"[COLMAP] 💻 Using {multiprocessing.cpu_count()} CPU cores")
    print(f"[COLMAP] 📁 Output directory: {output_folder}")
    
    # Import required functions
    from .feature_extraction import feature_extraction
    from .matching import sequential_matching, transitive_matching
    from .reconstruction import mapping, model_conversion, image_undistortion
    
    feature_extraction(database_path, images_folder)
    sequential_matching(database_path)  # Speed optimized
    transitive_matching(database_path)   # Speed optimized
    mapping(database_path, images_folder, sparse_folder)
    model_conversion(sparse_folder)
    image_undistortion(images_folder, sparse_folder, dense_folder)
    print(f"[COLMAP] 🎉 Pipeline complete for {images_folder}")
    return dense_folder 