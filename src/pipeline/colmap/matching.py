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

def exhaustive_matching(database_path):
    """Perform exhaustive matching with GPU acceleration"""
    print(f"[COLMAP] Starting exhaustive matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_ratio = getattr(config, 'colmap_params', {}).get('max_ratio', 0.8)
    max_distance = getattr(config, 'colmap_params', {}).get('max_distance', 0.7)
    
    # Run GPU-accelerated exhaustive matching
    print(f"[COLMAP] Running GPU-accelerated exhaustive matching...")
    run_cmd([
        colmap_cmd, "exhaustive_matcher",
        "--database_path", database_path,
        "--SiftMatching.use_gpu", "1",  # Enable GPU acceleration
        "--SiftMatching.max_ratio", str(max_ratio),
        "--SiftMatching.max_distance", str(max_distance),
        "--SiftMatching.cross_check", "1",
        "--SiftMatching.max_num_matches", "32768",  # Increase max matches
        "--SiftMatching.max_num_trials", "10000",   # Increase trials
        "--SiftMatching.min_inlier_ratio", "0.25"   # Lower inlier ratio
    ])
    print(f"[COLMAP] GPU-accelerated exhaustive matching completed")

def robust_matching(database_path):
    """Perform robust matching with fallback strategies"""
    print(f"[COLMAP] Starting robust matching")
    
    try:
        # Try standard exhaustive matching first
        exhaustive_matching(database_path)
    except Exception as e:
        print(f"[COLMAP] Standard exhaustive matching failed: {e}")
        print(f"[COLMAP] Trying fallback matching strategy...")
        
        # Fallback: Try more permissive parameters
        colmap_cmd = config.colmap_path or "colmap"
        print(f"[COLMAP] Running GPU-accelerated exhaustive matching with permissive parameters...")
        run_cmd([
            colmap_cmd, "exhaustive_matcher",
            "--database_path", database_path,
            "--SiftMatching.use_gpu", "1",  # Enable GPU acceleration
            "--SiftMatching.max_ratio", "0.9",  # More permissive
            "--SiftMatching.max_distance", "1.0",  # More permissive
            "--SiftMatching.cross_check", "1",
            "--SiftMatching.max_num_matches", "65536",  # Even more matches
            "--SiftMatching.max_num_trials", "20000"
        ])
        print(f"[COLMAP] GPU-accelerated exhaustive matching with permissive parameters completed")

# Legacy function names for backward compatibility
def sequential_matching(database_path):
    """Alias for exhaustive matching (sequential_matcher not available on this COLMAP version)"""
    print(f"[COLMAP] sequential_matcher not available, using exhaustive_matcher instead")
    exhaustive_matching(database_path)

def spatial_matching(database_path):
    """Alias for exhaustive matching (spatial_matcher not available on this COLMAP version)"""
    print(f"[COLMAP] spatial_matcher not available, using exhaustive_matcher instead")
    exhaustive_matching(database_path) 