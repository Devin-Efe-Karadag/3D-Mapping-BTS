#!/usr/bin/env python3
"""
Test script to check available pycolmap API functions
"""
import pycolmap

def test_pycolmap_api():
    """Test what pycolmap functions are available"""
    print("🔍 Testing pycolmap API availability")
    print("=" * 50)
    
    # Check pycolmap version
    print(f"pycolmap version: {pycolmap.__version__}")
    print()
    
    # List all available attributes and functions
    print("📋 Available pycolmap functions and attributes:")
    print("-" * 40)
    
    available_functions = []
    unavailable_functions = []
    
    # Test common functions
    functions_to_test = [
        'mapper',
        'reconstruction', 
        'model_converter',
        'undistort_images',
        'extract_features',
        'match_exhaustive',
        'match_spatial',
        'patch_match_stereo',
        'stereo_fusion',
        'poisson_mesher',
        'has_cuda',
        'Database',
        'Reconstruction'
    ]
    
    for func_name in functions_to_test:
        if hasattr(pycolmap, func_name):
            func = getattr(pycolmap, func_name)
            if callable(func):
                available_functions.append(f"✅ {func_name}() - function")
            else:
                available_functions.append(f"✅ {func_name} - attribute")
        else:
            unavailable_functions.append(f"❌ {func_name} - not found")
    
    # Print available functions
    for func in available_functions:
        print(func)
    
    print()
    
    # Print unavailable functions
    if unavailable_functions:
        print("❌ Unavailable functions:")
        for func in unavailable_functions:
            print(func)
        print()
    
    # Test specific function signatures
    print("🔧 Testing function signatures:")
    print("-" * 40)
    
    if hasattr(pycolmap, 'mapper'):
        try:
            import inspect
            sig = inspect.signature(pycolmap.mapper)
            print(f"mapper{str(sig)}")
        except:
            print("mapper() - signature inspection failed")
    
    if hasattr(pycolmap, 'extract_features'):
        try:
            import inspect
            sig = inspect.signature(pycolmap.extract_features)
            print(f"extract_features{str(sig)}")
        except:
            print("extract_features() - signature inspection failed")
    
    if hasattr(pycolmap, 'match_exhaustive'):
        try:
            import inspect
            sig = inspect.signature(pycolmap.match_exhaustive)
            print(f"match_exhaustive{str(sig)}")
        except:
            print("match_exhaustive() - signature inspection failed")
    
    print()
    
    # Test CUDA availability
    print("🚀 CUDA Support:")
    print("-" * 40)
    if hasattr(pycolmap, 'has_cuda'):
        try:
            cuda_available = pycolmap.has_cuda()
            print(f"CUDA available: {cuda_available}")
        except Exception as e:
            print(f"CUDA check failed: {e}")
    else:
        print("has_cuda() function not available")
    
    print()
    print("=" * 50)
    print("💡 Recommendations:")
    
    if len(available_functions) > len(unavailable_functions):
        print("✅ Most pycolmap functions are available")
        print("   You can use the pycolmap API directly")
    else:
        print("❌ Many pycolmap functions are missing")
        print("   You may need to use subprocess fallbacks")
    
    print()
    print("🔧 Next steps:")
    print("1. Check if the available functions work with your data")
    print("2. Use subprocess fallbacks for missing functions")
    print("3. Consider updating pycolmap if many functions are missing")

if __name__ == "__main__":
    test_pycolmap_api()
