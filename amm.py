import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QTextEdit, QListWidget, QListWidgetItem, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
import os
import datetime
import getpass
from PIL import Image
from PySide6.QtGui import QIcon
# Ensure the script's directory is in the path to find model_loader
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function that will likely look for the CSV relative to itself
# Always use absolute path relative to script for CSV (This comment implies model_loader.py should handle path resolution)
from model_loader import load_models_from_csv

# Helper to log errors to user's Downloads folder
def log_error(message, file_path=None, error=None):
    try:
        user = getpass.getuser()
        downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
        log_file = os.path.join(downloads, 'AMM_error_log.txt')
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] ")
            if file_path:
                f.write(f"File: {file_path} | ")
            if error:
                f.write(f"Error: {repr(error)} | ")
            f.write(f"{message}\n")
            # Add human-readable explanation for decode errors
            if error and (isinstance(error, UnicodeDecodeError) or 'decode' in str(type(error)).lower() or 'decode' in str(error).lower()):
                f.write("    If you see this, it means the file is not a text file (e.g., it's a video, image, or other binary file). This is normal for non-text files.\n")
    except Exception as e:
        print(f"Failed to write to error log: {e}")

class AMMApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Model Assessor (AMM)")
        self.setMinimumSize(900, 700)

        # This is the line where the error occurs if model_loader.py can't find the CSV
        try:
            self.models = load_models_from_csv()
        except FileNotFoundError as e:
            # You might want to handle this more gracefully, maybe show an error message
            print(f"CRITICAL ERROR: Could not load model data. {e}")
            print("Ensure 'model_reference.csv' is in the same directory as 'model_loader.py'.")
            # You could exit, or disable parts of the UI, or load default empty data
            self.models = [] # Assign empty list to avoid further errors using self.models
            # Maybe pop up a message box:
            # from PySide6.QtWidgets import QMessageBox
            # QMessageBox.critical(self, "Error", f"Failed to load model data:\n{e}\n\nPlease ensure 'model_reference.csv' exists next to 'model_loader.py'.")
            # sys.exit(1) # Or maybe just disable features

        self.sorted_models = self.models  # Default unsorted

        self.layout = QVBoxLayout(self)

        # Sort controls
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        # Ensure models aren't empty before trying to access keys if loading failed
        if self.models:
            # Assuming models is a list of dicts like [{'company': 'A', 'model': 'B', 'max_tokens': 100}, ...]
            # Let's dynamically get sort keys if possible, or use safe defaults
            # Note: Max Tokens needs numerical sort, others alphabetical
            self.sort_combo.addItems(["Company", "Model", "Max Tokens"])
        else:
             self.sort_combo.addItems(["N/A - Load Failed"]) # Indicate problem
             self.sort_combo.setEnabled(False) # Disable if no models

        self.sort_combo.currentIndexChanged.connect(self.sort_models)
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        self.layout.addLayout(sort_layout)

        # Model selection table with checkboxes
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(5)
        self.model_table.setHorizontalHeaderLabels(["Select", "Company", "Model", "Version", "Max Tokens"])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.model_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.model_table.setSortingEnabled(True)
        self.layout.addWidget(self.model_table)

        # Select All / Clear All buttons (stacked vertically, blue above red, centered)
        select_clear_layout = QVBoxLayout()
        select_clear_layout.setAlignment(Qt.AlignHCenter)
        self.select_all_button = QPushButton("Select All")
        self.clear_all_button = QPushButton("Clear All")
        self.select_all_button.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; min-width: 160px; max-width: 220px; min-height: 28px; max-height: 32px; border-radius: 6px; margin-bottom: 6px;")
        self.clear_all_button.setStyleSheet("background-color: #d70022; color: white; font-weight: bold; min-width: 160px; max-width: 220px; min-height: 28px; max-height: 32px; border-radius: 6px; margin-top: 6px;")
        self.select_all_button.clicked.connect(self.select_all_models)
        self.clear_all_button.clicked.connect(self.clear_all_models)
        select_clear_layout.addWidget(self.select_all_button, alignment=Qt.AlignHCenter)
        select_clear_layout.addWidget(self.clear_all_button, alignment=Qt.AlignHCenter)
        self.layout.addLayout(select_clear_layout)

        # Upload and Run buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        self.run_button = QPushButton("Run Assessment") # Slightly more descriptive
        self.run_button.clicked.connect(self.run_assessment)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.run_button)
        self.layout.addLayout(button_layout)

        # Word and Character counters
        self.word_count_label = QLabel("Words: 0")
        self.char_count_label = QLabel("Characters: 0")
        counter_layout = QHBoxLayout()
        counter_layout.addWidget(self.word_count_label)
        counter_layout.addWidget(self.char_count_label)
        self.layout.addLayout(counter_layout)

        # Text box
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Paste text here or upload a file...")
        self.text_edit.textChanged.connect(self.update_counters)
        self.layout.addWidget(self.text_edit)

        # Remove old Clear Text and Close button layouts
        # Add new bottom button row: Clear Text (blue) and Close (red), centered
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addStretch()
        self.clear_text_button = QPushButton("Clear Text")
        self.clear_text_button.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; min-width: 120px; max-width: 160px; min-height: 28px; max-height: 32px; border-radius: 6px;")
        self.clear_text_button.clicked.connect(self.clear_text_and_file)
        bottom_button_layout.addWidget(self.clear_text_button)

        self.exit_button = QPushButton("Close")
        self.exit_button.setStyleSheet("background-color: #d70022; color: white; font-weight: bold; min-width: 120px; max-width: 160px; min-height: 28px; max-height: 32px; border-radius: 6px;")
        self.exit_button.clicked.connect(self.close)
        bottom_button_layout.addWidget(self.exit_button)

        # Add fluffy green 'ico' button to the right of Close
        self.icon_button = QPushButton("ico")
        self.icon_button.setMinimumWidth(60)
        self.icon_button.setMaximumWidth(90)
        self.icon_button.setMinimumHeight(32)
        self.icon_button.setMaximumHeight(36)
        self.icon_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc40;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 12px;
                padding: 6px 18px;
                margin-left: 12px;
                margin-right: 8px;
                /* box-shadow: 0 2px 8px rgba(46,204,64,0.25); */
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.icon_button.setToolTip("Change app icon (.ico)")
        self.icon_button.clicked.connect(self.change_app_icon)
        bottom_button_layout.addWidget(self.icon_button)

        bottom_button_layout.addStretch()
        self.layout.addLayout(bottom_button_layout)

        self.uploaded_file_path = None
        self.uploaded_file_type_label = None

        # Load icon from config if exists
        self.icon_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'amm_icon_path.txt')
        if os.path.exists(self.icon_config_path):
            try:
                with open(self.icon_config_path, 'r', encoding='utf-8') as f:
                    icon_path = f.read().strip()
                    if os.path.exists(icon_path):
                        self.setWindowIcon(QIcon(icon_path))
            except Exception as e:
                log_error("Failed to load saved icon path.", error=e)

        # Populate table initially only if models loaded successfully
        if self.models:
            self.sort_models() # Populate table initially
        else:
            self.model_table.setRowCount(1)
            for col in range(self.model_table.columnCount()):
                self.model_table.setItem(0, col, QTableWidgetItem("Model loading failed."))
                self.model_table.item(0, col).setFlags(Qt.NoItemFlags)

    def sort_models(self):
        if not self.models: # Don't try to sort if loading failed
             return

        current_sort_key = self.sort_combo.currentText()

        if current_sort_key == "Max Tokens":
             sort_func = lambda x: int(x.get("max_tokens", 0))
             reverse = True
        elif current_sort_key == "Company":
             sort_func = lambda x: x.get("company", "").lower() # Sort case-insensitive
        elif current_sort_key == "Model":
             sort_func = lambda x: x.get("model", "").lower() # Sort case-insensitive
        else: # Default or fallback
             sort_func = lambda x: x.get("company", "").lower()

        try:
            self.sorted_models = sorted(self.models, key=sort_func)
        except Exception as e:
            print(f"Error during sorting: {e}")
            # Handle error, maybe revert to unsorted or default sort
            self.sorted_models = self.models
        self.populate_model_list()

    def populate_model_list(self):
        self.model_table.setRowCount(0)
        if not self.sorted_models:
            self.model_table.setRowCount(1)
            for col in range(self.model_table.columnCount()):
                self.model_table.setItem(0, col, QTableWidgetItem("No models available."))
                self.model_table.item(0, col).setFlags(Qt.NoItemFlags)
            return
        for row, model in enumerate(self.sorted_models):
            self.model_table.insertRow(row)
            # Checkbox with left padding
            checkbox = QCheckBox()
            checkbox.setStyleSheet("padding-left: 16px;")
            self.model_table.setCellWidget(row, 0, checkbox)
            self.model_table.setItem(row, 1, QTableWidgetItem(model.get('company', 'N/A')))
            self.model_table.setItem(row, 2, QTableWidgetItem(model.get('model', 'N/A')))
            self.model_table.setItem(row, 3, QTableWidgetItem(str(model.get('version', 'N/A'))))
            self.model_table.setItem(row, 4, QTableWidgetItem(str(model.get('max_tokens', 'N/A'))))

    def select_all_models(self):
        for row in range(self.model_table.rowCount()):
            widget = self.model_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(True)

    def clear_all_models(self):
        for row in range(self.model_table.rowCount()):
            widget = self.model_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)

    def selected_models_info(self):
        selected = []
        for row, model in enumerate(self.sorted_models):
            widget = self.model_table.cellWidget(row, 0)
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected.append(model)
        return selected

    def update_counters(self):
        text = self.text_edit.toPlainText()
        # Simple word count, might not be perfect for all cases
        word_count = len(text.split()) if text else 0
        char_count = len(text)
        self.word_count_label.setText(f"Words: {word_count}")
        self.char_count_label.setText(f"Characters: {char_count}")

    def is_text_only_selected(self):
        selected_models = [item.text() for item in self.model_table.selectedIndexes()]
        for model in self.sorted_models:
            model_label = f"{model['company']} - {model['model']} - {model['max_tokens']} tokens"
            if model_label in selected_models:
                if 'Text' not in model.get('api_types', []):
                    return False
        return True if selected_models else False

    def file_type_supported(self, file_is_binary, model):
        api_types = [t.lower() for t in model.get('api_types', [])]
        if file_is_binary:
            return any(t in api_types for t in ['image', 'multi-modal', 'multimodal'])
        else:
            return 'text' in api_types

    def get_file_type_label(self, path, is_binary):
        if not is_binary:
            ext = os.path.splitext(path)[1].lower()
            if ext in ['.py', '.js', '.cpp', '.c', '.java', '.rb', '.go', '.rs', '.ts', '.php', '.cs', '.swift', '.kt', '.scala', '.sh', '.bat', '.pl', '.r', '.jl', '.lua', '.sql', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.md', '.ipynb']:
                return 'Code'
            return 'Text'
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
            return 'Video'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico']:
            return 'Image'
        elif ext in ['.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a']:
            return 'Audio'
        elif ext in ['.pdf']:
            return 'PDF'
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return 'Archive'
        else:
            return 'Unknown'

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File to Assess", "", "All Files (*.*)")
        if path:
            self.uploaded_file_path = path
            try:
                is_binary = False
                ext = os.path.splitext(path)[1].lower()
                # Check for image file
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico']:
                    try:
                        with Image.open(path) as img:
                            img.verify()  # Will raise if image is corrupt
                    except Exception as e:
                        log_error("Failed to decode image file (possibly corrupt or unsupported).", file_path=path, error=e)
                        self.text_edit.setPlainText(f"Could not decode image: {os.path.basename(path)}")
                        return  # Stop further processing
                # Existing logic for text/binary detection...
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        f.read(1024)
                except Exception as e:
                    is_binary = True
                    log_error("File detected as binary or failed to read as text.", file_path=path, error=e)
                if is_binary:
                    file_size = os.path.getsize(path)
                    self.text_edit.setPlainText(f"Binary file detected. Size: {file_size} bytes")
                else:
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()  # No character limit
                            self.text_edit.setPlainText(content)
                    except Exception as e:
                        log_error("Failed to read file as text.", file_path=path, error=e)
                        self.text_edit.setPlaceholderText(f"Could not read file: {os.path.basename(path)}")
                print(f"File selected: {path}")
            except Exception as e:
                log_error("General file read error in upload_file.", file_path=path, error=e)
                print(f"Error reading file {path}: {e}")
                self.text_edit.setPlaceholderText(f"Could not read file: {os.path.basename(path)}")

    def run_assessment(self):
        selected_models = self.selected_models_info()
        if not selected_models:
            print("No models selected.")
            return
        data = None
        file_is_binary = False
        file_type_label = None
        file_size_bytes = 0
        if self.uploaded_file_path:
            data_type = "File"
            try:
                try:
                    with open(self.uploaded_file_path, 'r', encoding='utf-8') as f:
                        f.read(1024)
                except Exception as e:
                    file_is_binary = True
                    log_error("File detected as binary or failed to read as text in run_assessment.", file_path=self.uploaded_file_path, error=e)
                file_type_label = self.get_file_type_label(self.uploaded_file_path, file_is_binary)
                file_size_bytes = os.path.getsize(self.uploaded_file_path)
                if file_is_binary:
                    data = "X" * file_size_bytes
                else:
                    try:
                        with open(self.uploaded_file_path, 'r', encoding='utf-8') as f:
                            data = f.read()
                    except Exception as e:
                        log_error("Failed to read file as text in run_assessment.", file_path=self.uploaded_file_path, error=e)
                        return
            except Exception as e:
                log_error("General file read error in run_assessment.", file_path=self.uploaded_file_path, error=e)
                print(f"Failed to read file: {e}")
                return
        elif self.text_edit.toPlainText():
            data_type = "Text"
            data = self.text_edit.toPlainText()
            file_type_label = 'Text'
            file_size_bytes = len(data.encode('utf-8'))
        else:
            print("No input data.")
            return
        if not data:
            print("Input data is empty.")
            return
        results = []
        unsupported_models = []
        for model in selected_models:
            considered_type = file_type_label
            api_types = [t.lower() for t in model.get('api_types', [])]
            cost = 'Not Supported'
            send_tokens = get_tokens = total_model_tokens = total_tokens = 'Not Supported'
            # Treat code files as text if model supports text but not code
            if considered_type == 'Code' and ('code' in api_types or 'text' in api_types):
                # Use text logic for code files if 'text' is supported
                if model['input_cost'] is not None and model['output_cost'] is not None and model['max_tokens'] is not None:
                    estimated_input_tokens = max(1, int(file_size_bytes / 4))
                    estimated_output_tokens = int(estimated_input_tokens * 0.5)
                    total_model_tokens = estimated_input_tokens + estimated_output_tokens
                    send_tokens = estimated_input_tokens
                    get_tokens = estimated_output_tokens
                    total_tokens = total_model_tokens
                    cost = (send_tokens / 1000000) * model['input_cost'] + (get_tokens / 1000000) * model['output_cost']
                    cost = f"${cost:.6f}"
                else:
                    cost = 'Not Supported'
            # TEXT
            elif considered_type == 'Text' and 'text' in api_types:
                if model['input_cost'] is not None and model['output_cost'] is not None and model['max_tokens'] is not None:
                    estimated_input_tokens = max(1, int(file_size_bytes / 4))
                    estimated_output_tokens = int(estimated_input_tokens * 0.5)
                    total_model_tokens = estimated_input_tokens + estimated_output_tokens
                    send_tokens = estimated_input_tokens
                    get_tokens = estimated_output_tokens
                    total_tokens = total_model_tokens
                    cost = (send_tokens / 1000000) * model['input_cost'] + (get_tokens / 1000000) * model['output_cost']
                    cost = f"${cost:.6f}"
                else:
                    cost = 'Not Supported'
            # VIDEO
            elif considered_type == 'Video' and ('video' in api_types or 'multi-modal' in api_types or 'multimodal' in api_types):
                file_size_mb = file_size_bytes / (1024 * 1024)
                estimated_minutes = file_size_mb
                per_min_cost = model.get('video_cost', None)
                if per_min_cost is not None:
                    cost = estimated_minutes * per_min_cost
                    cost = f"${cost:.6f}"
                else:
                    # Use hardcoded default if not found
                    default_video_cost = 0.05
                    cost = estimated_minutes * default_video_cost
                    cost = f"${cost:.6f} (default rate)"
            # AUDIO
            elif considered_type == 'Audio' and ('audio' in api_types or 'multi-modal' in api_types or 'multimodal' in api_types):
                file_size_mb = file_size_bytes / (1024 * 1024)
                estimated_minutes = file_size_mb
                per_min_cost = model.get('audio_cost', None)
                if per_min_cost is not None:
                    cost = estimated_minutes * per_min_cost
                    cost = f"${cost:.6f}"
                else:
                    cost = 'Not Supported'
            # IMAGE
            elif considered_type == 'Image' and ('image' in api_types or 'multi-modal' in api_types or 'multimodal' in api_types):
                per_image_cost = model.get('image_cost', None)
                estimated_output_tokens = 512  # or model.get('image_output_tokens', 512)
                if per_image_cost is not None and model['output_cost'] is not None:
                    cost = per_image_cost + ((estimated_output_tokens / 1000000) * model['output_cost'])
                    cost = f"${cost:.6f}"
                    get_tokens = estimated_output_tokens
                    send_tokens = total_model_tokens = total_tokens = 'Not Supported'
                else:
                    cost = 'Not Supported'
            # UNKNOWN
            else:
                cost = 'Not Supported'
            if cost == 'Not Supported':
                unsupported_models.append(f"{model['company']} - {model['model']}")
                continue
            results.append({
                "Company": model['company'],
                "Model": model['model'],
                "Version": model['version'],
                "File Type Considered": considered_type,
                "API Types": ", ".join(model['api_types']),
                "Max Tokens per Call": model['max_tokens'] if model['max_tokens'] is not None else 'Not Supported',
                "Send Tokens": send_tokens,
                "Get Tokens": get_tokens,
                "Total Tokens": total_tokens,
                "Total Cost (USD)": cost
            })
        if unsupported_models:
            # Show a pop-up with a copyable text box listing unsupported models
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
            dialog = QDialog(self)
            dialog.setWindowTitle("Unsupported Models")
            layout = QVBoxLayout(dialog)
            label = QLabel("These LLMs will not support this file type or have no pricing available:")
            layout.addWidget(label)
            text_box = QTextEdit()
            text_box.setReadOnly(True)
            text_box.setPlainText("\n".join(unsupported_models))
            layout.addWidget(text_box)
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)
            dialog.exec()
        if results:
            self.show_assessment_modal(results)
        elif not results and not unsupported_models:
            print("No matching models found for assessment.")

    def show_assessment_modal(self, results):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog

        dialog = QDialog(self)
        dialog.setWindowTitle("Assessment Results")
        dialog.resize(1200, 600)  # 2x wider than typical
        layout = QVBoxLayout(dialog)

        table = QTableWidget()
        table.setColumnCount(len(results[0]))
        table.setHorizontalHeaderLabels(results[0].keys())
        table.setRowCount(len(results))
        for row_num, row_data in enumerate(results):
            for col_num, (key, value) in enumerate(row_data.items()):
                table.setItem(row_num, col_num, QTableWidgetItem(str(value)))

        table.setSortingEnabled(True)  # Enable sorting on columns

        layout.addWidget(table)

        export_button = QPushButton("Export to Excel")
        export_button.clicked.connect(lambda: self.export_to_excel(results))
        layout.addWidget(export_button)

        # Add blue Clear button and red Close button
        button_row_layout = QHBoxLayout()
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; min-width: 120px; max-width: 160px; min-height: 28px; max-height: 32px; border-radius: 6px;")
        clear_button.clicked.connect(table.clearContents)
        button_row_layout.addWidget(clear_button)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: #d70022; color: white; font-weight: bold; min-width: 120px; max-width: 160px; min-height: 28px; max-height: 32px; border-radius: 6px;")
        close_button.clicked.connect(dialog.close)
        button_row_layout.addWidget(close_button)

        layout.addLayout(button_row_layout)

        dialog.exec()

    def export_to_excel(self, results):
        import pandas as pd

        path, _ = QFileDialog.getSaveFileName(self, "Save As", "assessment_results.xlsx", "Excel Files (*.xlsx)")
        if path:
            df = pd.DataFrame(results)
            df.to_excel(path, index=False)
            print(f"Exported assessment results to {path}")

        # Maybe display results in a new window or a dedicated results area

    def clear_text_and_file(self):
        self.text_edit.clear()
        self.uploaded_file_path = None
        self.uploaded_file_type_label = None

    def change_app_icon(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select .ico file for app icon", "", "Icon Files (*.ico)")
        if path:
            try:
                self.setWindowIcon(QIcon(path))
                # Save path to config
                with open(self.icon_config_path, 'w', encoding='utf-8') as f:
                    f.write(path)
            except Exception as e:
                log_error("Failed to set or save app icon.", file_path=path, error=e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Apply styles or settings to the app if desired
    # app.setStyle('Fusion')
    window = AMMApp()
    window.show()
    sys.exit(app.exec())