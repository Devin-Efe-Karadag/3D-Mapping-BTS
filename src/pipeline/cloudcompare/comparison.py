"""
CloudCompare Comparison Module
"""
import os
import subprocess
from config import config

def run_c2c_comparison(mesh1, aligned_mesh2, output_dir):
    """Run Cloud-to-Cloud distance comparison"""
    print("Running C2C distance comparison")
    
    # Use config for CloudCompare path
    cloudcompare_cmd = config.cloudcompare_path
    if not cloudcompare_cmd:
        raise RuntimeError("CloudCompare not found. Please install CloudCompare.")
    
    # C2C distance comparison
    c2c_csv = os.path.join(output_dir, "cloudcompare_c2c_distances.csv")
    c2c_screenshot = os.path.join(output_dir, "cloudcompare_c2c_screenshot.png")
    c2c_log = os.path.join(output_dir, "cloudcompare_c2c_report.txt")
    
    subprocess.run([
        cloudcompare_cmd, "-SILENT",
        "-O", mesh1,
        "-O", aligned_mesh2,
        "-C2C_DIST",
        "-SF_STATISTICS",
        "-C_EXPORT_FMT", "CSV",
        "-C_EXPORT_PATH", c2c_csv,
        "-SS", c2c_screenshot,
        "-LOG_FILE", c2c_log,
        "-NO_TIMESTAMP"
    ], capture_output=True, text=True)
    
    print("C2C comparison completed")
    print(f"  - CSV: {c2c_csv}")
    print(f"  - Screenshot: {c2c_screenshot}")
    print(f"  - Log: {c2c_log}")
    
    return c2c_csv, c2c_screenshot, c2c_log

def run_c2m_comparison(mesh1, aligned_mesh2, output_dir):
    """Run Cloud-to-Mesh distance comparison (signed)"""
    print("Running C2M distance comparison")
    
    # Use config for CloudCompare path
    cloudcompare_cmd = config.cloudcompare_path
    if not cloudcompare_cmd:
        raise RuntimeError("CloudCompare not found. Please install CloudCompare.")
    
    # C2M distance comparison (signed)
    c2m_csv = os.path.join(output_dir, "cloudcompare_c2m_distances.csv")
    c2m_screenshot = os.path.join(output_dir, "cloudcompare_c2m_screenshot.png")
    c2m_log = os.path.join(output_dir, "cloudcompare_c2m_report.txt")
    
    subprocess.run([
        cloudcompare_cmd, "-SILENT",
        "-O", mesh1,
        "-O", aligned_mesh2,
        "-C2M_DIST", "-SIGNED",
        "-SF_STATISTICS",
        "-C_EXPORT_FMT", "CSV",
        "-C_EXPORT_PATH", c2m_csv,
        "-SS", c2m_screenshot,
        "-LOG_FILE", c2m_log,
        "-NO_TIMESTAMP"
    ], capture_output=True, text=True)
    
    print("C2M comparison completed")
    print(f"  - CSV: {c2m_csv}")
    print(f"  - Screenshot: {c2m_screenshot}")
    print(f"  - Log: {c2m_log}")
    
    return c2m_csv, c2m_screenshot, c2m_log 