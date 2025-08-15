"""
COLMAP Sparse Reconstruction Module using pycolmap
"""
import os
import sys
import pycolmap
from config import config

def mapping(database_path, images_folder, sparse_folder):
    """Perform sparse reconstruction mapping using pycolmap"""
    print(f"[COLMAP] Starting sparse reconstruction")
    os.makedirs(sparse_folder, exist_ok=True)
    
    # Get configurable parameters
    min_matches = getattr(config, 'colmap_params', {}).get('min_matches', 15)
    max_iterations = getattr(config, 'colmap_params', {}).get('max_iterations', 50)
    max_refinements = getattr(config, 'colmap_params', {}).get('max_refinements', 3)
    
    # Use pycolmap's incremental_mapping function
    print(f"[COLMAP] Using pycolmap incremental_mapping for sparse reconstruction...")
    
    try:
        # Use pycolmap's incremental_mapping function
        pycolmap.incremental_mapping(
            database_path=database_path,
            image_path=images_folder,
            output_path=sparse_folder,
            min_num_matches=min_matches,
            ba_global_max_num_iterations=max_iterations,
            ba_global_max_refinements=max_refinements
        )
        print(f"[COLMAP] Sparse reconstruction completed using pycolmap")
        
    except Exception as e:
        print(f"[COLMAP] pycolmap incremental_mapping failed: {e}")
        print(f"[COLMAP] Trying alternative pycolmap approach...")
        
        try:
            # Alternative: Use pycolmap's incremental pipeline
            options = pycolmap.IncrementalPipelineOptions()
            options.min_num_matches = min_matches
            options.ba_global_max_num_iterations = max_iterations
            options.ba_global_max_refinements = max_refinements
            
            pycolmap.IncrementalPipeline(
                database_path=database_path,
                image_path=images_folder,
                output_path=sparse_folder,
                options=options
            ).run()
            print(f"[COLMAP] Alternative pycolmap reconstruction completed")
            
        except Exception as alt_error:
            print(f"[COLMAP] Alternative pycolmap approach also failed: {alt_error}")
            print(f"[COLMAP] Using fallback subprocess method...")
            
            # Fallback to subprocess if pycolmap fails
            import subprocess
            colmap_cmd = "colmap"
            
            try:
                subprocess.run([
                    colmap_cmd, "mapper",
                    "--database_path", database_path,
                    "--image_path", images_folder,
                    "--output_path", sparse_folder,
                    "--Mapper.min_num_matches", str(min_matches),
                    "--Mapper.ba_global_max_num_iterations", str(max_iterations),
                    "--Mapper.ba_global_max_refinements", str(max_refinements)
                ], check=True, capture_output=True, text=True)
                print(f"[COLMAP] Subprocess fallback reconstruction completed")
            except Exception as sub_error:
                print(f"[COLMAP] All reconstruction methods failed: {sub_error}")
                raise RuntimeError("Could not perform sparse reconstruction with any method")

