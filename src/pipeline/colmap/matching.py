"""
COLMAP Matching Module using pycolmap
"""
import os
import sys
import pycolmap
from config import config

def sequential_matching(database_path):
    """Perform sequential matching between images using pycolmap"""
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
    
    # Get configurable parameters
    max_ratio = getattr(config, 'colmap_params', {}).get('max_ratio', 0.8)
    max_distance = getattr(config, 'colmap_params', {}).get('max_distance', 0.7)
    
    # Try GPU matching first, fallback to CPU if GPU fails
    try:
        print(f"[COLMAP] Trying GPU-accelerated sequential matching...")
        
        pycolmap.match_exhaustive(
            database_path=database_path,
            sift_options=pycolmap.SiftMatchingOptions(
                max_ratio=max_ratio,
                max_distance=max_distance,
                cross_check=True,
                max_num_matches=32768,
                use_gpu=True  # Enable GPU acceleration
            )
        )
        
        print(f"[COLMAP] GPU-accelerated sequential matching completed")
        
    except Exception as gpu_error:
        print(f"[COLMAP] GPU matching failed: {gpu_error}")
        print(f"[COLMAP] Falling back to CPU matching...")
        
        # Fallback: CPU matching
        pycolmap.match_exhaustive(
            database_path=database_path,
            sift_options=pycolmap.SiftMatchingOptions(
                max_ratio=max_ratio,
                max_distance=max_distance,
                cross_check=True,
                max_num_matches=32768,
                use_gpu=False  # Force CPU matching
            )
        )
        print(f"[COLMAP] CPU fallback sequential matching completed")

def robust_sequential_matching(database_path):
    """Perform sequential matching with fallback strategies using pycolmap"""
    print(f"[COLMAP] Starting robust sequential matching")
    
    try:
        # Try standard sequential matching first
        sequential_matching(database_path)
    except Exception as e:
        print(f"[COLMAP] Standard sequential matching failed: {e}")
        print(f"[COLMAP] Trying fallback matching strategy...")
        
        # Fallback: Try GPU matching first, then CPU if GPU fails
        try:
            print(f"[COLMAP] Trying GPU-accelerated exhaustive matching...")
            
            pycolmap.match_exhaustive(
                database_path=database_path,
                sift_options=pycolmap.SiftMatchingOptions(
                    max_ratio=0.9,  # More permissive
                    max_distance=1.0,  # More permissive
                    cross_check=True,
                    max_num_matches=65536,  # Even more matches
                    use_gpu=True  # Enable GPU acceleration
                )
            )
            
            print(f"[COLMAP] GPU-accelerated exhaustive matching completed")
            
        except Exception as gpu_error:
            print(f"[COLMAP] GPU matching failed: {gpu_error}")
            print(f"[COLMAP] Falling back to CPU matching...")
            
            # Final fallback: CPU matching
            pycolmap.match_exhaustive(
                database_path=database_path,
                sift_options=pycolmap.SiftMatchingOptions(
                    max_ratio=0.9,  # More permissive
                    max_distance=1.0,  # More permissive
                    cross_check=True,
                    max_num_matches=65536,  # Even more matches
                    use_gpu=False  # Force CPU matching
                )
            )
            print(f"[COLMAP] CPU fallback exhaustive matching completed")

def spatial_matching(database_path):
    """Perform spatial matching for better coverage using pycolmap"""
    print(f"[COLMAP] Starting spatial matching")
    
    # Try GPU matching first, fallback to CPU if GPU fails
    try:
        print(f"[COLMAP] Trying GPU-accelerated spatial matching...")
        
        pycolmap.match_spatial(
            database_path=database_path,
            sift_options=pycolmap.SiftMatchingOptions(
                max_ratio=0.8,
                max_distance=0.7,
                cross_check=True,
                max_num_matches=32768,
                use_gpu=True  # Enable GPU acceleration
            ),
            spatial_options=pycolmap.SpatialMatchingOptions(
                max_num_neighbors=50
            )
        )
        
        print(f"[COLMAP] GPU-accelerated spatial matching completed")
        
    except Exception as gpu_error:
        print(f"[COLMAP] GPU matching failed: {gpu_error}")
        print(f"[COLMAP] Falling back to CPU matching...")
        
        # Fallback: CPU matching
        pycolmap.match_exhaustive(
            database_path=database_path,
            sift_options=pycolmap.SiftMatchingOptions(
                max_ratio=0.8,
                max_distance=0.7,
                cross_check=True,
                max_num_matches=32768,
                use_gpu=False  # Force CPU matching
            )
        )
        print(f"[COLMAP] CPU fallback spatial matching completed") 