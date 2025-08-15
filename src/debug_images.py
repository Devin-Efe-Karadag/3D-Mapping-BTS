#!/usr/bin/env python3
"""
Debug script to check image files and diagnose COLMAP issues
"""
import os
import sys
from PIL import Image
import sqlite3

def check_images_folder(folder_path):
    """Check images in a folder for common issues"""
    print(f"🔍 Checking images in: {folder_path}")
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return False
    
    # Find image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = [f for f in os.listdir(folder_path) 
                   if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not image_files:
        print(f"❌ No image files found in {folder_path}")
        return False
    
    print(f"📸 Found {len(image_files)} image files")
    
    # Check each image
    valid_images = []
    total_size = 0
    
    for img_file in image_files:
        img_path = os.path.join(folder_path, img_file)
        try:
            file_size = os.path.getsize(img_path)
            total_size += file_size
            
            with Image.open(img_path) as img:
                width, height = img.size
                mode = img.mode
                
                if width > 0 and height > 0:
                    valid_images.append(img_file)
                    print(f"  ✅ {img_file}: {width}x{height} ({mode}) - {file_size} bytes")
                else:
                    print(f"  ❌ {img_file}: Invalid dimensions {width}x{height}")
                    
        except Exception as e:
            print(f"  ❌ {img_file}: Error - {e}")
    
    print(f"\n📊 Summary:")
    print(f"  Total images: {len(image_files)}")
    print(f"  Valid images: {len(valid_images)}")
    print(f"  Total size: {total_size} bytes ({total_size/1024/1024:.2f} MB)")
    
    if len(valid_images) == 0:
        print(f"❌ No valid images found!")
        return False
    
    return True

def check_database(database_path):
    """Check COLMAP database for features"""
    print(f"\n🗄️ Checking database: {database_path}")
    
    if not os.path.exists(database_path):
        print(f"❌ Database not found: {database_path}")
        return False
    
    db_size = os.path.getsize(database_path)
    print(f"📁 Database size: {db_size} bytes ({db_size/1024:.2f} KB)")
    
    if db_size < 1024:
        print(f"❌ Database is too small - likely empty")
        return False
    
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tables: {', '.join(tables)}")
        
        # Check keypoints
        if 'keypoints' in tables:
            cursor.execute("SELECT COUNT(*) FROM keypoints")
            keypoint_count = cursor.fetchone()[0]
            print(f"🔑 Keypoints: {keypoint_count}")
            
            if keypoint_count > 0:
                cursor.execute("SELECT COUNT(DISTINCT image_id) FROM keypoints")
                image_count = cursor.fetchone()[0]
                print(f"🖼️ Images with keypoints: {image_count}")
            else:
                print(f"❌ No keypoints found!")
                
        # Check descriptors
        if 'descriptors' in tables:
            cursor.execute("SELECT COUNT(*) FROM descriptors")
            descriptor_count = cursor.fetchone()[0]
            print(f"📝 Descriptors: {descriptor_count}")
        
        # Check images
        if 'images' in tables:
            cursor.execute("SELECT COUNT(*) FROM images")
            image_count = cursor.fetchone()[0]
            print(f"🖼️ Images in database: {image_count}")
            
            if image_count > 0:
                cursor.execute("SELECT name FROM images LIMIT 5")
                image_names = [row[0] for row in cursor.fetchall()]
                print(f"📸 Sample images: {', '.join(image_names)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return False
    
    return True

def main():
    """Main debug function"""
    print("🔍 COLMAP Image Debug Tool")
    print("=" * 50)
    
    # Check timestamp1
    timestamp1_path = "data/timestamp1/images"
    if check_images_folder(timestamp1_path):
        print(f"✅ Timestamp1 images are valid")
    else:
        print(f"❌ Timestamp1 has issues")
    
    # Check timestamp2
    timestamp2_path = "data/timestamp2/images"
    if check_images_folder(timestamp2_path):
        print(f"✅ Timestamp2 images are valid")
    else:
        print(f"❌ Timestamp2 has issues")
    
    # Check if there are any existing databases
    outputs_dir = "outputs"
    if os.path.exists(outputs_dir):
        print(f"\n🔍 Checking existing outputs...")
        for run_dir in os.listdir(outputs_dir):
            if run_dir.startswith("run_"):
                run_path = os.path.join(outputs_dir, run_dir)
                for timestamp_dir in os.listdir(run_path):
                    if timestamp_dir in ["timestamp1", "timestamp2"]:
                        db_path = os.path.join(run_path, timestamp_dir, "database.db")
                        if os.path.exists(db_path):
                            print(f"\n📁 Found database: {db_path}")
                            check_database(db_path)
    
    print(f"\n💡 Recommendations:")
    print(f"  - Ensure images are in JPG, PNG, or TIFF format")
    print(f"  - Images should have distinctive features (not plain walls)")
    print(f"  - Images should have good contrast and lighting")
    print(f"  - Images should overlap by 60-80% for good matching")
    print(f"  - Avoid motion blur or very similar images")

if __name__ == "__main__":
    main()
