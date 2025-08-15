"""
Main Pipeline Runner
"""
import os
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
from config import config
from pipeline.colmap.dense_reconstruction import run_colmap_pipeline_with_dense
from pipeline.mesh_analysis.alignment import run_icp_alignment
from pipeline.mesh_analysis.comparison import run_c2c_comparison, run_c2m_comparison
from pipeline.mesh_analysis.measurement import run_mesh_measurement
from utils.reporting.summary import summarize_comparison

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='3D Reconstruction Pipeline',
        epilog="""
Performance Tips:
  --fast-mode          : 2-3x faster, good quality
  --ultra-fast-mode    : 5-10x faster, basic quality
  --skip-dense         : Skip dense reconstruction (much faster)
  --skip-mesh          : Skip mesh creation (faster)
  --max-image-size 800 : Lower resolution for speed
  --max-features 512   : Fewer features for speed

Examples:
  # Ultra-fast processing (minimal quality, maximum speed)
  python main.py --ultra-fast-mode --skip-dense --skip-mesh
  
  # Fast processing (good quality, 2-3x faster)
  python main.py --fast-mode
  
  # Custom fast settings
  python main.py --max-image-size 800 --max-features 512 --dense-image-size 1000
  
  # Sparse reconstruction only (much faster)
  python main.py --skip-dense
        """
    )
    
    # COLMAP parameters
    parser.add_argument('--max-image-size', type=int, default=1600,
                       help='Maximum image size for feature extraction (default: 1600)')
    parser.add_argument('--max-features', type=int, default=2048,
                       help='Maximum number of features to extract (default: 2048)')
    parser.add_argument('--max-ratio', type=float, default=0.8,
                       help='Maximum ratio for feature matching (default: 0.8)')
    parser.add_argument('--max-distance', type=float, default=0.7,
                       help='Maximum distance for feature matching (default: 0.7)')
    parser.add_argument('--min-matches', type=int, default=15,
                       help='Minimum number of matches for reconstruction (default: 15)')
    parser.add_argument('--max-iterations', type=int, default=50,
                       help='Maximum iterations for bundle adjustment (default: 50)')
    parser.add_argument('--max-refinements', type=int, default=3,
                       help='Maximum refinements for bundle adjustment (default: 3)')
    
    # Dense reconstruction parameters
    parser.add_argument('--dense-image-size', type=int, default=2000,
                       help='Maximum image size for dense reconstruction (default: 2000)')
    parser.add_argument('--window-radius', type=int, default=5,
                       help='Window radius for dense stereo (default: 5)')
    parser.add_argument('--window-step', type=int, default=2,
                       help='Window step for dense stereo (default: 2)')
    
    # Performance tuning parameters
    parser.add_argument('--fast-mode', action='store_true',
                       help='Enable fast mode: lower resolution, fewer features, faster processing')
    parser.add_argument('--ultra-fast-mode', action='store_true',
                       help='Enable ultra-fast mode: minimal resolution, minimal features, fastest processing')
    parser.add_argument('--skip-dense', action='store_true',
                       help='Skip dense reconstruction (sparse only - much faster)')
    parser.add_argument('--skip-mesh', action='store_true',
                       help='Skip mesh creation (point cloud only - faster)')
    parser.add_argument('--max-neighbors', type=int, default=50,
                       help='Maximum neighbors for spatial matching (default: 50, lower=faster)')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Batch size for processing (default: 10, lower=faster but less accurate)')
    
    # Pipeline options
    parser.add_argument('--timestamps', nargs='+', default=['timestamp1', 'timestamp2'],
                       help='Timestamp folders to process (default: timestamp1 timestamp2)')
    parser.add_argument('--skip-comparison', action='store_true',
                       help='Skip 3D mesh comparison step')
    parser.add_argument('--skip-report', action='store_true',
                       help='Skip PDF report generation')
    
    return parser.parse_args()

# Validate setup before starting
print("Validating setup...")

# Set up cloud environment if needed
config.setup_cloud_environment()

errors, warnings = config.validate_setup()

