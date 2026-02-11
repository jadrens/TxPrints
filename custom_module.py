import logging
import os

from mem_disk import MemDisk

from tools import (
    add_graphical_page_numbers,
    add_simple_page_numbers,
    rearrange_for_stapling,
    merge_4_in_1
)

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ADMIN = True


def add_page_number_graph(input_pdf_path: str, output_pdf_path: str):
    """Add graphical page numbers (circles with adaptive sizing)"""
    logger.info("Adding graphical page numbers to: %s", input_pdf_path)
    add_graphical_page_numbers(input_pdf_path, output_pdf_path)



def add_page_number(input_pdf_path: str, output_pdf_path: str):
    """Add simple inverted page numbers (current/total format)"""
    logger.info("Adding simple page numbers to: %s", input_pdf_path)
    add_simple_page_numbers(input_pdf_path, output_pdf_path)



def re_2page_staple(input_pdf_path: str, output_pdf_path: str):
    """Rearrange PDF for 2-page stapling (with folding)"""
    logger.info("Rearranging for 2-page stapling: %s", input_pdf_path)
    rearrange_for_stapling(input_pdf_path, output_pdf_path, no_folding=False)



def re_2page_nofold(input_pdf_path: str, output_pdf_path: str):
    """Rearrange PDF for 2-page layout (no folding)"""
    logger.info("Rearranging for 2-page layout (no folding): %s", input_pdf_path)
    rearrange_for_stapling(input_pdf_path, output_pdf_path, no_folding=True)



def suit_normal_envelop(input_pdf_path: str, output_pdf_path: str):
    """Add page numbers + rearrange for 2-page stapling (suitable for normal envelopes)"""
    logger.info("Processing for normal envelope: %s", input_pdf_path)
    if not ADMIN:
        temp_path = output_pdf_path.replace('.pdf', '_temp.pdf')
        add_simple_page_numbers(input_pdf_path, temp_path)
        # Then rearrange for stapling
        rearrange_for_stapling(temp_path, output_pdf_path, no_folding=False)
    else:
        # 使用内存盘做缓冲
        mem_disk = MemDisk(size="512MB", driver_letter="Z")
        try:
            mem_disk.mount_mem_disk()
            temp_path = output_pdf_path.replace('.pdf', '_temp.pdf')
            temp_path_file_name = os.path.basename(temp_path)
            temp_path = mem_disk.get_file_path(temp_path_file_name)
            add_simple_page_numbers(input_pdf_path, temp_path)
            # Then rearrange for stapling
            rearrange_for_stapling(temp_path, output_pdf_path, no_folding=False)
        finally:
            mem_disk.unmount_mem_disk()
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

def suit_unifold_envelop(input_pdf_path: str, output_pdf_path: str):
    """Add page numbers + rearrange for 2-page stapling (suitable for normal envelopes)"""
    logger.info("Processing for unfold envelope: %s", input_pdf_path)
    if not ADMIN:
        temp_path = output_pdf_path.replace('.pdf', '_temp.pdf')
        add_simple_page_numbers(input_pdf_path, temp_path)
        # Then rearrange for stapling
        rearrange_for_stapling(temp_path, output_pdf_path, no_folding=False, unipage=True)
    else:
        # 使用内存盘做缓冲
        mem_disk = MemDisk(size="512MB", driver_letter="Z")
        try:
            mem_disk.mount_mem_disk()
            temp_path = output_pdf_path.replace('.pdf', '_temp.pdf')
            temp_path_file_name = os.path.basename(temp_path)
            temp_path = mem_disk.get_file_path(temp_path_file_name)
            add_simple_page_numbers(input_pdf_path, temp_path)
            # Then rearrange for stapling
            rearrange_for_stapling(temp_path, output_pdf_path, no_folding=False, unipage=True)
        finally:
            mem_disk.unmount_mem_disk()
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)