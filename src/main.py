# Moved to src/main.py as part of project restructuring
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pipeline import colmap_runner, openmvs_runner
import subprocess
import datetime
from utils.inference import summarize_comparison

# Configurable paths (for now, hardcoded)
TIMESTAMPS = ["timestamp1", "timestamp2"]
DATA_DIR = "data"
OUTPUTS_DIR = "outputs"
CLOUDCOMPARE_CLI = "cloudcompare"  # or full path if needed

# Ensure we're running from the correct directory (src/)
if not os.path.exists(DATA_DIR):
    print(f"[ERROR] Data directory '{DATA_DIR}' not found. Make sure you're running from the src/ directory.")
    sys.exit(1)

# Images are directly in timestamp/images/
timestamp_image_folders = [os.path.join(DATA_DIR, t, "images") for t in TIMESTAMPS]
timestamp_output_folders = [os.path.join(OUTPUTS_DIR, t) for t in TIMESTAMPS]
timestamp_meshes = [os.path.join(OUTPUTS_DIR, t, "model.obj") for t in TIMESTAMPS]

def run_full_pipeline(images_folder, output_folder):
    # Run COLMAP pipeline
    dense_folder = colmap_runner.run_colmap_pipeline(images_folder, output_folder)
    # Run OpenMVS pipeline
    obj_file = openmvs_runner.run_openmvs_pipeline(dense_folder, output_folder)
    return obj_file

def run_cloudcompare(mesh1, mesh2, base_output_dir):
    # Create a unique run folder using timestamp
    run_id = datetime.datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_output_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)

    # --- ICP ALIGNMENT ---
    # Align mesh2 to mesh1 using ICP
    subprocess.run([
        CLOUDCOMPARE_CLI, "-SILENT",
        "-O", mesh1,
        "-O", mesh2,
        "-ICP",
        "-SAVE_MESHES",
        "-NO_TIMESTAMP"
    ], capture_output=True, text=True)
    # The aligned mesh2 will be saved as mesh2_REGISTERED.obj or similar
    # We need to find the aligned mesh file
    aligned_mesh2 = None
    for f in os.listdir(output_dir):
        if f.endswith('.obj') and 'REGISTERED' in f:
            aligned_mesh2 = os.path.join(output_dir, f)
            break
    if not aligned_mesh2:
        print(f"[WARNING] Could not find aligned mesh, using original mesh2")
        aligned_mesh2 = mesh2

    # --- C2C DISTANCE ---
    c2c_csv = os.path.join(output_dir, "cloudcompare_c2c_distances.csv")
    c2c_screenshot = os.path.join(output_dir, "cloudcompare_c2c_screenshot.png")
    c2c_log = os.path.join(output_dir, "cloudcompare_c2c_report.txt")
    subprocess.run([
        CLOUDCOMPARE_CLI, "-SILENT",
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

    # --- C2M DISTANCE (signed) ---
    c2m_csv = os.path.join(output_dir, "cloudcompare_c2m_distances.csv")
    c2m_screenshot = os.path.join(output_dir, "cloudcompare_c2m_screenshot.png")
    c2m_log = os.path.join(output_dir, "cloudcompare_c2m_report.txt")
    subprocess.run([
        CLOUDCOMPARE_CLI, "-SILENT",
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

    # --- MESH MEASURE (area/volume) ---
    mesh1_measure = os.path.join(output_dir, "mesh1_measure.txt")
    mesh2_measure = os.path.join(output_dir, "mesh2_measure.txt")
    subprocess.run([
        CLOUDCOMPARE_CLI, "-SILENT", "-O", mesh1, "-MESH_MEASURE", "-LOG_FILE", mesh1_measure, "-NO_TIMESTAMP"], capture_output=True, text=True)
    subprocess.run([
        CLOUDCOMPARE_CLI, "-SILENT", "-O", aligned_mesh2, "-MESH_MEASURE", "-LOG_FILE", mesh2_measure, "-NO_TIMESTAMP"], capture_output=True, text=True)

    print(f"[INFO] CloudCompare comparison completed. All outputs saved in: {output_dir}")
    print(f"  - C2C distances CSV: {c2c_csv}")
    print(f"  - C2C screenshot: {c2c_screenshot}")
    print(f"  - C2C log: {c2c_log}")
    print(f"  - C2M distances CSV: {c2m_csv}")
    print(f"  - C2M screenshot: {c2m_screenshot}")
    print(f"  - C2M log: {c2m_log}")
    print(f"  - Mesh1 area/volume: {mesh1_measure}")
    print(f"  - Mesh2 area/volume: {mesh2_measure}")
    return output_dir

def main():
    # Step 1: Run both pipelines in parallel
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
                print(f"[FATAL] One of the reconstructions failed: {e}")
                return
    # Step 2: Run CloudCompare
    base_output_dir = os.path.join("outputs", "comparison")
    run_dir = run_cloudcompare(timestamp_meshes[0], timestamp_meshes[1], base_output_dir)
    # Step 3: Summarize and interpret results (moved to utils.inference)
    summarize_comparison(run_dir)

if __name__ == "__main__":
    main() 