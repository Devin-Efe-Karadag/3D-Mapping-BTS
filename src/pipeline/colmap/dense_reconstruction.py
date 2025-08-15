"""
COLMAP Dense Reconstruction Module
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

def check_cuda_availability():
    """Check if CUDA is available for dense reconstruction"""
    try:
        # Use PyTorch for reliable CUDA detection
        import torch
        return torch.cuda.is_available()
    except ImportError:
        # Fallback to COLMAP-based detection if PyTorch not available
        try:
            colmap_cmd = config.colmap_path or "colmap"
            result = subprocess.run([colmap_cmd, "patch_match_stereo", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            # Check if CUDA-related options are available
            if "cuda" in result.stdout.lower() or "gpu" in result.stdout.lower():
                return True
        except:
            pass
        return False

def run_colmap_pipeline_with_dense(images_folder, output_folder):
    """Run COLMAP pipeline including dense reconstruction if CUDA is available"""
    
    # Early CUDA availability check
    print(f"[COLMAP] Checking CUDA availability for dense reconstruction...")
    if not check_cuda_availability():
        print(f"[COLMAP] CUDA not available on this system")
        print(f"[COLMAP] Dense reconstruction requires CUDA support")
        print(f"[COLMAP] Stopping process - cannot create 3D meshes without dense reconstruction")
        print(f"[COLMAP] Solutions:")
        print(f"[COLMAP]    - Use a system with NVIDIA GPU and CUDA")
        print(f"[COLMAP]    - Use a different reconstruction pipeline")
        sys.exit(1)
    
    print(f"[COLMAP] CUDA is available - proceeding with dense reconstruction")
    
    database_path = os.path.join(output_folder, "database.db")
    sparse_folder = os.path.join(output_folder, "sparse")
    dense_folder = os.path.join(output_folder, "dense")
    
    # Ensure output directories exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(sparse_folder, exist_ok=True)
    os.makedirs(dense_folder, exist_ok=True)
    
    print(f"[COLMAP] Starting pipeline with dense reconstruction for {images_folder}")
    print(f"[COLMAP] Using {multiprocessing.cpu_count()} CPU cores")
    print(f"[COLMAP] Output directory: {output_folder}")
    
    # Import sparse reconstruction functions
    from .feature_extraction import feature_extraction
    from .matching import sequential_matching, spatial_matching
    from .reconstruction import mapping, model_conversion, image_undistortion
    from .mesh_creation import run_colmap_pipeline
    
    # Standard COLMAP pipeline
    feature_extraction(database_path, images_folder)
    sequential_matching(database_path)
    spatial_matching(database_path)
    mapping(database_path, images_folder, sparse_folder)
    model_conversion(sparse_folder)
    image_undistortion(images_folder, sparse_folder, dense_folder)
    
    # Dense reconstruction (CUDA is available)
    print(f"[COLMAP] Starting dense stereo reconstruction")
    stereo_folder = os.path.join(dense_folder, "stereo")
    os.makedirs(stereo_folder, exist_ok=True)
    
    # Use config for COLMAP path
    colmap_cmd = config.colmap_path or "colmap"
    
    # Get configurable parameters
    dense_image_size = getattr(config, 'colmap_params', {}).get('dense_image_size', 2000)
    window_radius = getattr(config, 'colmap_params', {}).get('window_radius', 5)
    window_step = getattr(config, 'colmap_params', {}).get('window_step', 2)
    
    run_cmd([
        colmap_cmd, "patch_match_stereo",
        "--workspace_path", dense_folder,
        "--workspace_format", "COLMAP",
        "--PatchMatchStereo.max_image_size", str(dense_image_size),
        "--PatchMatchStereo.window_radius", str(window_radius),
        "--PatchMatchStereo.window_step", str(window_step)
    ])
    print(f"[COLMAP] Dense stereo reconstruction completed")
    
    # Dense fusion
    print(f"[COLMAP] Starting dense fusion")
    fused_folder = os.path.join(dense_folder, "fused")
    os.makedirs(fused_folder, exist_ok=True)
    
    run_cmd([
        colmap_cmd, "stereo_fusion",
        "--workspace_path", dense_folder,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", os.path.join(fused_folder, "fused.ply")
    ])
    print(f"[COLMAP] Dense fusion completed")
    
    # Mesh creation
    print(f"[COLMAP] Creating mesh from point cloud")
    mesh_folder = os.path.join(output_folder, "mesh")
    os.makedirs(mesh_folder, exist_ok=True)
    
    run_cmd([
        colmap_cmd, "poisson_mesher",
        "--input_path", os.path.join(fused_folder, "fused.ply"),
        "--output_path", os.path.join(mesh_folder, "mesh.ply")
    ])
    print(f"[COLMAP] Mesh creation completed")
    
            # Convert to OBJ format for 3D mesh analysis
    obj_file = os.path.join(mesh_folder, "model.obj")
    run_cmd([
        colmap_cmd, "model_converter",
        "--input_path", os.path.join(mesh_folder, "mesh.ply"),
        "--output_path", obj_file,
        "--output_type", "OBJ"
    ])
    print(f"[COLMAP] Model conversion to OBJ completed")
    
    print(f"[COLMAP] Pipeline complete with mesh: {obj_file}")
    return obj_file 