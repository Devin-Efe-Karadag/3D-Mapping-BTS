"""
CloudCompare ICP Alignment Module
"""
import os
import subprocess
from config import config

def run_icp_alignment(mesh1, mesh2, output_dir):
    """Align mesh2 to mesh1 using ICP"""
    print("Starting ICP alignment")
    
    # Use config for CloudCompare path
    cloudcompare_cmd = config.cloudcompare_path
    if not cloudcompare_cmd:
        raise RuntimeError("CloudCompare not found. Please install CloudCompare.")
    
    # Run ICP alignment
    subprocess.run([
        cloudcompare_cmd, "-SILENT",
        "-O", mesh1,
        "-O", mesh2,
        "-ICP",
        "-SAVE_MESHES",
        "-NO_TIMESTAMP"
    ], capture_output=True, text=True)
    
    # Find the aligned mesh file
    aligned_mesh2 = None
    for f in os.listdir(output_dir):
        if f.endswith('.obj') and 'REGISTERED' in f:
            aligned_mesh2 = os.path.join(output_dir, f)
            break
    
    if not aligned_mesh2:
        print("Could not find aligned mesh, using original mesh2")
        aligned_mesh2 = mesh2
    else:
        print(f"ICP alignment completed: {aligned_mesh2}")
    
    return aligned_mesh2 