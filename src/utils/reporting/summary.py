"""
Summary Generation Module
"""
import os
from ..analysis.statistics import parse_statistics, parse_mesh_measure
from .pdf_generator import generate_pdf_report

def summarize_comparison(run_dir):
    """Parse the comparison outputs and generate a human-readable summary"""
    c2c_stats = parse_statistics(os.path.join(run_dir, 'cloudcompare_c2c_report.txt'))
    c2m_stats = parse_statistics(os.path.join(run_dir, 'cloudcompare_c2m_report.txt'))
    mesh1_area, mesh1_volume = parse_mesh_measure(os.path.join(run_dir, 'mesh1_measure.txt'))
    mesh2_area, mesh2_volume = parse_mesh_measure(os.path.join(run_dir, 'mesh2_measure.txt'))
    
    area_diff = mesh2_area - mesh1_area if mesh1_area is not None and mesh2_area is not None else None
    volume_diff = mesh2_volume - mesh1_volume if mesh1_volume is not None and mesh2_volume is not None else None
    
    summary = []
    summary.append(f"Comparison Summary ({os.path.basename(run_dir)}):\n")
    summary.append(f"- Mean C2C distance: {c2c_stats.get('mean', 'N/A')} m")
    summary.append(f"- Max C2C distance: {c2c_stats.get('max', 'N/A')} m")
    summary.append(f"- Mean signed C2M distance: {c2m_stats.get('mean', 'N/A')} m")
    summary.append(f"- Max signed C2M distance: {c2m_stats.get('max', 'N/A')} m")
    summary.append(f"- Mesh1 area: {mesh1_area} m², Mesh2 area: {mesh2_area} m²" + (f" (Δ {area_diff:+.3f} m²)" if area_diff is not None else ""))
    summary.append(f"- Mesh1 volume: {mesh1_volume} m³, Mesh2 volume: {mesh2_volume} m³" + (f" (Δ {volume_diff:+.3f} m³)" if volume_diff is not None else ""))
    summary.append("")
    
    interpretation = []
    if area_diff is not None and abs(area_diff) > 0.01:
        interpretation.append(f"Surface area changed by {area_diff:+.3f} m².")
    if volume_diff is not None and abs(volume_diff) > 0.01:
        interpretation.append(f"Volume changed by {volume_diff:+.3f} m³.")
    if c2c_stats.get('max', 0) > 0.05:
        interpretation.append(f"Largest local change: {c2c_stats['max']*100:.1f} cm.")
    if not interpretation:
        interpretation.append("No significant anomalies detected.")
    
    summary.append("Interpretation:")
    for line in interpretation:
        summary.append(f"- {line}")
    
    summary_text = '\n'.join(summary)
    print(summary_text)
    
    with open(os.path.join(run_dir, 'summary.txt'), 'w') as f:
        f.write(summary_text)
    
    # Generate PDF report
    generate_pdf_report(run_dir) 