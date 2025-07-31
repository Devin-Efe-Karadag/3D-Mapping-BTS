# 3D Reconstruction Pipeline

A Python-based pipeline for 3D reconstruction using COLMAP and mesh comparison using CloudCompare.

## ⚠️ Important: CUDA Requirement

**This project requires CUDA support for dense 3D reconstruction.** 

- **Systems without CUDA (like Macs without NVIDIA GPU) will fail early with a clear error message**
- **For full functionality, you must use a system with NVIDIA GPU and CUDA**
- The pipeline will automatically detect CUDA availability and stop if not available

## Dependencies

### Python Dependencies
Install these using pip:
```bash
pip install -r requirements.txt
```

### System Dependencies

#### COLMAP
COLMAP is required for 3D reconstruction. Install it based on your system:

**macOS:**
```bash
brew install colmap
```

**Windows:**
Download from [COLMAP releases](https://github.com/colmap/colmap/releases)

**From Source:**
See [COLMAP installation guide](https://colmap.github.io/install.html#build-from-source)

#### CloudCompare
CloudCompare is required for mesh comparison. Install it based on your system:

**macOS:**
Download from [CloudCompare website](https://www.danielgm.net/cc/)

**Windows:**
Download from [CloudCompare website](https://www.danielgm.net/cc/)

## Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd OdineProj
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

4. **Install system dependencies:**
   - **COLMAP**: See installation instructions above
   - **CloudCompare**: See installation instructions above

5. **Run setup validation:**
```bash
cd src
python setup.py
```

6. **Run the pipeline:**
```bash
python main.py
```

## Usage

### Basic Usage
```bash
# Run with default settings
python main.py

# Run with custom timestamps
python main.py --timestamps timestamp1 timestamp3

# Skip comparison step (only reconstruction)
python main.py --skip-comparison

# Skip report generation
python main.py --skip-report
```

### COLMAP Parameters
You can customize COLMAP reconstruction parameters:

```bash
# High quality reconstruction (slower)
python main.py --max-image-size 3200 --max-features 4096 --min-matches 20

# Fast reconstruction (lower quality)
python main.py --max-image-size 800 --max-features 1024 --min-matches 10

# Custom dense reconstruction
python main.py --dense-image-size 3000 --window-radius 7 --window-step 3
```

### Available Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max-image-size` | 1600 | Maximum image size for feature extraction |
| `--max-features` | 2048 | Maximum number of features to extract |
| `--max-ratio` | 0.8 | Maximum ratio for feature matching |
| `--max-distance` | 0.7 | Maximum distance for feature matching |
| `--min-matches` | 15 | Minimum matches for reconstruction |
| `--max-iterations` | 50 | Bundle adjustment iterations |
| `--max-refinements` | 3 | Bundle adjustment refinements |
| `--dense-image-size` | 2000 | Image size for dense reconstruction |
| `--window-radius` | 5 | Window radius for dense stereo |
| `--window-step` | 2 | Window step for dense stereo |
| `--timestamps` | timestamp1 timestamp2 | Folders to process |
| `--skip-comparison` | False | Skip CloudCompare comparison |
| `--skip-report` | False | Skip PDF report generation |

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

### 2. CloudCompare Comparison Outputs
```
outputs/run_YYYYMMDD_HHMMSS/comparison/run_YYYYMMDD_HHMMSS/
├── cloudcompare_c2c_distances.csv      # Cloud-to-cloud distances
├── cloudcompare_c2c_screenshot.png     # C2C visualization
├── cloudcompare_c2c_report.txt         # C2C statistics
├── cloudcompare_c2m_distances.csv      # Cloud-to-mesh distances
├── cloudcompare_c2m_screenshot.png     # C2M visualization
├── cloudcompare_c2m_report.txt         # C2M statistics
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