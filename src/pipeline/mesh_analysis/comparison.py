"""
Custom Comparison Module
"""
import os
import numpy as np
import open3d as o3d
import pandas as pd
from config import config

def run_c2c_comparison(mesh1, aligned_mesh2, output_dir):
    """Run Cloud-to-Cloud distance comparison"""
    print("Running C2C distance comparison using custom implementation")
    
    try:
        # Load meshes
        mesh1_o3d = o3d.io.read_triangle_mesh(mesh1)
        mesh2_o3d = o3d.io.read_triangle_mesh(aligned_mesh2)
        
        # Sample points from both meshes
        mesh1_pcd = mesh1_o3d.sample_points_uniformly(number_of_points=50000)
        mesh2_pcd = mesh2_o3d.sample_points_uniformly(number_of_points=50000)
        
        # Compute distances from mesh1 points to mesh2
        distances_1to2 = []
        mesh2_tree = o3d.geometry.KDTreeFlann(mesh2_pcd)
        
        for point in mesh1_pcd.points:
            # Find nearest neighbor in mesh2
            [k, idx, dist] = mesh2_tree.search_knn_vector_3d(point, 1)
            distances_1to2.append(np.sqrt(dist[0]))
        
        # Compute distances from mesh2 points to mesh1
        distances_2to1 = []
        mesh1_tree = o3d.geometry.KDTreeFlann(mesh1_pcd)
        
        for point in mesh2_pcd.points:
            # Find nearest neighbor in mesh1
            [k, idx, dist] = mesh1_tree.search_knn_vector_3d(point, 1)
            distances_2to1.append(np.sqrt(dist[0]))
        
        # Combine all distances
        all_distances = np.array(distances_1to2 + distances_2to1)
        
        # Calculate statistics
        stats = {
            'mean': np.mean(all_distances),
            'std': np.std(all_distances),
            'min': np.min(all_distances),
            'max': np.max(all_distances),
            'median': np.median(all_distances),
            'rms': np.sqrt(np.mean(all_distances**2))
        }
        
        # Create CSV with distance data
        c2c_csv = os.path.join(output_dir, "custom_c2c_distances.csv")
        distance_df = pd.DataFrame({
            'distance': all_distances,
            'source': ['mesh1_to_mesh2'] * len(distances_1to2) + ['mesh2_to_mesh1'] * len(distances_2to1)
        })
        distance_df.to_csv(c2c_csv, index=False)
        
        # Create statistics CSV
        stats_csv = os.path.join(output_dir, "custom_c2c_statistics.csv")
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(stats_csv, index=False)
        
        # Create log file
        c2c_log = os.path.join(output_dir, "custom_c2c_report.txt")
        with open(c2c_log, 'w') as f:
            f.write("Custom C2C Distance Comparison Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Mesh 1: {mesh1}\n")
            f.write(f"Mesh 2: {aligned_mesh2}\n\n")
            f.write("Distance Statistics:\n")
            for key, value in stats.items():
                f.write(f"  {key.upper()}: {value:.6f}\n")
            f.write(f"\nTotal points analyzed: {len(all_distances)}\n")
            f.write(f"Points from mesh1 to mesh2: {len(distances_1to2)}\n")
            f.write(f"Points from mesh2 to mesh1: {len(distances_2to1)}\n")
        
        # Create visualization (point cloud with colors based on distance)
        c2c_screenshot = os.path.join(output_dir, "custom_c2c_visualization.png")
        _create_distance_visualization(mesh1_pcd, mesh2_pcd, distances_1to2, distances_2to1, c2c_screenshot)
        
        print("C2C comparison completed")
        print(f"  - CSV: {c2c_csv}")
        print(f"  - Statistics: {stats_csv}")
        print(f"  - Screenshot: {c2c_screenshot}")
        print(f"  - Log: {c2c_log}")
        print(f"  - Mean distance: {stats['mean']:.6f}")
        print(f"  - Max distance: {stats['max']:.6f}")
        
        return c2c_csv, c2c_screenshot, c2c_log
        
    except Exception as e:
        print(f"C2C comparison failed: {e}")
        # Return dummy files to maintain compatibility
        dummy_csv = os.path.join(output_dir, "custom_c2c_distances.csv")
        dummy_screenshot = os.path.join(output_dir, "custom_c2c_visualization.png")
        dummy_log = os.path.join(output_dir, "custom_c2c_report.txt")
        
        # Create dummy files
        pd.DataFrame({'distance': [0], 'source': ['error']}).to_csv(dummy_csv, index=False)
        with open(dummy_log, 'w') as f:
            f.write(f"C2C comparison failed: {e}")
        
        return dummy_csv, dummy_screenshot, dummy_log