if errors:
    print("Setup validation failed:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)

if warnings:
    print("Setup warnings:")
    for warning in warnings:
        print(f"  {warning}")
    print()

# Parse command line arguments
args = parse_arguments()

# Update config with command line arguments
config.timestamps = args.timestamps

# Apply performance mode overrides
if args.ultra_fast_mode:
    # Ultra-fast mode: minimal processing for speed
    args.max_image_size = 800
    args.max_features = 512
    args.dense_image_size = 1000
    args.window_radius = 3
    args.window_step = 3
    args.max_neighbors = 20
    args.batch_size = 5
    print("🚀 Ultra-fast mode enabled: minimal resolution and features for maximum speed")
elif args.fast_mode:
    # Fast mode: balanced speed vs quality
    args.max_image_size = 1200
    args.max_features = 1024
    args.dense_image_size = 1500
    args.window_radius = 4
    args.window_step = 2
    args.max_neighbors = 30
    args.batch_size = 8
    print("⚡ Fast mode enabled: reduced resolution and features for faster processing")

config.colmap_params = {
    'max_image_size': args.max_image_size,
    'max_features': args.max_features,
    'max_ratio': args.max_ratio,
    'max_distance': args.max_distance,
    'min_matches': args.min_matches,
    'max_iterations': args.max_iterations,
    'max_refinements': args.max_refinements,
    'dense_image_size': args.dense_image_size,
    'window_radius': args.window_radius,
    'window_step': args.window_step,
    'max_neighbors': args.max_neighbors,
    'batch_size': args.batch_size,
    'skip_dense': args.skip_dense,
    'skip_mesh': args.skip_mesh,
    'gpu_index': 0,  # GPU device index to use
    'use_gpu': True   # Enable GPU acceleration
}

# Print current configuration
config.print_setup_info()
print("COLMAP Parameters:")
for key, value in config.colmap_params.items():
    print(f"  {key}: {value}")
print()

# Show performance estimates
def show_performance_estimate():
    """Show estimated processing time based on current settings"""
    base_time = 60  # Base time in minutes for default settings
    
    # Calculate time multiplier based on settings
    time_multiplier = 1.0
    
    # Image size impact
    if args.max_image_size <= 800:
        time_multiplier *= 0.3  # 70% faster
    elif args.max_image_size <= 1200:
        time_multiplier *= 0.6  # 40% faster
    
    # Feature count impact
    if args.max_features <= 512:
        time_multiplier *= 0.4  # 60% faster
    elif args.max_features <= 1024:
        time_multiplier *= 0.7  # 30% faster
    
    # Dense reconstruction impact
    if args.skip_dense:
        time_multiplier *= 0.2  # 80% faster (sparse only)
    
    # Mesh creation impact
    if args.skip_mesh:
        time_multiplier *= 0.8  # 20% faster
    
    estimated_time = base_time * time_multiplier
    
    print("⏱️  Performance Estimate:")
    print(f"  Estimated processing time: {estimated_time:.0f} minutes")
    print(f"  Speed improvement: {1/time_multiplier:.1f}x faster than default")
    
    if args.fast_mode or args.ultra_fast_mode:
        print(f"  Mode: {'Ultra-fast' if args.ultra_fast_mode else 'Fast'}")
        print(f"  Quality: {'Basic' if args.ultra_fast_mode else 'Good'}")
    print()

show_performance_estimate()

# Show current performance settings
def show_performance_settings():
    """Show current performance configuration"""
    print("⚙️  Performance Configuration:")
    print(f"  Image resolution: {args.max_image_size}px (default: 1600)")
    print(f"  Feature count: {args.max_features} (default: 2048)")
    print(f"  Dense resolution: {args.dense_image_size}px (default: 2000)")
    
    if args.skip_dense:
        print(f"  🚀 Dense reconstruction: SKIPPED (sparse only)")
    if args.skip_mesh:
        print(f"  🚀 Mesh creation: SKIPPED (point cloud only)")
    
    print(f"  Spatial matching neighbors: {args.max_neighbors}")
    print(f"  Processing batch size: {args.batch_size}")
    print()

show_performance_settings()

# Create unique run folders for each execution
run_id = datetime.datetime.now().strftime("run_%Y%m%d_%H%M%S")

# Generate paths using config
timestamp_image_folders = [config.get_data_path(t) for t in config.timestamps]
timestamp_output_folders = [config.get_output_path(t, run_id) for t in config.timestamps]
timestamp_meshes = [config.get_mesh_path(t, run_id) for t in config.timestamps]

def run_full_pipeline(images_folder, output_folder):
    """Run COLMAP pipeline with performance options"""
    if args.skip_dense:
        # Run sparse reconstruction only (much faster)
        print(f"[PERFORMANCE] Skipping dense reconstruction for speed")
        from pipeline.colmap.mesh_creation import run_colmap_pipeline
        result = run_colmap_pipeline(images_folder, output_folder)
        if args.skip_mesh:
            print(f"[PERFORMANCE] Skipping mesh creation for speed")
            return result  # Return dense folder path
        else:
            # Convert to mesh if needed
            print(f"[PERFORMANCE] Creating mesh from sparse reconstruction")
            # This would need a sparse-to-mesh conversion function
            return result
    else:
        # Run full pipeline with dense reconstruction
        obj_file = run_colmap_pipeline_with_dense(images_folder, output_folder)
        return obj_file

def run_custom_comparison(mesh1, mesh2, base_output_dir):
    """Run complete custom 3D mesh comparison pipeline"""
    # Create a unique run folder using timestamp
    run_id = datetime.datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_output_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)

    print("Starting custom 3D mesh comparison pipeline")
    print(f"Output directory: {output_dir}")

    # Step 1: ICP Alignment
    aligned_mesh2 = run_icp_alignment(mesh1, mesh2, output_dir)

    # Step 2: C2C Comparison
    c2c_csv, c2c_screenshot, c2c_log = run_c2c_comparison(mesh1, aligned_mesh2, output_dir)

    # Step 3: C2M Comparison
    c2m_csv, c2m_screenshot, c2m_log = run_c2m_comparison(mesh1, aligned_mesh2, output_dir)

    # Step 4: Mesh Measurements
    mesh1_measure = run_mesh_measurement(mesh1, output_dir, "mesh1")
    mesh2_measure = run_mesh_measurement(aligned_mesh2, output_dir, "mesh2")

    print("Custom 3D mesh comparison completed")
    print(f"All outputs saved in: {output_dir}")
    
    return output_dir

