from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTextEdit, QLabel, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
import os
import sys
import ctypes
from logger import default_logger as logger


ADMIN = True

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class Worker(QThread):
    output_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, command_args):
        super().__init__()
        self.command_args = command_args

    def run(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            process = subprocess.Popen(
                ["python", "batch_processor.py"] + self.command_args,
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                self.output_signal.emit(line.rstrip())
            
            process.wait()
        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()


class BatchProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None

    def initUI(self):
        self.setWindowTitle("Batch Processor GUI" + (" (Admin)" if ADMIN else " (No Admin)"))
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Command selection
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Select Command:"))
        self.command_combo = QComboBox()
        self.commands = {
            "Add Graphical Page Numbers": "add_page_number_graph",
            "Add Simple Page Numbers": "add_page_number",
            "Rearrange for 2-Page Stapling": "re_2page_staple",
            "Rearrange for 2-Page Layout (No Folding)": "re_2page_nofold",
            "Suit Normal Envelope": "suit_normal_envelop",
            "Suit Unifold Envelope": "suit_unifold_envelop",
            "Archive Files": "archive",
            "Clean Output Folder": "clean"
        }
        self.command_combo.addItems(self.commands.keys())
        hbox.addWidget(self.command_combo)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_command)
        hbox.addWidget(self.run_button)

        layout.addLayout(hbox)

        # Output
        layout.addWidget(QLabel("Output:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def run_command(self):
        selected_command = self.command_combo.currentText()
        if not selected_command:
            self.output_text.append("Please select a command.")
            return

        command_arg = self.commands[selected_command]
        if not ADMIN:
            command_args = [command_arg, "noadmin"]
        else:
            command_args = [command_arg]
        self.output_text.clear()
        self.output_text.append(f"Running: python batch_processor.py {command_arg}")
        self.run_button.setEnabled(False)

        self.worker = Worker(command_args)
        self.worker.output_signal.connect(self.update_output)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def update_output(self, output):
        logger.info(output)
        self.output_text.append(output)
    
    def worker_finished(self):
        self.run_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not is_admin():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("使用管理员可以使用MemDisk。")
        msg.setInformativeText("是否以管理员身份重启？")
        msg.setWindowTitle("需要管理员权限")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            script_path = os.path.abspath(__file__)
            subprocess.run(['powershell', 'Start-Process', 'python', f'"{script_path}"', '-Verb', 'RunAs'], check=True)
            sys.exit(0)
        else:
            ADMIN = False
            
    window = BatchProcessorGUI()
    window.show()
    sys.exit(app.exec())