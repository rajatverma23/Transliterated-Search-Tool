import fitz  # PyMuPDF
from PIL import Image

class DocumentHandler:
    def __init__(self):
        self.pages = []  # List of PIL Images

    def load_document(self, file_path):
        self.pages = []
        if file_path.lower().endswith('.pdf'):
            self._load_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            self._load_image(file_path)
        return len(self.pages)

    def _load_pdf(self, file_path):
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300, alpha=False) # Force RGB (alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.pages.append(img)
        doc.close()

    def _load_image(self, file_path):
        img = Image.open(file_path)
        self.pages.append(img.convert('RGB'))

    def get_page(self, index):
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None
