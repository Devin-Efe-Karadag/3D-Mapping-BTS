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
    from .matching import sequential_matching, transitive_matching
    from .reconstruction import mapping, model_conversion, image_undistortion
    from .mesh_creation import run_colmap_pipeline
    
    # Standard COLMAP pipeline
    try:
        feature_extraction(database_path, images_folder)
        sequential_matching(database_path)
        transitive_matching(database_path)
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
    dense_image_size = getattr(config, 'colmap_params', {}).get('dense_image_size', 1800)  # Increased from 1600 for better quality
    window_radius = getattr(config, 'colmap_params', {}).get('window_radius', 4)  # Increased from 3 for better quality
    window_step = getattr(config, 'colmap_params', {}).get('window_step', 2)  # Keep at 2
    
    print(f"[COLMAP] 🚀 Using BALANCED speed optimization for dense stereo:")
    print(f"[COLMAP]   - dense_image_size: {dense_image_size} (balanced for quality)")
    print(f"[COLMAP]   - window_radius: {window_radius} (balanced for quality)")
    print(f"[COLMAP]   - window_step: {window_step} (balanced for speed)")
    print(f"[COLMAP]   - GPU acceleration: ENABLED")
    
    # Build command with BALANCED speed optimization options
    cmd = [
        colmap_cmd, "patch_match_stereo",
        "--workspace_path", dense_folder,
        "--workspace_format", "COLMAP",
        # BALANCED PATCH MATCH STEREO OPTIMIZATIONS FOR SPEED + QUALITY
        "--PatchMatchStereo.max_image_size", str(dense_image_size),  # Balanced for quality
        "--PatchMatchStereo.gpu_index", "0",  # Use first CUDA GPU device
        "--PatchMatchStereo.depth_min", "-1",  # Auto-detect
        "--PatchMatchStereo.depth_max", "-1",  # Auto-detect
        "--PatchMatchStereo.window_radius", str(window_radius),  # Balanced for quality
        "--PatchMatchStereo.window_step", str(window_step),  # Balanced for speed
        "--PatchMatchStereo.sigma_spatial", "-1",  # Auto-detect
        "--PatchMatchStereo.sigma_color", "0.25",  # Balanced threshold
        "--PatchMatchStereo.num_samples", "12",  # Balanced for quality
        "--PatchMatchStereo.ncc_sigma", "0.7",  # Balanced threshold
        "--PatchMatchStereo.min_triangulation_angle", "0.9",  # Balanced threshold
        "--PatchMatchStereo.incident_angle_sigma", "1.0",  # Balanced threshold
        "--PatchMatchStereo.num_iterations", "4",  # Balanced for quality
        "--PatchMatchStereo.geom_consistency", "0",  # Disabled for speed
        "--PatchMatchStereo.geom_consistency_regularizer", "0.4",  # Balanced threshold
        "--PatchMatchStereo.geom_consistency_max_cost", "4",  # Balanced threshold
        "--PatchMatchStereo.filter", "1",  # Keep filtering
        "--PatchMatchStereo.filter_min_ncc", "0.09",  # Balanced threshold
        "--PatchMatchStereo.filter_min_triangulation_angle", "2.5",  # Balanced threshold
        "--PatchMatchStereo.filter_min_num_consistent", "1",  # Keep minimal
        "--PatchMatchStereo.filter_geom_consistency_max_cost", "1.5",  # Balanced threshold
        "--PatchMatchStereo.cache_size", "20",  # Balanced memory usage
        "--PatchMatchStereo.allow_missing_files", "0",  # Keep default
        "--PatchMatchStereo.write_consistency_graph", "0"  # Already disabled
    ]
    
    print(f"[COLMAP] Speed optimization summary:")
    print(f"[COLMAP]   • Max image size: {dense_image_size}px (vs default unlimited)")
    print(f"[COLMAP]   • Window radius: {window_radius} (vs default 5)")
    print(f"[COLMAP]   • Window step: {window_step} (vs default 1)")
    print(f"[COLMAP]   • Num samples: 12 (vs default 15)")
    print(f"[COLMAP]   • Num iterations: 4 (vs default 5)")
    print(f"[COLMAP]   • Geom consistency: DISABLED for speed")
    print(f"[COLMAP]   • Cache size: 20GB (vs default 32GB)")
    print(f"[COLMAP]   • GPU acceleration: ENABLED")
    
    run_cmd(cmd)
    print(f"[COLMAP] 🎉 BALANCED CUDA GPU-accelerated dense stereo reconstruction completed!")
    print(f"[COLMAP] Expected speed improvement: 2-4x faster than default settings")
    print(f"[COLMAP] Note: Balanced for quality to prevent downstream crashes")
    
    # Dense fusion
    print(f"[COLMAP] Starting ULTRA-FAST dense fusion")
    fused_folder = os.path.join(dense_folder, "fused")
    os.makedirs(fused_folder, exist_ok=True)
    
    # AGGRESSIVE SPEED OPTIMIZATION PARAMETERS FOR STEREO FUSION
    print(f"[COLMAP] 🚀 Using AGGRESSIVE speed optimization for stereo fusion:")
    print(f"[COLMAP]   - GPU acceleration: AUTOMATIC when CUDA available")
    print(f"[COLMAP]   - Cache optimization: ENABLED for speed")
    print(f"[COLMAP]   - Thread optimization: ALL CPU cores")
    
    # Build command with AGGRESSIVE speed optimization options
    run_cmd([
        colmap_cmd, "stereo_fusion",
        "--workspace_path", dense_folder,
        "--workspace_format", "COLMAP",
        "--input_type", "geometric",
        "--output_path", os.path.join(fused_folder, "fused.ply"),
        # AGGRESSIVE STEREO FUSION OPTIMIZATIONS FOR MAXIMUM SPEED
        "--StereoFusion.num_threads", str(multiprocessing.cpu_count()),  # Use all CPU cores
        "--StereoFusion.max_image_size", "1600",  # Limited for speed (vs unlimited -1)
        "--StereoFusion.min_num_pixels", "3",  # Reduced from 5 = faster processing
        "--StereoFusion.max_num_pixels", "5000",  # Reduced from 10000 = faster processing
        "--StereoFusion.max_traversal_depth", "50",  # Reduced from 100 = faster
        "--StereoFusion.max_reproj_error", "3",  # Increased from 2 = faster filtering
        "--StereoFusion.max_depth_error", "0.02",  # Increased from 0.01 = faster
        "--StereoFusion.max_normal_error", "15",  # Increased from 10 = faster
        "--StereoFusion.check_num_images", "25",  # Reduced from 50 = faster
        "--StereoFusion.cache_size", "16",  # Reduced from 32 = less memory usage
        "--StereoFusion.use_cache", "1"  # Enable cache for speed
    ])
    
    print(f"[COLMAP] Speed optimization summary:")
    print(f"[COLMAP]   • Max image size: 1600px (vs unlimited)")
    print(f"[COLMAP]   • Min pixels: 3 (vs default 5)")
    print(f"[COLMAP]   • Max pixels: 5000 (vs default 10000)")
    print(f"[COLMAP]   • Traversal depth: 50 (vs default 100)")
    print(f"[COLMAP]   • Max reproj error: 3 (vs default 2)")
    print(f"[COLMAP]   • Check images: 25 (vs default 50)")
    print(f"[COLMAP]   • Cache size: 16GB (vs default 32GB)")
    print(f"[COLMAP]   • Cache enabled: YES")
    print(f"[COLMAP]   • CPU threads: {multiprocessing.cpu_count()}")
    
    print(f"[COLMAP] 🎉 ULTRA-FAST dense fusion completed!")
    print(f"[COLMAP] Expected speed improvement: 2-4x faster than default settings")
    
    # Mesh creation
    print(f"[COLMAP] Creating mesh from point cloud")
    mesh_folder = os.path.join(output_folder, "mesh")
    os.makedirs(mesh_folder, exist_ok=True)
    
    # Use DEFAULT values for maximum stability
    print(f"[COLMAP] Using DEFAULT Poisson meshing parameters for maximum stability:")
    print(f"[COLMAP]   - CPU optimization: ALL CPU cores")
    print(f"[COLMAP]   - All other parameters: DEFAULT values (stable)")
    
    # Build command with DEFAULT values for stability
    run_cmd([
        colmap_cmd, "poisson_mesher",
        "--input_path", os.path.join(fused_folder, "fused.ply"),
        "--output_path", os.path.join(mesh_folder, "mesh.ply"),
        # Use DEFAULT values for maximum stability
        "--PoissonMeshing.point_weight", "1",  # Default
        "--PoissonMeshing.depth", "13",  # Default = 13
        "--PoissonMeshing.color", "32",  # Default = 32
        "--PoissonMeshing.trim", "10",  # Default = 10
        "--PoissonMeshing.num_threads", str(multiprocessing.cpu_count())  # Use all CPU cores
    ])
    
    print(f"[COLMAP] Parameter summary:")
    print(f"[COLMAP]   • Depth: 13 (default)")
    print(f"[COLMAP]   • Color: 32 (default)")
    print(f"[COLMAP]   • Trim: 10 (default)")
    print(f"[COLMAP]   • CPU threads: {multiprocessing.cpu_count()}")
    
    print(f"[COLMAP] Mesh creation completed!")
    print(f"[COLMAP] Note: Using default parameters for maximum stability")
    
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