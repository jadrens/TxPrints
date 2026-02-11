import os
import sys
from logger import default_logger as logger
import ctypes
import subprocess

ADMIN=True

from custom_module import (
    add_page_number_graph,
    add_page_number,
    re_2page_staple,
    re_2page_nofold,
    suit_normal_envelop,
    suit_unifold_envelop
)
import custom_module



def get_folders():
    """Get input and output folder paths."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, "input")
    output_folder = os.path.join(script_dir, "output")
    return input_folder, output_folder


def check_folders(input_folder, output_folder):
    """Check if folders exist, create output if needed."""
    if not os.path.exists(input_folder):
        logger.error(f"Input folder '{input_folder}' does not exist.")
        return False

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logger.info(f"Created output folder: {output_folder}")
    return True


def get_pdf_files(input_folder):
    """Get list of PDF files in input folder."""
    return [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]


def get_output_filename(pdf_file, process_type):
    """Generate output filename based on process type."""
    name, ext = os.path.splitext(pdf_file)
    return f"{name}_processed{ext}"


def process_single_pdf(input_path, output_path, process_type, custom_function=None):
    """Process a single PDF file."""
    if not custom_function:
        logger.error("No custom function provided for processing.")
        return
    try:
        custom_function(input_path, output_path)
    except Exception as e:
        logger.error(f"Error processing file '{os.path.basename(input_path)}': {e}")


def process_pdfs_in_folders(custom_function=None):
    """
    Automatically scan PDF files in the input folder, process them using a custom function, and save to output folder.

    :param custom_function: Custom processing function, defined in custom_module.py
    """
    input_folder, output_folder = get_folders()

    if not check_folders(input_folder, output_folder):
        return

    pdf_files = get_pdf_files(input_folder)

    if not pdf_files:
        logger.warning("No PDF files found in input folder.")
        return

    logger.info("Found %s PDF files to process.", len(pdf_files))

    for pdf_file in pdf_files:
        input_path = os.path.join(input_folder, pdf_file)
        output_file = get_output_filename(pdf_file, "custom")
        output_path = os.path.join(output_folder, output_file)

        logger.info("Processing file: %s", pdf_file)
        process_single_pdf(input_path, output_path, "custom", custom_function)

    logger.info("All files processed!")


def parse_command_line_args():
    """Parse command line arguments and return custom_function."""

    # other commands
    other_commands = sys.argv[1:] if len(sys.argv) > 2 else None
    print(other_commands)
    if other_commands:
        for cmd in other_commands:
            match cmd:
                case "noadmin":
                    logger.debug("Setting ADMIN to False")
                    custom_module.ADMIN=False
    
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:  # pylint: disable=W0718
            logger.error("Error checking admin privileges: %s", e)
            return False

    if not is_admin() and custom_module.ADMIN:
        # Restart script with admin privileges
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, 
            " ".join(sys.argv), None, 1
        )
        sys.exit(0)

    if len(sys.argv) <= 1:
        print("Usage: python batch_processor.py <command>")
        print("Available commands:")
        print("  add_page_number_graph - Add graphical page numbers")
        print("  add_page_number - Add simple inverted page numbers")
        print("  re_2page_staple - Rearrange for 2-page stapling")
        print("  re_2page_nofold - Rearrange for 2-page layout (no folding)")
        print("  suit_normal_envelop - Add page numbers + 2-page stapling")
        print("  suit_unifold_envelop - Add page numbers + 2-page stapling (for unifold envelope)")
        print("  archive - Move input files to cache")
        print("  clean/clear - Clean output folder")
        sys.exit(1)

    custom_function = None  # pylint: disable=W0621

    arg = sys.argv[1].lower()
    if arg == "add_page_number_graph":
        custom_function = add_page_number_graph
    elif arg == "add_page_number":
        custom_function = add_page_number
    elif arg == "re_2page_staple":
        custom_function = re_2page_staple
    elif arg == "re_2page_nofold":
        custom_function = re_2page_nofold
    elif arg == "suit_normal_envelop":
        custom_function = suit_normal_envelop
    elif arg == "suit_unifold_envelop":
        custom_function = suit_unifold_envelop
    elif arg in ["clean", "clear"]:
        run_file_manager("clean")
        return None
    elif arg == "archive":
        run_file_manager("archive")
        return None
    else:
        logger.error("Unknown command: %s", sys.argv[1])
        print("Available commands:")
        print("  add_page_number_graph - Add graphical page numbers")
        print("  add_page_number - Add simple inverted page numbers")
        print("  re_2page_staple - Rearrange for 2-page stapling")
        print("  re_2page_nofold - Rearrange for 2-page layout (no folding)")
        print("  suit_normal_envelop - Add page numbers + 2-page stapling")
        print("  suit_unifold_envelop - Add page numbers + 2-page stapling (for unifold envelope)")
        print("  archive - Move input files to cache")
        print("  clean/clear - Clean output folder")
        sys.exit(1)
                    


    return custom_function


def run_file_manager(action):
    """Run file_manager.py with the specified action."""
    python_cmd = "python" if os.name == 'nt' else "python3"
    result = subprocess.run(
        [python_cmd, "file_manager.py", action],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        check=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)


if __name__ == "__main__":
    custom_function = parse_command_line_args()
    if custom_function is not None:
        try:
            process_pdfs_in_folders(custom_function)
        except Exception as e:  # pylint: disable=W0718
            logger.error("Error processing PDFs: %s", e)
