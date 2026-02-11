[中文版本 (Chinese Version)](docs/README_cn.md)

# PDF Printing Tool

This is a collection of tools for PDF file processing and print preparation, mainly used for adding page numbers, rearranging pages to adapt to different printing needs (such as two-page stapling), and processing PDF formats suitable for different types of envelopes.

## Project Structure

- `batch_processor.py` - Command-line tool
- `gui_app.py` - GUI version (based on PyQt6)
- `custom_module.py` - Core functionality module
- `tools/` - Specific PDF processing tool implementations
- `logger.py` - Logging module
- `mem_disk.py` - Memory disk management module (for improving processing speed)
- `file_manager.py` - File management tool
- `input/` - Input PDF file directory
- `output/` - Output directory for processed PDF files
- `docs/` - Documentation directory

## Features

### 1. Add Page Numbers
- `add_page_number_graph` - Add graphical page numbers (circles with adaptive sizing)
- `add_page_number` - Add simple inverted page numbers (current/total format)

### 2. Page Rearrangement
- `re_2page_staple` - Rearrange PDF pages for 2-page stapling (with folding)
- `re_2page_nofold` - Rearrange PDF pages for 2-page layout (no folding)

### 3. Envelope Adaptation
- `suit_normal_envelop` - Add page numbers and rearrange pages for standard envelopes
- `suit_unifold_envelop` - Add page numbers and rearrange pages for unifold envelopes

### 4. File Management
- `archive` - Move input files to cache directory
- `clean/clear` - Clean output folder

## Installation

1. Ensure Python 3.7+ is installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Ensure `input` and `output` directories exist, they will be created automatically if not present

## Usage

### Command-line Tool (batch_processor.py)

```bash
python batch_processor.py <command>
```

Examples:
```bash
# Add graphical page numbers
python batch_processor.py add_page_number_graph

# Rearrange pages for 2-page stapling
python batch_processor.py re_2page_staple

# Process PDF for standard envelope
python batch_processor.py suit_normal_envelop

# Clean output folder
python batch_processor.py clean
```

### GUI Tool (gui_app.py)

1. Run the GUI application:
   ```bash
   python gui_app.py
   ```

2. Select the desired command in the interface and click the "Run" button to execute

3. Execution results will be displayed in the output window below

## Notes

1. **Administrator Privileges**:
   - When running as administrator, the tool uses memory disk as buffer to improve processing speed
   - When running without administrator privileges, it uses temporary files as buffer

2. **File Processing**:
   - The tool automatically processes all PDF files in the `input` directory
   - Processed files are saved in the `output` directory with `_processed` suffix added to the filename

3. **Dependencies**:
   - GUI version requires PyQt6 installation
   - Core functionality depends on PDF processing modules in the `tools` directory

4. **Limitations**:
   - Only supports PDF files
   - Large PDF files may require longer processing time
   - Some features may require specific printer support

## FAQ

- **Why do I need administrator privileges?**
  - Administrator privileges are used to create and manage memory disks to improve processing speed, especially for large PDF files

- **Where are the processed files?**
  - Processed files are saved in the `output` directory

- **How to process multiple PDF files?**
  - Simply put all PDF files into the `input` directory, and the tool will automatically process all files

## Version Information

- Personal use tool, no maintenance guarantee
- For any issues, please modify the code yourself

## License

This project is for personal use only, no specific license specified.

---

