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
    """Perform sequential matching with GPU acceleration"""
    print(f"[COLMAP] Starting sequential matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_ratio = getattr(config, 'colmap_params', {}).get('max_ratio', 0.8)
    max_distance = getattr(config, 'colmap_params', {}).get('max_distance', 0.7)
    
    # Run sequential matching (GPU acceleration automatic)
    print(f"[COLMAP] Running sequential matching (GPU acceleration automatic if CUDA available)...")
    
    # Build command with essential options
    cmd = [
        colmap_cmd, "sequential_matcher",
        "--database_path", database_path
    ]
    
    # Add SiftMatching options if they're supported (try-catch approach)
    try:
        # Test if SiftMatching options are supported
        test_cmd = [colmap_cmd, "sequential_matcher", "--help"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if "--SiftMatching.max_ratio" in result.stdout:
            cmd.extend(["--SiftMatching.max_ratio", str(max_ratio)])
        if "--SiftMatching.max_distance" in result.stdout:
            cmd.extend(["--SiftMatching.max_distance", str(max_distance)])
        if "--SiftMatching.cross_check" in result.stdout:
            cmd.extend(["--SiftMatching.cross_check", "1"])
        if "--SiftMatching.max_num_matches" in result.stdout:
            cmd.extend(["--SiftMatching.max_num_matches", "32768"])
        if "--SiftMatching.max_num_trials" in result.stdout:
            cmd.extend(["--SiftMatching.max_num_trials", "10000"])
        if "--SiftMatching.min_inlier_ratio" in result.stdout:
            cmd.extend(["--SiftMatching.min_inlier_ratio", "0.25"])
    except:
        # If help command fails, just use basic options
        pass
    
    run_cmd(cmd)
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
        
        # Fallback: Try exhaustive matching
        colmap_cmd = config.colmap_path or "colmap"
        print(f"[COLMAP] Running exhaustive matching...")
        
        # Build command with essential options
        cmd = [
            colmap_cmd, "exhaustive_matcher",
            "--database_path", database_path
        ]
        
        # Add SiftMatching options if they're supported (try-catch approach)
        try:
            # Test if SiftMatching options are supported
            test_cmd = [colmap_cmd, "exhaustive_matcher", "--help"]
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            if "--SiftMatching.max_ratio" in result.stdout:
                cmd.extend(["--SiftMatching.max_ratio", "0.9"])
            if "--SiftMatching.max_distance" in result.stdout:
                cmd.extend(["--SiftMatching.max_distance", "1.0"])
            if "--SiftMatching.cross_check" in result.stdout:
                cmd.extend(["--SiftMatching.cross_check", "1"])
            if "--SiftMatching.max_num_matches" in result.stdout:
                cmd.extend(["--SiftMatching.max_num_matches", "65536"])
            if "--SiftMatching.max_num_trials" in result.stdout:
                cmd.extend(["--SiftMatching.max_num_trials", "20000"])
        except:
            # If help command fails, just use basic options
            pass
        
        run_cmd(cmd)
        print(f"[COLMAP] Exhaustive matching completed")

def spatial_matching(database_path):
    """Perform spatial matching for better coverage"""
    print(f"[COLMAP] Starting spatial matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Run spatial matching (GPU acceleration automatic)
    print(f"[COLMAP] Running spatial matching (GPU acceleration automatic if CUDA available)...")
    
    # Build command with essential options
    cmd = [
        colmap_cmd, "spatial_matcher",
        "--database_path", database_path
    ]
    
    # Add SiftMatching options if they're supported (try-catch approach)
    try:
        # Test if SiftMatching options are supported
        test_cmd = [colmap_cmd, "spatial_matcher", "--help"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if "--SpatialMatching.max_num_neighbors" in result.stdout:
            cmd.extend(["--SpatialMatching.max_num_neighbors", "50"])
        if "--SiftMatching.max_num_matches" in result.stdout:
            cmd.extend(["--SiftMatching.max_num_matches", "32768"])
        if "--SiftMatching.max_num_trials" in result.stdout:
            cmd.extend(["--SiftMatching.max_num_trials", "10000"])
        if "--SiftMatching.min_inlier_ratio" in result.stdout:
            cmd.extend(["--SiftMatching.min_inlier_ratio", "0.25"])
    except:
        # If help command fails, just use basic options
        pass
    
    run_cmd(cmd)
    print(f"[COLMAP] Spatial matching completed")

# Keep exhaustive matching as a separate function
def exhaustive_matching(database_path):
    """Perform exhaustive matching with GPU acceleration"""
    print(f"[COLMAP] Starting exhaustive matching")
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    max_ratio = getattr(config, 'colmap_params', {}).get('max_ratio', 0.8)
    max_distance = getattr(config, 'colmap_params', {}).get('max_distance', 0.7)
    
    # Run exhaustive matching (GPU acceleration automatic)
    print(f"[COLMAP] Running exhaustive matching (GPU acceleration automatic if CUDA available)...")
    
    # Build command with essential options
    cmd = [
        colmap_cmd, "exhaustive_matcher",
        "--database_path", database_path
    ]
    
    # Add SiftMatching options if they're supported (try-catch approach)
    try:
        # Test if SiftMatching options are supported
        test_cmd = [colmap_cmd, "exhaustive_matcher", "--help"]
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        if "--SiftMatching.max_ratio" in result.stdout:
            cmd.extend(["--SiftMatching.max_ratio", str(max_ratio)])
        if "--SiftMatching.max_distance" in result.stdout:
            cmd.extend(["--SiftMatching.max_distance", str(max_distance)])
        if "--SiftMatching.cross_check" in result.stdout:
            cmd.extend(["--SiftMatching.cross_check", "1"])
        if "--SiftMatching.max_num_matches" in result.stdout:
            cmd.extend(["--SiftMatching.max_num_matches", "32768"])
        if "--SiftMatching.max_num_trials" in result.stdout:
            cmd.extend(["--SiftMatching.max_num_trials", "10000"])
        if "--SiftMatching.min_inlier_ratio" in result.stdout:
            cmd.extend(["--SiftMatching.min_inlier_ratio", "0.25"])
    except:
        # If help command fails, just use basic options
        pass
    
    run_cmd(cmd)
    print(f"[COLMAP] Exhaustive matching completed")

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
        print(f"[COLMAP] Running exhaustive matching with permissive parameters...")
        
        # Build command with essential options
        cmd = [
            colmap_cmd, "exhaustive_matcher",
            "--database_path", database_path
        ]
        
        # Add SiftMatching options if they're supported (try-catch approach)
        try:
            # Test if SiftMatching options are supported
            test_cmd = [colmap_cmd, "exhaustive_matcher", "--help"]
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
            if "--SiftMatching.max_ratio" in result.stdout:
                cmd.extend(["--SiftMatching.max_ratio", "0.9"])
            if "--SiftMatching.max_distance" in result.stdout:
                cmd.extend(["--SiftMatching.max_distance", "1.0"])
            if "--SiftMatching.cross_check" in result.stdout:
                cmd.extend(["--SiftMatching.cross_check", "1"])
            if "--SiftMatching.max_num_matches" in result.stdout:
                cmd.extend(["--SiftMatching.max_num_matches", "65536"])
            if "--SiftMatching.max_num_trials" in result.stdout:
                cmd.extend(["--SiftMatching.max_num_trials", "20000"])
        except:
            # If help command fails, just use basic options
            pass
        
        run_cmd(cmd)
        print(f"[COLMAP] Exhaustive matching with permissive parameters completed") 