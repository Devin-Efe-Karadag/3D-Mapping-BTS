"""
Statistics Analysis Module
"""
import os

def parse_statistics(log_file):
    """Parse statistics from CloudCompare log files"""
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
    """Parse area and volume from mesh measurement files"""
    area = None
    volume = None
    with open(measure_file, 'r') as f:
        for line in f:
            if 'Surface' in line and 'area' in line:
                area = float(line.split(':')[-1].strip().split()[0])
            elif 'Volume' in line:
                volume = float(line.split(':')[-1].strip().split()[0])
    return area, volume 