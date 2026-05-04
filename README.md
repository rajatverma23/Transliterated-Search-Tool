# Transliterated-Search Tool

Welcome to the **Transliterated-Search Tool**! This is a PyQt5-based desktop application that allows users to upload PDF files or images, perform OCR using custom Tesseract weights, and perform powerful searches against the extracted text.

Our tool uniquely supports **Transliterated Search** (allowing you to type in ITRANS English and instantly search for Devanagari text) and **Fuzzy Search** (to account for OCR errors and misspelled variations) using an efficient Trie-based algorithm.

---

## 🌟 Features

- **Document Viewer & OCR Panel:** Side-by-side view comparing original document pages with OCR-extracted text. The OCR text is fully editable for manual corrections.
- **Save & Export OCR Text:** Save the extracted and edited text to multiple formats, including `.txt`, `.docx` (Word Document), and `.pdf`.
- **Load Existing OCR Text:** Resume your work by loading previously saved `.txt` or `.docx` OCR texts alongside your document without having to re-run OCR.
- **Language Selection:** Dynamically select from available Tesseract languages on your system via a dialog box right before starting the OCR process.
- **Large PDF Optimization & Background OCR:** Load and navigate massive PDFs effortlessly via a new pagination interface and lazy-loading. Run OCR entirely in the background, allowing you to freely view and edit already-processed pages without being blocked!
- **Custom OCR Modeling:** Load `.traineddata` Tesseract models to perform highly accurate OCR tailored for your use cases.
- **Transliteration (ITRANS to Devanagari):** Instead of needing a native Devanagari keyboard, simply type `bhaarat` in English, and the tool intelligently searches for `भारत`.
- **Fuzzy Search:** Built-in Levenshtein distance and Trie implementation intelligently match search terms even if the OCR result contains minor spelling errors.
- **Multi-document support:** Open and OCR multiple pages from PDFs or image files (.pdf, .png, .jpg, .jpeg, .bmp, .tiff).

## 🛠️ Prerequisites

Before you start, make sure you have the following installed on your system:
- **Python 3.8+**
- **Tesseract OCR Engine:** Install Tesseract on your system and add it to your system PATH. 
  - *Mac:* `brew install tesseract`
  - *Ubuntu:* `sudo apt-get install tesseract-ocr`
  - *Windows:* Download from the [UB-Mannheim repository](https://github.com/UB-Mannheim/tesseract/wiki).

## 🚀 Getting Started

Follow these steps to set up the tool locally:

### 1. Clone the repository
First, clone this repository to your local machine:
```bash
git clone https://github.com/rajatverma23/Transliterated-Search-Tool.git
cd Transliterated-Search Tool
```

### 1.1 Set the path to your tessdata
* On mac : `export TESSDATA_PREFIX=/opt/homebrew/share/tessdata`
* On Ubuntu : `export TESSDATA_PREFIX=/usr/share/tessdata`
* On Windows : `set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata`

### 2. Set up a virtual environment (Recommended)
It is highly recommended to use a virtual environment to keep dependencies isolated:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Requirements
Install all necessary Python libraries using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Finally, start the application:
```bash
python main.py
```

## 🧠 Application Architecture

For beginners wanting to understand the codebase:
- `main.py`: The entry point to start the PyQt UI.
- `ui_components.py`: Contains the `MainWindow` and `OCRWorker` logic defining the GUI, split panes, search coordination, and signals/slots.
- `document_handler.py`: Validates uploaded files and converts PDF pages to image slices using PyMuPDF and Pillow.
- `ocr_engine.py`: Encapsulates Tesseract configuration, custom model injections, and text extractions.
- `search_util.py`: Implements our custom search functionalities, including the `SearchUtil` for ITRANS conversions and the custom `Trie` struct for rapid fuzzy searching.

---

## 📜 License
This project is licensed under the MIT License.
