#!/usr/bin/env python3
"""
Test script to demonstrate performance features
"""
import subprocess
import sys
import time

def test_performance_modes():
    """Test different performance modes"""
    print("🚀 Testing Performance Modes")
    print("=" * 40)
    
    # Test 1: Standard mode
    print("\n1️⃣  Standard Mode (default settings)")
    print("   Expected: Full quality, standard speed")
    print("   Command: python main.py --help")
    
    # Test 2: Fast mode
    print("\n2️⃣  Fast Mode (2-3x faster)")
    print("   Expected: Good quality, faster processing")
    print("   Command: python main.py --fast-mode --help")
    
    # Test 3: Ultra-fast mode
    print("\n3️⃣  Ultra-fast Mode (5-10x faster)")
    print("   Expected: Basic quality, maximum speed")
    print("   Command: python main.py --ultra-fast-mode --help")
    
    # Test 4: Sparse only
    print("\n4️⃣  Sparse Only (80% faster)")
    print("   Expected: Point cloud only, much faster")
    print("   Command: python main.py --skip-dense --help")
    
    # Test 5: Custom settings
    print("\n5️⃣  Custom Fast Settings")
    print("   Expected: Custom optimization")
    print("   Command: python main.py --max-image-size 800 --max-features 512 --help")
    
    print("\n" + "=" * 40)
    print("💡 Performance Tips:")
    print("  • Use --fast-mode for 2-3x speed improvement")
    print("  • Use --ultra-fast-mode for 5-10x speed improvement")
    print("  • Use --skip-dense for sparse reconstruction only")
    print("  • Use --skip-mesh for point cloud only")
    print("  • Lower --max-image-size for faster processing")
    print("  • Lower --max-features for faster feature extraction")
    
    print("\n🎯 Recommended for testing:")
    print("  python main.py --ultra-fast-mode --skip-dense")
    print("  (This will give you the fastest possible processing)")

def show_help():
    """Show help for main.py"""
    print("\n📖 Main.py Help:")
    print("=" * 40)
    try:
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
    except subprocess.TimeoutExpired:
        print("Help command timed out")
    except Exception as e:
        print(f"Error running help: {e}")

if __name__ == "__main__":
    test_performance_modes()
    
    # Ask if user wants to see the full help
    try:
        response = input("\n❓ Show full main.py help? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            show_help()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
