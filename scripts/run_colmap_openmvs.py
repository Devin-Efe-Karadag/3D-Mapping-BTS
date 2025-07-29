import os
import sys
import subprocess

def run_cmd(cmd, cwd=None):
    print(f"[INFO] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed: {' '.join(cmd)}\n{result.stderr}")
        sys.exit(result.returncode)
    return result

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_colmap_openmvs.py <images_folder> <output_folder>")
        sys.exit(1)
    images_folder = os.path.abspath(sys.argv[1])
    output_folder = os.path.abspath(sys.argv[2])
    os.makedirs(output_folder, exist_ok=True)
    database_path = os.path.join(output_folder, "database.db")
    sparse_folder = os.path.join(output_folder, "sparse")
    dense_folder = os.path.join(output_folder, "dense")
    # 1. COLMAP feature extraction
    run_cmd([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--ImageReader.camera_model", "PINHOLE"
    ])
    # 2. COLMAP matching
    run_cmd([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ])
    # 3. COLMAP mapping
    os.makedirs(sparse_folder, exist_ok=True)
    run_cmd([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--output_path", sparse_folder
    ])
    # 4. COLMAP model_converter (to TXT)
    run_cmd([
        "colmap", "model_converter",
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", sparse_folder,
        "--output_type", "TXT"
    ])
    # 5. COLMAP image_undistorter
    os.makedirs(dense_folder, exist_ok=True)
    run_cmd([
        "colmap", "image_undistorter",
        "--image_path", images_folder,
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", dense_folder,
        "--output_type", "COLMAP"
    ])
    # 6. OpenMVS: InterfaceCOLMAP
    run_cmd([
        "InterfaceCOLMAP",
        "--working-folder", output_folder,
        "--input-file", os.path.join(dense_folder),
        "--output-file", os.path.join(output_folder, "model_colmap.mvs")
    ])
    # 7. OpenMVS: DensifyPointCloud
    run_cmd([
        "DensifyPointCloud",
        "--input-file", os.path.join(output_folder, "model_colmap.mvs"),
        "--working-folder", output_folder,
        "--output-file", os.path.join(output_folder, "model_dense.mvs"),
        "--archive-type", "-1"
    ])
    # 8. OpenMVS: ReconstructMesh
    run_cmd([
        "ReconstructMesh",
        "--input-file", os.path.join(output_folder, "model_dense.mvs"),
        "--working-folder", output_folder,
        "--output-file", os.path.join(output_folder, "model_dense_mesh.mvs")
    ])
    # 9. OpenMVS: RefineMesh
    run_cmd([
        "RefineMesh",
        "--resolution-level", "1",
        "--input-file", os.path.join(output_folder, "model_dense_mesh.mvs"),
        "--working-folder", output_folder,
        "--output-file", os.path.join(output_folder, "model_dense_mesh_refine.mvs")
    ])
    # 10. OpenMVS: TextureMesh
    run_cmd([
        "TextureMesh",
        "--export-type", "obj",
        "--output-file", os.path.join(output_folder, "model.obj"),
        "--working-folder", output_folder,
        "--input-file", os.path.join(output_folder, "model_dense_mesh_refine.mvs")
    ])
    print(f"[INFO] Finished pipeline for {images_folder}. Final model at {os.path.join(output_folder, 'model.obj')}")

if __name__ == "__main__":
    main() 