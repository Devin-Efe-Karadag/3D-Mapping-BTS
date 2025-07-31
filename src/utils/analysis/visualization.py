"""
Visualization Module
"""
import csv
import matplotlib.pyplot as plt

def plot_histogram(csv_file, title, out_path):
    """Create histogram from distance data"""
    # Read distances from CSV (assume first column is distance)
    distances = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                val = float(row[0])
                distances.append(val)
            except Exception:
                continue
    
    if not distances:
        return None
    
    plt.figure(figsize=(6, 3))
    plt.hist(distances, bins=50, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel('Distance (m)')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    return out_path 