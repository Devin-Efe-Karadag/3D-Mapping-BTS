# 3D Reconstruction Pipeline

A Python-based pipeline for 3D reconstruction using COLMAP and custom 3D mesh analysis.

## ⚠️ CUDA Requirement

**This project requires CUDA for dense 3D reconstruction.**

- Systems without CUDA (like Macs without NVIDIA GPU) will fail with a clear error message
- Use a system with NVIDIA GPU and CUDA for full functionality
- The pipeline automatically detects CUDA availability

## 🖥️ Display Environment (Linux)

**On Linux systems, the pipeline automatically handles headless environments:**

- Automatically sets `QT_QPA_PLATFORM=offscreen` for Qt applications
- Attempts to start virtual display (`Xvfb`) if available
- Falls back to offscreen mode if virtual display fails
- No manual display configuration needed

## ☁️ Cloud Environment Support

**The pipeline automatically detects and adapts to cloud environments (Google Colab, etc.):**

- **Automatic detection**: Recognizes `/content/`, `/tmp/`, `/workspace/` paths
- **Path adaptation**: Uses current working directory instead of src directory
- **Directory creation**: Automatically creates required data structure
- **Cross-platform**: Works on both local and cloud systems

## Dependencies

### Python Dependencies
Install these using pip:
```bash
pip install -r requirements.txt
```

### System Dependencies

#### pycolmap
pycolmap is the Python library for 3D reconstruction. Install it via pip:

```bash
pip install pycolmap
```

**Note:** pycolmap automatically handles COLMAP backend installation and CUDA support.

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

4. **Install Python dependencies:**
   - **pycolmap**: `pip install pycolmap`
   - **Other packages**: `pip install -r requirements.txt`

5. **Run setup validation:**
```bash
cd src
python setup.py
```

6. **Test the custom implementations (optional but recommended):**
```bash
python test_custom_implementations.py
```

7. **Run the pipeline:**
   ```bash
   # Standard mode (full quality)
   python main.py
   
   # Fast mode (2-3x faster, good quality)
   python main.py --fast-mode
   
   # Ultra-fast mode (5-10x faster, basic quality)
   python main.py --ultra-fast-mode
   
   # Sparse reconstruction only (much faster)
   python main.py --skip-dense
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
| `--skip-comparison` | False | Skip custom 3D mesh comparison |
| `--skip-report` | False | Skip PDF report generation |

### Performance Tuning Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--fast-mode` | False | Enable fast mode (2-3x faster, good quality) |
| `--ultra-fast-mode` | False | Enable ultra-fast mode (5-10x faster, basic quality) |
| `--skip-dense` | False | Skip dense reconstruction (sparse only, much faster) |
| `--skip-mesh` | False | Skip mesh creation (point cloud only, faster) |
| `--max-neighbors` | 50 | Maximum neighbors for spatial matching (lower=faster) |
| `--batch-size` | 10 | Processing batch size (lower=faster but less accurate) |

## Performance Optimization

### 🚀 Performance Modes

The pipeline offers several performance modes to balance speed vs. quality:

#### **Fast Mode** (`--fast-mode`)
- **Speed**: 2-3x faster than standard
- **Quality**: Good quality reconstruction
- **Settings**: 1200px resolution, 1024 features, optimized parameters
- **Use case**: Development, testing, quick results

#### **Ultra-Fast Mode** (`--ultra-fast-mode`)
- **Speed**: 5-10x faster than standard
- **Quality**: Basic quality reconstruction
- **Settings**: 800px resolution, 512 features, minimal parameters
- **Use case**: Rapid prototyping, debugging, time-critical scenarios

#### **Sparse Only** (`--skip-dense`)
- **Speed**: 80% faster (sparse reconstruction only)
- **Quality**: Point cloud without dense reconstruction
- **Use case**: When you only need sparse 3D points

#### **Point Cloud Only** (`--skip-mesh`)
- **Speed**: 20% faster (no mesh generation)
- **Quality**: Dense point cloud without mesh
- **Use case**: When mesh quality isn't critical

### ⚡ Performance Tips

1. **For Development/Testing:**
   ```bash
   python main.py --fast-mode
   ```

2. **For Maximum Speed:**
   ```bash
   python main.py --ultra-fast-mode --skip-dense --skip-mesh
   ```

3. **For Balanced Speed/Quality:**
   ```bash
   python main.py --max-image-size 1200 --max-features 1024
   ```

4. **For Custom Optimization:**
   ```bash
   python main.py --max-image-size 800 --max-features 512 --dense-image-size 1000
   ```

### 📊 Performance Estimates

| Mode | Time | Quality | Use Case |
|------|------|---------|----------|
| **Standard** | 60 min | High | Production, research |
| **Fast** | 20-30 min | Good | Development, testing |
| **Ultra-Fast** | 6-12 min | Basic | Prototyping, debugging |
| **Sparse Only** | 12 min | Medium | Quick 3D overview |
| **Custom** | Variable | Variable | Specific requirements |

### 🔧 Advanced Performance Tuning

You can fine-tune individual parameters for optimal performance:

```bash
# Minimal processing for maximum speed
python main.py \
  --max-image-size 600 \
  --max-features 256 \
  --dense-image-size 800 \
  --window-radius 3 \
  --window-step 3 \
  --max-neighbors 20 \
  --batch-size 5

# Balanced speed/quality for development
python main.py \
  --max-image-size 1000 \
  --max-features 768 \
  --dense-image-size 1200 \
  --window-radius 4 \
  --window-step 2
```

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

### Testing

Run the test script to verify all custom implementations work correctly:
```bash
cd src
python test_custom_implementations.py
```

## Troubleshooting

### Qt Display Errors on Linux

If you encounter errors like:
```
qt.qpa.xcb: could not connect to display
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**The pipeline now automatically fixes this by:**
1. Setting `QT_QPA_PLATFORM=offscreen`
2. Attempting to start a virtual display (`Xvfb`)
3. Using headless mode as fallback

**Manual fix (if needed):**
```bash
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:0
```

### CUDA Issues

- **CUDA not available**: Use a system with NVIDIA GPU
- **CUDA version mismatch**: Update CUDA drivers and PyTorch
- **Memory errors**: Reduce `--dense-image-size` parameter

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