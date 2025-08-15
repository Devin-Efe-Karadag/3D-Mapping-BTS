"""
Custom ICP Alignment Module
"""
import os
import numpy as np
import open3d as o3d
from config import config

def run_icp_alignment(mesh1, mesh2, output_dir):
    """Align mesh2 to mesh1 using ICP"""
    print("Starting ICP alignment using custom implementation")
    
    try:
        # Load meshes using Open3D
        mesh1_o3d = o3d.io.read_triangle_mesh(mesh1)
        mesh2_o3d = o3d.io.read_triangle_mesh(mesh2)
        
        # Convert meshes to point clouds for ICP
        # Sample points from mesh surfaces
        mesh1_pcd = mesh1_o3d.sample_points_uniformly(number_of_points=10000)
        mesh2_pcd = mesh2_o3d.sample_points_uniformly(number_of_points=10000)
        
        # Estimate normals for better alignment
        mesh1_pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        mesh2_pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
        
        # Run ICP alignment
        print("Running ICP alignment...")
        icp_result = o3d.pipelines.registration.registration_icp(
            mesh2_pcd, mesh1_pcd, 
            max_correspondence_distance=0.05,
            init=np.eye(4),
            estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(),
            criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100)
        )
        
        # Apply transformation to mesh2
        mesh2_o3d.transform(icp_result.transformation)
        
        # Save aligned mesh
        aligned_mesh_path = os.path.join(output_dir, "mesh2_aligned.obj")
        o3d.io.write_triangle_mesh(aligned_mesh_path, mesh2_o3d)
        
        # Save transformation matrix for reference
        transform_path = os.path.join(output_dir, "icp_transformation.txt")
        np.savetxt(transform_path, icp_result.transformation, 
                   header="ICP Transformation Matrix (4x4)")
        
        print(f"ICP alignment completed successfully")
        print(f"  - Fitness: {icp_result.fitness:.6f}")
        print(f"  - RMSE: {icp_result.inlier_rmse:.6f}")
        print(f"  - Aligned mesh: {aligned_mesh_path}")
        print(f"  - Transformation: {transform_path}")
        
        return aligned_mesh_path
        
    except Exception as e:
        print(f"ICP alignment failed: {e}")
        print("Using original mesh2")
        return mesh2 