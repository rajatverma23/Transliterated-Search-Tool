import sys
import json
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSplitter, QScrollArea, QLabel, 
                             QTextEdit, QFileDialog, QLineEdit, QCheckBox, 
                             QMessageBox, QProgressDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QTextCursor, QTextDocument

from document_handler import DocumentHandler
from ocr_engine import OCREngine
from search_util import SearchUtil, Trie

class OCRWorker(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(int, str)
    finished = pyqtSignal()

    def __init__(self, document_handler, ocr_engine):
        super().__init__()
        self.doc_handler = document_handler
        self.ocr_engine = ocr_engine
        self.is_running = True

    def run(self):
        total_pages = len(self.doc_handler.pages)
        for i in range(total_pages):
            if not self.is_running:
                break
            img = self.doc_handler.get_page(i)
            text = self.ocr_engine.process_image(img)
            self.result.emit(i, text)
            self.progress.emit(i + 1)
        self.finished.emit()

    def stop(self):
        self.is_running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transliterated-Search Tool")
        self.resize(1200, 800)

        self.doc_handler = DocumentHandler()
        self.ocr_engine = OCREngine()
        
        self.page_labels = []
        self.text_edits = []
        self.current_search_results = []
        self.current_search_index = -1

        self.worker = None

        self.init_ui()
        self.load_config()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # ---- Top Toolbar ----
        toolbar_layout = QHBoxLayout()
        
        self.btn_open = QPushButton("Open PDF/Image")
        self.btn_open.setMinimumWidth(180)
        self.btn_open.clicked.connect(self.open_file)

        self.btn_load_model = QPushButton("Load Custom Model")
        self.btn_load_model.setMinimumWidth(180)
        self.btn_load_model.clicked.connect(self.load_model)
        
        self.btn_ocr = QPushButton("Run OCR")
        self.btn_ocr.setMinimumWidth(100)
        self.btn_ocr.clicked.connect(self.run_ocr)
        self.btn_ocr.setEnabled(False)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search OCR Text (Use ITRANS for transliteration e.g. bhaarat)")
        
        self.chk_transliterate = QCheckBox("Transliterate (to Devanagari)")
        self.chk_transliterate.setChecked(True)

        self.chk_fuzzy = QCheckBox("Fuzzy Search")
        self.chk_fuzzy.setChecked(False)

        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.perform_search)

        self.btn_prev = QPushButton("< Prev")
        self.btn_prev.clicked.connect(self.search_prev)

        self.btn_next = QPushButton("Next >")
        self.btn_next.clicked.connect(self.search_next)

        toolbar_layout.addWidget(self.btn_open)
        toolbar_layout.addWidget(self.btn_load_model)
        toolbar_layout.addWidget(self.btn_ocr)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.chk_transliterate)
        toolbar_layout.addWidget(self.chk_fuzzy)
        toolbar_layout.addWidget(self.btn_search)
        toolbar_layout.addWidget(self.btn_prev)
        toolbar_layout.addWidget(self.btn_next)

        # ---- Main Content Splitter ----
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Document)
        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        # Using AlignCenter for the layout so the placeholder is centered vertically and horizontally initially
        self.left_layout.setAlignment(Qt.AlignCenter)

        self.left_placeholder = QLabel("PDF Viewer Area")
        self.left_placeholder.setAlignment(Qt.AlignCenter)
        self.left_placeholder.setStyleSheet("color: gray; font-size: 24px;")
        self.left_layout.addWidget(self.left_placeholder)

        self.left_scroll.setWidget(self.left_widget)

        # Right Panel (OCR Text)
        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setAlignment(Qt.AlignCenter)

        self.right_placeholder = QLabel("OCR Text Area")
        self.right_placeholder.setAlignment(Qt.AlignCenter)
        self.right_placeholder.setStyleSheet("color: gray; font-size: 24px;")
        self.right_layout.addWidget(self.right_placeholder)

        self.right_scroll.setWidget(self.right_widget)

        self.splitter.addWidget(self.left_scroll)
        self.splitter.addWidget(self.right_scroll)
        self.splitter.setSizes([600, 600])

        main_layout.addLayout(toolbar_layout)
        main_layout.addWidget(self.splitter)

        # Link scrollbars
        self.left_scroll.verticalScrollBar().valueChanged.connect(self.sync_scroll_right)
        self.right_scroll.verticalScrollBar().valueChanged.connect(self.sync_scroll_left)

    def sync_scroll_right(self, value):
        self.right_scroll.verticalScrollBar().setValue(value)

    def sync_scroll_left(self, value):
        self.left_scroll.verticalScrollBar().setValue(value)

    def clear_panels(self):
        for i in reversed(range(self.left_layout.count())): 
            self.left_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.right_layout.count())): 
            self.right_layout.itemAt(i).widget().setParent(None)
        
        self.page_labels.clear()
        self.text_edits.clear()
        self.current_search_results.clear()
        self.current_search_index = -1

    def load_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Tesseract Model (.traineddata)", "", "Tesseract Model (*.traineddata)")
        if file_path:
            tessdata_dir = os.path.dirname(file_path)
            model_name = os.path.basename(file_path).split('.')[0]
            self.ocr_engine.set_config(lang=model_name, tessdata_dir=tessdata_dir)
            
            # Save config
            config_data = {"lang": model_name, "tessdata_dir": tessdata_dir}
            try:
                with open("config.json", "w") as f:
                    json.dump(config_data, f)
            except Exception as e:
                print(f"Failed to save config: {e}")

            QMessageBox.information(self, "Model Loaded", f"Successfully loaded custom OCR model: {model_name}\n\nConfiguration has been saved for future sessions.")
            self.btn_ocr.setText(f"Run OCR")

    def load_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                    lang = config_data.get("lang")
                    tessdata_dir = config_data.get("tessdata_dir")
                    if lang and tessdata_dir and os.path.exists(tessdata_dir):
                        self.ocr_engine.set_config(lang=lang, tessdata_dir=tessdata_dir)
                        self.btn_ocr.setText(f"Run OCR")
            except Exception as e:
                print(f"Failed to load config: {e}")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Document", "", "Supported Files (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff)")
        if file_path:
            self.clear_panels()
            self.left_layout.setAlignment(Qt.AlignTop)
            self.right_layout.setAlignment(Qt.AlignTop)
            try:
                num_pages = self.doc_handler.load_document(file_path)
                
                for i in range(num_pages):
                    img = self.doc_handler.get_page(i)
                    
                    # Convert PIL to QPixmap
                    data = img.tobytes("raw", "RGB")
                    # Use .copy() to decouple QImage from the temporary python bytes object `data`
                    bytes_per_line = 3 * img.size[0]
                    qim = QImage(data, img.size[0], img.size[1], bytes_per_line, QImage.Format_RGB888).copy()
                    pixmap = QPixmap.fromImage(qim)
                    
                    label = QLabel()
                    # Scale down slightly to fit typical screen width (e.g. 500 px width)
                    scaled_pixmap = pixmap.scaledToWidth(550, Qt.SmoothTransformation)
                    label.setPixmap(scaled_pixmap)
                    label.setAlignment(Qt.AlignCenter)
                    self.page_labels.append(label)
                    self.left_layout.addWidget(label)
                    
                    text_edit = QTextEdit()
                    text_edit.setReadOnly(True)
                    text_edit.setMinimumHeight(scaled_pixmap.height() + 10)
                    text_edit.setPlaceholderText(f"Waiting for OCR (Page {i+1})...")
                    self.text_edits.append(text_edit)
                    self.right_layout.addWidget(text_edit)
                    
                self.btn_ocr.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load document: {e}")

    def run_ocr(self):
        if not self.doc_handler.pages:
            return

        self.btn_ocr.setEnabled(False)
        self.btn_open.setEnabled(False)
        
        self.progress_dialog = QProgressDialog("Running OCR...", "Cancel", 0, len(self.doc_handler.pages), self)
        self.progress_dialog.setWindowTitle("Processing")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.canceled.connect(self.cancel_ocr)

        self.worker = OCRWorker(self.doc_handler, self.ocr_engine)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.result.connect(self.update_ocr_text)
        self.worker.finished.connect(self.ocr_finished)
        self.worker.start()

    def update_ocr_text(self, index, text):
        if 0 <= index < len(self.text_edits):
            self.text_edits[index].setPlainText(text)

    def cancel_ocr(self):
        if self.worker:
            self.worker.stop()

    def ocr_finished(self):
        self.btn_ocr.setEnabled(True)
        self.btn_open.setEnabled(True)
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

    def perform_search(self):
        self.current_search_results.clear()
        self.current_search_index = -1
        
        # Clear previous highlights
        for te in self.text_edits:
            cursor = te.textCursor()
            cursor.select(QTextCursor.Document)
            fmt = cursor.charFormat()
            fmt.setBackground(Qt.transparent)
            cursor.setCharFormat(fmt)
            cursor.clearSelection()
            te.setTextCursor(cursor)
            
        raw_query = self.search_input.text()
        if not raw_query.strip():
            return

        query = raw_query
        if self.chk_transliterate.isChecked():
            query = SearchUtil.transliterate_query(raw_query)
            # Update search box to show the transliterated text? Or keep visual feedback.
            # We will show the actual search term in the box
            self.search_input.setText(f"{raw_query} => {query}")
        else:
            # If changed mind, strip => part
            if "=>" in raw_query:
                query = raw_query.split("=>")[1].strip()

        words_to_search = {query}

        if self.chk_fuzzy.isChecked():
            trie = Trie()
            for te in self.text_edits:
                text = te.toPlainText()
                for token in text.split():
                    cleaned = token.strip('.,()[]{}"\'`~?!;:-\n\t')
                    if cleaned:
                        trie.insert(cleaned)
            
            fuzzy_matches = set()
            for q_word in query.split():
                matches = trie.search(q_word)
                for m, _ in matches:
                    fuzzy_matches.add(m)
            
            if fuzzy_matches:
                words_to_search = fuzzy_matches

        # Find all occurrences in all text edits
        for i, te in enumerate(self.text_edits):
            doc = te.document()
            for w in words_to_search:
                cursor = QTextCursor(doc)
                
                while not cursor.isNull() and not cursor.atEnd():
                    if self.chk_fuzzy.isChecked():
                        cursor = doc.find(w, cursor)
                    else:
                        cursor = doc.find(w, cursor, QTextDocument.FindCaseSensitively)
                        
                    if not cursor.isNull():
                        # Highlight
                        fmt = cursor.charFormat()
                        fmt.setBackground(Qt.yellow)
                        cursor.setCharFormat(fmt)
                        self.current_search_results.append((i, cursor))

        # Sort the results by page index and then by position within page
        self.current_search_results.sort(key=lambda x: (x[0], x[1].position()))

        if self.current_search_results:
            self.current_search_index = 0
            self.highlight_current_search()
        else:
            QMessageBox.information(self, "Search", f"No results found for '{query}'.")

    def highlight_current_search(self):
        if not self.current_search_results or self.current_search_index < 0:
            return
            
        page_idx, cursor = self.current_search_results[self.current_search_index]
        target_editor = self.text_edits[page_idx]
        
        target_editor.setFocus()
        target_editor.setTextCursor(cursor)
        
        # Scroll the right panel to the widget
        self.right_scroll.ensureWidgetVisible(target_editor)

    def search_next(self):
        if not self.current_search_results:
            return
        self.current_search_index = (self.current_search_index + 1) % len(self.current_search_results)
        self.highlight_current_search()

    def search_prev(self):
        if not self.current_search_results:
            return
        self.current_search_index = (self.current_search_index - 1) % len(self.current_search_results)
        self.highlight_current_search()