def run_c2m_comparison(mesh1, aligned_mesh2, output_dir):
    """Run Cloud-to-Mesh distance comparison (signed)"""
    print("Running C2M distance comparison using custom implementation")
    
    try:
        # Load meshes
        mesh1_o3d = o3d.io.read_triangle_mesh(mesh1)
        mesh2_o3d = o3d.io.read_triangle_mesh(aligned_mesh2)
        
        # Sample points from mesh2 (the "cloud")
        mesh2_pcd = mesh2_o3d.sample_points_uniformly(number_of_points=50000)
        
        # Compute signed distances from mesh2 points to mesh1
        distances = []
        
        # Convert vertices to numpy array for easier processing
        mesh1_vertices = np.array(mesh1_o3d.vertices)
        
        for point in mesh2_pcd.points:
            # Find nearest neighbor in mesh1 using simple distance calculation
            point_array = np.array(point)
            distances_to_vertices = np.linalg.norm(mesh1_vertices - point_array, axis=1)
            nearest_idx = np.argmin(distances_to_vertices)
            nearest_vertex = mesh1_vertices[nearest_idx]
            
            # Calculate distance
            distance = distances_to_vertices[nearest_idx]
            
            # Simple heuristic for sign: if point is "outside" the mesh bounds, positive
            # This is approximate - more sophisticated methods could be implemented
            if np.any(point_array > np.max(mesh1_vertices, axis=0)) or np.any(point_array < np.min(mesh1_vertices, axis=0)):
                distances.append(distance)
            else:
                distances.append(-distance)
        
        distances = np.array(distances)
        
        # Calculate statistics
        stats = {
            'mean': np.mean(distances),
            'std': np.std(distances),
            'min': np.min(distances),
            'max': np.max(distances),
            'median': np.median(distances),
            'rms': np.sqrt(np.mean(distances**2)),
            'positive_count': np.sum(distances > 0),
            'negative_count': np.sum(distances < 0),
            'zero_count': np.sum(distances == 0)
        }
        
        # Create CSV with distance data
        c2m_csv = os.path.join(output_dir, "custom_c2m_distances.csv")
        distance_df = pd.DataFrame({
            'signed_distance': distances,
            'absolute_distance': np.abs(distances)
        })
        distance_df.to_csv(c2m_csv, index=False)
        
        # Create statistics CSV
        stats_csv = os.path.join(output_dir, "custom_c2m_statistics.csv")
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(stats_csv, index=False)
        
        # Create log file
        c2m_log = os.path.join(output_dir, "custom_c2m_report.txt")
        with open(c2m_log, 'w') as f:
            f.write("Custom C2M Distance Comparison Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Reference Mesh: {mesh1}\n")
            f.write(f"Cloud Mesh: {aligned_mesh2}\n\n")
            f.write("Signed Distance Statistics:\n")
            for key, value in stats.items():
                if isinstance(value, float):
                    f.write(f"  {key.upper()}: {value:.6f}\n")
                else:
                    f.write(f"  {key.upper()}: {value}\n")
            f.write(f"\nTotal points analyzed: {len(distances)}\n")
            f.write(f"Positive distances (outside): {stats['positive_count']}\n")
            f.write(f"Negative distances (inside): {stats['negative_count']}\n")
            f.write(f"Zero distances: {stats['zero_count']}\n")
        
        # Create visualization
        c2m_screenshot = os.path.join(output_dir, "custom_c2m_visualization.png")
        _create_signed_distance_visualization(mesh2_pcd, distances, c2m_screenshot)
        
        print("C2M comparison completed")
        print(f"  - CSV: {c2m_csv}")
        print(f"  - Statistics: {stats_csv}")
        print(f"  - Screenshot: {c2m_screenshot}")
        print(f"  - Log: {c2m_log}")
        print(f"  - Mean signed distance: {stats['mean']:.6f}")
        print(f"  - Positive distances: {stats['positive_count']}")
        print(f"  - Negative distances: {stats['negative_count']}")
        
        return c2m_csv, c2m_screenshot, c2m_log
        
    except Exception as e:
        print(f"C2M comparison failed: {e}")
        # Return dummy files to maintain compatibility
        dummy_csv = os.path.join(output_dir, "custom_c2m_distances.csv")
        dummy_screenshot = os.path.join(output_dir, "custom_c2m_visualization.png")
        dummy_log = os.path.join(output_dir, "custom_c2m_report.txt")
        
        # Create dummy files
        pd.DataFrame({'signed_distance': [0], 'absolute_distance': [0]}).to_csv(dummy_csv, index=False)
        with open(dummy_log, 'w') as f:
            f.write(f"C2M comparison failed: {e}")
        
        return dummy_csv, dummy_screenshot, dummy_log

