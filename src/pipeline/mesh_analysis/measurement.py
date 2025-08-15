"""
Custom Mesh Measurement Module
"""
import os
import numpy as np
import open3d as o3d
from config import config

def run_mesh_measurement(mesh_path, output_dir, mesh_name):
    """Measure area and volume of a mesh"""
    print(f"Measuring {mesh_name} using custom implementation")
    
    try:
        # Load mesh using Open3D
        mesh = o3d.io.read_triangle_mesh(mesh_path)
        
        # Ensure mesh is valid
        if not mesh.has_vertices() or not mesh.has_triangles():
            raise ValueError("Invalid mesh: no vertices or triangles")
        
        # Calculate surface area
        surface_area = mesh.get_surface_area()
        
        # Calculate volume (requires watertight mesh)
        volume = mesh.get_volume()
        
        # Calculate additional metrics
        vertex_count = len(mesh.vertices)
        triangle_count = len(mesh.triangles)
        
        # Calculate bounding box dimensions
        bbox = mesh.get_axis_aligned_bounding_box()
        bbox_extent = bbox.get_extent()
        bbox_volume = bbox_extent[0] * bbox_extent[1] * bbox_extent[2]
        
        # Calculate mesh density (triangles per unit volume)
        mesh_density = triangle_count / bbox_volume if bbox_volume > 0 else 0
        
        # Check if mesh is watertight (closed)
        is_watertight = mesh.is_watertight()
        
        # Create measurement file
        measure_file = os.path.join(output_dir, f"{mesh_name}_measure.txt")
        
        with open(measure_file, 'w') as f:
            f.write(f"Mesh Measurement Report for {mesh_name}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Mesh File: {mesh_path}\n")
            f.write(f"Measurement Date: {os.path.basename(output_dir)}\n\n")
            
            f.write("GEOMETRIC PROPERTIES:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Surface Area: {surface_area:.6f} square units\n")
            f.write(f"Volume: {volume:.6f} cubic units\n")
            f.write(f"Vertex Count: {vertex_count:,}\n")
            f.write(f"Triangle Count: {triangle_count:,}\n\n")
            
            f.write("BOUNDING BOX:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Width (X): {bbox_extent[0]:.6f} units\n")
            f.write(f"Height (Y): {bbox_extent[1]:.6f} units\n")
            f.write(f"Depth (Z): {bbox_extent[2]:.6f} units\n")
            f.write(f"Bounding Box Volume: {bbox_volume:.6f} cubic units\n\n")
            
            f.write("QUALITY METRICS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Mesh Density: {mesh_density:.2f} triangles/cubic unit\n")
            f.write(f"Watertight: {'Yes' if is_watertight else 'No'}\n")
            f.write(f"Average Triangle Area: {surface_area/triangle_count:.6f} square units\n")
            
            # Calculate triangle quality metrics
            if triangle_count > 0:
                areas = _calculate_triangle_areas(mesh)
                f.write(f"Triangle Area Statistics:\n")
                f.write(f"  - Min: {np.min(areas):.6f}\n")
                f.write(f"  - Max: {np.max(areas):.6f}\n")
                f.write(f"  - Mean: {np.mean(areas):.6f}\n")
                f.write(f"  - Std Dev: {np.std(areas):.6f}\n")
        
        # Create CSV with detailed measurements
        csv_file = os.path.join(output_dir, f"{mesh_name}_measurements.csv")
        import pandas as pd
        
        measurements_df = pd.DataFrame({
            'metric': ['surface_area', 'volume', 'vertex_count', 'triangle_count', 
                      'bbox_width', 'bbox_height', 'bbox_depth', 'bbox_volume', 
                      'mesh_density', 'is_watertight'],
            'value': [surface_area, volume, vertex_count, triangle_count,
                     bbox_extent[0], bbox_extent[1], bbox_extent[2], bbox_volume,
                     mesh_density, is_watertight],
            'unit': ['square_units', 'cubic_units', 'count', 'count',
                    'units', 'units', 'units', 'cubic_units',
                    'triangles_per_cubic_unit', 'boolean']
        })
        measurements_df.to_csv(csv_file, index=False)
        
        print(f"{mesh_name} measurement completed successfully")
        print(f"  - Surface Area: {surface_area:.6f} square units")
        print(f"  - Volume: {volume:.6f} cubic units")
        print(f"  - Vertices: {vertex_count:,}")
        print(f"  - Triangles: {triangle_count:,}")
        print(f"  - Watertight: {'Yes' if is_watertight else 'No'}")
        print(f"  - Report: {measure_file}")
        print(f"  - CSV: {csv_file}")
        
        return measure_file
        
    except Exception as e:
        print(f"Mesh measurement failed for {mesh_name}: {e}")
        
        # Create error report
        error_file = os.path.join(output_dir, f"{mesh_name}_measure_error.txt")
        with open(error_file, 'w') as f:
            f.write(f"Mesh Measurement Error for {mesh_name}\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Error: {str(e)}\n")
            f.write(f"Mesh Path: {mesh_path}\n")
            f.write(f"Timestamp: {os.path.basename(output_dir)}\n")
        
        return error_file

def _calculate_triangle_areas(mesh):
    """Calculate areas of all triangles in the mesh"""
    areas = []
    vertices = np.array(mesh.vertices)
    triangles = np.array(mesh.triangles)
    
    for triangle in triangles:
        # Get triangle vertices
        v1 = vertices[triangle[0]]
        v2 = vertices[triangle[1]]
        v3 = vertices[triangle[2]]
        
        # Calculate triangle area using cross product
        edge1 = v2 - v1
        edge2 = v3 - v1
        cross_product = np.cross(edge1, edge2)
        area = 0.5 * np.linalg.norm(cross_product)
        areas.append(area)
    
    return np.array(areas) 