"""
COLMAP Dense Reconstruction Module using pycolmap
"""
import os
import sys
import pycolmap
from config import config

def check_cuda_availability():
    """Check if CUDA is available for dense reconstruction"""
    try:
        # Use PyTorch for reliable CUDA detection
        import torch
        return torch.cuda.is_available()
    except ImportError:
        # Fallback to pycolmap-based detection if PyTorch not available
        try:
            # Check if pycolmap supports CUDA
            return hasattr(pycolmap, 'has_cuda') and pycolmap.has_cuda()
        except:
            return False

def run_colmap_pipeline_with_dense(images_folder, output_folder):
    """Run COLMAP pipeline including dense reconstruction if CUDA is available"""
    
    # Early CUDA availability check
    print(f"[COLMAP] Checking CUDA availability for dense reconstruction...")
    if not check_cuda_availability():
        print(f"[COLMAP] CUDA not available on this system")
        print(f"[COLMAP] Dense reconstruction requires CUDA support")
        print(f"[COLMAP] Stopping process - cannot create 3D meshes without dense reconstruction")
        print(f"[COLMAP] Solutions:")
        print(f"[COLMAP]    - Use a system with NVIDIA GPU and CUDA")
        print(f"[COLMAP]    - Use a different reconstruction pipeline")
        sys.exit(1)
    
    print(f"[COLMAP] CUDA is available - proceeding with dense reconstruction")
    
    # Create output directories
    database_path = os.path.join(output_folder, "database.db")
    sparse_folder = os.path.join(output_folder, "sparse")
    dense_folder = os.path.join(output_folder, "dense")
    mesh_folder = os.path.join(output_folder, "mesh")
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(sparse_folder, exist_ok=True)
    os.makedirs(dense_folder, exist_ok=True)
    os.makedirs(mesh_folder, exist_ok=True)
    
    print(f"[COLMAP] Starting pipeline with dense reconstruction for {images_folder}")
    print(f"[COLMAP] Output directory: {output_folder}")
    
    # Import sparse reconstruction functions
    from .feature_extraction import feature_extraction
    from .matching import robust_sequential_matching, spatial_matching
    from .reconstruction import mapping, model_conversion, image_undistortion
    from .mesh_creation import run_colmap_pipeline
    
    # Standard COLMAP pipeline
    try:
        feature_extraction(database_path, images_folder)
        robust_sequential_matching(database_path)
        spatial_matching(database_path)
        mapping(database_path, images_folder, sparse_folder)
    except Exception as e:
        print(f"[COLMAP][ERROR] Pipeline failed: {e}")
        print(f"[COLMAP] Attempting to diagnose the issue...")
        
        # Check if database exists and has content
        if os.path.exists(database_path):
            db_size = os.path.getsize(database_path)
            print(f"[COLMAP] Database size: {db_size} bytes")
            
            if db_size < 1024:
                print(f"[COLMAP][ERROR] Database is too small - feature extraction likely failed")
                print(f"[COLMAP] Possible causes:")
                print(f"  - Images are corrupted or unreadable")
                print(f"  - Images have no distinctive features")
                print(f"  - Images are too similar or too different")
                print(f"  - Image format not supported by COLMAP")
                print(f"[COLMAP] Check the images in: {images_folder}")
                sys.exit(1)
        else:
            print(f"[COLMAP][ERROR] Database was never created")
            print(f"[COLMAP] Feature extraction completely failed")
            sys.exit(1)
        
        # Re-raise the exception if we can't handle it
        raise
    
    model_conversion(sparse_folder)
    image_undistortion(images_folder, sparse_folder, dense_folder)
    
    # Dense reconstruction (CUDA is available)
    print(f"[COLMAP] Starting dense stereo reconstruction")
    stereo_folder = os.path.join(dense_folder, "stereo")
    os.makedirs(stereo_folder, exist_ok=True)
    
    # Get configurable parameters
    dense_image_size = getattr(config, 'colmap_params', {}).get('dense_image_size', 2000)
    window_radius = getattr(config, 'colmap_params', {}).get('window_radius', 5)
    window_step = getattr(config, 'colmap_params', {}).get('window_step', 2)
    
    try:
        print(f"[COLMAP] Starting pycolmap dense stereo reconstruction...")
        
        pycolmap.patch_match_stereo(
            workspace_path=dense_folder,
            workspace_format="COLMAP",
            patch_match_stereo_options=pycolmap.PatchMatchOptions(
                max_image_size=dense_image_size,
                window_radius=window_radius,
                window_step=window_step
            )
        )
        
        print(f"[COLMAP] Dense stereo reconstruction completed")
        
    except Exception as e:
        print(f"[COLMAP] Dense stereo reconstruction failed: {e}")
        print(f"[COLMAP] Continuing without dense reconstruction...")
        return None
    
    # Dense fusion
    print(f"[COLMAP] Starting dense fusion")
    fused_folder = os.path.join(dense_folder, "fused")
    os.makedirs(fused_folder, exist_ok=True)
    
    try:
        pycolmap.stereo_fusion(
            workspace_path=dense_folder,
            workspace_format="COLMAP",
            input_type="geometric",
            output_path=os.path.join(fused_folder, "fused.ply")
        )
        print(f"[COLMAP] Dense fusion completed")
        
    except Exception as e:
        print(f"[COLMAP] Dense fusion failed: {e}")
        print(f"[COLMAP] Continuing without fusion...")
        return None
    
    # Mesh creation
    print(f"[COLMAP] Creating mesh from point cloud")
    
    try:
        # Use pycolmap's poisson_meshing function
        print(f"[COLMAP] Using pycolmap poisson_meshing for mesh creation...")
        
        pycolmap.poisson_meshing(
            input_path=os.path.join(fused_folder, "fused.ply"),
            output_path=os.path.join(mesh_folder, "mesh.ply")
        )
        print(f"[COLMAP] Mesh creation completed using pycolmap")
        
    except Exception as e:
        print(f"[COLMAP] pycolmap poisson_meshing failed: {e}")
        print(f"[COLMAP] Using fallback subprocess method...")
        
        # Fallback to subprocess
        import subprocess
        colmap_cmd = "colmap"
        
        try:
            subprocess.run([
                colmap_cmd, "poisson_mesher",
                "--input_path", os.path.join(fused_folder, "fused.ply"),
                "--output_path", os.path.join(mesh_folder, "mesh.ply")
            ], check=True, capture_output=True, text=True)
            print(f"[COLMAP] Subprocess fallback mesh creation completed")
            
        except subprocess.CalledProcessError as e:
            print(f"[COLMAP] Subprocess mesh creation failed: {e}")
            print(f"[COLMAP] Continuing without mesh...")
            return None
        except FileNotFoundError:
            print(f"[COLMAP] COLMAP executable not found for mesh creation")
            print(f"[COLMAP] Continuing without mesh...")
            return None
        except Exception as sub_error:
            print(f"[COLMAP] Subprocess mesh creation also failed: {sub_error}")
            print(f"[COLMAP] Continuing without mesh...")
            return None
    
    # Convert to OBJ format for 3D mesh analysis
    obj_file = os.path.join(mesh_folder, "model.obj")
    
    try:
        # Use pycolmap to convert PLY to OBJ
        import trimesh
        mesh = trimesh.load(os.path.join(mesh_folder, "mesh.ply"))
        mesh.export(obj_file)
        print(f"[COLMAP] Model conversion to OBJ completed")
        
    except ImportError:
        print(f"[COLMAP] trimesh not available, using pycolmap conversion...")
        try:
            # Try to use pycolmap's Reconstruction class for conversion
            print(f"[COLMAP] Using pycolmap for PLY to OBJ conversion...")
            
            # Load the PLY file and convert to OBJ using trimesh
            import trimesh
            mesh = trimesh.load(os.path.join(mesh_folder, "mesh.ply"))
            mesh.export(obj_file)
            print(f"[COLMAP] Model conversion to OBJ completed using pycolmap + trimesh")
            
        except ImportError:
            print(f"[COLMAP] trimesh not available, using subprocess conversion...")
            # Fallback to subprocess
            import subprocess
            colmap_cmd = "colmap"
            
            try:
                subprocess.run([
                    colmap_cmd, "model_converter",
                    "--input_path", os.path.join(mesh_folder, "mesh.ply"),
                    "--output_path", obj_file,
                    "--output_type", "OBJ"
                ], check=True, capture_output=True, text=True)
                print(f"[COLMAP] Subprocess fallback model conversion completed")
                
            except subprocess.CalledProcessError as e:
                print(f"[COLMAP] Subprocess model conversion failed: {e}")
                print(f"[COLMAP] Error output: {e.stderr}")
                return None
            except FileNotFoundError:
                print(f"[COLMAP] COLMAP executable not found for model conversion")
                return None
            except Exception as sub_error:
                print(f"[COLMAP] Subprocess model conversion also failed: {sub_error}")
                return None
        except Exception as e:
            print(f"[COLMAP] pycolmap + trimesh conversion failed: {e}")
            print(f"[COLMAP] Using subprocess fallback...")
            
            # Final fallback to subprocess
            import subprocess
            colmap_cmd = "colmap"
            
            try:
                subprocess.run([
                    colmap_cmd, "model_converter",
                    "--input_path", os.path.join(mesh_folder, "mesh.ply"),
                    "--output_path", obj_file,
                    "--output_type", "OBJ"
                ], check=True, capture_output=True, text=True)
                print(f"[COLMAP] Subprocess fallback model conversion completed")
                
            except subprocess.CalledProcessError as e:
                print(f"[COLMAP] Subprocess model conversion failed: {e}")
                print(f"[COLMAP] Error output: {e.stderr}")
                return None
            except FileNotFoundError:
                print(f"[COLMAP] COLMAP executable not found for model conversion")
                return None
            except Exception as sub_error:
                print(f"[COLMAP] Subprocess model conversion also failed: {sub_error}")
                return None
    
    print(f"[COLMAP] Pipeline complete with mesh: {obj_file}")
    return obj_file 