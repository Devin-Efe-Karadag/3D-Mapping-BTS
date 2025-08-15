# 🚀 Performance Optimization Guide

## Overview

This guide explains how to use the new performance optimization features in the 3D Reconstruction Pipeline to significantly reduce processing time while maintaining acceptable quality for your use case.

## ⚡ Performance Modes

### 1. **Fast Mode** (`--fast-mode`)
- **Speed Improvement**: 2-3x faster than standard
- **Quality**: Good quality reconstruction
- **Best For**: Development, testing, quick results
- **Settings Applied**:
  - Image resolution: 1200px (vs 1600px default)
  - Feature count: 1024 (vs 2048 default)
  - Dense resolution: 1500px (vs 2000px default)
  - Window radius: 4 (vs 5 default)
  - Spatial neighbors: 30 (vs 50 default)
  - Batch size: 8 (vs 10 default)

### 2. **Ultra-Fast Mode** (`--ultra-fast-mode`)
- **Speed Improvement**: 5-10x faster than standard
- **Quality**: Basic quality reconstruction
- **Best For**: Rapid prototyping, debugging, time-critical scenarios
- **Settings Applied**:
  - Image resolution: 800px (vs 1600px default)
  - Feature count: 512 (vs 2048 default)
  - Dense resolution: 1000px (vs 2000px default)
  - Window radius: 3 (vs 5 default)
  - Window step: 3 (vs 2 default)
  - Spatial neighbors: 20 (vs 50 default)
  - Batch size: 5 (vs 10 default)

### 3. **Sparse Only** (`--skip-dense`)
- **Speed Improvement**: 80% faster (sparse reconstruction only)
- **Quality**: Point cloud without dense reconstruction
- **Best For**: When you only need sparse 3D points
- **Output**: Sparse point cloud, no dense reconstruction or mesh

### 4. **Point Cloud Only** (`--skip-mesh`)
- **Speed Improvement**: 20% faster (no mesh generation)
- **Quality**: Dense point cloud without mesh
- **Best For**: When mesh quality isn't critical
- **Output**: Dense point cloud, no mesh file

## 🎯 Usage Examples

### Quick Development/Testing
```bash
# Fast mode for development
python main.py --fast-mode

# Ultra-fast mode for debugging
python main.py --ultra-fast-mode
```

### Maximum Speed (Minimal Quality)
```bash
# Ultra-fast with sparse only
python main.py --ultra-fast-mode --skip-dense

# Ultra-fast with no mesh
python main.py --ultra-fast-mode --skip-dense --skip-mesh
```

### Custom Optimization
```bash
# Custom fast settings
python main.py --max-image-size 800 --max-features 512 --dense-image-size 1000

# Minimal processing
python main.py --max-image-size 600 --max-features 256 --dense-image-size 800
```

### Production vs Development
```bash
# Production (full quality)
python main.py

# Development (fast)
python main.py --fast-mode

# Testing (ultra-fast)
python main.py --ultra-fast-mode --skip-dense
```

## 📊 Performance Estimates

| Mode | Time | Quality | Use Case |
|------|------|---------|----------|
| **Standard** | 60 min | High | Production, research |
| **Fast** | 20-30 min | Good | Development, testing |
| **Ultra-Fast** | 6-12 min | Basic | Prototyping, debugging |
| **Sparse Only** | 12 min | Medium | Quick 3D overview |
| **Custom** | Variable | Variable | Specific requirements |

## 🔧 Parameter Reference

### Image Processing
- `--max-image-size`: Maximum image size for feature extraction
  - **Default**: 1600px
  - **Fast**: 1200px
  - **Ultra-fast**: 800px
  - **Lower = Faster** (but less detail)

- `--max-features`: Maximum number of features to extract
  - **Default**: 2048
  - **Fast**: 1024
  - **Ultra-fast**: 512
  - **Lower = Faster** (but less accurate matching)

### Dense Reconstruction
- `--dense-image-size`: Maximum image size for dense reconstruction
  - **Default**: 2000px
  - **Fast**: 1500px
  - **Ultra-fast**: 1000px
  - **Lower = Faster** (but lower resolution)

- `--window-radius`: Window radius for dense stereo
  - **Default**: 5
  - **Fast**: 4
  - **Ultra-fast**: 3
  - **Lower = Faster** (but less smooth)

- `--window-step`: Window step for dense stereo
  - **Default**: 2
  - **Fast**: 2
  - **Ultra-fast**: 3
  - **Higher = Faster** (but less detailed)

### Matching & Processing
- `--max-neighbors`: Maximum neighbors for spatial matching
  - **Default**: 50
  - **Fast**: 30
  - **Ultra-fast**: 20
  - **Lower = Faster** (but less coverage)

- `--batch-size`: Processing batch size
  - **Default**: 10
  - **Fast**: 8
  - **Ultra-fast**: 5
  - **Lower = Faster** (but less accurate)

## 🚨 Quality vs Speed Trade-offs

### **High Quality (Standard Mode)**
- ✅ Maximum detail and accuracy
- ✅ Best reconstruction quality
- ✅ Suitable for production
- ❌ Slowest processing time
- ❌ Highest resource usage

### **Balanced (Fast Mode)**
- ✅ Good quality for most use cases
- ✅ 2-3x speed improvement
- ✅ Suitable for development
- ⚠️ Some detail loss
- ⚠️ Moderate resource usage

### **Basic Quality (Ultra-Fast Mode)**
- ✅ Maximum speed improvement
- ✅ Suitable for prototyping
- ✅ Low resource usage
- ❌ Significant detail loss
- ❌ Basic reconstruction quality

### **Sparse Only**
- ✅ 80% time savings
- ✅ Good for overview/planning
- ❌ No dense reconstruction
- ❌ No mesh generation

## 💡 Best Practices

### **For Development**
1. Start with `--fast-mode` for good balance
2. Use `--ultra-fast-mode` for debugging
3. Skip dense reconstruction when testing features

### **For Production**
1. Use standard mode for final results
2. Consider `--fast-mode` if time is critical
3. Test performance modes on sample data first

### **For Research**
1. Use standard mode for publication-quality results
2. Use fast modes for parameter exploration
3. Document which mode was used for reproducibility

## 🔍 Troubleshooting

### **Common Issues**

#### **Quality Too Low**
- Increase `--max-image-size` (e.g., 1200, 1600)
- Increase `--max-features` (e.g., 1024, 2048)
- Use `--fast-mode` instead of `--ultra-fast-mode`

#### **Still Too Slow**
- Use `--ultra-fast-mode`
- Add `--skip-dense` for sparse only
- Lower `--max-image-size` further (e.g., 600)
- Lower `--max-features` further (e.g., 256)

#### **Memory Issues**
- Lower `--max-image-size`
- Lower `--dense-image-size`
- Use `--skip-dense` for sparse only

### **Performance Monitoring**
The pipeline shows:
- Current performance mode
- Estimated processing time
- Speed improvements
- Final parameter values
- Total processing time

## 📚 Additional Resources

- **Test Script**: `python test_performance.py`
- **Help**: `python main.py --help`
- **Examples**: See help output for usage examples
- **README**: Comprehensive project documentation

## 🎉 Quick Start Commands

```bash
# Test performance features
python test_performance.py

# Fast development
python main.py --fast-mode

# Maximum speed
python main.py --ultra-fast-mode --skip-dense

# Custom optimization
python main.py --max-image-size 800 --max-features 512
```

---

**Remember**: Start with `--fast-mode` for development, use standard mode for production, and experiment with custom parameters to find your optimal balance of speed vs. quality!
