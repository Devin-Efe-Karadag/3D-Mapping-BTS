"""
PDF Report Generator Module
"""
import os
from fpdf import FPDF
from ..analysis.statistics import parse_statistics, parse_mesh_measure
from ..analysis.visualization import plot_histogram

def generate_pdf_report(run_dir):
    """Generate a PDF report with summary, images, tables, and plots"""
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
    for label, fname in [("C2C Screenshot", 'custom_c2c_visualization.png'),
                        ("C2M Screenshot", 'custom_c2m_visualization.png')]:
        img_path = os.path.join(run_dir, fname)
        if os.path.exists(img_path):
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 8, label, ln=True)
            pdf.image(img_path, w=100)
            pdf.ln(5)
    
    # Add statistics tables
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, "Key Statistics:", ln=True)
    c2c_stats = parse_statistics(os.path.join(run_dir, 'custom_c2c_report.txt'))
    c2m_stats = parse_statistics(os.path.join(run_dir, 'custom_c2m_report.txt'))
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
        ("C2C Distance Histogram", 'custom_c2c_distances.csv', 'c2c_hist.png'),
        ("C2M Distance Histogram", 'custom_c2m_distances.csv', 'c2m_hist.png')]:
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
    return pdf_path 