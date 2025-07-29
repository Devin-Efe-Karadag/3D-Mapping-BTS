import os
import csv
import matplotlib.pyplot as plt
from fpdf import FPDF

def parse_statistics(log_file):
    stats = {}
    with open(log_file, 'r') as f:
        for line in f:
            if 'Mean' in line:
                stats['mean'] = float(line.split(':')[-1].strip().split()[0])
            elif 'Std. dev.' in line:
                stats['stddev'] = float(line.split(':')[-1].strip().split()[0])
            elif 'Min dist.' in line or 'Min distance' in line:
                stats['min'] = float(line.split(':')[-1].strip().split()[0])
            elif 'Max dist.' in line or 'Max distance' in line:
                stats['max'] = float(line.split(':')[-1].strip().split()[0])
            elif 'RMS' in line:
                stats['rms'] = float(line.split(':')[-1].strip().split()[0])
    return stats

def parse_mesh_measure(measure_file):
    area = None
    volume = None
    with open(measure_file, 'r') as f:
        for line in f:
            if 'Surface' in line and 'area' in line:
                area = float(line.split(':')[-1].strip().split()[0])
            elif 'Volume' in line:
                volume = float(line.split(':')[-1].strip().split()[0])
    return area, volume

def plot_histogram(csv_file, title, out_path):
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

def generate_pdf_report(run_dir):
    """
    Generate a PDF report with summary, images, tables, and plots for the comparison in run_dir.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"3D Comparison Report: {os.path.basename(run_dir)}", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(5)
    # Add summary text
    summary_path = os.path.join(run_dir, 'summary.txt')
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            for line in f:
                pdf.multi_cell(0, 8, line.strip())
        pdf.ln(5)
    # Add screenshots
    for label, fname in [("C2C Screenshot", 'cloudcompare_c2c_screenshot.png'), ("C2M Screenshot", 'cloudcompare_c2m_screenshot.png')]:
        img_path = os.path.join(run_dir, fname)
        if os.path.exists(img_path):
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 8, label, ln=True)
            pdf.image(img_path, w=100)
            pdf.ln(5)
    # Add statistics tables
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, "Key Statistics:", ln=True)
    c2c_stats = parse_statistics(os.path.join(run_dir, 'cloudcompare_c2c_report.txt'))
    c2m_stats = parse_statistics(os.path.join(run_dir, 'cloudcompare_c2m_report.txt'))
    mesh1_area, mesh1_volume = parse_mesh_measure(os.path.join(run_dir, 'mesh1_measure.txt'))
    mesh2_area, mesh2_volume = parse_mesh_measure(os.path.join(run_dir, 'mesh2_measure.txt'))
    def stat_row(label, stats):
        return f"{label}: Mean={stats.get('mean', 'N/A')}, Max={stats.get('max', 'N/A')}, Min={stats.get('min', 'N/A')}, Stddev={stats.get('stddev', 'N/A')}, RMS={stats.get('rms', 'N/A')}"
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 7, stat_row("C2C", c2c_stats), ln=True)
    pdf.cell(0, 7, stat_row("C2M", c2m_stats), ln=True)
    pdf.cell(0, 7, f"Mesh1 area: {mesh1_area} m², volume: {mesh1_volume} m³", ln=True)
    pdf.cell(0, 7, f"Mesh2 area: {mesh2_area} m², volume: {mesh2_volume} m³", ln=True)
    pdf.ln(5)
    # Add histograms
    for label, csvname, plotname in [
        ("C2C Distance Histogram", 'cloudcompare_c2c_distances.csv', 'c2c_hist.png'),
        ("C2M Distance Histogram", 'cloudcompare_c2m_distances.csv', 'c2m_hist.png')]:
        csv_path = os.path.join(run_dir, csvname)
        plot_path = os.path.join(run_dir, plotname)
        if os.path.exists(csv_path):
            plot_histogram(csv_path, label, plot_path)
            if os.path.exists(plot_path):
                pdf.set_font("Arial", size=11)
                pdf.cell(0, 8, label, ln=True)
                pdf.image(plot_path, w=100)
                pdf.ln(5)
    # Save PDF
    pdf_path = os.path.join(run_dir, 'report.pdf')
    pdf.output(pdf_path)
    print(f"[INFO] PDF report generated: {pdf_path}")

def summarize_comparison(run_dir):
    """
    Parse the comparison outputs in run_dir, compute differences, print and save a human-readable summary.
    """
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
    # At the end, generate the PDF report
    generate_pdf_report(run_dir) 