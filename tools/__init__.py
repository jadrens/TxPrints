"""
PDF Processing Tools Package

This package provides unified access to all PDF processing tools
with consistent naming and default output suffixes.
"""

import os
import config
from .page_number_graph import add_page_numbers_graph
from .page_number_simple import add_page_numbers_simple
from .two_page import process_pdf_for_folding
from .four_paper import merge_pdf_pages_4_in_1_compatible


def add_graphical_page_numbers(input_path, output_path=None):
    """
    Add graphical page numbers (circles with adaptive sizing).
    
    :param input_path: Input PDF file path
    :param output_path: Output PDF file path (auto-generated if None)
    """
    if output_path is None:
        output_path = _generate_output_path(input_path, "graphical")
    add_page_numbers_graph(input_path, output_path)
    return output_path


def add_simple_page_numbers(input_path, output_path=None):
    """
    Add simple inverted page numbers (current/total format).
    
    :param input_path: Input PDF file path
    :param output_path: Output PDF file path (auto-generated if None)
    """
    if output_path is None:
        output_path = _generate_output_path(input_path, "simple")
    add_page_numbers_simple(input_path, output_path)
    return output_path


def rearrange_for_stapling(input_path, output_path=None, no_folding=False, unipage=False):
    """
    Rearrange PDF for 2-page stapling or layout.
    
    :param input_path: Input PDF file path
    :param output_path: Output PDF file path (auto-generated if None)
    :param no_folding: If True, no folding rearrangement
    :param unipage: If True, rearrange for unipage layout
    """
    if output_path is None:
        suffix = "nofold" if no_folding else "staple"
        output_path = _generate_output_path(input_path, suffix)
    
    split_page_num = config.NOFOLDING_PAGE_SPLIT if no_folding else config.NORMAL_PAGE_SPLIT
    process_pdf_for_folding(input_path, split_page_num=split_page_num, 
                          output_path=output_path, no_folding=no_folding, unipage=unipage)
    return output_path


def merge_4_in_1(input_path, output_path=None):
    """
    Merge PDF pages 4-in-1 format.
    
    :param input_path: Input PDF file path
    :param output_path: Output PDF file path (auto-generated if None)
    """
    if output_path is None:
        output_path = _generate_output_path(input_path, "4in1")
    merge_pdf_pages_4_in_1_compatible(input_path, output_path)
    return output_path


def _generate_output_path(input_path, suffix):
    """
    Generate output path with default suffix.
    
    :param input_path: Input file path
    :param suffix: Suffix to add
    :return: Output file path
    """
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_filename = f"{name}_{suffix}{ext}"
    return os.path.join(directory, output_filename)


# Legacy function names for backward compatibility
def add_page_number_graph(input_path, output_path):
    raise DeprecationWarning("Use add_graphical_page_numbers instead.")


def add_page_number(input_path, output_path):
    raise DeprecationWarning("Use add_simple_page_numbers instead.")


def re_2page_staple(input_path, output_path):
    raise DeprecationWarning("Use rearrange_for_stapling instead.")

def re_2page_nofold(input_path, output_path):
    raise DeprecationWarning("Use rearrange_for_stapling with no_folding=True instead.")