def model_conversion(sparse_folder):
    """Convert model to TXT format using pycolmap"""
    print(f"[COLMAP] Converting model to TXT format")
    
    try:
        # Use pycolmap's Reconstruction class to load and export
        print(f"[COLMAP] Using pycolmap Reconstruction class for model conversion...")
        
        # Find the first reconstruction folder
        reconstruction_folders = [f for f in os.listdir(sparse_folder) if os.path.isdir(os.path.join(sparse_folder, f))]
        if reconstruction_folders:
            input_path = os.path.join(sparse_folder, reconstruction_folders[0])
            
            # Load reconstruction using pycolmap
            reconstruction = pycolmap.Reconstruction(input_path)
            
            # Export to TXT format
            reconstruction.export_txt(sparse_folder)
            print(f"[COLMAP] Model conversion completed using pycolmap")
            
        else:
            print(f"[COLMAP] No reconstruction folders found in {sparse_folder}")
            print(f"[COLMAP] Model conversion skipped - no reconstruction to convert")
            
    except Exception as e:
        print(f"[COLMAP] pycolmap model conversion failed: {e}")
        print(f"[COLMAP] Using fallback subprocess method...")
        
        # Fallback to subprocess
        import subprocess
        colmap_cmd = "colmap"
        
        try:
            # Find the first reconstruction folder
            reconstruction_folders = [f for f in os.listdir(sparse_folder) if os.path.isdir(os.path.join(sparse_folder, f))]
            if reconstruction_folders:
                input_path = os.path.join(sparse_folder, reconstruction_folders[0])
                subprocess.run([
                    colmap_cmd, "model_converter",
                    "--input_path", input_path,
                    "--output_path", sparse_folder,
                    "--output_type", "TXT"
                ], check=True, capture_output=True, text=True)
                print(f"[COLMAP] Subprocess fallback model conversion completed")
            else:
                print(f"[COLMAP] No reconstruction folders found in {sparse_folder}")
                print(f"[COLMAP] Model conversion failed - continuing without TXT export")
                
        except subprocess.CalledProcessError as e:
            print(f"[COLMAP] Subprocess model conversion failed: {e}")
            print(f"[COLMAP] Error output: {e.stderr}")
            print(f"[COLMAP] Model conversion failed - continuing without TXT export")
        except FileNotFoundError:
            print(f"[COLMAP] COLMAP executable not found in PATH")
            print(f"[COLMAP] Model conversion failed - continuing without TXT export")
        except Exception as sub_error:
            print(f"[COLMAP] Subprocess model conversion also failed: {sub_error}")
            print(f"[COLMAP] Model conversion failed - continuing without TXT export")

def image_undistortion(images_folder, sparse_folder, dense_folder):
    """Undistort images for dense reconstruction using pycolmap"""
    print(f"[COLMAP] Starting image undistortion")
    os.makedirs(dense_folder, exist_ok=True)
    
    try:
        print(f"[COLMAP] Starting pycolmap image undistortion...")
        
        # Try to use pycolmap's undistort_images function
        pycolmap.undistort_images(
            image_path=images_folder,
            input_path=sparse_folder,
            output_path=dense_folder,
            output_type="COLMAP"
        )
        
        print(f"[COLMAP] Image undistortion completed using pycolmap")
        
    except Exception as e:
        print(f"[COLMAP] pycolmap image undistortion failed: {e}")
        print(f"[COLMAP] Using fallback subprocess method...")
        
        # Fallback to subprocess
        import subprocess
        colmap_cmd = "colmap"
        
        try:
            # Find the first reconstruction folder
            reconstruction_folders = [f for f in os.listdir(sparse_folder) if os.path.isdir(os.path.join(sparse_folder, f))]
            if reconstruction_folders:
                input_path = os.path.join(sparse_folder, reconstruction_folders[0])
                subprocess.run([
                    colmap_cmd, "image_undistorter",
                    "--image_path", images_folder,
                    "--input_path", input_path,
                    "--output_path", dense_folder,
                    "--output_type", "COLMAP"
                ], check=True, capture_output=True, text=True)
                print(f"[COLMAP] Subprocess fallback image undistortion completed")
            else:
                print(f"[COLMAP] No reconstruction folders found, copying original images...")
                # Copy original images to dense folder as fallback
                import shutil
                for img_file in os.listdir(images_folder):
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')):
                        src = os.path.join(images_folder, img_file)
                        dst = os.path.join(dense_folder, img_file)
                        shutil.copy2(src, dst)
                print(f"[COLMAP] Copied original images as fallback")
        except Exception as sub_error:
            print(f"[COLMAP] Subprocess image undistortion also failed: {sub_error}")
            print(f"[COLMAP] Copying original images as final fallback...")
            # Final fallback: copy original images
            import shutil
            for img_file in os.listdir(images_folder):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')):
                    src = os.path.join(images_folder, img_file)
                    dst = os.path.join(dense_folder, img_file)
                    shutil.copy2(src, dst)
            print(f"[COLMAP] Copied original images as final fallback") 