def _create_distance_visualization(mesh1_pcd, mesh2_pcd, distances_1to2, distances_2to1, output_path):
    """Create visualization of distances between meshes"""
    try:
        import matplotlib.pyplot as plt
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot distance distributions
        ax1.hist(distances_1to2, bins=50, alpha=0.7, label='Mesh1 → Mesh2', color='blue')
        ax1.hist(distances_2to1, bins=50, alpha=0.7, label='Mesh2 → Mesh1', color='red')
        ax1.set_xlabel('Distance')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Distance Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot cumulative distribution
        ax2.hist(distances_1to2, bins=50, alpha=0.7, label='Mesh1 → Mesh2', 
                cumulative=True, density=True, color='blue')
        ax2.hist(distances_2to1, bins=50, alpha=0.7, label='Mesh2 → Mesh1', 
                cumulative=True, density=True, color='red')
        ax2.set_xlabel('Distance')
        ax2.set_ylabel('Cumulative Probability')
        ax2.set_title('Cumulative Distance Distribution')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    except ImportError:
        print("Matplotlib not available, skipping visualization")
        # Create a simple text file instead
        with open(output_path.replace('.png', '.txt'), 'w') as f:
            f.write("Visualization not available - matplotlib required\n")
            f.write(f"Distance statistics saved in CSV files\n")

def _create_signed_distance_visualization(mesh2_pcd, distances, output_path):
    """Create visualization of signed distances"""
    try:
        import matplotlib.pyplot as plt
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot signed distance distribution
        ax1.hist(distances, bins=50, alpha=0.7, color='green', edgecolor='black')
        ax1.axvline(x=0, color='red', linestyle='--', label='Zero distance')
        ax1.set_xlabel('Signed Distance')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Signed Distance Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot positive vs negative counts
        positive_count = np.sum(distances > 0)
        negative_count = np.sum(distances < 0)
        zero_count = np.sum(distances == 0)
        
        labels = ['Positive', 'Negative', 'Zero']
        counts = [positive_count, negative_count, zero_count]
        colors = ['green', 'red', 'blue']
        
        ax2.bar(labels, counts, color=colors, alpha=0.7)
        ax2.set_ylabel('Count')
        ax2.set_title('Distance Sign Distribution')
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, count in enumerate(counts):
            ax2.text(i, count + max(counts)*0.01, str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
    except ImportError:
        print("Matplotlib not available, skipping visualization")
        # Create a simple text file instead
        with open(output_path.replace('.png', '.txt'), 'w') as f:
            f.write("Visualization not available - matplotlib required\n")
            f.write(f"Distance statistics saved in CSV files\n") 