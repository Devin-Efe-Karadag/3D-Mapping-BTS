"""
COLMAP Matching Module
"""
import os
import subprocess
import sys
from config import config
import multiprocessing

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
    """Perform sequential matching with basic settings"""
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Build command with basic options
    cmd = [
        colmap_cmd, "sequential_matcher",
        "--database_path", database_path,
        "--FeatureMatching.use_gpu", "1",
        "--FeatureMatching.gpu_index", "0"
    ]
    
    run_cmd(cmd)
    print(f"[COLMAP] Sequential matching completed")

def transitive_matching(database_path):
    """Perform transitive matching with basic settings"""
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Build command with basic options
    cmd = [
        colmap_cmd, "transitive_matcher",
        "--database_path", database_path,
        "--FeatureMatching.use_gpu", "1",
        "--FeatureMatching.gpu_index", "0"
    ]
    
    run_cmd(cmd)
    print(f"[COLMAP] Transitive matching completed")

# Legacy function names for backward compatibility
def robust_sequential_matching(database_path):
    """Alias for sequential matching (using defaults)"""
    sequential_matching(database_path) 