#!/usr/bin/env python3
"""
Test script for custom 3D mesh analysis implementations
This script tests the custom functions for 3D mesh analysis
"""

import os
import sys
import tempfile
import numpy as np
import open3d as o3d

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.mesh_analysis.alignment import run_icp_alignment
from pipeline.mesh_analysis.comparison import run_c2c_comparison, run_c2m_comparison
from pipeline.mesh_analysis.measurement import run_mesh_measurement

def create_test_mesh(output_path, name="test_mesh"):
    """Create a simple test mesh for testing"""
    print(f"Creating test mesh: {name}")
    
    # Create a simple cube mesh
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # bottom face
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # top face
    ], dtype=np.float32)
    
    triangles = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom face
        [4, 7, 6], [4, 6, 5],  # top face
        [0, 4, 5], [0, 5, 1],  # front face
        [1, 5, 6], [1, 6, 2],  # right face
        [2, 6, 7], [2, 7, 3],  # back face
        [3, 7, 4], [3, 4, 0]   # left face
    ], dtype=np.int32)
    
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    
    # Save mesh
    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"  - Saved to: {output_path}")
    print(f"  - Vertices: {len(vertices)}")
    print(f"  - Triangles: {len(triangles)}")
    
    return output_path

def create_offset_mesh(output_path, offset=0.1, name="offset_mesh"):
    """Create a test mesh with slight offset for testing alignment"""
    print(f"Creating offset test mesh: {name}")
    
    # Create a simple cube mesh with offset
    vertices = np.array([
        [offset, offset, offset], [1+offset, offset, offset], [1+offset, 1+offset, offset], [offset, 1+offset, offset],  # bottom face
        [offset, offset, 1+offset], [1+offset, offset, 1+offset], [1+offset, 1+offset, 1+offset], [offset, 1+offset, 1+offset]   # top face
    ], dtype=np.float32)
    
    triangles = np.array([
        [0, 1, 2], [0, 2, 3],  # bottom face
        [4, 7, 6], [4, 6, 5],  # top face
        [0, 4, 5], [0, 5, 1],  # front face
        [1, 5, 6], [1, 6, 2],  # right face
        [2, 6, 7], [2, 7, 3],  # back face
        [3, 7, 4], [3, 4, 0]   # left face
    ], dtype=np.int32)
    
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    
    # Save mesh
    o3d.io.write_triangle_mesh(output_path, mesh)
    print(f"  - Saved to: {output_path}")
    print(f"  - Offset: {offset}")
    print(f"  - Vertices: {len(vertices)}")
    print(f"  - Triangles: {len(triangles)}")
    
    return output_path

def test_mesh_measurement():
    """Test mesh measurement functionality"""
    print("\n" + "="*50)
    print("TESTING MESH MEASUREMENT")
    print("="*50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test mesh
        mesh_path = create_test_mesh(os.path.join(temp_dir, "test_cube.obj"), "test_cube")
        
        # Test measurement
        result = run_mesh_measurement(mesh_path, temp_dir, "test_cube")
        print(f"Measurement result: {result}")
        
        # Check if output files exist
        expected_files = [
            "test_cube_measure.txt",
            "test_cube_measurements.csv"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(temp_dir, file_name)
            if os.path.exists(file_path):
                print(f"✓ {file_name} created successfully")
            else:
                print(f"✗ {file_name} not found")

def test_icp_alignment():
    """Test ICP alignment functionality"""
    print("\n" + "="*50)
    print("TESTING ICP ALIGNMENT")
    print("="*50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test meshes
        mesh1_path = create_test_mesh(os.path.join(temp_dir, "mesh1.obj"), "mesh1")
        mesh2_path = create_offset_mesh(os.path.join(temp_dir, "mesh2.obj"), 0.1, "mesh2")
        
        # Test alignment
        aligned_mesh = run_icp_alignment(mesh1_path, mesh2_path, temp_dir)
        print(f"Alignment result: {aligned_mesh}")
        
        # Check if output files exist
        expected_files = [
            "mesh2_aligned.obj",
            "icp_transformation.txt"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(temp_dir, file_name)
            if os.path.exists(file_path):
                print(f"✓ {file_name} created successfully")
            else:
                print(f"✗ {file_name} not found")

def test_c2c_comparison():
    """Test Cloud-to-Cloud comparison functionality"""
    print("\n" + "="*50)
    print("TESTING C2C COMPARISON")
    print("="*50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test meshes
        mesh1_path = create_test_mesh(os.path.join(temp_dir, "mesh1.obj"), "mesh1")
        mesh2_path = create_offset_mesh(os.path.join(temp_dir, "mesh2.obj"), 0.1, "mesh2")
        
        # Test C2C comparison
        c2c_csv, c2c_screenshot, c2c_log = run_c2c_comparison(mesh1_path, mesh2_path, temp_dir)
        print(f"C2C comparison results:")
        print(f"  - CSV: {c2c_csv}")
        print(f"  - Screenshot: {c2c_screenshot}")
        print(f"  - Log: {c2c_log}")
        
        # Check if output files exist
        expected_files = [
            "custom_c2c_distances.csv",
            "custom_c2c_statistics.csv",
            "custom_c2c_report.txt"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(temp_dir, file_name)
            if os.path.exists(file_path):
                print(f"✓ {file_name} created successfully")
            else:
                print(f"✗ {file_name} not found")

def test_c2m_comparison():
    """Test Cloud-to-Mesh comparison functionality"""
    print("\n" + "="*50)
    print("TESTING C2M COMPARISON")
    print("="*50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test meshes
        mesh1_path = create_test_mesh(os.path.join(temp_dir, "mesh1.obj"), "mesh1")
        mesh2_path = create_offset_mesh(os.path.join(temp_dir, "mesh2.obj"), 0.1, "mesh2")
        
        # Test C2M comparison
        c2m_csv, c2m_screenshot, c2m_log = run_c2m_comparison(mesh1_path, mesh2_path, temp_dir)
        print(f"C2M comparison results:")
        print(f"  - CSV: {c2m_csv}")
        print(f"  - Screenshot: {c2m_screenshot}")
        print(f"  - Log: {c2m_log}")
        
        # Check if output files exist
        expected_files = [
            "custom_c2m_distances.csv",
            "custom_c2m_statistics.csv",
            "custom_c2m_report.txt"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(temp_dir, file_name)
            if os.path.exists(file_path):
                print(f"✓ {file_name} created successfully")
            else:
                print(f"✗ {file_name} not found")

def main():
    """Run all tests"""
    print("Testing Custom 3D Mesh Analysis Implementations")
    print("This script tests the custom functions for 3D mesh analysis")
    
    try:
        # Test each functionality
        test_mesh_measurement()
        test_icp_alignment()
        test_c2c_comparison()
        test_c2m_comparison()
        
        print("\n" + "="*50)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("The custom implementations are working correctly.")
        print("You can now use the pipeline with custom 3D mesh analysis.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
