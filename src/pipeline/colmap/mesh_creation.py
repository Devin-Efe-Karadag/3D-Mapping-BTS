"""
COLMAP Basic Pipeline Module using pycolmap
"""
import os
import sys
import pycolmap
from config import config

def run_colmap_pipeline(images_folder, output_folder):
    """Run basic COLMAP pipeline (sparse reconstruction only) using pycolmap"""
    database_path = os.path.join(output_folder, "database.db")
    sparse_folder = os.path.join(output_folder, "sparse")
    dense_folder = os.path.join(output_folder, "dense")
    
    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(sparse_folder, exist_ok=True)
    os.makedirs(dense_folder, exist_ok=True)
    
    print(f"[COLMAP] 🚀 Starting pycolmap pipeline for {images_folder}")
    print(f"[COLMAP] 📁 Output directory: {output_folder}")
    
    # Import required functions
    from .feature_extraction import feature_extraction
    from .matching import robust_sequential_matching, spatial_matching
    from .reconstruction import mapping, model_conversion, image_undistortion
    
    # Run pycolmap pipeline
    feature_extraction(database_path, images_folder)
    robust_sequential_matching(database_path)  # Much faster than exhaustive
    spatial_matching(database_path)     # Additional matching for coverage
    mapping(database_path, images_folder, sparse_folder)
    model_conversion(sparse_folder)
    image_undistortion(images_folder, sparse_folder, dense_folder)
    
    print(f"[COLMAP] 🎉 pycolmap pipeline complete for {images_folder}")
    return dense_folder 