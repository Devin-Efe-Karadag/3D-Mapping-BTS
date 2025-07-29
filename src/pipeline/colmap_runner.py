# Moved to src/pipeline/colmap_runner.py as part of project restructuring
import os
import subprocess
import sys

def run_cmd(cmd, cwd=None):
    print(f"[COLMAP] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[COLMAP][ERROR] Command failed: {' '.join(cmd)}\n{result.stderr}")
        sys.exit(result.returncode)
    return result

def feature_extraction(database_path, images_folder):
    run_cmd([
        "colmap", "feature_extractor",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--ImageReader.camera_model", "PINHOLE"
    ])

def exhaustive_matching(database_path):
    run_cmd([
        "colmap", "exhaustive_matcher",
        "--database_path", database_path
    ])

def mapping(database_path, images_folder, sparse_folder):
    os.makedirs(sparse_folder, exist_ok=True)
    run_cmd([
        "colmap", "mapper",
        "--database_path", database_path,
        "--image_path", images_folder,
        "--output_path", sparse_folder
    ])

def model_conversion(sparse_folder):
    run_cmd([
        "colmap", "model_converter",
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", sparse_folder,
        "--output_type", "TXT"
    ])

def image_undistortion(images_folder, sparse_folder, dense_folder):
    os.makedirs(dense_folder, exist_ok=True)
    run_cmd([
        "colmap", "image_undistorter",
        "--image_path", images_folder,
        "--input_path", os.path.join(sparse_folder, "0"),
        "--output_path", dense_folder,
        "--output_type", "COLMAP"
    ])

def run_colmap_pipeline(images_folder, output_folder):
    database_path = os.path.join(output_folder, "database.db")
    sparse_folder = os.path.join(output_folder, "sparse")
    dense_folder = os.path.join(output_folder, "dense")
    feature_extraction(database_path, images_folder)
    exhaustive_matching(database_path)
    mapping(database_path, images_folder, sparse_folder)
    model_conversion(sparse_folder)
    image_undistortion(images_folder, sparse_folder, dense_folder)
    print(f"[COLMAP] Pipeline complete for {images_folder}")
    return dense_folder 