# Moved to src/pipeline/openmvs_runner.py as part of project restructuring
import os
import subprocess
import sys

def run_cmd(cmd, cwd=None):
    print(f"[OpenMVS] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[OpenMVS][ERROR] Command failed: {' '.join(cmd)}\n{result.stderr}")
        sys.exit(result.returncode)
    return result

def interface_colmap(dense_folder, output_folder):
    run_cmd([
        "InterfaceCOLMAP",
        "--working-folder", output_folder,
        "--input-file", dense_folder,
        "--output-file", os.path.join(output_folder, "model_colmap.mvs")
    ])
    return os.path.join(output_folder, "model_colmap.mvs")

def densify_point_cloud(mvs_file, output_folder):
    run_cmd([
        "DensifyPointCloud",
        "--input-file", mvs_file,
        "--working-folder", output_folder,
        "--output-file", os.path.join(output_folder, "model_dense.mvs"),
        "--archive-type", "-1"
    ])
    return os.path.join(output_folder, "model_dense.mvs")

def reconstruct_mesh(dense_mvs_file, output_folder):
    run_cmd([
        "ReconstructMesh",
        "--input-file", dense_mvs_file,
        "--working-folder", output_folder,
        "--output-file", os.path.join(output_folder, "model_dense_mesh.mvs")
    ])
    return os.path.join(output_folder, "model_dense_mesh.mvs")

def refine_mesh(mesh_mvs_file, output_folder):
    run_cmd([
        "RefineMesh",
        "--resolution-level", "1",
        "--input-file", mesh_mvs_file,
        "--working-folder", output_folder,
        "--output-file", os.path.join(output_folder, "model_dense_mesh_refine.mvs")
    ])
    return os.path.join(output_folder, "model_dense_mesh_refine.mvs")

def texture_mesh(refined_mesh_file, output_folder):
    run_cmd([
        "TextureMesh",
        "--export-type", "obj",
        "--output-file", os.path.join(output_folder, "model.obj"),
        "--working-folder", output_folder,
        "--input-file", refined_mesh_file
    ])
    return os.path.join(output_folder, "model.obj")

def run_openmvs_pipeline(dense_folder, output_folder):
    mvs_file = interface_colmap(dense_folder, output_folder)
    dense_mvs_file = densify_point_cloud(mvs_file, output_folder)
    mesh_mvs_file = reconstruct_mesh(dense_mvs_file, output_folder)
    refined_mesh_file = refine_mesh(mesh_mvs_file, output_folder)
    obj_file = texture_mesh(refined_mesh_file, output_folder)
    print(f"[OpenMVS] Pipeline complete for {dense_folder}. OBJ: {obj_file}")
    return obj_file 