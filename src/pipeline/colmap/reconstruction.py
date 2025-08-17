"""
COLMAP Sparse Reconstruction Module
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
    print(f"[COLMAP] Command completed successfully")
    return result

def mapping(database_path, images_folder, sparse_folder):
    """Perform sparse reconstruction mapping using hierarchical mapper with basic settings"""
    os.makedirs(sparse_folder, exist_ok=True)
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Build command with basic options
    cmd = [
        colmap_cmd, "hierarchical_mapper",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--output_path", sparse_folder,
        "--Mapper.ba_use_gpu", "1",
        "--Mapper.ba_gpu_index", "0"
    ]
    
    run_cmd(cmd)
    print(f"[COLMAP] Hierarchical mapping completed")

def model_conversion(sparse_folder):
    """Convert model to TXT format"""
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    run_cmd([
        colmap_cmd, "model_converter",
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", sparse_folder,
        "--output_type", "TXT"
    ])
    print(f"[COLMAP] Model conversion completed")

def image_undistortion(images_folder, sparse_folder, dense_folder):
    """Undistort images for dense reconstruction with basic settings"""
    os.makedirs(dense_folder, exist_ok=True)
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Build command with basic options
    cmd = [
        colmap_cmd, "image_undistorter",
        "--image_path", images_folder,
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", dense_folder,
        "--output_type", "COLMAP"
    ]
    
    run_cmd(cmd)
    print(f"[COLMAP] Image undistortion completed") 