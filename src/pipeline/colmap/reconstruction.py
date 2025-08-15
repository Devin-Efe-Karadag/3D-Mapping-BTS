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
    
    # Diagnose feature quality before reconstruction
    print(f"[COLMAP] Diagnosing feature quality...")
    try:
        database = pycolmap.Database(database_path)
        num_images = database.num_images()
        num_keypoints = database.num_keypoints()
        num_matches = database.num_matches()
        
        print(f"[COLMAP] Database statistics:")
        print(f"  - Images: {num_images}")
        print(f"  - Keypoints: {num_keypoints}")
        print(f"  - Matches: {num_matches}")
        
        if num_keypoints == 0:
            raise RuntimeError("No keypoints extracted - check image quality and feature extraction")
        
        if num_matches == 0:
            raise RuntimeError("No feature matches found - images may be too similar/different")
        
        avg_keypoints_per_image = num_keypoints / num_images if num_images > 0 else 0
        if avg_keypoints_per_image < 100:
            print(f"[COLMAP][WARNING] Low average keypoints per image: {avg_keypoints_per_image:.1f}")
            print(f"[COLMAP][WARNING] This may cause reconstruction failures")
        
        database.close()
        
    except Exception as e:
        print(f"[COLMAP][WARNING] Could not diagnose database: {e}")
        print(f"[COLMAP] Continuing with reconstruction...")
    
    # Use pycolmap's incremental_mapping function
    print(f"[COLMAP] Using pycolmap incremental_mapping for sparse reconstruction...")
    
    try:
        # Use pycolmap's incremental_mapping function with proper options
        print(f"[COLMAP] Creating pycolmap IncrementalPipelineOptions...")
        
        # Create options object with the correct parameters
        options = pycolmap.IncrementalPipelineOptions()
        options.min_num_matches = min_matches
        options.ba_global_max_num_iterations = max_iterations
        options.ba_global_max_refinements = max_refinements
        
        # Improve initial pair selection and reconstruction stability
        options.init_num_trials = 500  # Increase trials for better initial pair
        options.min_model_size = 5     # Lower minimum model size
        options.max_model_overlap = 30 # Increase overlap tolerance
        
        # Improve bundle adjustment
        options.ba_global_frames_ratio = 1.2
        options.ba_global_points_ratio = 1.2
        options.ba_global_frames_freq = 100
        options.ba_global_points_freq = 100000
        
        # Improve mapper options
        mapper_options = options.get_mapper()
        mapper_options.init_min_num_inliers = 80  # Lower threshold
        mapper_options.init_max_error = 6.0       # Higher error tolerance
        mapper_options.abs_pose_min_num_inliers = 25  # Lower threshold
        mapper_options.abs_pose_min_inlier_ratio = 0.2  # Lower ratio
        mapper_options.filter_min_tri_angle = 1.0  # Lower angle threshold
        
        print(f"[COLMAP] Using pycolmap incremental_mapping with options...")
        pycolmap.incremental_mapping(
            database_path=database_path,
            image_path=images_folder,
            output_path=sparse_folder,
            options=options
        )
        print(f"[COLMAP] Sparse reconstruction completed using pycolmap")
        
        # Verify that reconstruction actually produced output
        reconstruction_folders = [f for f in os.listdir(sparse_folder) if os.path.isdir(os.path.join(sparse_folder, f))]
        if not reconstruction_folders:
            print(f"[COLMAP][WARNING] No reconstruction folders found - reconstruction may have failed")
            print(f"[COLMAP][WARNING] This could indicate poor image quality or insufficient features")
            raise RuntimeError("Reconstruction completed but no output files were created")
        
        print(f"[COLMAP] Reconstruction output verified: {len(reconstruction_folders)} folders created")
        
    except Exception as e:
        print(f"[COLMAP] pycolmap incremental_mapping failed: {e}")
        print(f"[COLMAP] This often indicates:")
        print(f"  - Insufficient feature matches between images")
        print(f"  - Poor image quality or too few distinctive features")
        print(f"  - Images are too similar or too different")
        print(f"  - Camera motion is insufficient for reconstruction")
        print(f"[COLMAP] Trying alternative pycolmap approach...")
        
        try:
            # Alternative: Use pycolmap's incremental pipeline directly
            print(f"[COLMAP] Trying pycolmap IncrementalPipeline...")
            
            # Create options object with improved settings
            options = pycolmap.IncrementalPipelineOptions()
            options.min_num_matches = min_matches
            options.ba_global_max_num_iterations = max_iterations
            options.ba_global_max_refinements = max_refinements
            
            # Apply the same improvements as above
            options.init_num_trials = 500
            options.min_model_size = 5
            options.max_model_overlap = 30
            options.ba_global_frames_ratio = 1.2
            options.ba_global_points_ratio = 1.2
            options.ba_global_frames_freq = 100
            options.ba_global_points_freq = 100000
            
            # Improve mapper options
            mapper_options = options.get_mapper()
            mapper_options.init_min_num_inliers = 80
            mapper_options.init_max_error = 6.0
            mapper_options.abs_pose_min_num_inliers = 25
            mapper_options.abs_pose_min_inlier_ratio = 0.2
            mapper_options.filter_min_tri_angle = 1.0
            
            # Create and run the pipeline
            pipeline = pycolmap.IncrementalPipeline(
                options=options,
                image_path=images_folder,
                database_path=database_path
            )
            pipeline.run()
            
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
                print(f"[COLMAP] DIAGNOSIS: Reconstruction failure likely due to:")
                print(f"  1. Insufficient feature matches between images")
                print(f"  2. Poor image quality or too few distinctive features")
                print(f"  3. Images are too similar (not enough viewpoint variation)")
                print(f"  4. Images are too different (no common features)")
                print(f"  5. Insufficient camera motion between images")
                print(f"[COLMAP] SOLUTIONS:")
                print(f"  - Use higher quality images with more texture")
                print(f"  - Ensure images have sufficient overlap (60-80%)")
                print(f"  - Capture images from different viewpoints")
                print(f"  - Check that images are not corrupted")
                print(f"  - Try reducing --max-image-size for faster processing")
                print(f"  - Try increasing --max-features for more features")
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
            
            # Export to TXT format using the correct method
            reconstruction.write_text(sparse_folder)
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
            output_path=dense_folder,
            input_path=sparse_folder,
            image_path=images_folder,
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