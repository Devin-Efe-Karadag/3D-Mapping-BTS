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

timestamp_image_folders = [os.path.join(DATA_DIR, t, "images") for t in TIMESTAMPS]
timestamp_output_folders = [os.path.join(OUTPUTS_DIR, t) for t in TIMESTAMPS]
timestamp_meshes = [os.path.join(OUTPUTS_DIR, t, "model.obj") for t in TIMESTAMPS]

def run_full_pipeline(images_folder, output_folder):
    # Run COLMAP pipeline
    dense_folder = colmap_runner.run_colmap_pipeline(images_folder, output_folder)
    # Run OpenMVS pipeline
    obj_file = openmvs_runner.run_openmvs_pipeline(dense_folder, output_folder)
    return obj_file

def run_icp_alignment(mesh1, mesh2, output_dir):
    """
    Align mesh2 to mesh1 using ICP and return the path to the aligned mesh2.
    """
    icp_log = os.path.join(output_dir, "icp_log.txt")
    cmd = [
        CLOUDCOMPARE_CLI, "-SILENT",
        "-O", mesh1,
        "-O", mesh2,
        "-ICP",
        "-SAVE_MESHES",
        "-LOG_FILE", icp_log,
        "-NO_TIMESTAMP"
    ]
    print(f"[INFO] Running ICP alignment...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] ICP alignment failed:\n{result.stderr}")
        return mesh2, icp_log
    # Find the aligned mesh filename (CloudCompare usually appends _REGISTERED)
    registered_mesh = None
    for fname in os.listdir(output_dir):
        if fname.endswith("_REGISTERED.obj"):
            registered_mesh = os.path.join(output_dir, fname)
    if not registered_mesh:
        # Fallback: try mesh2 with _REGISTERED appended
        base, ext = os.path.splitext(mesh2)
        registered_mesh = base + "_REGISTERED" + ext
        if not os.path.exists(registered_mesh):
            registered_mesh = mesh2  # fallback to original
    print(f"[INFO] ICP alignment complete. Aligned mesh: {registered_mesh}")
    return registered_mesh, icp_log

def run_cloudcompare(mesh1, mesh2, base_output_dir):
    # Create a unique run folder using timestamp
    run_id = datetime.datetime.now().strftime("run_%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_output_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: ICP alignment
    aligned_mesh2, icp_log = run_icp_alignment(mesh1, mesh2, output_dir)

    # Step 2: C2C DISTANCE
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

    # Step 3: C2M DISTANCE (signed)
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

    # Step 4: MESH MEASURE (area/volume)
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
    print(f"  - ICP log: {icp_log}")
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