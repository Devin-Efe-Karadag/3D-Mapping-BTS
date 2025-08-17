# 3D Reconstruction Pipeline

A Python-based pipeline for 3D reconstruction using COLMAP and custom 3D mesh analysis.

## ⚠️ CUDA Requirement

**This project requires CUDA for dense 3D reconstruction.**

- Systems without CUDA (like Macs without NVIDIA GPU) will fail with a clear error message
- Use a system with NVIDIA GPU and CUDA for full functionality
- The pipeline automatically detects CUDA availability

## Dependencies

### Python Dependencies
Install these using pip:
```bash
pip install -r requirements.txt
```

### System Dependencies

#### COLMAP
COLMAP is required for 3D reconstruction. Build it from source following the [official installation guide](https://colmap.github.io/install.html).

#### Custom 3D Mesh Analysis
The pipeline includes custom Python implementations for 3D mesh analysis. All functionality is provided through Python libraries:

**Required Python packages:**
```bash
pip install open3d numpy pandas matplotlib scipy scikit-learn
```

**Features:**
- **ICP Alignment**: Iterative Closest Point mesh alignment using Open3D
- **Cloud-to-Cloud (C2C)**: Point-to-point distance computation between meshes
- **Cloud-to-Mesh (C2M)**: Signed distance computation with inside/outside detection
- **Mesh Measurements**: Surface area, volume, and quality metrics calculation
- **Visualizations**: Distance distribution plots and statistical analysis

## Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd 3D-Mapping-BTS
```

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Build COLMAP from source:**
   - Follow the [official COLMAP installation guide](https://colmap.github.io/install.html)
   - Ensure CUDA support is enabled during compilation

5. **Run the pipeline:**
```bash
python main.py
```

## Usage

### Basic Usage
```bash
# Run with default settings
python main.py
```

The pipeline automatically:
1. **Extracts features** from images using COLMAP with GPU acceleration
2. **Matches features** between images using sequential and transitive matching
3. **Creates sparse reconstruction** using hierarchical mapping
4. **Performs dense reconstruction** using patch match stereo
5. **Generates 3D meshes** using Poisson meshing
6. **Runs custom 3D analysis** including ICP alignment and distance measurements

### Understanding the Pipeline

Our pipeline adapts the standard COLMAP workflow described in the [COLMAP CLI documentation](https://colmap.github.io/cli.html) with the following modifications:

- **GPU acceleration** enabled for all supported operations
- **Minimal parameter tuning** - uses COLMAP's intelligent defaults
- **Custom 3D mesh analysis** after reconstruction
- **Automated pipeline execution** - no manual step-by-step commands needed

## Expected Outputs

### 1. COLMAP Reconstruction Outputs
```
outputs/run_YYYYMMDD_HHMMSS/
├── timestamp1/
│   ├── database.db          # COLMAP database
│   ├── sparse/              # Sparse reconstruction
│   ├── dense/               # Dense reconstruction
│   └── mesh/
│       └── model.obj        # 3D mesh file
└── timestamp2/
    └── [same structure]
```

**What these files mean:**
- **`database.db`**: COLMAP database with features and matches
- **`sparse/`**: Camera poses and sparse 3D points
- **`dense/`**: Dense point cloud and depth maps
- **`model.obj`**: Final 3D mesh ready for comparison

### 2. Custom 3D Mesh Comparison Outputs
```
outputs/run_YYYYMMDD_HHMMSS/comparison/run_YYYYMMDD_HHMMSS/
├── custom_c2c_distances.csv            # Cloud-to-cloud distances
├── custom_c2c_visualization.png        # C2C visualization
├── custom_c2c_report.txt               # C2C statistics
├── custom_c2m_distances.csv            # Cloud-to-mesh distances
├── custom_c2m_visualization.png        # C2M visualization
├── custom_c2m_report.txt               # C2M statistics
├── mesh1_measure.txt                   # Mesh1 area/volume
├── mesh2_measure.txt                   # Mesh2 area/volume
├── summary.txt                         # Human-readable summary
└── report.pdf                          # Comprehensive PDF report
```

**What these files mean:**
- **C2C distances**: Point-to-point distances between meshes
- **C2M distances**: Signed distances (positive = outside, negative = inside)
- **Screenshots**: Visual representations of differences
- **Statistics**: Mean, max, min, standard deviation of distances
- **Measurements**: Surface area and volume of each mesh
- **Summary**: Human-readable interpretation of results
- **PDF Report**: Complete analysis with plots and tables

## Custom 3D Mesh Analysis

The pipeline includes custom Python implementations for 3D mesh analysis:

### Features Implemented

- **ICP Alignment**: Iterative Closest Point algorithm for aligning two 3D meshes
- **Cloud-to-Cloud (C2C)**: Computes point-to-point distances between corresponding locations on two meshes
- **Cloud-to-Mesh (C2M)**: Computes signed distances from one mesh to another (positive = outside, negative = inside)
- **Mesh Measurements**: Calculates surface area, volume, and quality metrics for individual meshes
- **Visualizations**: Generates distance distribution plots and statistical analysis charts

### Technical Details

- **Open3D**: Used for mesh loading, point cloud operations, and ICP alignment
- **NumPy**: Numerical computations and statistical analysis
- **Pandas**: Data export to CSV format
- **Matplotlib**: Visualization generation (optional dependency)





## Understanding the Results

### Distance Metrics
- **C2C (Cloud-to-Cloud)**: Measures how far apart corresponding points are
- **C2M (Cloud-to-Mesh)**: Measures signed distance from one mesh to another
  - **Positive values**: Points outside the reference mesh
  - **Negative values**: Points inside the reference mesh

### What the Numbers Mean
- **Mean distance**: Average difference between meshes
- **Max distance**: Largest local difference (highlights major changes)
- **Standard deviation**: How consistent the differences are
- **RMS**: Root mean square error (overall quality metric)

### Interpreting Results
- **Small distances (< 1cm)**: Good alignment, minor differences
- **Medium distances (1-5cm)**: Noticeable differences, check alignment
- **Large distances (> 5cm)**: Significant differences or poor alignment
- **High standard deviation**: Inconsistent differences across the model

### Area/Volume Changes
- **Positive area difference**: Surface area increased
- **Negative area difference**: Surface area decreased
- **Positive volume difference**: Volume increased
- **Negative volume difference**: Volume decreased 