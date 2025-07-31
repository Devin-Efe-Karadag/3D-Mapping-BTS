#!/usr/bin/env python3
"""
Setup script for the 3D reconstruction pipeline
"""
import os
import sys
from config import config

def main():
    print("3D Reconstruction Pipeline Setup")
    print("=" * 50)
    
    # Print current configuration
    config.print_setup_info()
    print()
    
    # Validate setup
    print("Validating setup...")
    errors, warnings = config.validate_setup()
    
    if errors:
        print("Setup validation failed:")
        for error in errors:
            print(f"  {error}")
        print()
        print("Please fix the issues above and run setup again.")
        return False
    
    if warnings:
        print("Setup warnings:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    print("Setup validation passed!")
    print()
    
    # Check CUDA availability
    print("Checking CUDA availability...")
    if config.colmap_path:
        try:
            result = config._check_cuda_availability()
            if result:
                print("CUDA is available - full dense reconstruction will work")
            else:
                print("CUDA not available - dense reconstruction will fail")
                print("   This is expected on Mac systems without NVIDIA GPU")
        except Exception as e:
            print(f"Could not check CUDA availability: {e}")
    else:
        print("COLMAP not found - cannot check CUDA availability")
    
    print()
    print("Setup complete! You can now run:")
    print("   python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 