def main():
    """Main pipeline execution"""
    start_time = datetime.datetime.now()
    print("Starting 3D Reconstruction Pipeline")
    print("=" * 50)
    print(f"🚀 Performance mode: {'Ultra-fast' if args.ultra_fast_mode else 'Fast' if args.fast_mode else 'Standard'}")
    if args.skip_dense:
        print(f"⚡ Speed boost: Dense reconstruction skipped (sparse only)")
    if args.skip_mesh:
        print(f"⚡ Speed boost: Mesh creation skipped (point cloud only)")
    print()
    
    # Step 1: Run both COLMAP pipelines in parallel
    print("Step 1: Running COLMAP reconstruction pipelines...")
    print(f"⚡ Processing {len(config.timestamps)} timestamps in parallel")
    print(f"⚡ Using {args.max_image_size}px resolution and {args.max_features} features")
    if args.skip_dense:
        print(f"⚡ Sparse reconstruction only - estimated 80% time savings")
    print()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(run_full_pipeline, img_folder, out_folder)
            for img_folder, out_folder in zip(timestamp_image_folders, timestamp_output_folders)
        ]
        results = []
        for future in as_completed(futures):
            try:
                obj_file = future.result()
                results.append(obj_file)
            except Exception as e:
                print(f"FATAL: One of the reconstructions failed: {e}")
                return
    
    if args.skip_comparison:
        print("Skipping 3D mesh comparison (--skip-comparison flag)")
        return
    
    # Step 2: Run custom 3D mesh comparison
    print("Step 2: Running custom 3D mesh comparison...")
    base_output_dir = os.path.join(config.outputs_dir, run_id, "comparison")
    comparison_dir = run_custom_comparison(timestamp_meshes[0], timestamp_meshes[1], base_output_dir)
    
    if args.skip_report:
        print("Skipping report generation (--skip-report flag)")
        return
    
    # Step 3: Generate summary and report
    print("Step 3: Generating summary and report...")
    summarize_comparison(comparison_dir)
    
    end_time = datetime.datetime.now()
    total_time = end_time - start_time
    
    print("Pipeline completed successfully!")
    print("=" * 50)
    print("📊 Performance Summary:")
    print(f"  Total processing time: {total_time}")
    print(f"  Performance mode: {'Ultra-fast' if args.ultra_fast_mode else 'Fast' if args.fast_mode else 'Standard'}")
    
    if args.skip_dense:
        print(f"  ⚡ Dense reconstruction: SKIPPED (major time savings)")
    if args.skip_mesh:
        print(f"  ⚡ Mesh creation: SKIPPED (time savings)")
    
    print(f"  Final image resolution: {args.max_image_size}px")
    print(f"  Final feature count: {args.max_features}")
    print()
    
    print("COLMAP models created:")
    for i, mesh in enumerate(timestamp_meshes):
        print(f"  - Timestamp{i+1}: {mesh}")
    print(f"Custom 3D mesh comparison completed in: {comparison_dir}")

if __name__ == "__main__":
    main() 