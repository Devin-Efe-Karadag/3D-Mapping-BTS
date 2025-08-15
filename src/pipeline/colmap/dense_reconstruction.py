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

def setup_display_environment():
    """Set up display environment for headless operation"""
    print(f"[COLMAP] Setting up display environment for headless operation...")
    
    # Set environment variables to force headless mode
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    os.environ['DISPLAY'] = ':0'
    
    # Check if we're in a headless environment
    if not os.environ.get('DISPLAY') or os.environ.get('DISPLAY') == '':
        print(f"[COLMAP] No display detected, using headless mode")
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        os.environ['DISPLAY'] = ':0'
    
    print(f"[COLMAP] Display environment: QT_QPA_PLATFORM={os.environ.get('QT_QPA_PLATFORM')}, DISPLAY={os.environ.get('DISPLAY')}")
    
    # Try to start virtual display if needed (Linux only)
    if os.name == 'posix' and os.uname().sysname == 'Linux':
        try:
            # Check if Xvfb is available
            result = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[COLMAP] Xvfb available, starting virtual display...")
                # Start virtual display in background
                subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.environ['DISPLAY'] = ':99'
                print(f"[COLMAP] Virtual display started on :99")
        except Exception as e:
            print(f"[COLMAP] Could not start virtual display: {e}")
            print(f"[COLMAP] Continuing with offscreen mode")
    
    print(f"[COLMAP] Display environment setup complete")

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
    
    # Set up display environment for headless operation
    setup_display_environment()
    
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
    from .matching import robust_sequential_matching, spatial_matching
    from .reconstruction import mapping, model_conversion, image_undistortion
    from .mesh_creation import run_colmap_pipeline
    
    # Standard COLMAP pipeline
    try:
        feature_extraction(database_path, images_folder)
        robust_sequential_matching(database_path)
        spatial_matching(database_path)
        mapping(database_path, images_folder, sparse_folder)
    except Exception as e:
        print(f"[COLMAP][ERROR] Pipeline failed: {e}")
        print(f"[COLMAP] Attempting to diagnose the issue...")
        
        # Check if database exists and has content
        if os.path.exists(database_path):
            db_size = os.path.getsize(database_path)
            print(f"[COLMAP] Database size: {db_size} bytes")
            
            if db_size < 1024:
                print(f"[COLMAP][ERROR] Database is too small - feature extraction likely failed")
                print(f"[COLMAP] Possible causes:")
                print(f"  - Images are corrupted or unreadable")
                print(f"  - Images have no distinctive features")
                print(f"  - Images are too similar or too different")
                print(f"  - Image format not supported by COLMAP")
                print(f"[COLMAP] Check the images in: {images_folder}")
                sys.exit(1)
        else:
            print(f"[COLMAP][ERROR] Database was never created")
            print(f"[COLMAP] Feature extraction completely failed")
            sys.exit(1)
        
        # Re-raise the exception if we can't handle it
        raise
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
        "--PatchMatchStereo.window_step", str(window_step),
        "--PatchMatchStereo.gpu_index", "0"  # Use first GPU
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
        "--output_path", os.path.join(fused_folder, "fused.ply"),
        "--StereoFusion.gpu_index", "0"  # Use first GPU
    ])
    print(f"[COLMAP] Dense fusion completed")
    
    # Mesh creation
    print(f"[COLMAP] Creating mesh from point cloud")
    mesh_folder = os.path.join(output_folder, "mesh")
    os.makedirs(mesh_folder, exist_ok=True)
    
    run_cmd([
        colmap_cmd, "poisson_mesher",
        "--input_path", os.path.join(fused_folder, "fused.ply"),
        "--output_path", os.path.join(mesh_folder, "mesh.ply"),
        "--PoissonMesher.gpu_index", "0"  # Use first GPU
    ])
    print(f"[COLMAP] Mesh creation completed")
    
            # Convert to OBJ format for 3D mesh analysis
    obj_file = os.path.join(mesh_folder, "model.obj")
    run_cmd([
        colmap_cmd, "model_converter",
        "--input_path", os.path.join(mesh_folder, "mesh.ply"),
        "--output_path", obj_file,
        "--output_type", "OBJ"
        # Note: model_converter doesn't support GPU acceleration
    ])
    print(f"[COLMAP] Model conversion to OBJ completed")
    
    print(f"[COLMAP] Pipeline complete with mesh: {obj_file}")
    return obj_file 