"""
Main Pipeline Runner
"""
import os
import sys
import argparse
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
    
    # No additional arguments needed - speed optimizations are built into COLMAP functions
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

# Use basic COLMAP parameters
config.colmap_params = {
    'gpu_index': 0,              # GPU device index to use
    'use_gpu': True              # Enable GPU acceleration
}

# Update timestamps config
config.timestamps = ['timestamp1', 'timestamp2'] # Default to two timestamps

# Print current configuration
config.print_setup_info()
print("COLMAP Parameters:")
for key, value in config.colmap_params.items():
    print(f"  {key}: {value}")
print()
print("🚀 COLMAP pipeline configuration:")
print("   - Feature extraction: Basic with defaults")
print("   - Feature matching: Basic with defaults")
print("   - Sparse reconstruction: Basic with defaults")
print("   - Dense reconstruction: Basic with defaults")
print("   - Stereo fusion: Basic with defaults")
print("   - Poisson meshing: Basic with defaults")
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
    
    # Step 1: Run COLMAP pipelines sequentially (better for single GPU)
    print("Step 1: Running COLMAP reconstruction pipelines sequentially...")
    results = []
    
    # Process timestamp1 first
    print(f"Processing {config.timestamps[0]}...")
    try:
        obj_file1 = run_full_pipeline(timestamp_image_folders[0], timestamp_output_folders[0])
        results.append(obj_file1)
        print(f"✅ {config.timestamps[0]} completed successfully")
    except Exception as e:
        print(f"❌ {config.timestamps[0]} failed: {e}")
        return
    
    # Process timestamp2 second
    print(f"Processing {config.timestamps[1]}...")
    try:
        obj_file2 = run_full_pipeline(timestamp_image_folders[1], timestamp_output_folders[1])
        results.append(obj_file2)
        print(f"✅ {config.timestamps[1]} completed successfully")
    except Exception as e:
        print(f"❌ {config.timestamps[1]} failed: {e}")
        return
    
    print("✅ Both COLMAP pipelines completed successfully")
    
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
        print(f"  - {config.timestamps[i]}: {mesh}")
    print(f"Custom 3D mesh comparison completed in: {comparison_dir}")
    
    # Show final status
    print("\n🚀 Pipeline completed successfully!")
    print("   - Feature extraction: Basic with defaults")
    print("   - Feature matching: Basic with defaults")
    print("   - Sparse reconstruction: Basic with defaults")
    print("   - Dense reconstruction: Basic with defaults")
    print("   - Stereo fusion: Basic with defaults")
    print("   - Poisson meshing: Basic with defaults")
    print("   - GPU acceleration: Auto-detected")
    print("   - Quality maintained for 3D mapping applications")

if __name__ == "__main__":
    main() 