"""
Reporting Module
"""
from .pdf_generator import generate_pdf_report
from .summary import summarize_comparison

__all__ = [
    'generate_pdf_report',
    'summarize_comparison'
] 