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
    
    # Since pycolmap.mapper doesn't exist, use subprocess directly
    print(f"[COLMAP] Using subprocess for sparse reconstruction...")
    
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
        print(f"[COLMAP] Sparse reconstruction completed using subprocess")
        
    except subprocess.CalledProcessError as e:
        print(f"[COLMAP] Subprocess reconstruction failed: {e}")
        print(f"[COLMAP] Error output: {e.stderr}")
        raise RuntimeError(f"COLMAP reconstruction failed: {e}")
    except FileNotFoundError:
        print(f"[COLMAP] COLMAP executable not found in PATH")
        raise RuntimeError("COLMAP executable not found. Please install COLMAP or add it to PATH")
    except Exception as e:
        print(f"[COLMAP] Unexpected error during reconstruction: {e}")
        raise RuntimeError(f"Unexpected error during reconstruction: {e}")

def model_conversion(sparse_folder):
    """Convert model to TXT format using pycolmap"""
    print(f"[COLMAP] Converting model to TXT format")
    
    # Since pycolmap.model_converter doesn't exist, use subprocess directly
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
            print(f"[COLMAP] Model conversion completed using subprocess")
        else:
            print(f"[COLMAP] No reconstruction folders found in {sparse_folder}")
            print(f"[COLMAP] Model conversion skipped - no reconstruction to convert")
            
    except subprocess.CalledProcessError as e:
        print(f"[COLMAP] Subprocess model conversion failed: {e}")
        print(f"[COLMAP] Error output: {e.stderr}")
        print(f"[COLMAP] Model conversion failed - continuing without TXT export")
    except FileNotFoundError:
        print(f"[COLMAP] COLMAP executable not found in PATH")
        print(f"[COLMAP] Model conversion failed - continuing without TXT export")
    except Exception as e:
        print(f"[COLMAP] Unexpected error during model conversion: {e}")
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