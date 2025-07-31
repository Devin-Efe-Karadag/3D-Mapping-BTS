"""
COLMAP Matching Module
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

def sequential_matching(database_path):
    """Perform sequential matching between images"""
    print(f"[COLMAP] Starting sequential matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_ratio = getattr(config, 'colmap_params', {}).get('max_ratio', 0.8)
    max_distance = getattr(config, 'colmap_params', {}).get('max_distance', 0.7)
    
    run_cmd([
        colmap_cmd, "sequential_matcher",
        "--database_path", database_path,
        "--SiftMatching.use_gpu", "0",  # Disable GPU, use CPU only
        "--SiftMatching.max_ratio", str(max_ratio),
        "--SiftMatching.max_distance", str(max_distance),
        "--SiftMatching.cross_check", "1"
    ])
    print(f"[COLMAP] Sequential matching completed")

def spatial_matching(database_path):
    """Perform spatial matching for better coverage"""
    print(f"[COLMAP] Starting spatial matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    # Additional spatial matching for better coverage
    run_cmd([
        colmap_cmd, "spatial_matcher",
        "--database_path", database_path,
        "--SiftMatching.use_gpu", "0",  # Disable GPU, use CPU only
        "--SpatialMatching.max_num_neighbors", "50"
    ])
    print(f"[COLMAP] Spatial matching completed") 