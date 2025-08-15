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
        
        # Get the directory where this config file is located (src directory)
        self.src_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Detect if we're in a cloud environment (Colab, etc.)
        self.is_cloud = self._detect_cloud_environment()
        
        # Timestamp folders (configurable)
        self.timestamps = ["timestamp1", "timestamp2"]
        
        # Custom 3D mesh analysis implementation
        pass
        
        # pycolmap is used instead of COLMAP executable
        self.colmap_path = None
    
    def _detect_cloud_environment(self):
        """Detect if we're running in a cloud environment (Colab, etc.)"""
        # Check for common cloud environment indicators
        cloud_indicators = [
            '/content/',  # Google Colab
            '/tmp/',      # Temporary cloud environments
            '/home/notebook/',  # Some cloud platforms
            '/workspace/',  # Gitpod, etc.
        ]
        
        current_path = os.getcwd()
        for indicator in cloud_indicators:
            if indicator in current_path:
                return True
        return False
    
    # Custom 3D mesh analysis implementation - no external dependencies needed
    
    # COLMAP executable finding removed - using pycolmap instead
    
    def get_data_path(self, timestamp):
        """Get path to data directory for a specific timestamp"""
        if self.is_cloud:
            # In cloud environments, use current working directory
            return os.path.join(os.getcwd(), self.data_dir, timestamp, "images")
        else:
            # In local environments, use src directory
            return os.path.join(self.src_dir, self.data_dir, timestamp, "images")
    
    def get_output_path(self, timestamp, run_id):
        """Get path to output directory for a specific timestamp and run"""
        if self.is_cloud:
            # In cloud environments, use current working directory
            return os.path.join(os.getcwd(), self.outputs_dir, run_id, timestamp)
        else:
            # In local environments, use src directory
            return os.path.join(self.src_dir, self.outputs_dir, run_id, timestamp)
    
    def get_mesh_path(self, timestamp, run_id):
        """Get expected mesh file path for a specific timestamp and run"""
        if self.is_cloud:
            # In cloud environments, use current working directory
            return os.path.join(os.getcwd(), self.outputs_dir, run_id, timestamp, "model.obj")
        else:
            # In local environments, use src directory
            return os.path.join(self.src_dir, self.outputs_dir, run_id, timestamp, "model.obj")
    
    def validate_setup(self):
        """Validate that all required dependencies are available"""
        errors = []
        warnings = []
        
        # Check pycolmap
        try:
            import pycolmap
            print(f"pycolmap found: version {pycolmap.__version__}")
        except ImportError:
            errors.append("pycolmap not found. Please install pycolmap:")
            errors.append("  pip install pycolmap")
        
        # Custom 3D mesh analysis implementation
        print("3D Mesh Analysis: Custom Python implementation")
        
        # Check data directories
        for timestamp in self.timestamps:
            data_path = self.get_data_path(timestamp)
            if not os.path.exists(data_path):
                warnings.append(f"Data directory not found: {data_path}")
                warnings.append(f"  Expected structure: {self.data_dir}/{timestamp}/images/")
        
        # Check if running from correct directory
        if self.is_cloud:
            # In cloud environments, check current working directory
            data_path = os.path.join(os.getcwd(), self.data_dir)
            if not os.path.exists(data_path):
                errors.append(f"Data directory '{data_path}' not found.")
                errors.append("Make sure the data directory exists in the current working directory.")
        else:
            # In local environments, check src directory
            data_path = os.path.join(self.src_dir, self.data_dir)
            if not os.path.exists(data_path):
                errors.append(f"Data directory '{data_path}' not found.")
                errors.append("Make sure the data directory exists in the src/ folder.")
        
        return errors, warnings
    
    def _check_cuda_availability(self):
        """Check if CUDA is available for dense reconstruction"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            # Fallback to pycolmap-based detection if PyTorch not available
            try:
                import pycolmap
                # Check if pycolmap supports CUDA
                return hasattr(pycolmap, 'has_cuda') and pycolmap.has_cuda()
            except:
                pass
            return False
    
    def print_setup_info(self):
        """Print current configuration"""
        print("Configuration:")
        print(f"  Platform: {self.system}")
        print(f"  Environment: {'Cloud' if self.is_cloud else 'Local'}")
        print(f"  Source directory: {self.src_dir}")
        
        if self.is_cloud:
            print(f"  Data directory: {os.path.join(os.getcwd(), self.data_dir)}")
            print(f"  Outputs directory: {os.path.join(os.getcwd(), self.outputs_dir)}")
        else:
            print(f"  Data directory: {os.path.join(self.src_dir, self.data_dir)}")
            print(f"  Outputs directory: {os.path.join(self.src_dir, self.outputs_dir)}")
            
        print(f"  Timestamps: {', '.join(self.timestamps)}")
        print(f"  pycolmap: Python library")
        print(f"  3D Mesh Analysis: Custom Python implementation")
    
    def setup_cloud_environment(self):
        """Set up directory structure for cloud environments"""
        if not self.is_cloud:
            return
            
        print(f"[SETUP] Setting up cloud environment...")
        
        # Create data directory structure if it doesn't exist
        data_dir = os.path.join(os.getcwd(), self.data_dir)
        if not os.path.exists(data_dir):
            print(f"[SETUP] Creating data directory: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
            
        # Create timestamp directories
        for timestamp in self.timestamps:
            timestamp_dir = os.path.join(data_dir, timestamp, "images")
            if not os.path.exists(timestamp_dir):
                print(f"[SETUP] Creating timestamp directory: {timestamp_dir}")
                os.makedirs(timestamp_dir, exist_ok=True)
                
        print(f"[SETUP] Cloud environment setup complete")

# Global config instance
config = Config() 