"""
Configuration file for cross-platform compatibility
"""
import os
import platform
import subprocess
from pathlib import Path

class Config:
    """Cross-platform configuration for the 3D reconstruction pipeline"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_macos = self.system == "Darwin"
        self.is_linux = self.system == "Linux"
        
        # Project paths (relative to src directory)
        self.data_dir = "data"
        self.outputs_dir = "outputs"
        
        # Timestamp folders (configurable)
        self.timestamps = ["timestamp1", "timestamp2"]
        
        # Custom 3D mesh analysis implementation
        pass
        
        # Find COLMAP executable
        self.colmap_path = self._find_colmap()
    
    # Custom 3D mesh analysis implementation - no external dependencies needed
    
    def _find_colmap(self):
        """Find COLMAP executable based on platform"""
        possible_paths = []
        
        if self.is_macos:
            possible_paths = [
                "/opt/homebrew/bin/colmap",
                "/usr/local/bin/colmap",
                "/Applications/COLMAP.app/Contents/MacOS/colmap"
            ]
        elif self.is_linux:
            possible_paths = [
                "/usr/bin/colmap",
                "/usr/local/bin/colmap"
            ]
        elif self.is_windows:
            possible_paths = [
                "C:\\Program Files\\COLMAP\\colmap.exe",
                "C:\\Program Files (x86)\\COLMAP\\colmap.exe",
                "colmap.exe"  # If in PATH
            ]
        
        # Check if COLMAP is in PATH
        try:
            result = subprocess.run(["which", "colmap"] if not self.is_windows else ["where", "colmap"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                possible_paths.append(result.stdout.strip())
        except:
            pass
        
        # Try each possible path
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If not found, return None and let the user know
        return None
    
    def get_data_path(self, timestamp):
        """Get path to data directory for a specific timestamp"""
        return os.path.join(self.data_dir, timestamp, "images")
    
    def get_output_path(self, timestamp, run_id):
        """Get path to output directory for a specific timestamp and run"""
        return os.path.join(self.outputs_dir, run_id, timestamp)
    
    def get_mesh_path(self, timestamp, run_id):
        """Get expected mesh file path for a specific timestamp and run"""
        return os.path.join(self.outputs_dir, run_id, timestamp, "model.obj")
    
    def validate_setup(self):
        """Validate that all required dependencies are available"""
        errors = []
        warnings = []
        
        # Check COLMAP
        if not self.colmap_path:
            errors.append("COLMAP not found. Please install COLMAP:")
            if self.is_macos:
                errors.append("  brew install colmap")
            elif self.is_linux:
                errors.append("  sudo apt-get install colmap")
            elif self.is_windows:
                errors.append("  Download from https://github.com/colmap/colmap/releases")
        else:
            print(f"COLMAP found at: {self.colmap_path}")
        
        # Custom 3D mesh analysis implementation
        print("3D Mesh Analysis: Custom Python implementation")
        
        # Check data directories
        for timestamp in self.timestamps:
            data_path = self.get_data_path(timestamp)
            if not os.path.exists(data_path):
                warnings.append(f"Data directory not found: {data_path}")
                warnings.append(f"  Expected structure: {self.data_dir}/{timestamp}/images/")
        
        # Check if running from correct directory
        if not os.path.exists(self.data_dir):
            errors.append(f"Data directory '{self.data_dir}' not found.")
            errors.append("Make sure you're running from the src/ directory.")
        
        return errors, warnings
    
    def _check_cuda_availability(self):
        """Check if CUDA is available for dense reconstruction"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            # Fallback to COLMAP-based detection if PyTorch not available
            if self.colmap_path:
                try:
                    result = subprocess.run([self.colmap_path, "patch_match_stereo", "--help"], 
                                          capture_output=True, text=True, timeout=10)
                    # Check if CUDA-related options are available
                    if "cuda" in result.stdout.lower() or "gpu" in result.stdout.lower():
                        return True
                except:
                    pass
            return False
    
    def print_setup_info(self):
        """Print current configuration"""
        print("Configuration:")
        print(f"  Platform: {self.system}")
        print(f"  Data directory: {self.data_dir}")
        print(f"  Outputs directory: {self.outputs_dir}")
        print(f"  Timestamps: {', '.join(self.timestamps)}")
        print(f"  COLMAP: {self.colmap_path or 'NOT FOUND'}")
        print(f"  3D Mesh Analysis: Custom Python implementation")

# Global config instance
config = Config() 