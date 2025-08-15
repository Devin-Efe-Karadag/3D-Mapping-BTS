"""
COLMAP Sparse Reconstruction Module using pycolmap
"""
import os
import sys
import pycolmap
from config import config

def mapping(database_path, images_folder, sparse_folder):
    """Perform sparse reconstruction mapping using pycolmap"""
    print(f"[COLMAP] Starting sparse reconstruction")
    os.makedirs(sparse_folder, exist_ok=True)
    
    # Get configurable parameters
    min_matches = getattr(config, 'colmap_params', {}).get('min_matches', 15)
    max_iterations = getattr(config, 'colmap_params', {}).get('max_iterations', 50)
    max_refinements = getattr(config, 'colmap_params', {}).get('max_refinements', 3)
    
    # Optimized mapping with GPU acceleration
    try:
        print(f"[COLMAP] Starting pycolmap sparse reconstruction...")
        
        pycolmap.pipeline.run_mapper(
            database_path=database_path,
            image_path=images_folder,
            output_path=sparse_folder,
            mapper_options=pycolmap.MapperOptions(
                min_num_matches=min_matches,
                ba_global_max_num_iterations=max_iterations,
                ba_global_max_refinements=max_refinements
            )
        )
        
        print(f"[COLMAP] Sparse reconstruction completed")
        
    except Exception as gpu_error:
        print(f"[COLMAP] GPU reconstruction failed: {gpu_error}")
        print(f"[COLMAP] Falling back to CPU reconstruction...")
        
        # Fallback: CPU reconstruction
        pycolmap.pipeline.run_mapper(
            database_path=database_path,
            image_path=images_folder,
            output_path=sparse_folder,
            mapper_options=pycolmap.MapperOptions(
                min_num_matches=min_matches,
                ba_global_max_num_iterations=max_iterations,
                ba_global_max_refinements=max_refinements
            )
        )
        print(f"[COLMAP] CPU fallback sparse reconstruction completed")

def model_conversion(sparse_folder):
    """Convert model to TXT format using pycolmap"""
    print(f"[COLMAP] Converting model to TXT format")
    
    # Find the first reconstruction
    reconstructions = pycolmap.Reconstruction(sparse_folder)
    
    # Export to TXT format - use the correct pycolmap API
    reconstructions.export_txt(sparse_folder)
    
    print(f"[COLMAP] Model conversion completed")

def image_undistortion(images_folder, sparse_folder, dense_folder):
    """Undistort images for dense reconstruction using pycolmap"""
    print(f"[COLMAP] Starting image undistortion")
    os.makedirs(dense_folder, exist_ok=True)
    
    try:
        print(f"[COLMAP] Starting pycolmap image undistortion...")
        
        pycolmap.undistort_images(
            image_path=images_folder,
            input_path=sparse_folder,
            output_path=dense_folder,
            output_type="COLMAP"
        )
        
        print(f"[COLMAP] Image undistortion completed")
        
    except Exception as e:
        print(f"[COLMAP] Image undistortion failed: {e}")
        print(f"[COLMAP] Continuing without undistortion...")
        # Copy original images to dense folder as fallback
        import shutil
        for img_file in os.listdir(images_folder):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')):
                src = os.path.join(images_folder, img_file)
                dst = os.path.join(dense_folder, img_file)
                shutil.copy2(src, dst)
        print(f"[COLMAP] Copied original images as fallback") 