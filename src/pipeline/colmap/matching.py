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
    
    # Set environment variables to force headless mode for Qt applications
    env = os.environ.copy()
    env['QT_QPA_PLATFORM'] = 'offscreen'
    env['DISPLAY'] = ':0'
    
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"[COLMAP][ERROR] Command failed: {' '.join(cmd)}")
        if result.stderr:
            print(f"[COLMAP][ERROR] Error output: {result.stderr}")
        if result.stdout:
            print(f"[COLMAP][ERROR] Standard output: {result.stdout}")
        
        # Don't exit immediately, let the calling function handle it
        raise RuntimeError(f"COLMAP command failed with return code {result.returncode}")
    
    print(f"[COLMAP] Command completed successfully")
    return result

def sequential_matching(database_path):
    """Perform sequential matching between images"""
    print(f"[COLMAP] Starting sequential matching")
    
    # Validate database before matching
    if not os.path.exists(database_path):
        print(f"[COLMAP][ERROR] Database not found: {database_path}")
        sys.exit(1)
    
    # Check database size to ensure it's not empty
    db_size = os.path.getsize(database_path)
    if db_size < 1024:  # Less than 1KB
        print(f"[COLMAP][ERROR] Database appears to be empty or corrupted: {database_path} (size: {db_size} bytes)")
        sys.exit(1)
    
    print(f"[COLMAP] Database validated: {database_path} (size: {db_size} bytes)")
    
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_ratio = getattr(config, 'colmap_params', {}).get('max_ratio', 0.8)
    max_distance = getattr(config, 'colmap_params', {}).get('max_distance', 0.7)
    
    # Add cache and memory parameters to prevent initialization errors
    run_cmd([
        colmap_cmd, "sequential_matcher",
        "--database_path", database_path,
        "--SiftMatching.max_ratio", str(max_ratio),
        "--SiftMatching.max_distance", str(max_distance),
        "--SiftMatching.cross_check", "1",
        "--SiftMatching.max_num_matches", "32768",  # Increase max matches
        "--SiftMatching.max_num_trials", "10000",   # Increase trials
        "--SiftMatching.min_inlier_ratio", "0.25"   # Lower inlier ratio
    ])
    print(f"[COLMAP] Sequential matching completed")

def robust_sequential_matching(database_path):
    """Perform sequential matching with fallback strategies"""
    print(f"[COLMAP] Starting robust sequential matching")
    
    try:
        # Try standard sequential matching first
        sequential_matching(database_path)
    except Exception as e:
        print(f"[COLMAP] Standard sequential matching failed: {e}")
        print(f"[COLMAP] Trying fallback matching strategy...")
        
        # Fallback: Use exhaustive matching instead
        colmap_cmd = config.colmap_path or "colmap"
        run_cmd([
            colmap_cmd, "exhaustive_matcher",
            "--database_path", database_path,
            "--SiftMatching.max_ratio", "0.9",  # More permissive
            "--SiftMatching.max_distance", "1.0",  # More permissive
            "--SiftMatching.cross_check", "1",
            "--SiftMatching.max_num_matches", "65536",  # Even more matches
            "--SiftMatching.max_num_trials", "20000"
        ])
        print(f"[COLMAP] Fallback exhaustive matching completed")

def spatial_matching(database_path):
    """Perform spatial matching for better coverage"""
    print(f"[COLMAP] Starting spatial matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    # Additional spatial matching for better coverage
    run_cmd([
        colmap_cmd, "spatial_matcher",
        "--database_path", database_path,
        "--SpatialMatching.max_num_neighbors", "50",
        "--SiftMatching.max_num_matches", "32768",  # Increase max matches
        "--SiftMatching.max_num_trials", "10000",   # Increase trials
        "--SiftMatching.min_inlier_ratio", "0.25"   # Lower inlier ratio
    ])
    print(f"[COLMAP] Spatial matching completed") 