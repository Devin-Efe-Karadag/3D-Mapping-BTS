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
    """Perform sparse reconstruction mapping"""
    print(f"[COLMAP] Starting sparse reconstruction")
    os.makedirs(sparse_folder, exist_ok=True)
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    min_matches = getattr(config, 'colmap_params', {}).get('min_matches', 15)
    max_iterations = getattr(config, 'colmap_params', {}).get('max_iterations', 50)
    max_refinements = getattr(config, 'colmap_params', {}).get('max_refinements', 3)
    
    # Optimized mapping with CUDA GPU acceleration
    print(f"[COLMAP] Using min_matches: {min_matches}, max_iterations: {max_iterations}, max_refinements: {max_refinements}")
    
    # Build command with essential options
    cmd = [
        colmap_cmd, "mapper",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--output_path", sparse_folder,
        "--Mapper.ba_use_gpu", "1",  # Enable CUDA GPU acceleration for bundle adjustment
        "--Mapper.ba_gpu_index", "0"  # Use first CUDA GPU device
    ]
    
    # Add Mapper options if they're supported (try-catch approach)
    try:
        # Test if Mapper options are supported
        test_cmd = [colmap_cmd, "mapper", "--help"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if "--Mapper.min_num_matches" in result.stdout:
            cmd.extend(["--Mapper.min_num_matches", str(min_matches)])
        if "--Mapper.ba_global_max_num_iterations" in result.stdout:
            cmd.extend(["--Mapper.ba_global_max_num_iterations", str(max_iterations)])
        if "--Mapper.ba_global_max_refinements" in result.stdout:
            cmd.extend(["--Mapper.ba_global_max_refinements", str(max_refinements)])
    except:
        # If help command fails, just use basic options
        pass
    
    run_cmd(cmd)
    print(f"[COLMAP] CUDA GPU-accelerated sparse reconstruction completed")

def model_conversion(sparse_folder):
    """Convert model to TXT format"""
    print(f"[COLMAP] Converting model to TXT format")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    run_cmd([
        colmap_cmd, "model_converter",
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", sparse_folder,
        "--output_type", "TXT"
        # Note: model_converter doesn't support GPU acceleration
    ])
    print(f"[COLMAP] Model conversion completed")

def image_undistortion(images_folder, sparse_folder, dense_folder):
    """Undistort images for dense reconstruction"""
    print(f"[COLMAP] Starting image undistortion")
    os.makedirs(dense_folder, exist_ok=True)
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    run_cmd([
        colmap_cmd, "image_undistorter",
        "--image_path", images_folder,
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", dense_folder,
        "--output_type", "COLMAP"
        # GPU acceleration is automatic when CUDA is available
    ])
    print(f"[COLMAP] Image undistortion completed") 