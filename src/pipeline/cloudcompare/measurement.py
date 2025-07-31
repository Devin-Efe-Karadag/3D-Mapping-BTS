"""
CloudCompare Mesh Measurement Module
"""
import os
import subprocess
from config import config

def run_mesh_measurement(mesh_path, output_dir, mesh_name):
    """Measure area and volume of a mesh"""
    print(f"Measuring {mesh_name}")
    
    # Use config for CloudCompare path
    cloudcompare_cmd = config.cloudcompare_path
    if not cloudcompare_cmd:
        raise RuntimeError("CloudCompare not found. Please install CloudCompare.")
    
    # Mesh measurement
    measure_file = os.path.join(output_dir, f"{mesh_name}_measure.txt")
    
    subprocess.run([
        cloudcompare_cmd, "-SILENT", 
        "-O", mesh_path, 
        "-MESH_MEASURE", 
        "-LOG_FILE", measure_file, 
        "-NO_TIMESTAMP"
    ], capture_output=True, text=True)
    
    print(f"{mesh_name} measurement completed: {measure_file}")
    return measure_file 