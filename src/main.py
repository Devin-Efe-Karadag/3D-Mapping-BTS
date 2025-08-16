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
    parser = argparse.ArgumentParser(description='3D Reconstruction Pipeline')
    
    # Pipeline modes
    parser.add_argument('--fast-mode', action='store_true',
                       help='Run in fast mode with lower resolution for faster processing')
    
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

# Apply fast mode if requested
if args.fast_mode:
    print("🚀 Fast mode enabled - using lower resolution for faster processing")
    # Override parameters with fast mode values
    fast_mode_params = {
        'max_image_size': 800,      # Lower resolution for feature extraction
        'max_features': 1024,       # Fewer features for faster processing
        'max_ratio': 0.9,           # More permissive matching
        'max_distance': 1.0,        # More permissive matching
        'min_matches': 10,          # Lower threshold for reconstruction
        'max_iterations': 25,       # Fewer iterations for faster convergence
        'max_refinements': 2,       # Fewer refinements
        'dense_image_size': 1000,   # Lower resolution for dense reconstruction
        'window_radius': 3,         # Smaller window for faster stereo
        'window_step': 1,           # Smaller step for faster stereo
        'gpu_index': 0,             # GPU device index to use
        'use_gpu': True             # Enable GPU acceleration
    }
    config.colmap_params = fast_mode_params
    print("Fast mode parameters applied:")
    for key, value in fast_mode_params.items():
        print(f"  {key}: {value}")
    print()
else:
    # Use command line arguments for normal mode
    config.colmap_params = {
        'max_image_size': 1600,
        'max_features': 2048,
        'max_ratio': 0.8,
        'max_distance': 0.7,
        'min_matches': 15,
        'max_iterations': 50,
        'max_refinements': 3,
        'dense_image_size': 2000,
        'window_radius': 5,
        'window_step': 2,
        'gpu_index': 0,  # GPU device index to use
        'use_gpu': True   # Enable GPU acceleration
    }

# Update timestamps config
config.timestamps = ['timestamp1', 'timestamp2'] # Default to two timestamps

# Print current configuration
config.print_setup_info()
print("COLMAP Parameters:")
for key, value in config.colmap_params.items():
    print(f"  {key}: {value}")
print()

# Create unique run folders for each execution
run_id = datetime.datetime.now().strftime("run_%Y%m%d_%H%M%S")

# Generate paths using config
timestamp_image_folders = [config.get_data_path(t) for t in config.timestamps]
timestamp_output_folders = [config.get_output_path(t, run_id) for t in config.timestamps]
timestamp_meshes = [config.get_mesh_path(t, run_id) for t in config.timestamps]

def run_full_pipeline(images_folder, output_folder):
    """Run COLMAP pipeline (including dense reconstruction)"""
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
    print("Starting 3D Reconstruction Pipeline")
    print("=" * 50)
    
    # Step 1: Run both COLMAP pipelines in parallel
    print("Step 1: Running COLMAP reconstruction pipelines...")
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
    
    # Step 2: Run custom 3D mesh comparison
    print("Step 2: Running custom 3D mesh comparison...")
    base_output_dir = os.path.join(config.outputs_dir, run_id, "comparison")
    comparison_dir = run_custom_comparison(timestamp_meshes[0], timestamp_meshes[1], base_output_dir)
    
    # Step 3: Generate summary and report
    print("Step 3: Generating summary and report...")
    summarize_comparison(comparison_dir)
    
    print("Pipeline completed successfully!")
    print("COLMAP models created:")
    for i, mesh in enumerate(timestamp_meshes):
        print(f"  - Timestamp{i+1}: {mesh}")
    print(f"Custom 3D mesh comparison completed in: {comparison_dir}")
    
    # Show final mode and parameters
    if args.fast_mode:
        print("\n🚀 Pipeline completed in FAST MODE")
        print("   - Lower resolution for faster processing")
        print("   - All functionality preserved")
        print("   - Use without --fast-mode for higher quality")
    else:
        print("\n📊 Pipeline completed in STANDARD MODE")
        print("   - Standard resolution and quality")
        print("   - Use --fast-mode for faster processing")

if __name__ == "__main__":
    main() 